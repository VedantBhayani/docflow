"""HTTP API: the seam an automation (the n8n intake workflow) calls.

    uvicorn docflow.api:app --port 8000

POST /extract  multipart `file` (a PDF, max 10 MB) + form `kind` (invoice | statement)
               -> the DocResult JSON (plus `statement_lines` for statements)
GET  /health   -> {"status": "ok"}

No auth, queue or database: it runs locally next to the workflow. LLM and OCR results are
cached by document hash, so re-sending a document costs nothing.
"""

import hashlib
import json
import logging
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from docflow.pipeline import process, statement_lines

MAX_BYTES = 10 * 1024 * 1024
UPLOADS = Path(tempfile.gettempdir()) / "docflow-uploads"
log = logging.getLogger("docflow.api")

app = FastAPI(title="DocFlow", version="1.0", description="Grounded extraction and audit checks for GST invoices and bank statements.")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/extract")
def extract(file: UploadFile = File(...), kind: Literal["invoice", "statement"] = Form("invoice"),
            trust: Literal["nic", "nic-sandbox", "test"] | None = Form(None)) -> dict:
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, f"File is larger than {MAX_BYTES // (1024 * 1024)} MB.")
    if not data.startswith(b"%PDF-"):
        raise HTTPException(415, "Only PDF files are accepted.")
    sha = hashlib.sha256(data).hexdigest()
    UPLOADS.mkdir(parents=True, exist_ok=True)
    path = UPLOADS / f"{sha}.pdf"  # named by content, so the user's file name never reaches the file system
    path.write_bytes(data)
    try:
        result = process(path, kind=kind, trust=trust) if kind == "invoice" else process(path, kind=kind)
    except Exception as exc:  # report the failure, never internals (which could include configuration)
        log.exception("extract failed for %s", sha)
        raise HTTPException(422, f"Could not process this document ({type(exc).__name__}).") from None
    body = json.loads(json.dumps(result.to_dict(), default=str))
    body["path"] = file.filename or f"{sha}.pdf"
    if kind == "statement":
        body["statement_lines"] = json.loads(json.dumps(statement_lines(result), default=str))
    body["blocking"] = sorted({f["check_id"] for f in body["flags"] if f["severity"] == "BLOCKING"})
    return body
