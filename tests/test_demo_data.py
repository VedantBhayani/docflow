"""The cached demo must be self-contained and show what ticket 12 promises."""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "demo" / "data"


def _docs():
    return [json.loads((DATA / f"{d['id']}.json").read_text(encoding="utf-8")) for d in json.loads((DATA / "index.json").read_text(encoding="utf-8"))]


def test_every_evidence_box_points_at_an_exported_page():
    for doc in _docs():
        pages = doc["demo"]["pages"]
        assert all((DATA / p).exists() for p in pages)
        cells = list(doc["fields"].values()) + [f for line in doc["lines"] for f in line.values()]
        for f in cells:
            if f["evidence"]:
                assert 0 <= f["evidence"]["page"] < len(pages)
                x0, y0, x1, y1 = f["evidence"]["bbox"]
                assert 0 <= x0 <= x1 <= 1 and 0 <= y0 <= y1 <= 1


def test_demo_covers_the_promised_cases():
    docs = {d["demo"]["id"]: d for d in _docs()}
    blocking = {k: {f["check_id"] for f in d["flags"] if f["severity"] == "BLOCKING"} for k, d in docs.items()}
    assert any(d["status"] == "CLEAN" and d["qr"] and d["qr"]["status"] == "VERIFIED" for d in docs.values())
    assert any("Q2" in b for b in blocking.values())
    assert any("S1" in b for b in blocking.values())
    assert any(d["page_sources"][0] == "ocr" for d in docs.values())


def test_demo_data_holds_no_secrets():
    text = "".join(p.read_text(encoding="utf-8") for p in DATA.glob("*.json"))
    assert "MISTRAL_API_KEY" not in text and "api_key" not in text.lower()
