"""Source Document -> grounded Fields -> Checks -> DocResult."""

import dataclasses
import re
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from docflow.checks import check_duplicates, run_invoice_checks
from docflow.checks_statement import run_statement_checks
from docflow.models import Document
from docflow.narration import classify, extract_reference
from docflow.extract import extract
from docflow.ground import ground_ref
from docflow.ingest import load, rows, serialise, serialise_table_page
from docflow.gstin import normalise as norm_gstin
from docflow.models import Field, FieldStatus, Flag, Severity
from docflow.parse import parse_amount, parse_date
from docflow.qr import TrustStore, check_document_qr, verify_document_qr
from docflow.rules import RuleValue, rule_extract, rule_extract_statement

# E1 is blocking only where an unproven value would feed a Check; elsewhere it is a warning.
CHECKED_HEADER_FIELDS = {"cgst_total", "sgst_total", "igst_total", "round_off", "place_of_supply"}
CHECKED_LINE_FIELDS = {"qty", "unit_price", "taxable_value", "gst_rate", "cgst", "sgst", "igst"}
INVOICE_KEY_FIELDS = ("supplier_gstin", "recipient_gstin", "invoice_no", "invoice_date", "taxable_total", "grand_total")


class DocStatus(StrEnum):
    CLEAN = "CLEAN"
    FLAGGED = "FLAGGED"


@dataclass
class DocResult:
    path: str
    sha256: str
    kind: str
    status: DocStatus
    fields: dict[str, Field]
    lines: list[dict[str, Field]]
    flags: list[Flag]
    page_sources: list[str]
    llm: dict = field(default_factory=dict)
    qr: dict | None = None
    seconds: float = 0.0

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


_COMPARE = {
    "supplier_gstin": norm_gstin, "recipient_gstin": norm_gstin,
    "invoice_no": lambda v: v.strip().upper(), "invoice_date": parse_date,
    "taxable_total": parse_amount, "grand_total": parse_amount,
    "opening_balance": parse_amount, "closing_balance": parse_amount,
}


def corroborate(fields: dict[str, Field], second: dict[str, RuleValue], source: str = "rules") -> None:
    """Compare an independent source with the grounded extraction, by meaning (dates, amounts, IDs)."""
    for name, rv in second.items():
        f = fields.get(name)
        if f is None or f.status == FieldStatus.UNGROUNDED:
            continue
        key = _COMPARE.get(name, lambda v: v.strip())
        if f.status == FieldStatus.MISSING or key(f.text) != key(rv.value):
            f.status = FieldStatus.CONFLICT
            f.conflicts[source] = rv.value
        elif f.status in (FieldStatus.GROUNDED, FieldStatus.VERIFIED):
            f.status = FieldStatus.VERIFIED
            if source not in f.sources:
                f.sources.append(source)


def scan_flags(doc) -> list[Flag]:
    from docflow.ocr import POOR_SCAN_CONFIDENCE

    return [
        Flag("P1", Severity.BLOCKING, f"Page {p.index + 1} is a poor scan (mean OCR confidence {p.mean_confidence:.2f} < {POOR_SCAN_CONFIDENCE}); check every value against the paper.", ())
        for p in doc.pages if p.source == "ocr" and p.mean_confidence < POOR_SCAN_CONFIDENCE
    ]


def evidence_flags(fields: dict[str, Field], lines: list[dict[str, Field]], key_fields: tuple[str, ...]) -> list[Flag]:
    flags = []
    for name, f in fields.items():
        if f.status == FieldStatus.UNGROUNDED:
            sev = Severity.BLOCKING if name in key_fields or name in CHECKED_HEADER_FIELDS else Severity.WARNING
            flags.append(Flag("E1", sev, f"'{name}' value '{f.text}' could not be found where the extractor said it is printed.", (name,)))
        elif f.status == FieldStatus.MISSING and name in key_fields:
            flags.append(Flag("E2", Severity.BLOCKING, f"Key field '{name}' was not found on the document.", (name,)))
        elif f.status == FieldStatus.CONFLICT and any(src != "qr" for src in f.conflicts):  # QR-only conflicts are reported by Q2
            others = "; ".join(f"{src} read '{v}'" for src, v in f.conflicts.items())
            flags.append(Flag("E3", Severity.BLOCKING, f"Independent sources disagree on '{name}': extractor read '{f.text}', {others}.", (name,)))
    for i, ln in enumerate(lines):
        for name, f in ln.items():
            if f.status == FieldStatus.UNGROUNDED:
                sev = Severity.BLOCKING if name in CHECKED_LINE_FIELDS else Severity.WARNING
                flags.append(Flag("E1", sev, f"Line {i + 1} '{name}' value '{f.text}' could not be found where the extractor said it is printed.", (f.name,)))
    return flags


def default_trust() -> str:
    return os.environ.get("DOCFLOW_TRUST", "nic")


