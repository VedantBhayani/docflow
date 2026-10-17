"""Deterministic Checks on extracted Fields. IDs follow research note 01 and spec section 6.

Each Check reads parsed values only. A value that is MISSING or unparseable is not
re-flagged here; its Field status already raises a Flag in the pipeline.
"""

from decimal import Decimal

from docflow.gstin import validate_gstin
from docflow.models import Field, Flag, Severity
from docflow.parse import parse_amount, parse_rate

GSTIN_MESSAGES = {
    "G1": "GSTIN is not in the 15-character GSTIN format.",
    "G2": "GSTIN state code is not in the GST state-code master.",
    "G3": "GSTIN's PAN part has an invalid holder-type character.",
    "G4": "GSTIN entity number cannot be 0.",
    "G5": "GSTIN check digit is wrong: the number is mistyped, misread or invalid.",
}
SOURCES = {
    "G": "https://einvoice1.gst.gov.in/Others/MasterCodes ; check digit: research note 01 (empirical, 74/74)",
    "C6": "CGST Act s.170 (rounding of tax payable); tolerances are a design choice, see research note 01",
}
ONE = Decimal("1")
CENT = Decimal("0.01")


def _amt(f: Field | None) -> Decimal | None:
    return parse_amount(f.text) if f is not None else None


def _zero_if_missing(f: Field | None) -> Decimal:
    v = _amt(f)
    return v if v is not None else Decimal("0")


def _line_tolerance(expected: Decimal) -> Decimal:
    return max(ONE, abs(expected) * Decimal("0.005"))


def check_gstins(fields: dict[str, Field]) -> list[Flag]:
    flags = []
    for name in ("supplier_gstin", "recipient_gstin"):
        f = fields.get(name)
        if f is None or not f.text:
            continue
        for check_id in validate_gstin(f.text)[:1]:  # first failure is the actionable one
            who = "Supplier" if name.startswith("supplier") else "Recipient"
            flags.append(Flag(check_id, Severity.BLOCKING, f"{who} {GSTIN_MESSAGES[check_id]}", (name,)))
    return flags


def check_arithmetic(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    flags: list[Flag] = []
    sums = {"taxable_value": Decimal(0), "cgst": Decimal(0), "sgst": Decimal(0), "igst": Decimal(0)}

    for i, ln in enumerate(lines):
        taxable, rate = _amt(ln.get("taxable_value")), parse_rate(ln["gst_rate"].text) if ln.get("gst_rate") else None
        tax = sum((_zero_if_missing(ln.get(h)) for h in ("cgst", "sgst", "igst")), Decimal(0))
        for key in sums:
            sums[key] += _zero_if_missing(ln.get(key))
        if taxable is not None and rate is not None:
            expected = taxable * rate / 100
            if abs(tax - expected) > _line_tolerance(expected):
                flags.append(Flag("C6", Severity.BLOCKING,
                                  f"Line {i + 1}: tax charged {tax:.2f} does not equal taxable value {taxable:.2f} x {rate}% = {expected:.2f}.",
                                  tuple(f"lines.{i}.{k}" for k in ("taxable_value", "gst_rate", "cgst", "sgst", "igst"))))
        qty, price = _amt(ln.get("qty")), _amt(ln.get("unit_price"))
        if taxable is not None and qty is not None and price is not None and abs(qty * price - taxable) > ONE:
            flags.append(Flag("C6Q", Severity.WARNING,
                              f"Line {i + 1}: qty {qty} x rate {price:.2f} = {qty * price:.2f}, but taxable value is {taxable:.2f} (a discount, or an error).",
                              tuple(f"lines.{i}.{k}" for k in ("qty", "unit_price", "taxable_value"))))

    for key, total_name, label in [("taxable_value", "taxable_total", "Taxable value"), ("cgst", "cgst_total", "CGST"),
                                   ("sgst", "sgst_total", "SGST"), ("igst", "igst_total", "IGST")]:
        total = _amt(fields.get(total_name))
        if total is None and sums[key] == 0:
            continue  # tax head not printed and not charged on any line
        if total is not None and lines and abs(total - sums[key]) > ONE:
            flags.append(Flag("C6", Severity.BLOCKING, f"{label} total {total:.2f} does not equal the sum of lines {sums[key]:.2f}.", (total_name,)))

    taxable_total, grand, round_off = _amt(fields.get("taxable_total")), _amt(fields.get("grand_total")), _zero_if_missing(fields.get("round_off"))
    if taxable_total is not None and grand is not None:
        taxes = sum((_zero_if_missing(fields.get(n)) for n in ("cgst_total", "sgst_total", "igst_total")), Decimal(0))
        computed = taxable_total + taxes + round_off
        if abs(computed - grand) > CENT:
            flags.append(Flag("C6", Severity.BLOCKING,
                              f"Grand total {grand:.2f} does not equal taxable {taxable_total:.2f} + taxes {taxes:.2f} + round-off {round_off:.2f} = {computed:.2f}.",
                              ("grand_total", "taxable_total", "round_off")))
    if abs(round_off) >= ONE:
        flags.append(Flag("C6", Severity.BLOCKING, f"Round-off {round_off:.2f} is a rupee or more; rounding to the nearest rupee can never need that.", ("round_off",)))
    return flags


def run_invoice_checks(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    return check_gstins(fields) + check_arithmetic(fields, lines)
