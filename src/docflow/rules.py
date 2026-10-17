"""Independent rule-based extractor for key invoice Fields (regexes and label anchors).

It shares nothing with the LLM path except the words on the page, so agreement between
the two is evidence. It abstains (returns no value) whenever a field is ambiguous: a
wrong second source would raise false CONFLICT flags, which is worse than no source.
Tax-head totals are deliberately left out; C6 already verifies them arithmetically.
"""

import re
from dataclasses import dataclass

from docflow.ingest import rows
from docflow.models import Document, Word
from docflow.parse import parse_amount, parse_date

GSTIN_TOKEN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]{3}$")  # format only: bad check digits still count
INVOICE_NO_TOKEN = re.compile(r"^(?=.*\d)[A-Za-z0-9/\-]{1,16}$")
AMOUNT_TOKEN = re.compile(r"^-?\(?[\d,]+\.\d{2}\)?$")
RECIPIENT_LABELS = {"bill to", "billed to", "buyer", "recipient", "consignee"}
SUPPLIER_LABELS = {"supplier", "seller"}
NO_LABELS = [("invoice", "no"), ("invoice#",), ("document", "no"), ("tax", "invoice", "no"), ("inv", "no"), ("bill", "no")]
DATE_LABELS = [("invoice", "date"), ("document", "date"), ("dated",), ("date",)]
GRAND_LABELS = [("grand", "total"), ("invoice", "total"), ("total", "inv", "amt"), ("total",)]
TAXABLE_LABELS = [("total", "taxable", "value"), ("taxable", "value"), ("sub", "total"), ("taxble", "amt")]
TABLE_HEADER_WORDS = {"hsn/sac", "hsn", "qty", "rate", "description", "narration", "particulars", "withdrawal", "deposit", "withdrawals", "deposits"}


@dataclass(frozen=True)
class RuleValue:
    value: str
    word_ids: tuple[str, ...]


def _tok(w: Word) -> str:
    return re.sub(r"[:.'’]+$", "", w.text.lower()).replace("'", "").replace("’", "")


def _label_at(row: list[Word], i: int, label: tuple[str, ...]) -> bool:
    toks = [_tok(w) for w in row[i : i + len(label)]]
    return tuple(toks) == label


def _find_labels(row: list[Word], labels: list[tuple[str, ...]]) -> list[tuple[int, tuple[str, ...]]]:
    """(index after the label, label), longest label first, skipping labels contained in a longer match."""
    hits, used = [], set()
    for label in sorted(labels, key=len, reverse=True):
        for i in range(len(row) - len(label) + 1):
            span = set(range(i, i + len(label)))
            if span & used or not _label_at(row, i, label):
                continue
            hits.append((i + len(label), label, i))
            used |= span
    return [(end, label) for end, label, start in sorted(hits, key=lambda h: h[2])]


def extract_gstins(doc: Document) -> dict[str, RuleValue]:
    found = [w for w in doc.words() if GSTIN_TOKEN.match(w.text)]
    if len(found) != 2 or found[0].page != found[1].page:
        return {}
    page_rows = rows(doc.pages[found[0].page])

    def nearest_label_above(g: Word) -> str | None:
        g_row = next(r for r in page_rows if g in r)
        col_x = g_row[0].bbox[0] if g_row[0].bbox[0] <= g.bbox[0] else g.bbox[0]
        # the label/value pair "GSTIN: X" starts the column; use the first word left of g in its row segment
        left = [w for w in g_row if w.bbox[2] <= g.bbox[0] + 1e-6]
        if left:
            col_x = max((w for w in left if g.bbox[0] - w.bbox[2] < 0.06), key=lambda w: w.bbox[0], default=g).bbox[0]
        best = None
        for r in page_rows:
            cy = (r[0].bbox[1] + r[0].bbox[3]) / 2
            gy = (g.bbox[1] + g.bbox[3]) / 2
            if not (0 < gy - cy <= 0.12):
                continue
            for i, w in enumerate(r):
                if abs(w.bbox[0] - col_x) > 0.05:
                    continue
                two = " ".join(_tok(x) for x in r[i : i + 2])
                one = _tok(w)
                kind = "recipient" if (one in RECIPIENT_LABELS or two in RECIPIENT_LABELS) else "supplier" if one in SUPPLIER_LABELS else None
                if kind and (best is None or cy > best[0]):
                    best = (cy, kind)
        return best[1] if best else None

    kinds = [nearest_label_above(g) for g in found]
    recipients = [g for g, k in zip(found, kinds) if k == "recipient"]
    if len(recipients) != 1:
        return {}
    supplier = next(g for g in found if g is not recipients[0])
    return {"supplier_gstin": RuleValue(supplier.text, (supplier.id,)), "recipient_gstin": RuleValue(recipients[0].text, (recipients[0].id,))}


