"""Load a Source Document into pages of Words with normalised boxes.

Pages with a real text layer use PyMuPDF words. Pages without one are oriented,
deskewed and read by RapidOCR (docflow.ocr); their boxes refer to the corrected image.
"""

import hashlib
import re
from pathlib import Path

import pymupdf

from docflow.models import Document, Page, Word
from docflow.ocr import ocr_page

MIN_TEXT_LAYER_WORDS = 20
_GLUED_LABEL = re.compile(r"^([A-Za-z][A-Za-z .#/]{1,24}:)[-.,;]*([A-Za-z0-9].*)$")
# A narrow column gap read as '~' or '|': "67.64.203.63~2671" is a balance and the next column's branch code.
_GLUED_AMOUNT = re.compile(r"^(-?[\d,.]*\d[.,]\d{2})([~|_]+[A-Za-z0-9].*)$")


def split_glued_labels(words: list[Word]) -> list[Word]:
    """OCR often drops the space after a label ("GSTIN:07RADCT..."). Split it into label and value,
    dividing the box by character count. Times ("12:30") and URLs ("https://") are left alone."""
    out = []
    for w in words:
        m = _GLUED_LABEL.match(w.text) or _GLUED_AMOUNT.match(w.text)
        if not m or m.group(2).startswith("//"):
            out.append(w)
            continue
        label, value = m.group(1), m.group(2)
        if m.re is _GLUED_AMOUNT:
            value = value.lstrip("~|_")
        x0, y0, x1, y1 = w.bbox
        cut = x0 + (x1 - x0) * len(label) / len(w.text)
        out.append(Word(id=w.id, text=label, page=w.page, bbox=(x0, y0, cut, y1), confidence=w.confidence))
        out.append(Word(id=w.id, text=value, page=w.page, bbox=(cut, y0, x1, y1), confidence=w.confidence))
    return out


def load(path: str | Path) -> Document:
    path = Path(path)
    data = path.read_bytes()
    pdf = pymupdf.open(stream=data, filetype="pdf")
    sha = hashlib.sha256(data).hexdigest()
    pages, n = [], 0
    for page in pdf:
        w, h = page.rect.width, page.rect.height
        raw = page.get_text("words", sort=True)  # x0, y0, x1, y1, text, block, line, word_no
        if len(raw) < MIN_TEXT_LAYER_WORDS:
            r = ocr_page(path, page.number, sha)
            raw_words = [Word(id="", text=ow["text"], page=page.number, bbox=tuple(ow["bbox"]), confidence=ow["confidence"]) for ow in r["words"]]
            words = []
            for w0 in split_glued_labels(raw_words):
                n += 1
                words.append(Word(id=f"w{n}", text=w0.text, page=w0.page, bbox=w0.bbox, confidence=w0.confidence))
            pages.append(Page(index=page.number, width=r["width"], height=r["height"], source="ocr", words=words,
                              mean_confidence=r["mean_confidence"],
                              transform={"quarter_turns": r["quarter_turns"], "deskew_deg": r["deskew_deg"], "dpi": r["dpi"]}))
            continue
        words = []
        for x0, y0, x1, y1, text, *_ in raw:
            n += 1
            words.append(Word(id=f"w{n}", text=text, page=page.number, bbox=(x0 / w, y0 / h, x1 / w, y1 / h)))
        pages.append(Page(index=page.number, width=w, height=h, source="pdf_text", words=words))
    return Document(path=str(path), sha256=sha, pages=pages)


def rows(page: Page) -> list[list[Word]]:
    """Group a page's words into visual lines (left to right), top to bottom."""
    out: list[list[Word]] = []
    for word in sorted(page.words, key=lambda w: ((w.bbox[1] + w.bbox[3]) / 2, w.bbox[0])):
        cy = (word.bbox[1] + word.bbox[3]) / 2
        height = word.bbox[3] - word.bbox[1]
        if out:
            row = out[-1]
            row_cy = sum((w.bbox[1] + w.bbox[3]) / 2 for w in row) / len(row)
            if abs(cy - row_cy) <= height / 2:
                row.append(word)
                continue
        out.append([word])
    for row in out:
        row.sort(key=lambda w: w.bbox[0])
    return out


