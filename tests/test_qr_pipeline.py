import json
from pathlib import Path

import pytest

from docflow.qr import QrStatus, TrustStore, check_document_qr, verify_document_qr

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic" / "invoices"
NIC_FIX = ROOT / "tests" / "fixtures" / "nic"
MANIFEST = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["documents"]


def _dev(defect=None, scan="digital"):
    return next(d for d in MANIFEST if d["split"] == "dev" and d["qr"] and d["scan"] == scan and d["defect"] == defect)


def test_test_signed_qr_verifies_in_test_mode():
    r = verify_document_qr(DATA / f"{_dev()['id']}.pdf", TrustStore.load("test"))
    assert r.status == QrStatus.VERIFIED and r.trust == "test"
    assert r.payload.issuer == "DOCFLOW-TEST-NOT-NIC"


def test_test_signed_qr_never_passes_in_nic_mode():
    r = verify_document_qr(DATA / f"{_dev()['id']}.pdf", TrustStore.load("nic"))
    assert r.status == QrStatus.UNKNOWN_KEY


def test_rogue_signature_under_a_held_kid_is_invalid():
    r = verify_document_qr(DATA / f"{_dev('qr_bad_signature')['id']}.pdf", TrustStore.load("test"))
    assert r.status == QrStatus.INVALID_SIGNATURE


def test_nic_published_sample_verifies_in_nic_mode():
    token = (NIC_FIX / "sample_signed_qr.jwt").read_text().strip()
    r = TrustStore.load("nic").verify(token)
    assert r.status == QrStatus.VERIFIED and r.payload.issuer == "NIC"


def test_nic_pdf_image_token_signed_by_a_key_we_do_not_hold_is_unknown_not_invalid():
    r = verify_document_qr(NIC_FIX / "Qrcode_procedure.pdf", TrustStore.load("nic"))
    assert r.status == QrStatus.UNKNOWN_KEY


def test_document_without_qr():
    no_qr = next(d for d in MANIFEST if d["split"] == "dev" and not d["qr"] and d["scan"] == "digital")
    assert verify_document_qr(DATA / f"{no_qr['id']}.pdf", TrustStore.load("test")).status == QrStatus.NO_QR


def _fields_from_truth(truth):
    from docflow.models import Field, FieldStatus

    fs = {k: Field(k, v, FieldStatus.GROUNDED) for k, v in truth["fields"].items()}
    ls = [{k: Field(f"lines.{i}.{k}", v, FieldStatus.GROUNDED) for k, v in ln.items()} for i, ln in enumerate(truth["lines"])]
    return fs, ls


def test_matching_qr_raises_nothing_and_upgrades_fields():
    d = _dev()
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
    fields, lines = _fields_from_truth(truth)
    qr = verify_document_qr(DATA / f"{d['id']}.pdf", TrustStore.load("test"))
    flags = check_document_qr(qr, fields, lines)
    assert [f for f in flags if f.severity == "BLOCKING"] == []
    for name in ("supplier_gstin", "recipient_gstin", "invoice_no", "invoice_date", "grand_total"):
        assert fields[name].status == "VERIFIED" and "qr" in fields[name].sources, name


def test_total_mismatch_is_q2_and_names_the_field():
    d = _dev("qr_total_mismatch")
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
    fields, lines = _fields_from_truth(truth)
    flags = check_document_qr(verify_document_qr(DATA / f"{d['id']}.pdf", TrustStore.load("test")), fields, lines)
    q2 = [f for f in flags if f.check_id == "Q2"]
    assert len(q2) == 1 and q2[0].severity == "BLOCKING" and "grand_total" in q2[0].fields
    assert fields["grand_total"].status == "CONFLICT" and "qr" in fields["grand_total"].conflicts


def test_unknown_key_is_a_warning_and_qr_values_are_not_trusted():
    d = _dev()
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
    fields, lines = _fields_from_truth(truth)
    flags = check_document_qr(verify_document_qr(DATA / f"{d['id']}.pdf", TrustStore.load("nic")), fields, lines)
    assert [(f.check_id, f.severity) for f in flags] == [("Q1", "WARNING")]
    assert all(f.status == "GROUNDED" for f in fields.values())


def test_invalid_signature_is_blocking_q1():
    d = _dev("qr_bad_signature")
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
    fields, lines = _fields_from_truth(truth)
    flags = check_document_qr(verify_document_qr(DATA / f"{d['id']}.pdf", TrustStore.load("test")), fields, lines)
    assert [(f.check_id, f.severity) for f in flags] == [("Q1", "BLOCKING")]


def test_printed_irn_differing_from_qr_irn_is_q3():
    d = _dev()
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
    fields, lines = _fields_from_truth(truth)
    fields["irn"].text = "0" * 64
    flags = check_document_qr(verify_document_qr(DATA / f"{d['id']}.pdf", TrustStore.load("test")), fields, lines)
    assert "Q3" in {f.check_id for f in flags if f.severity == "BLOCKING"}


def test_garbled_printed_irn_is_a_warning_not_an_accusation():
    d = _dev()
    truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
    fields, lines = _fields_from_truth(truth)
    fields["irn"].text = truth["fields"]["irn"][:30]  # OCR lost half of the 6.5 pt IRN
    flags = check_document_qr(verify_document_qr(DATA / f"{d['id']}.pdf", TrustStore.load("test")), fields, lines)
    assert [(f.check_id, f.severity) for f in flags if f.check_id == "Q3"] == [("Q3", "WARNING")]
