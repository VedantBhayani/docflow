"""Deterministic transaction-table parser for bank statements.

Transaction tables are structured data, so they are not guessed by a language model:
header cells are mapped to roles by keyword (Credit / Deposits / Deposit (Cr.) all mean
"credit"), every word is assigned to a column by position, wrapped narration lines are
joined to their row, and balance-forward / opening / total rows are recognised. Every
value carries the IDs of the words it came from, so it is grounded by construction.
"""

import re
from dataclasses import dataclass, field

from docflow.ingest import _assign, _cells, _table_header, rows
from docflow.models import Document, Evidence, Field, FieldStatus, Word
from docflow.parse import parse_amount, parse_date

ROLE_RULES = [  # first match wins; tested on lower-cased header cell text
    ("value_date", re.compile(r"value")),
    ("debit", re.compile(r"withdraw|debit|\(dr")),
    ("credit", re.compile(r"deposit|credit|\(cr")),
    ("balance", re.compile(r"balance")),
    ("txn_date", re.compile(r"date|^dt$")),
    ("narration", re.compile(r"narration|description|particulars|remarks|details")),
    ("ref_col", re.compile(r"chq|cheque|ref")),
    ("mode", re.compile(r"^mode$")),
    ("seq", re.compile(r"^#$|^sl|^s\.? ?no")),
]
CARRY = re.compile(r"\b(B/F|BROUGHT FORWARD|BALANCE B/F|OPENING BALANCE|C/F|CARRIED FORWARD)\b", re.I)
TOTAL = re.compile(r"^\s*(PAGE\s+)?TOTAL\b", re.I)
EMPTY_TOKENS = {"-", "--", "nil"}
LINE_KEYS = ("txn_date", "value_date", "narration", "ref_col", "debit", "credit", "balance")


@dataclass
class TableResult:
    lines: list[dict[str, Field]] = field(default_factory=list)
    opening_row: Field | None = None  # balance on an "Opening Balance" / first-page "B/F" row
    pages_parsed: int = 0
    pages_without_table: list[int] = field(default_factory=list)


HEADER_STARTERS = {"date", "txn", "tran", "narration", "description", "particulars", "remarks", "chq", "chq./ref.no.", "chq/ref.no.",
                   "cheque", "ref", "value", "withdrawal", "withdrawals", "deposit", "deposits", "debit", "credit", "closing", "balance", "mode", "#"}
PHRASE_PAIRS = {("closing", "balance"), ("txn", "date"), ("tran", "date"), ("value", "date"), ("value", "dt")}


def _is_junk(w: Word) -> bool:
    """OCR noise such as '.', a replacement character or stray strokes. '#' (row-number header) and '-' (empty cell) are real."""
    return w.text.strip() not in {"#", "-", "--"} and not any(ch.isalnum() for ch in w.text)


def header_cells(row: list[Word]) -> list[list[Word]]:
    """Header cells split at wide gaps AND where a new column label starts, so OCR that narrows
    a gap ("Withdrawal Amt. Deposit Amt.") cannot merge two columns."""
    out: list[list[Word]] = []
    for cell in _cells([w for w in row if not _is_junk(w)]):
        for w in cell:
            tok = w.text.lower().strip(":")
            prev = out[-1][-1].text.lower().strip(":") if out and out[-1] else None
            starts = tok in HEADER_STARTERS and (prev is None or (prev, tok) not in PHRASE_PAIRS)
            if not out or w is cell[0] or starts:
                out.append([w])
            else:
                out[-1].append(w)
    return out


def roles_for(header_cells: list[list[Word]]) -> list[str | None]:
    out = []
    for cell in header_cells:
        text = " ".join(w.text for w in cell).lower().strip()
        out.append(next((role for role, rx in ROLE_RULES if rx.search(text)), None))
    return out


AMOUNT_CELL = re.compile(r"^-?\(?[\d,.]*\d[.,]\d{2}\)?[.,]?$")
AMOUNT_ROLES = ("debit", "credit", "balance")


