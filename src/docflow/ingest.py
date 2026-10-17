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


def serialise(doc: Document) -> str:
    """Words with IDs, one visual line per row, for the extraction prompt."""
    out = []
    for page in doc.pages:
        out.append(f"=== page {page.index + 1} ===")
        rows: list[list[Word]] = []
        for word in page.words:
            # Same visual line if vertical centres are within half a word height.
            cy = (word.bbox[1] + word.bbox[3]) / 2
            height = word.bbox[3] - word.bbox[1]
            if rows:
                last = rows[-1][-1]
                last_cy = (last.bbox[1] + last.bbox[3]) / 2
                if abs(cy - last_cy) <= height / 2:
                    rows[-1].append(word)
                    continue
            rows.append([word])
        for row in rows:
            row.sort(key=lambda w: w.bbox[0])
            out.append(" ".join(f"[{w.id}]{w.text}" for w in row))
    return "\n".join(out)