def process(path: str | Path, kind: str = "invoice", trust: str | None = None) -> DocResult:
    if kind == "statement":
        return process_statement(path)
    if kind != "invoice":
        raise ValueError(f"unknown kind {kind!r}")
    t0 = time.perf_counter()
    doc = load(path)
    parsed, meta = extract(kind, serialise(doc))
    index = {w.id: w for w in doc.words()}

    fields = {name: ground_ref(name, ref.text, ref.word_ids, index) for name, ref in parsed if name != "lines"}
    lines = [
        {name: ground_ref(f"lines.{i}.{name}", ref.text, ref.word_ids, index) for name, ref in line}
        for i, line in enumerate(parsed.lines)
    ]
    corroborate(fields, rule_extract(doc))
    qr = verify_document_qr(Path(path), TrustStore.load(trust or default_trust()))
    qr_flags = check_document_qr(qr, fields, lines)
    flags = (scan_flags(doc) + evidence_flags(fields, lines, INVOICE_KEY_FIELDS)
             + run_invoice_checks(fields, lines, has_qr=qr.status.value != "NO_QR") + qr_flags)
    status = _status(flags)
    return DocResult(
        path=str(path), sha256=doc.sha256, kind=kind, status=status, fields=fields, lines=lines, flags=flags,
        page_sources=[p.source for p in doc.pages], llm=meta, seconds=round(time.perf_counter() - t0, 2),
        qr={"status": qr.status.value, "trust": qr.trust, "kid": qr.kid, "detail": qr.detail,
            "payload": dataclasses.asdict(qr.payload) if qr.payload else None},
    )


def _status(flags: list[Flag]) -> DocStatus:
    return DocStatus.FLAGGED if any(f.severity == Severity.BLOCKING for f in flags) else DocStatus.CLEAN


def process_batch(paths: list[str | Path], kind: str = "invoice", trust: str | None = None) -> list[DocResult]:
    """Process every document, then run batch-level Checks (A3 duplicates) across them."""
    results = [process(p, kind=kind, trust=trust) for p in paths]
    if kind == "invoice":
        dupes = check_duplicates({r.path: r.fields for r in results})
        for r in results:
            if r.path in dupes:
                r.flags.extend(dupes[r.path])
                r.status = _status(r.flags)
    return results


STATEMENT_KEY_FIELDS = ("account_number", "period_from", "period_to", "opening_balance", "closing_balance")
STATEMENT_HEADER = ("bank_name", "account_number", "account_holder", "period_from", "period_to", "opening_balance", "closing_balance")
STATEMENT_CHECKED_LINE_FIELDS = {"txn_date", "debit", "credit", "balance"}


