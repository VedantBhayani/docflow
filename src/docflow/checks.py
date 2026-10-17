"""Deterministic Checks on extracted Fields. IDs follow research note 01 and spec section 6.

Checks read parsed values only. A key field that is MISSING or UNGROUNDED already
raises an Evidence Flag (E1/E2) in the pipeline; the presence Checks here (A-series)
report the legal requirement it breaks.
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from docflow.gstin import STATE_CODES, normalise, validate_gstin
from docflow.models import Field, Flag, Severity
from docflow.parse import parse_amount, parse_date, parse_rate

B, W = Severity.BLOCKING, Severity.WARNING
R46 = "CGST Rule 46, https://taxinformation.cbic.gov.in (research note 01, section A)"
IGST_ACT = "IGST Act s.7 and s.8, https://taxinformation.cbic.gov.in (research note 01, section C)"
N9_2025 = "Notification 9/2025-Integrated Tax (Rate), 17-9-2025 (research note 01, addendum)"


@dataclass(frozen=True)
class CheckInfo:
    id: str
    severity: Severity
    description: str
    source: str


CATALOGUE = [
    CheckInfo("E1", B, "A value's text is not printed where the extractor says it is (not grounded). Blocking for key fields, tax totals, place of supply and line amounts/rates; warning for names, addresses, IRN, descriptions and units.", "DocFlow evidence rule"),
    CheckInfo("E2", B, "A key field was not found on the document.", "DocFlow evidence rule"),
    CheckInfo("E3", B, "Independent sources (LLM, rule extractor, QR) disagree on a field.", "DocFlow evidence rule"),
    CheckInfo("G1", B, "GSTIN is in the 15-character GSTIN format.", "GSTIN structure, research note 01, section G"),
    CheckInfo("G2", B, "GSTIN state code is in the GST state-code master.", "https://einvoice1.gst.gov.in/Others/MasterCodes"),
    CheckInfo("G3", B, "GSTIN's PAN part has a valid holder-type character.", "PAN structure, research note 01, G3"),
    CheckInfo("G4", B, "GSTIN entity number is not 0.", "research note 01, G4"),
    CheckInfo("G5", B, "GSTIN check digit (Luhn mod 36) is correct.", "Empirical, 74/74 bank-published GSTINs; research note 01"),
    CheckInfo("A1", B, "Supplier name, address and GSTIN are printed.", R46 + " (a)"),
    CheckInfo("A2", B, "Invoice number is printed: at most 16 characters, only letters, digits, / and -.", R46 + " (b)"),
    CheckInfo("A3", B, "Invoice number is unique for the supplier within a financial year (checked across the batch).", R46 + " (b)"),
    CheckInfo("A4", B, "Invoice date is printed and is a real date.", R46 + " (c)"),
    CheckInfo("A5", B, "Recipient name, address and GSTIN are printed (B2B).", R46 + " (d)"),
    CheckInfo("A7", W, "HSN/SAC has at least 4 digits (6 if the supplier is e-invoice-liable, i.e. a QR is present).", "Notification 78/2020-CT; research note 01, section D"),
    CheckInfo("A9", W, "Goods lines show quantity and unit.", R46 + " (i)"),
    CheckInfo("A10", B, "Total value of supply is printed.", R46 + " (j)"),
    CheckInfo("A11", B, "Taxable value is printed (in total and on each line).", R46 + " (k)"),
    CheckInfo("A12", B, "Tax rate is printed on each line.", R46 + " (l)"),
    CheckInfo("A13", B, "Tax amount is printed on each line.", R46 + " (m)"),
    CheckInfo("A14", W, "Place of supply is printed for an inter-state supply.", R46 + " (n)"),
    CheckInfo("A16", W, "Reverse-charge indicator is printed.", R46 + " (p)"),
    CheckInfo("C2", B, "Intra-state supply carries CGST + SGST/UTGST, not IGST.", IGST_ACT),
    CheckInfo("C3", B, "Inter-state supply carries IGST, not CGST/SGST.", IGST_ACT),
    CheckInfo("C4", B, "CGST equals SGST/UTGST (rate and amount).", "Rate notifications set CGST at half the GST rate; research note 01, C4"),
    CheckInfo("C6", B, "Line tax = taxable x rate; totals = sum of lines; grand total reconciles; round-off < Rs 1.", "CGST Act s.170; tolerances are a design choice"),
    CheckInfo("C6Q", W, "Line quantity x unit price equals the taxable value (a mismatch may be a discount).", "Arithmetic consistency"),
    CheckInfo("C7", B, "Each rate is a valid slab on the invoice date (blocking for goods after 22.09.2025, warning otherwise).", N9_2025),
    CheckInfo("Q1", B, "E-invoice QR signature verifies against the selected trust store (blocking if a held key fails or the issuer is wrong; warning if the signing key is not held).", "NIC QR Code procedure; RFC 7515/7518 (RS256)"),
    CheckInfo("Q2", B, "Signed QR matches the printed supplier/recipient GSTIN, document no., date, total value (Rs 1), line count and main HSN.", "NIC QR Code procedure (research note 02)"),
    CheckInfo("Q3", B, "Printed IRN equals the IRN in the signed QR.", "Rule 46(r); research note 02"),
    CheckInfo("Q3R", W, "QR IRN equals SHA-256(GSTIN + FY + doc type + doc no.); NIC's canonicalisation is unverified, so warning only.", "einv-apisandbox.nic.in/irn.html"),
    CheckInfo("B3", W, "IRN generated within 30 days of the invoice date.", "GSTN advisory 05.11.2024 (AATO >= Rs 10 Cr)"),
    CheckInfo("P1", B, "Scanned page is readable (mean OCR confidence >= 0.80).", "DocFlow scan rule"),
    CheckInfo("C8", W, "Reverse charge is Yes but the supplier charged GST.", R46 + " (p), CGST Act s.9(3)/(4)"),
]
_INFO = {c.id: c for c in CATALOGUE}

REFORM_DATE = date(2025, 9, 22)
GOODS_SLABS_POST_REFORM = {Decimal(x) for x in ["0", "0.25", "1.5", "3", "5", "18", "28", "40"]}  # verified, N9_2025
SERVICE_SLABS_POST_REFORM = {Decimal(x) for x in ["0", "5", "18", "40"]}  # NOT verified -> warning only
SLABS_PRE_REFORM = {Decimal(x) for x in ["0", "0.1", "0.25", "3", "5", "12", "18", "28"]}  # NOT re-verified -> warning only
INVOICE_NO = re.compile(r"^[A-Za-z0-9/\-]{1,16}$")
STATE_NAMES = {
    "jammu and kashmir": "01", "himachal pradesh": "02", "punjab": "03", "chandigarh": "04", "uttarakhand": "05", "haryana": "06",
    "delhi": "07", "rajasthan": "08", "uttar pradesh": "09", "bihar": "10", "sikkim": "11", "arunachal pradesh": "12", "nagaland": "13",
    "manipur": "14", "mizoram": "15", "tripura": "16", "meghalaya": "17", "assam": "18", "west bengal": "19", "jharkhand": "20",
    "odisha": "21", "chhattisgarh": "22", "madhya pradesh": "23", "gujarat": "24", "maharashtra": "27", "karnataka": "29", "goa": "30",
    "lakshadweep": "31", "kerala": "32", "tamil nadu": "33", "puducherry": "34", "andaman and nicobar islands": "35", "telangana": "36",
    "andhra pradesh": "37", "ladakh": "38",
}
ONE, CENT = Decimal("1"), Decimal("0.01")


def flag(check_id: str, message: str, fields: tuple[str, ...] = (), severity: Severity | None = None) -> Flag:
    return Flag(check_id, severity or _INFO[check_id].severity, message, fields)


def _text(f: Field | None) -> str | None:
    return f.text.strip() if f is not None and f.text and f.text.strip() else None


def _amt(f: Field | None) -> Decimal | None:
    return parse_amount(_text(f))


def _z(f: Field | None) -> Decimal:
    v = _amt(f)
    return v if v is not None else Decimal(0)


def _is_service(hsn: str | None) -> bool:
    return bool(hsn) and re.sub(r"\D", "", hsn).startswith("99")


def financial_year(d: date) -> str:
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{(start + 1) % 100:02d}"


def pos_code(fields: dict[str, Field]) -> str | None:
    pos = _text(fields.get("place_of_supply"))
    if not pos:
        return None
    m = re.search(r"\b(\d{2})\b", pos)
    if m and m.group(1) in STATE_CODES:
        return m.group(1)
    name = re.sub(r"[^a-z ]", " ", pos.lower())
    for state, code in sorted(STATE_NAMES.items(), key=lambda kv: -len(kv[0])):
        if re.search(rf"\b{state}\b", name):
            return code
    return None


# ---------------------------------------------------------------- GSTIN (G1-G5)

GSTIN_MESSAGES = {
    "G1": "GSTIN is not in the 15-character GSTIN format.",
    "G2": "GSTIN state code is not in the GST state-code master.",
    "G3": "GSTIN's PAN part has an invalid holder-type character.",
    "G4": "GSTIN entity number cannot be 0.",
    "G5": "GSTIN check digit is wrong: the number is mistyped, misread or invalid.",
}


def check_gstins(fields: dict[str, Field]) -> list[Flag]:
    out = []
    for name in ("supplier_gstin", "recipient_gstin"):
        g = _text(fields.get(name))
        if not g:
            continue
        for check_id in validate_gstin(g)[:1]:  # the first failure is the actionable one
            who = "Supplier" if name.startswith("supplier") else "Recipient"
            out.append(flag(check_id, f"{who} {GSTIN_MESSAGES[check_id]}", (name,)))
    return out


# ---------------------------------------------------------------- Mandatory particulars (A-series)

def check_mandatory(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    out = []
    for check_id, party, names in [("A1", "Supplier", ("supplier_name", "supplier_address", "supplier_gstin")),
                                   ("A5", "Recipient", ("recipient_name", "recipient_address", "recipient_gstin"))]:
        missing = [n for n in names if not _text(fields.get(n))]
        if missing:
            out.append(flag(check_id, f"{party} particulars missing: {', '.join(m.split('_', 1)[1] for m in missing)}.", tuple(missing)))
    inv_no = _text(fields.get("invoice_no"))
    if not inv_no:
        out.append(flag("A2", "Invoice number is not printed.", ("invoice_no",)))
    elif not INVOICE_NO.match(inv_no):
        out.append(flag("A2", f"Invoice number '{inv_no}' breaks Rule 46(b): at most 16 characters, only letters, digits, '/' and '-'.", ("invoice_no",)))
    raw_date = _text(fields.get("invoice_date"))
    if not raw_date:
        out.append(flag("A4", "Invoice date is not printed.", ("invoice_date",)))
    elif parse_date(raw_date) is None:
        out.append(flag("A4", f"Invoice date '{raw_date}' is not a valid date.", ("invoice_date",)))
    if _amt(fields.get("grand_total")) is None:
        out.append(flag("A10", "Total value of supply (grand total) is not printed or unreadable.", ("grand_total",)))
    if _amt(fields.get("taxable_total")) is None:
        out.append(flag("A11", "Total taxable value is not printed or unreadable.", ("taxable_total",)))
    for i, ln in enumerate(lines):
        n = i + 1
        if _amt(ln.get("taxable_value")) is None:
            out.append(flag("A11", f"Line {n}: taxable value is not printed.", (f"lines.{i}.taxable_value",)))
        if parse_rate(_text(ln.get("gst_rate"))) is None:
            out.append(flag("A12", f"Line {n}: tax rate is not printed.", (f"lines.{i}.gst_rate",)))
        if all(_amt(ln.get(h)) is None for h in ("cgst", "sgst", "igst")):
            out.append(flag("A13", f"Line {n}: no tax amount is printed.", tuple(f"lines.{i}.{h}" for h in ("cgst", "sgst", "igst"))))
        hsn = _text(ln.get("hsn"))
        if not _is_service(hsn) and (not _text(ln.get("qty")) or not _text(ln.get("uqc"))):
            out.append(flag("A9", f"Line {n}: goods line without quantity or unit.", (f"lines.{i}.qty", f"lines.{i}.uqc")))
    if not _text(fields.get("reverse_charge")):
        out.append(flag("A16", "Reverse-charge indicator (Yes/No) is not printed.", ("reverse_charge",)))
    return out


def check_hsn(lines: list[dict[str, Field]], has_qr: bool) -> list[Flag]:
    need = 6 if has_qr else 4
    out = []
    for i, ln in enumerate(lines):
        hsn = _text(ln.get("hsn"))
        digits = re.sub(r"\D", "", hsn or "")
        if len(digits) < need:
            why = " (e-invoice QR present, so turnover exceeds Rs 5 Cr and 6 digits are required)" if has_qr else ""
            out.append(flag("A7", f"Line {i + 1}: HSN/SAC '{hsn or ''}' has {len(digits)} digits; at least {need} required{why}.", (f"lines.{i}.hsn",)))
    return out


# ---------------------------------------------------------------- Tax type and rates (C-series)

def check_tax_type(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    out = []
    sup = normalise(_text(fields.get("supplier_gstin")) or "")[:2]
    if sup not in STATE_CODES:
        return out  # G-checks already flag an unusable supplier GSTIN
    pos = pos_code(fields)
    if pos is None:
        rec = normalise(_text(fields.get("recipient_gstin")) or "")[:2]
        pos = rec if rec in STATE_CODES else None
        if pos is None:
            return out
        if pos != sup:
            out.append(flag("A14", f"Place of supply is not printed on an inter-state invoice; assumed the recipient's state ({pos}).", ("place_of_supply",)))
    intra = sup == pos
    if lines:
        igst = sum((_z(ln.get("igst")) for ln in lines), Decimal(0))
        cgst_sgst = sum((_z(ln.get("cgst")) + _z(ln.get("sgst")) for ln in lines), Decimal(0))
    else:
        igst = _z(fields.get("igst_total"))
        cgst_sgst = _z(fields.get("cgst_total")) + _z(fields.get("sgst_total"))
    if intra and igst > 0:
        out.append(flag("C2", f"Intra-state supply (supplier state {sup} = place of supply {pos}) but IGST {igst:.2f} was charged; it must be CGST + SGST.",
                        ("igst_total", "place_of_supply", "supplier_gstin")))
    if not intra and cgst_sgst > 0:
        out.append(flag("C3", f"Inter-state supply (supplier state {sup} -> place of supply {pos}) but CGST/SGST {cgst_sgst:.2f} was charged; it must be IGST.",
                        ("cgst_total", "sgst_total", "place_of_supply", "supplier_gstin")))
    if intra:
        for i, ln in enumerate(lines):
            c, s = _amt(ln.get("cgst")), _amt(ln.get("sgst"))
            if c is not None and s is not None and abs(c - s) > ONE:
                out.append(flag("C4", f"Line {i + 1}: CGST {c:.2f} and SGST {s:.2f} must be equal.", (f"lines.{i}.cgst", f"lines.{i}.sgst")))
        ct, st = _amt(fields.get("cgst_total")), _amt(fields.get("sgst_total"))
        if ct is not None and st is not None and abs(ct - st) > ONE:
            out.append(flag("C4", f"CGST total {ct:.2f} and SGST total {st:.2f} must be equal.", ("cgst_total", "sgst_total")))
    return out


def check_rates(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    d = parse_date(_text(fields.get("invoice_date")))
    if d is None:
        return []
    out = []
    for i, ln in enumerate(lines):
        rate = parse_rate(_text(ln.get("gst_rate")))
        if rate is None:
            continue
        service = _is_service(_text(ln.get("hsn")))
        if d >= REFORM_DATE:
            allowed = SERVICE_SLABS_POST_REFORM if service else GOODS_SLABS_POST_REFORM
            severity = W if service else B
            basis = "services slab list not verified" if service else "Notification 9/2025-IT(R)"
        else:
            allowed, severity, basis = SLABS_PRE_REFORM, W, "pre-reform slab list not re-verified"
        if rate not in allowed:
            out.append(flag("C7", f"Line {i + 1}: {rate}% is not a GST slab valid on {d:%d.%m.%Y} ({basis}).", (f"lines.{i}.gst_rate",), severity))
    return out


def check_reverse_charge(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    rc = (_text(fields.get("reverse_charge")) or "").lower()
    taxes = sum((_z(fields.get(n)) for n in ("cgst_total", "sgst_total", "igst_total")), Decimal(0))
    if rc in {"yes", "y"} and taxes > 0:
        return [flag("C8", f"Reverse charge is 'Yes' but the supplier charged GST {taxes:.2f}; under reverse charge the recipient pays.", ("reverse_charge",))]
    return []


# ---------------------------------------------------------------- Arithmetic (C6)

def _line_tolerance(expected: Decimal) -> Decimal:
    return max(ONE, abs(expected) * Decimal("0.005"))


def check_arithmetic(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    out: list[Flag] = []
    sums = {"taxable_value": Decimal(0), "cgst": Decimal(0), "sgst": Decimal(0), "igst": Decimal(0)}
    for i, ln in enumerate(lines):
        taxable, rate = _amt(ln.get("taxable_value")), parse_rate(_text(ln.get("gst_rate")))
        tax = sum((_z(ln.get(h)) for h in ("cgst", "sgst", "igst")), Decimal(0))
        for key in sums:
            sums[key] += _z(ln.get(key))
        if taxable is not None and rate is not None:
            expected = taxable * rate / 100
            if abs(tax - expected) > _line_tolerance(expected):
                out.append(flag("C6", f"Line {i + 1}: tax charged {tax:.2f} does not equal taxable value {taxable:.2f} x {rate}% = {expected:.2f}.",
                                tuple(f"lines.{i}.{k}" for k in ("taxable_value", "gst_rate", "cgst", "sgst", "igst"))))
        qty, price = _amt(ln.get("qty")), _amt(ln.get("unit_price"))
        if taxable is not None and qty is not None and price is not None and abs(qty * price - taxable) > ONE:
            out.append(flag("C6Q", f"Line {i + 1}: qty {qty} x rate {price:.2f} = {qty * price:.2f}, but taxable value is {taxable:.2f} (a discount, or an error).",
                            tuple(f"lines.{i}.{k}" for k in ("qty", "unit_price", "taxable_value"))))
    for key, total_name, label in [("taxable_value", "taxable_total", "Taxable value"), ("cgst", "cgst_total", "CGST"),
                                   ("sgst", "sgst_total", "SGST"), ("igst", "igst_total", "IGST")]:
        total = _amt(fields.get(total_name))
        if total is not None and lines and abs(total - sums[key]) > ONE:
            out.append(flag("C6", f"{label} total {total:.2f} does not equal the sum of lines {sums[key]:.2f}.", (total_name,)))
    taxable_total, grand, round_off = _amt(fields.get("taxable_total")), _amt(fields.get("grand_total")), _z(fields.get("round_off"))
    if taxable_total is not None and grand is not None:
        taxes = sum((_z(fields.get(n)) for n in ("cgst_total", "sgst_total", "igst_total")), Decimal(0))
        computed = taxable_total + taxes + round_off
        if abs(computed - grand) > CENT:
            out.append(flag("C6", f"Grand total {grand:.2f} does not equal taxable {taxable_total:.2f} + taxes {taxes:.2f} + round-off {round_off:.2f} = {computed:.2f}.",
                            ("grand_total", "taxable_total", "round_off")))
    if abs(round_off) >= ONE:
        out.append(flag("C6", f"Round-off {round_off:.2f} is a rupee or more; rounding to the nearest rupee can never need that.", ("round_off",)))
    return out


# ---------------------------------------------------------------- Entry points

def run_invoice_checks(fields: dict[str, Field], lines: list[dict[str, Field]], has_qr: bool = False) -> list[Flag]:
    return (check_gstins(fields) + check_mandatory(fields, lines) + check_hsn(lines, has_qr) + check_tax_type(fields, lines)
            + check_rates(fields, lines) + check_reverse_charge(fields, lines) + check_arithmetic(fields, lines))


def check_duplicates(batch: dict[str, dict[str, Field]]) -> dict[str, list[Flag]]:
    """A3: same supplier GSTIN + financial year + invoice number more than once in a batch."""
    groups: dict[tuple, list[str]] = defaultdict(list)
    for doc_id, fields in batch.items():
        g, no, d = _text(fields.get("supplier_gstin")), _text(fields.get("invoice_no")), parse_date(_text(fields.get("invoice_date")))
        if g and no and d:
            groups[(normalise(g), financial_year(d), no.upper())].append(doc_id)
    out: dict[str, list[Flag]] = {}
    for (g, fy, no), docs in groups.items():
        if len(docs) > 1:
            for doc_id in docs:
                others = ", ".join(x for x in docs if x != doc_id)
                out[doc_id] = [flag("A3", f"Invoice number {no} from supplier {g} appears more than once in FY {fy} (also in: {others}).", ("invoice_no",))]
    return out


def catalogue_markdown() -> str:
    from docflow.checks_statement import STATEMENT_CATALOGUE

    out = []
    for title, catalogue in (("Invoices", CATALOGUE), ("Bank statements", STATEMENT_CATALOGUE)):
        out += [f"## {title}", "", "| ID | Severity | Check | Source |", "|---|---|---|---|"]
        out += [f"| {c.id} | {c.severity.title()} | {c.description} | {c.source} |" for c in catalogue]
        out.append("")
    return "\n".join(out)
