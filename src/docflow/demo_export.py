"""Export the cached demo for the review UI: python -m docflow.demo_export

Runs the real pipeline on a handful of dev documents (LLM and OCR results come from the
committed caches) and writes, per document, the DocResult JSON and the page images the
Evidence boxes refer to. For OCR pages the image is re-rendered with the same rotation and
deskew the OCR used, so every box lands on the word it points to. The demo app reads only
these files: no API key, no OCR models.
"""

import json
from pathlib import Path

from PIL import Image

from docflow.ingest import load
from docflow.ocr import apply_transform, render
from docflow.pipeline import process, statement_lines

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "demo" / "data"
DPI = 110
DEMO = [  # (id, kind, title, what to look at)
    ("inv-0095", "invoice", "Clean e-invoice, QR signature verified",
     "Every value is traced to the words it was read from. The signed QR confirms the GSTINs, number, date and total, so those Fields are VERIFIED."),
    ("inv-0031", "invoice", "Tampered e-invoice: printed total differs from the signed QR",
     "The QR signature is valid, but the total printed on the page is not the total the government portal signed. Check Q2 blocks it."),
    ("inv-0070", "invoice", "Line arithmetic error",
     "One line's quantity x rate does not equal its printed amount. Check C6 names the line."),
    ("inv-0068", "invoice", "Invoice containing a hidden instruction to the AI",
     "The invoice text tells the AI to approve it. Extraction treats it as data; the values and checks are unaffected."),
    ("inv-0115", "invoice", "Heavily degraded scan",
     "Read by OCR after automatic deskew; the boxes sit on the scanned words. The tiny IRN line was too degraded to read reliably, so it is UNGROUNDED and raises a warning instead of being trusted; the signed QR still verifies the key Fields."),
    ("stmt-0002", "statement", "Bank statement with a broken balance chain",
     "One row's printed balance does not equal previous balance - debit + credit. Check S1 flags that row (and the next, whose arithmetic it breaks)."),
    ("stmt-0028", "statement", "Scanned overdraft (cash-credit) statement",
     "One Amount column with a Dr/Cr indicator and balances printed '45,000.00 Dr'. Includes a UPI reversal and a bounced cheque with charges."),
]

def _folder(doc_id: str) -> Path:
    return ROOT / "data" / "synthetic" / ("invoices" if doc_id.startswith("inv") else "statements")

def export() -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for doc_id, kind, title, note in DEMO:
        pdf = _folder(doc_id) / f"{doc_id}.pdf"
        result = process(pdf, kind=kind, trust="test") if kind == "invoice" else process(pdf, kind=kind)
        body = json.loads(json.dumps(result.to_dict(), default=str))
        body["path"] = pdf.name
        if kind == "statement":
            body["statement_lines"] = json.loads(json.dumps(statement_lines(result), default=str))

        doc = load(pdf)
        pages = []
        for page in doc.pages:
            img = render(pdf, page.index, DPI)
            if page.transform:
                img = apply_transform(img, page.transform["quarter_turns"], page.transform["deskew_deg"])
            name = f"{doc_id}-p{page.index}.png"
            Image.fromarray(img).save(OUT / name, optimize=True)
            pages.append(name)
        body["demo"] = {"id": doc_id, "title": title, "note": note, "pages": pages,
                        "trust_note": "Synthetic QR codes are signed with DocFlow's TEST key. Real e-invoices are verified against NIC's published certificates."
                        if kind == "invoice" else None}
        (OUT / f"{doc_id}.json").write_text(json.dumps(body, indent=1), encoding="utf-8")
        index.append({"id": doc_id, "kind": kind, "title": title, "status": body["status"]})
        print(f"{doc_id}: {body['status']} {sorted({f['check_id'] for f in body['flags']})}")
    (OUT / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    return index

if __name__ == "__main__":
    export()
