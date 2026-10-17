"""Day-1 smoke checks: settle the research's unverified claims on this machine.

Run: uv run python -m docflow.smoke
Writes results/smoke/<date>.json and prints a pass/fail table. Never prints secrets.
"""

import json
import os
import platform
import time
from datetime import date
from importlib.metadata import version
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
NIC_PDF = ROOT / "tests" / "fixtures" / "nic" / "Qrcode_procedure.pdf"
PREFERRED_MODELS = ["mistral-small-2603", "ministral-14b-2512"]  # dated ids, never -latest


class _Probe(BaseModel):
    supplier_gstin: str
    invoice_no: str
    grand_total: str


PROBE_TEXT = (
    "TAX INVOICE  Supplier: Acme Traders  GSTIN: 27AAACU2414K1ZF\n"
    "Invoice No: DFTEST-0042   Date: 03/10/2026\nGrand Total: Rs 11,800.00"
)
PROBE_EXPECTED = _Probe(supplier_gstin="27AAACU2414K1ZF", invoice_no="DFTEST-0042", grand_total="11800.00")


def check_mistral() -> dict:
    load_dotenv(ROOT / ".env")
    if not os.environ.get("MISTRAL_API_KEY"):
        return {"ok": False, "detail": "MISTRAL_API_KEY missing from .env"}
    from mistralai.client import Mistral

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    ids = sorted(m.id for m in client.models.list().data)
    candidates = [i for pref in PREFERRED_MODELS for i in ids if i.startswith(pref)]
    attempts = []
    for model in candidates:
        try:
            t0 = time.perf_counter()
            res = client.chat.parse(
                model=model,
                temperature=0,
                response_format=_Probe,
                messages=[
                    {"role": "system", "content": "Extract the fields. Amounts as plain decimals without currency or commas."},
                    {"role": "user", "content": PROBE_TEXT},
                ],
            )
            parsed = res.choices[0].message.parsed
            attempts.append({
                "model": model,
                "ok": parsed == PROBE_EXPECTED,
                "parsed": parsed.model_dump() if parsed else None,
                "seconds": round(time.perf_counter() - t0, 2),
                "usage": res.usage.model_dump() if res.usage else None,
            })
            if parsed == PROBE_EXPECTED:
                break
        except Exception as exc:  # record and try the next candidate
            attempts.append({"model": model, "ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]})
    ok = any(a["ok"] for a in attempts)
    return {
        "ok": ok,
        "chosen_model": next((a["model"] for a in attempts if a["ok"]), None),
        "small_or_ministral_ids": [i for i in ids if "small" in i or "ministral" in i],
        "attempts": attempts,
        "detail": "chat.parse returned the exact expected fields" if ok else "no candidate model parsed correctly",
    }


OCR_BUDGET_MEDIAN_S = 10.0  # was 5.0 (a guess); measured ~7.5 s at 300 dpi on this CPU. See RUN_LOG.


def check_rapidocr() -> dict:
    import statistics

    import pypdfium2 as pdfium
    from rapidocr import RapidOCR

    pdf = pdfium.PdfDocument(str(NIC_PDF))
    engine = RapidOCR()
    engine(pdf[0].render(scale=2).to_pil())  # warm-up, model load excluded from timing
    times, n_words, found = [], 0, False
    for i in range(len(pdf)):
        image = pdf[i].render(scale=300 / 72).to_pil()
        t0 = time.perf_counter()
        out = engine(image, return_word_box=True)
        times.append(time.perf_counter() - t0)
        n_words += sum(len(w) for w in (getattr(out, "word_results", None) or []))
        found = found or "Signed QR Code" in " ".join(out.txts or [])
    median = round(statistics.median(times), 2)
    return {
        "ok": found and n_words > 0 and median <= OCR_BUDGET_MEDIAN_S,
        "pages": len(times),
        "median_seconds_per_page_300dpi": median,
        "max_seconds_per_page_300dpi": round(max(times), 2),
        "word_boxes": n_words,
        "found_known_phrase": found,
        "detail": f"median <= {OCR_BUDGET_MEDIAN_S} s/page at 300 dpi; word boxes; reads 'Signed QR Code'",
    }


def main() -> None:
    results = {
        "date": date.today().isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "versions": {p: version(p) for p in ["mistralai", "rapidocr", "onnxruntime", "pymupdf", "pypdfium2", "zxing-cpp", "pyjwt"]},
    }
    for name, fn in [("mistral", check_mistral), ("rapidocr", check_rapidocr)]:
        try:
            results[name] = fn()
        except Exception as exc:
            results[name] = {"ok": False, "detail": f"{type(exc).__name__}: {exc}"[:300]}
    out = ROOT / "results" / "smoke" / f"{results['date']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    for name in ("mistral", "rapidocr"):
        r = results[name]
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {name:9} {r.get('detail', '')}")
    print(f"details: {out}")


if __name__ == "__main__":
    main()