def _after(row: list[Word], end: int) -> list[Word]:
    rest = row[end:]
    while rest and _tok(rest[0]) in {"", ":"}:
        rest = rest[1:]
    return rest


def _unique(cands: list[RuleValue], key) -> RuleValue | None:
    if not cands:
        return None
    keys = {key(c.value) for c in cands}
    return cands[0] if len(keys) == 1 and None not in keys else None


def extract_invoice_no(doc: Document) -> RuleValue | None:
    cands = []
    for page in doc.pages:
        for row in rows(page):
            for end, _ in _find_labels(row, NO_LABELS):
                rest = _after(row, end)
                if rest and INVOICE_NO_TOKEN.match(rest[0].text):
                    cands.append(RuleValue(rest[0].text, (rest[0].id,)))
    return _unique(cands, lambda v: v.upper())


def extract_invoice_date(doc: Document) -> RuleValue | None:
    cands = []
    for page in doc.pages:
        for row in rows(page):
            for end, label in _find_labels(row, DATE_LABELS):
                start = end - len(label)
                if label == ("date",) and start > 0 and _tok(row[start - 1]) in {"ack", "irn", "due", "supply", "order"}:
                    continue
                rest = _after(row, end)
                for n in (1, 3):
                    if len(rest) >= n and parse_date(" ".join(w.text for w in rest[:n])):
                        cands.append(RuleValue(" ".join(w.text for w in rest[:n]), tuple(w.id for w in rest[:n])))
                        break
    return _unique(cands, parse_date)


def _amount_for_label(page_rows: list[list[Word]], r_i: int, end: int, label_words: list[Word]) -> Word | None:
    row = page_rows[r_i]
    same_row = [w for w in row[end:] if AMOUNT_TOKEN.match(w.text)]
    if same_row:
        return same_row[-1] if len(same_row) == 1 or all(_tok(w) for w in row[end:]) else same_row[0]
    if TABLE_HEADER_WORDS & {_tok(w) for w in row}:
        return None  # a table header: the value below belongs to line items, not totals
    if r_i + 1 < len(page_rows):
        x0, x1 = label_words[0].bbox[0], label_words[-1].bbox[2]
        below = [w for w in page_rows[r_i + 1] if AMOUNT_TOKEN.match(w.text) and x0 - 0.02 <= w.bbox[0] <= x1 + 0.02]
        if len(below) == 1:
            return below[0]
    return None


def _extract_amount(doc: Document, labels: list[tuple[str, ...]], exclude_prefix: set[str]) -> RuleValue | None:
    cands = []
    for page in doc.pages:
        page_rows = rows(page)
        for r_i, row in enumerate(page_rows):
            for end, label in _find_labels(row, labels):
                start = end - len(label)
                if start > 0 and _tok(row[start - 1]) in exclude_prefix:
                    continue
                nxt = _tok(row[end]) if end < len(row) else ""
                if len(label) == 1 and re.match(r"^[a-z]", nxt) and nxt not in {"rs", "inr"}:
                    continue  # bare "Total" inside "Total Taxable Value" is not this label
                w = _amount_for_label(page_rows, r_i, end, row[start:end])
                if w is not None:
                    cands.append(RuleValue(w.text, (w.id,)))
    return _unique(cands, parse_amount)


def rule_extract(doc: Document) -> dict[str, RuleValue]:
    out = dict(extract_gstins(doc))
    for name, fn in [("invoice_no", extract_invoice_no), ("invoice_date", extract_invoice_date)]:
        v = fn(doc)
        if v:
            out[name] = v
    grand = _extract_amount(doc, GRAND_LABELS, exclude_prefix={"sub"})
    taxable = _extract_amount(doc, TAXABLE_LABELS, exclude_prefix=set())
    if grand:
        out["grand_total"] = grand
    if taxable:
        out["taxable_total"] = taxable
    return out


OPENING_LABELS = [("opening", "balance"), ("balance", "as", "on")]
CLOSING_LABELS = [("closing", "balance"), ("closing", "bal")]
CARRY_WORDS = {"b/f", "c/f", "brought", "carried"}


def rule_extract_statement(doc: Document) -> dict[str, RuleValue]:
    """Opening and closing balance from labelled summary values, never from carry-forward rows."""
    out = {}
    for name, labels in [("opening_balance", OPENING_LABELS), ("closing_balance", CLOSING_LABELS)]:
        cands = []
        for page in doc.pages:
            page_rows = rows(page)
            for r_i, row in enumerate(page_rows):
                if CARRY_WORDS & {_tok(w) for w in row}:
                    continue
                for end, label in _find_labels(row, labels):
                    start = end - len(label)
                    w = _amount_for_label(page_rows, r_i, end, row[start:end])
                    if w is not None:
                        cands.append(RuleValue(w.text, (w.id,)))
        v = _unique(cands, parse_amount)
        if v:
            out[name] = v
    return out
