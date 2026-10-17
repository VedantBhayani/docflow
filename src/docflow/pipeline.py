"""Source Document -> grounded Fields -> Checks -> DocResult."""

import dataclasses
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
from docflow.rules import RuleValue, rule_extract

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


def evidence_flags(fields: dict[str, Field], lines: list[dict[str, Field]], key_fields: tuple[str, ...]) -> list[Flag]:
    flags = []
    for name, f in fields.items():
        if f.status == FieldStatus.UNGROUNDED:
            flags.append(Flag("E1", Severity.BLOCKING, f"'{name}' value '{f.text}' could not be found where the extractor said it is printed.", (name,)))
        elif f.status == FieldStatus.MISSING and name in key_fields:
            flags.append(Flag("E2", Severity.BLOCKING, f"Key field '{name}' was not found on the document.", (name,)))
        elif f.status == FieldStatus.CONFLICT:
            others = "; ".join(f"{src} read '{v}'" for src, v in f.conflicts.items())
            flags.append(Flag("E3", Severity.BLOCKING, f"Independent sources disagree on '{name}': extractor read '{f.text}', {others}.", (name,)))
    for i, ln in enumerate(lines):
        for name, f in ln.items():
            if f.status == FieldStatus.UNGROUNDED:
                flags.append(Flag("E1", Severity.BLOCKING, f"Line {i + 1} '{name}' value '{f.text}' could not be found where the extractor said it is printed.", (f.name,)))
    return flags


def process(path: str | Path, kind: str = "invoice") -> DocResult:
    if kind != "invoice":
        raise NotImplementedError(f"kind={kind} arrives in build ticket 08")
    t0 = time.perf_counter()
    doc = load(path)
    if any(p.source == "needs_ocr" for p in doc.pages):
        raise NotImplementedError("scanned pages need the OCR route (build ticket 05)")
    parsed, meta = extract(kind, serialise(doc))
    index = {w.id: w for w in doc.words()}

    fields = {name: ground_ref(name, ref.text, ref.word_ids, index) for name, ref in parsed if name != "lines"}
    lines = [
        {name: ground_ref(f"lines.{i}.{name}", ref.text, ref.word_ids, index) for name, ref in line}
        for i, line in enumerate(parsed.lines)
    ]
    corroborate(fields, rule_extract(doc))
    flags = evidence_flags(fields, lines, INVOICE_KEY_FIELDS) + run_invoice_checks(fields, lines)
    status = _status(flags)
    return DocResult(
        path=str(path), sha256=doc.sha256, kind=kind, status=status, fields=fields, lines=lines, flags=flags,
        page_sources=[p.source for p in doc.pages], llm=meta, seconds=round(time.perf_counter() - t0, 2),
    )


def _status(flags: list[Flag]) -> DocStatus:
    return DocStatus.FLAGGED if any(f.severity == Severity.BLOCKING for f in flags) else DocStatus.CLEAN


def process_batch(paths: list[str | Path], kind: str = "invoice") -> list[DocResult]:
    """Process every document, then run batch-level Checks (A3 duplicates) across them."""
    results = [process(p, kind=kind) for p in paths]
    if kind == "invoice":
        dupes = check_duplicates({r.path: r.fields for r in results})
        for r in results:
            if r.path in dupes:
                r.flags.extend(dupes[r.path])
                r.status = _status(r.flags)
    return results