def _field(name: str, words: list[Word]) -> Field:
    words = [w for w in words if w.text.strip().lower() not in EMPTY_TOKENS]
    if name.split(".")[-1] in AMOUNT_ROLES and words and not any(AMOUNT_CELL.match(w.text) for w in words):
        # Bank amounts always carry 2 decimals; a lone "1" where "-" was printed is OCR noise, not an amount.
        if all(len(w.text.strip()) <= 2 for w in words):
            words = []
    if not words:
        return Field(name=name, text=None, status=FieldStatus.MISSING, sources=["table"])
    page = words[0].page
    same = [w for w in words if w.page == page]
    ev = Evidence(page, (min(w.bbox[0] for w in same), min(w.bbox[1] for w in same), max(w.bbox[2] for w in same), max(w.bbox[3] for w in same)))
    return Field(name=name, text=" ".join(w.text for w in words), status=FieldStatus.GROUNDED, word_ids=[w.id for w in words],
                 evidence=ev, match_score=100.0, sources=["table"])


def parse_tables(doc: Document) -> TableResult:
    res = TableResult()
    for page in doc.pages:
        page_rows = rows(page)
        h = _table_header(page_rows)
        if h is None:
            res.pages_without_table.append(page.index)
            continue
        hcells = header_cells(page_rows[h])
        roles = roles_for(hcells)
        if not {"txn_date", "narration", "balance"} <= set(roles) or not ({"debit", "credit"} & set(roles)):
            res.pages_without_table.append(page.index)
            continue
        res.pages_parsed += 1
        columns = [(c[0].bbox[0], c[-1].bbox[2]) for c in hcells]
        current: dict[str, list[Word]] | None = None
        for row in page_rows[h + 1 :]:
            slots: dict[str, list[Word]] = {}
            row = [w for w in row if not _is_junk(w)]
            if not row:
                continue
            for w in row:
                role = roles[_assign(w, columns)]
                if role:
                    slots.setdefault(role, []).append(w)
            text = " ".join(w.text for w in row)
            date_words = slots.get("txn_date", [])
            is_txn = bool(date_words) and parse_date(" ".join(w.text for w in date_words)) is not None
            if not is_txn and date_words and "balance" in slots and ({"debit", "credit"} & set(slots)) \
                    and parse_amount(" ".join(w.text for w in slots["balance"])) is not None:
                is_txn = True  # date unreadable (OCR) but the row is clearly a transaction; S4 will flag the date
            filled = [r for r in slots if r not in ("seq", "mode")]
            if is_txn:
                if current:
                    res.lines.append(_make_line(current, len(res.lines)))
                current = {k: list(v) for k, v in slots.items()}
                continue
            if CARRY.search(text) and "balance" in slots:
                if page.index == 0 and res.opening_row is None and not res.lines and current is None:
                    res.opening_row = _field("opening_balance", slots["balance"])
                continue  # balance brought forward: not a transaction
            if TOTAL.search(" ".join(w.text for w in slots.get("narration", row[:1]))) or TOTAL.search(text):
                break  # page totals end the table on this page
            if current is not None and filled == ["narration"]:
                current.setdefault("narration", []).extend(slots["narration"])  # wrapped narration line
                continue
            if current is not None and not filled:
                continue
            break  # anything else (summary box, footer) ends the table on this page
        if current:
            res.lines.append(_make_line(current, len(res.lines)))
    return res


def _make_line(slots: dict[str, list[Word]], i: int) -> dict[str, Field]:
    return {k: _field(f"lines.{i}.{k}", slots.get(k, [])) for k in LINE_KEYS}


def amount_sanity(line: dict[str, Field]) -> bool:
    """True if every amount cell that has text parses as an amount (used to decide whether to trust the table path)."""
    return all(line[k].text is None or parse_amount(line[k].text) is not None for k in ("debit", "credit", "balance"))
