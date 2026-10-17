"""Source Document -> grounded Fields -> Checks -> DocResult."""

import dataclasses
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from docflow.checks import check_duplicates, run_invoice_checks
from docflow.extract import extract
from docflow.ground import ground_ref
from docflow.ingest import load, serialise
from docflow.gstin import normalise as norm_gstin
from docflow.models import Field, FieldStatus, Flag, Severity
from docflow.parse import parse_amount, parse_date
from docflow.qr import TrustStore, check_document_qr, verify_document_qr
from docflow.rules import RuleValue, rule_extract

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
    if kind != "invoice":
        raise NotImplementedError(f"kind={kind} arrives in build ticket 08")
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
