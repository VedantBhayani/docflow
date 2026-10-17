"""Load a Source Document into pages of Words with normalised boxes.

Pages with a real text layer use PyMuPDF words. Pages without one go to OCR
(build ticket 05); until then they are returned empty with source "needs_ocr".
"""

import hashlib
from pathlib import Path

import pymupdf

from docflow.models import Document, Page, Word

MIN_TEXT_LAYER_WORDS = 20


def load(path: str | Path) -> Document:
    path = Path(path)
    data = path.read_bytes()
    pdf = pymupdf.open(stream=data, filetype="pdf")
    pages, n = [], 0
    for page in pdf:
        w, h = page.rect.width, page.rect.height
        raw = page.get_text("words", sort=True)  # x0, y0, x1, y1, text, block, line, word_no
        if len(raw) < MIN_TEXT_LAYER_WORDS:
            pages.append(Page(index=page.number, width=w, height=h, source="needs_ocr", words=[]))
            continue
        words = []
        for x0, y0, x1, y1, text, *_ in raw:
            n += 1
            words.append(Word(id=f"w{n}", text=text, page=page.number, bbox=(x0 / w, y0 / h, x1 / w, y1 / h)))
        pages.append(Page(index=page.number, width=w, height=h, source="pdf_text", words=words))
    return Document(path=str(path), sha256=hashlib.sha256(data).hexdigest(), pages=pages)


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