def _statement_evidence_flags(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    flags = []
    for name, f in fields.items():
        if f.status == FieldStatus.UNGROUNDED:
            sev = Severity.BLOCKING if name in STATEMENT_KEY_FIELDS else Severity.WARNING
            flags.append(Flag("E1", sev, f"'{name}' value '{f.text}' could not be found where the extractor said it is printed.", (name,)))
        elif f.status == FieldStatus.MISSING and name in STATEMENT_KEY_FIELDS:
            flags.append(Flag("E2", Severity.BLOCKING, f"Key field '{name}' was not found on the statement.", (name,)))
    for i, ln in enumerate(lines):
        for name, f in ln.items():
            if f.status == FieldStatus.UNGROUNDED:
                sev = Severity.BLOCKING if name in STATEMENT_CHECKED_LINE_FIELDS else Severity.WARNING
                flags.append(Flag("E1", sev, f"Row {i + 1} '{name}' value '{f.text}' could not be found where the extractor said it is printed.", (f.name,)))
    return flags


CARRY_MARKERS = ("B/F", "BROUGHT FORWARD", "CARRIED FORWARD", "C/F")


def _is_carry_forward(f: Field, page, index) -> bool:
    if page.index == 0 or not f.word_ids or f.word_ids[0] not in index:
        return False
    w = index[f.word_ids[0]]
    row = next((r for r in rows(page) if w in r), [])
    text = " ".join(x.text for x in row).upper()
    return any(m in text for m in CARRY_MARKERS)


def process_statement(path: str | Path) -> DocResult:
    """Page-by-page extraction; header values from whichever page prints them; chain checked across pages."""
    t0 = time.perf_counter()
    doc = load(path)
    index = {w.id: w for w in doc.words()}
    fields: dict[str, Field] = {}
    lines: list[dict[str, Field]] = []
    metas = []
    for page in doc.pages:
        parsed, meta = extract("statement_page", serialise_table_page(page))
        metas.append(meta)
        for name in STATEMENT_HEADER:
            ref = getattr(parsed, name)
            candidate = ground_ref(name, ref.text, ref.word_ids, index)
            if name == "opening_balance" and _is_carry_forward(candidate, page, index):
                continue  # a "BALANCE B/F" row on a later page is not the statement's opening balance
            if name not in fields or fields[name].status == FieldStatus.MISSING:
                fields[name] = candidate
        for line in parsed.lines:
            i = len(lines)
            lines.append({name: ground_ref(f"lines.{i}.{name}", ref.text, ref.word_ids, index) for name, ref in line})
    second = rule_extract_statement(doc)
    for name, rv in second.items():
        if fields.get(name) is None or fields[name].status == FieldStatus.MISSING:
            filled = ground_ref(name, rv.value, list(rv.word_ids), index)
            filled.sources = ["rules"]
            fields[name] = filled
    corroborate(fields, {k: v for k, v in second.items() if "llm" in fields[k].sources})
    flags = scan_flags(doc) + _statement_evidence_flags(fields, lines) + run_statement_checks(fields, lines)
    llm = {"model": metas[0]["model"] if metas else None, "prompt_version": metas[0]["prompt_version"] if metas else None,
           "pages": len(metas), "cache_hit": all(m["cache_hit"] for m in metas),
           "prompt_tokens": sum(m.get("prompt_tokens") or 0 for m in metas), "completion_tokens": sum(m.get("completion_tokens") or 0 for m in metas)}
    return DocResult(path=str(path), sha256=doc.sha256, kind="statement", status=_status(flags), fields=fields, lines=lines, flags=flags,
                     page_sources=[p.source for p in doc.pages], llm=llm, seconds=round(time.perf_counter() - t0, 2))


def statement_lines(result: DocResult) -> list[dict]:
    """The Statement Line handoff contract consumed by Recon (spec section 5). Amounts are decimal strings."""
    acct = (result.fields.get("account_number").text or "") if result.fields.get("account_number") else ""
    flags_by_line: dict[int, list[str]] = {}
    for f in result.flags:
        for name in f.fields:
            if name.startswith("lines."):
                flags_by_line.setdefault(int(name.split(".")[1]), []).append(f.check_id)
    rows = []
    for i, ln in enumerate(result.lines):
        def t(k):
            return ln[k].text.strip() if k in ln and ln[k].text else None
        narration = t("narration") or ""
        channel = classify(narration)
        dr, cr = parse_amount(t("debit")), parse_amount(t("credit"))
        txn, val = parse_date(t("txn_date")), parse_date(t("value_date"))
        evs = [f.evidence for f in ln.values() if f.evidence is not None]
        ev = None
        if evs:
            page0 = evs[0].page
            same = [e.bbox for e in evs if e.page == page0]
            from docflow.models import Evidence

            ev = Evidence(page0, (min(b[0] for b in same), min(b[1] for b in same), max(b[2] for b in same), max(b[3] for b in same)))
        statuses = {ln[k].status for k in ("txn_date", "debit", "credit", "balance") if k in ln and ln[k].text}
        rows.append({
            "statement_id": result.sha256[:16], "bank_hint": (result.fields["bank_name"].text if result.fields.get("bank_name") else None),
            "account_last4": acct[-4:] if acct else None, "line_no": i + 1,
            "txn_date": txn.isoformat() if txn else None, "value_date": val.isoformat() if val else None,
            "narration_raw": narration, "channel": channel, "ref_no": extract_reference(narration, channel),
            "bank_ref": t("ref_col"), "cheque_no": t("ref_col") if channel == "CHEQUE" else None,
            "counterparty_hint": _counterparty(narration, channel),
            "amount": str(dr if dr is not None else cr) if (dr is not None) != (cr is not None) else None,
            "direction": "DR" if dr is not None and cr is None else "CR" if cr is not None and dr is None else None,
            "balance": str(parse_amount(t("balance"))) if parse_amount(t("balance")) is not None else None,
            "page": ev.page if ev else None, "bbox": list(ev.bbox) if ev else None,
            "field_status": "VERIFIED" if statuses <= {"VERIFIED"} else "GROUNDED" if statuses <= {"GROUNDED", "VERIFIED"} else "UNPROVEN",
            "flag_ids": sorted(set(flags_by_line.get(i, []))),
        })
    return rows


_NOT_A_PARTY = re.compile(r"\b(UPI|IMPS|MMT|NEFT|RTGS|CR|DR|CHQ|PAID|MICR|CTS|CLG|ZENITH|PAYMENT|PURCHASE|ADVANCE|VENDOR|SALARY|REFUND|NETBANK|MUM)\b")


def _counterparty(narration: str, channel: str) -> str | None:
    """First narration segment that looks like a party name (letters only, not a channel/bank keyword)."""
    if channel in ("CHARGE", "INTEREST", "CASH"):
        return None  # the bank itself, or the account holder
    segs = [x.strip() for x in re.split(r"[-/*]", narration.upper()) if x.strip()]
    for seg in segs:
        if re.fullmatch(r"[A-Z][A-Z .&]{3,}", seg) and not _NOT_A_PARTY.search(seg):
            return seg
    return None


def write_statement_lines(result: DocResult, path: str | Path) -> Path:
    """Write the Statement Line contract as JSONL (canonical) or CSV (Excel / n8n), by file extension."""
    import csv
    import json

    path = Path(path)
    rows = statement_lines(result)
    if path.suffix.lower() == ".csv":
        with path.open("w", encoding="utf-8", newline="") as fh:
            if rows:
                writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
                writer.writeheader()
                for row in rows:
                    writer.writerow({k: (json.dumps(v) if isinstance(v, list) else v) for k, v in row.items()})
    else:
        with path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
    return path
