"""The HTTP seam the n8n workflow calls. Uses dev documents whose LLM results are cached, so no API calls are made."""

import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from docflow.api import MAX_BYTES, app

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "data" / "synthetic" / "invoices"
STM = ROOT / "data" / "synthetic" / "statements"
client = TestClient(app)


def _pick(folder: Path, **want) -> Path:
    docs = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["documents"]
    d = next(d for d in docs if d["split"] == "dev" and all(d[k] == v for k, v in want.items()))
    return folder / f"{d['id']}.pdf"


def _post(path: Path, **form):
    return client.post("/extract", files={"file": (path.name, path.read_bytes(), "application/pdf")}, data=form)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_extract_invoice_returns_a_docresult():
    r = _post(_pick(INV, scan="digital", defect=None, qr=True), kind="invoice", trust="test")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "invoice" and body["status"] == "CLEAN" and body["blocking"] == []
    assert body["qr"]["status"] == "VERIFIED"
    assert body["fields"]["grand_total"]["status"] == "VERIFIED" and body["fields"]["grand_total"]["evidence"]


def test_extract_statement_returns_statement_lines_and_flags():
    r = _post(_pick(STM, scan="digital", defect="broken_chain"), kind="statement")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "FLAGGED" and body["blocking"] == ["S1"]
    assert len(body["statement_lines"]) == len(body["lines"]) > 0
    assert {"txn_date", "direction", "amount", "ref_no"} <= set(body["statement_lines"][0])


def test_rejects_non_pdf():
    r = client.post("/extract", files={"file": ("notes.txt", b"hello", "text/plain")}, data={"kind": "invoice"})
    assert r.status_code == 415


def test_rejects_oversized_upload():
    r = client.post("/extract", files={"file": ("big.pdf", b"%PDF-" + b"0" * MAX_BYTES, "application/pdf")}, data={"kind": "invoice"})
    assert r.status_code == 413


def test_rejects_unknown_kind():
    r = _post(_pick(INV, scan="digital", defect=None), kind="receipt")
    assert r.status_code == 422


def test_broken_pdf_is_a_clean_4xx_without_internals():
    r = client.post("/extract", files={"file": ("bad.pdf", b"%PDF-1.7 truncated", "application/pdf")}, data={"kind": "invoice"})
    assert r.status_code == 422 and "Traceback" not in r.text


@pytest.mark.skipif(not os.environ.get("MISTRAL_API_KEY"), reason="no key in the environment")
def test_response_never_contains_the_api_key():
    r = _post(_pick(INV, scan="digital", defect=None), kind="invoice", trust="test")
    assert os.environ["MISTRAL_API_KEY"] not in r.text