COLUMN_GAP = 0.012  # fraction of page width; word spaces are ~0.004, table/column gaps >= ~0.017
HEADER_VOCAB = {"date", "txn", "tran", "narration", "description", "particulars", "remarks", "chq", "chq./ref.no.", "ref", "ref.no.",
                "cheque", "value", "dt", "withdrawal", "withdrawals", "deposit", "deposits", "debit", "credit", "balance", "amt.", "amount",
                "mode", "init.", "br", "#", "(dr.)", "(cr.)", "closing", "no.", "dr/cr"}
EMPTY_CELL = "<empty>"


def _cells(row: list[Word]) -> list[list[Word]]:
    """Split a row into cells at wide gaps."""
    cells: list[list[Word]] = []
    for i, w in enumerate(row):
        if i and w.bbox[0] - row[i - 1].bbox[2] > COLUMN_GAP:
            cells.append([w])
        elif cells:
            cells[-1].append(w)
        else:
            cells.append([w])
    return cells


def _table_header(page_rows: list[list[Word]]) -> int | None:
    for i, row in enumerate(page_rows):
        toks = [w.text.lower().strip(":") for w in row]
        if sum(t in HEADER_VOCAB for t in toks) >= 5 and len(_cells(row)) >= 5:
            return i
    return None


def _assign(word: Word, columns: list[tuple[float, float]]) -> int:
    """Column whose header overlaps the word; otherwise the right-most column starting at or before it."""
    overlaps = [max(0.0, min(word.bbox[2], x1) - max(word.bbox[0], x0)) for x0, x1 in columns]
    if max(overlaps) > 0:
        return overlaps.index(max(overlaps))
    starts = [i for i, (x0, _) in enumerate(columns) if x0 <= word.bbox[0] + 1e-6]
    return starts[-1] if starts else 0


def serialise_table_page(page: Page) -> str:
    """Statement pages: rows below the detected table header are emitted cell by cell under the
    header's columns, with an explicit empty-cell marker, so an amount's column is never lost."""
    page_rows = rows(page)
    h = _table_header(page_rows)
    out = [f"=== page {page.index + 1} ==="]
    if h is None:
        out.extend(" ".join(f"[{w.id}]{w.text}" for w in row) for row in page_rows)
        return "\n".join(out)
    header_cells = _cells(page_rows[h])
    columns = [(c[0].bbox[0], c[-1].bbox[2]) for c in header_cells]
    out.extend(" ".join(f"[{w.id}]{w.text}" for w in row) for row in page_rows[:h])
    out.append(" | ".join(" ".join(f"[{w.id}]{w.text}" for w in c) for c in header_cells))
    from docflow.parse import parse_date

    in_table = True
    for row in page_rows[h + 1 :]:
        slots: list[list[Word]] = [[] for _ in columns]
        for w in row:
            slots[_assign(w, columns)].append(w)
        filled = [i for i, s in enumerate(slots) if s]
        first = " ".join(w.text for w in slots[0])
        is_txn = bool(slots[0]) and parse_date(first) is not None
        is_continuation = len(filled) == 1 and filled[0] != 0  # wrapped description on its own line
        is_carry = not slots[0] and len(filled) == 2 and filled[-1] == len(columns) - 1  # "BALANCE B/F" + balance
        if in_table and (is_txn or is_continuation or is_carry):
            out.append(" | ".join(" ".join(f"[{w.id}]{w.text}" for w in s) if s else EMPTY_CELL for s in slots))
            continue
        in_table = False  # summary boxes, totals and footers below the table: plain rows with gap markers
        parts = []
        for i, w in enumerate(row):
            if i and w.bbox[0] - row[i - 1].bbox[2] > COLUMN_GAP:
                parts.append("|")
            parts.append(f"[{w.id}]{w.text}")
        out.append(" ".join(parts))
    return "\n".join(out)


def serialise(doc: Document) -> str:
    """Words with IDs, one visual line per row, for the extraction prompt.

    A " | " marks a wide horizontal gap (a column boundary), so values in adjacent
    table cells or side-by-side blocks are not read as one phrase.
    """
    out = []
    for page in doc.pages:
        out.append(f"=== page {page.index + 1} ===")
        for row in rows(page):
            parts = []
            for i, w in enumerate(row):
                if i and w.bbox[0] - row[i - 1].bbox[2] > COLUMN_GAP:
                    parts.append("|")
                parts.append(f"[{w.id}]{w.text}")
            out.append(" ".join(parts))
    return "\n".join(out)
