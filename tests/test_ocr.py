import json
import re
from pathlib import Path

import numpy as np
import pymupdf
import pytest
from PIL import Image

from docflow.ingest import load
from docflow.ocr import estimate_skew, render, rotate
from docflow.pipeline import scan_flags

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic" / "invoices"
TRACER = ROOT / "data" / "synthetic" / "tracer" / "inv-tracer-0042.pdf"
MANIFEST = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["documents"]


def _norm(s):
    return re.sub(r"\s+", "", s).upper()


@pytest.mark.parametrize("applied", [-3.0, -1.4, 0.0, 2.2, 3.0])
def test_deskew_recovers_a_known_rotation(applied):
    img = render(TRACER, 0)
    assert abs(estimate_skew(rotate(img, applied)) + applied) <= 0.3


def _dev(scan, defect=None):
    return next(d for d in MANIFEST if d["split"] == "dev" and d["scan"] == scan and d["defect"] == defect)


@pytest.mark.parametrize("scan", ["light", "heavy"])
def test_ocr_reads_key_values_on_dev_scans(scan):
    d = _dev(scan)
    doc = load(DATA / f"{d['id']}.pdf")
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))["fields"]
    page = doc.pages[0]
    assert page.source == "ocr" and len(page.words) > 50
    text = _norm(" ".join(w.text for w in page.words))
    for key in ("invoice_no", "supplier_gstin", "grand_total"):
        assert _norm(truth[key]) in text, (d["id"], key)
    assert all(0 <= w.bbox[0] < w.bbox[2] <= 1 and 0 <= w.bbox[1] < w.bbox[3] <= 1 for w in page.words)


def test_rotated_page_is_turned_upright_before_reading():
    d = _dev("light", "rotated_page")
    doc = load(DATA / f"{d['id']}.pdf")
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))["fields"]
    page = doc.pages[0]
    assert page.transform["quarter_turns"] in (1, 3)
    assert page.height > page.width
    assert _norm(truth["invoice_no"]) in _norm(" ".join(w.text for w in page.words))


def test_unreadable_page_raises_p1(tmp_path):
    rng = np.random.default_rng(0)
    noise = (rng.random((2339, 1654)) * 255).astype(np.uint8)  # A4 at 200 dpi, pure noise
    img_path = tmp_path / "noise.jpg"
    Image.fromarray(noise).save(img_path, quality=40)
    pdf = pymupdf.open()
    page = pdf.new_page(width=595, height=842)
    page.insert_image(page.rect, filename=str(img_path))
    pdf.save(tmp_path / "noise.pdf")
    flags = scan_flags(load(tmp_path / "noise.pdf"))
    assert [f.check_id for f in flags] == ["P1"]


def test_clean_scans_do_not_raise_p1():
    for scan in ("light", "heavy"):
        assert scan_flags(load(DATA / f"{_dev(scan)['id']}.pdf")) == []
