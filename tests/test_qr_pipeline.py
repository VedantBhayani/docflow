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


def test_nic_pdf_image_token_verifies_against_nic_2020_production_certificate():
    # A real IRP token (printed in NIC's own PDF), signed in Sept 2020 under the prodpubkey1 certificate.
    r = verify_document_qr(NIC_FIX / "Qrcode_procedure.pdf", TrustStore.load("nic"))
    assert r.status == QrStatus.VERIFIED and r.kid == "115F4426617A7938BE1BA06DBEE91A427584EDAB"
    assert r.payload.issuer == "NIC" and r.payload.doc_no == "QWE1-454565" and r.payload.total_value == 16655.99


def test_trust_store_matches_its_provenance_file():
    for mode in ("nic", "nic-sandbox"):
        sources = json.loads((ROOT / "trust" / mode / "SOURCES.json").read_text(encoding="utf-8"))
        store = TrustStore.load(mode)
        assert {e["kid"] for e in sources.values() if e["kid"]} == set(store.keys), mode
        assert len(store.unkeyed) == sum(1 for e in sources.values() if not e["kid"]), mode
        assert all(e["source"].startswith("https://einvoice1.gst.gov.in/Documents/") for e in sources.values())


def test_current_nic_signing_certificates_are_held():
    keys = TrustStore.load("nic").keys
    assert "CD01AC2B6E720CF0B9E048F1CCBC7509C766AF78" in keys  # IRP-1, 03/06/2026 - 01/05/2027
    assert "644956C46E4E947AAD72FD15DFDB01EB9A96A66B" in keys  # IRP-2, 03/06/2026 - 01/05/2027


def test_test_signed_qr_never_passes_in_sandbox_mode():
    r = verify_document_qr(DATA / f"{_dev()['id']}.pdf", TrustStore.load("nic-sandbox"))
    assert r.status == QrStatus.UNKNOWN_KEY


def test_unkeyed_fallback_never_accepts_a_token_it_cannot_verify():
    store = TrustStore.load("nic")
    token = (NIC_FIX / "sample_signed_qr.jwt").read_text().strip()
    h, b, sig = token.split(".")
    import base64
    hdr = base64.urlsafe_b64encode(b'{"alg":"RS256","kid":"0000000000000000000000000000000000000000","typ":"JWT"}').decode().rstrip("=")
    assert store.verify(".".join([hdr, b, sig])).status == QrStatus.UNKNOWN_KEY


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
