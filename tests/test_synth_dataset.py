"""The evaluation set is only worth its labels. These tests prove the labels.

- Every truth value is really printed in the PDF (digital docs).
- Running the Checks on truth values gives exactly the expected blocking flags, so
  "clean" docs are clean and each defect raises what its label says.
- QR codes decode from the page and verify with the right key (and the rogue key fails).
"""

import json
import re
from collections import Counter
from pathlib import Path

import pymupdf
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from docflow.checks import check_duplicates, run_invoice_checks
from docflow.gstin import validate_gstin
from docflow.models import Field, FieldStatus, Severity
from docflow.qr import QrSignatureError, read_qr_tokens, verify_signed_qr
from docflow.synth.invoice import QR_BANNER, SYNTHETIC_FOOTER, generate_invoice_set
from docflow.synth.testsigner import TEST_DIR

GEN_ONLY = {"Q1", "Q2", "A3", "E2"}  # raised by QR verification, batch checks or the pipeline, not run_invoice_checks


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    out = tmp_path_factory.mktemp("invoices")
    manifest = generate_invoice_set(out, seed=7)
    truths = {m["id"]: json.loads((out / f"{m['id']}.truth.json").read_text(encoding="utf-8")) for m in manifest}
    return out, manifest, truths


def _fields(truth):
    fs = {k: Field(k, v, FieldStatus.GROUNDED if v is not None else FieldStatus.MISSING) for k, v in truth["fields"].items()}
    ls = [{k: Field(f"lines.{i}.{k}", v, FieldStatus.GROUNDED) for k, v in ln.items()} for i, ln in enumerate(truth["lines"])]
    return fs, ls


def test_composition(dataset):
    _, manifest, _ = dataset
    assert len(manifest) == 120
    assert Counter(m["template"] for m in manifest) == {"tally": 30, "zoho": 30, "word": 30, "einvoice": 30}
    assert Counter(m["scan"] for m in manifest) == {"digital": 60, "light": 32, "heavy": 28}
    assert sum(m["qr"] for m in manifest) == 48
    defects = Counter(m["defect"] for m in manifest if m["defect"])
    assert all(n >= 2 for n in defects.values()) and len(defects) == 10
    splits = Counter(m["split"] for m in manifest)
    assert 30 <= splits["dev"] <= 40, splits
    for d in defects:  # every defect type is represented in both splits
        assert {m["split"] for m in manifest if m["defect"] == d} == {"dev", "heldout"}, d


def test_duplicate_pairs_share_a_split(dataset):
    _, manifest, truths = dataset
    by_no = {}
    for m in manifest:
        if m["defect"] == "duplicate_invoice_no":
            by_no.setdefault(truths[m["id"]]["fields"]["invoice_no"], set()).add(m["split"])
    assert len(by_no) == 2 and all(len(s) == 1 for s in by_no.values())


def test_gstins_are_valid_except_where_the_defect_breaks_them(dataset):
    _, manifest, truths = dataset
    for m in manifest:
        f = truths[m["id"]]["fields"]
        for key in ("supplier_gstin", "recipient_gstin"):
            if f[key] is None:
                assert m["defect"] == "missing_recipient_gstin"
                continue
            broken = m["defect"] == "bad_gstin_checksum" and key == "supplier_gstin"
            assert (validate_gstin(f[key]) == ["G5"]) if broken else (validate_gstin(f[key]) == []), (m["id"], key)


def test_every_truth_value_is_printed_on_digital_pages(dataset):
    out, manifest, truths = dataset
    for m in manifest:
        if m["scan"] != "digital":
            continue
        page_text = re.sub(r"\s+", "", "".join(p.get_text() for p in pymupdf.open(out / f"{m['id']}.pdf")))
        t = truths[m["id"]]
        values = [v for v in t["fields"].values() if v] + [v for ln in t["lines"] for v in ln.values() if v]
        for v in values:
            assert re.sub(r"\s+", "", v) in page_text, (m["id"], v)
        assert SYNTHETIC_FOOTER.replace(" ", "") in page_text
        if m["qr"]:
            assert QR_BANNER.replace(" ", "") in page_text


def test_checks_on_truth_give_exactly_the_expected_flags(dataset):
    _, manifest, truths = dataset
    for m in manifest:
        t = truths[m["id"]]
        fields, lines = _fields(t)
        blocking = {f.check_id for f in run_invoice_checks(fields, lines, has_qr=bool(t["qr"])) if f.severity == Severity.BLOCKING}
        expected = set(m["expected_flags"]) - GEN_ONLY
        assert blocking == expected, (m["id"], m["defect"], blocking, expected)


def test_duplicate_check_finds_exactly_the_pairs(dataset):
    _, manifest, truths = dataset
    for split in ("dev", "heldout"):
        batch = {m["id"]: _fields(truths[m["id"]])[0] for m in manifest if m["split"] == split}
        flagged = set(check_duplicates(batch))
        assert flagged == {m["id"] for m in manifest if m["split"] == split and m["defect"] == "duplicate_invoice_no"}


def test_qr_codes_decode_from_the_page_and_verify_correctly(dataset):
    out, manifest, truths = dataset
    cert = x509.load_pem_x509_certificate((TEST_DIR / "DOCFLOW-TEST-ONLY.cert.pem").read_bytes())
    pub = cert.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    checked = 0
    for m in manifest:
        if not m["qr"] or m["scan"] != "digital":
            continue
        tokens = read_qr_tokens(out / f"{m['id']}.pdf")
        assert tokens == [truths[m["id"]]["qr"]["token"]], m["id"]
        if m["defect"] == "qr_bad_signature":
            with pytest.raises(QrSignatureError):
                verify_signed_qr(tokens[0], pub)
        else:
            payload = verify_signed_qr(tokens[0], pub)
            assert payload.issuer == "DOCFLOW-TEST-NOT-NIC"
            printed_total = truths[m["id"]]["fields"]["grand_total"].replace(",", "")
            same = abs(float(printed_total) - payload.total_value) < 0.01
            assert same == (m["defect"] != "qr_total_mismatch"), m["id"]
        checked += 1
    assert checked >= 20


def test_scans_have_no_text_layer_and_rotated_pages_are_landscape(dataset):
    out, manifest, _ = dataset
    for m in manifest:
        if m["scan"] == "digital":
            continue
        page = pymupdf.open(out / f"{m['id']}.pdf")[0]
        assert page.get_text().strip() == "", m["id"]
        assert (page.rect.width > page.rect.height) == (m["defect"] == "rotated_page"), m["id"]


def test_generation_is_reproducible(dataset, tmp_path):
    out, manifest, _ = dataset
    again = generate_invoice_set(tmp_path, seed=7)
    assert again == manifest
    for m in manifest[:12] + manifest[-12:]:
        assert (tmp_path / f"{m['id']}.truth.json").read_bytes() == (out / f"{m['id']}.truth.json").read_bytes()
        assert (tmp_path / f"{m['id']}.pdf").read_bytes() == (out / f"{m['id']}.pdf").read_bytes(), m["id"]
