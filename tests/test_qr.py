from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from docflow.qr import QrSignatureError, verify_signed_qr

NIC = Path(__file__).parent / "fixtures" / "nic"
TOKEN = (NIC / "sample_signed_qr.jwt").read_text().strip()
NIC_SAMPLE_KEY = (NIC / "sample_public_key.pem").read_bytes()


def test_nic_published_sample_qr_verifies_with_nic_published_key():
    payload = verify_signed_qr(TOKEN, NIC_SAMPLE_KEY)

    # Expected values are the ones NIC prints in the same PDF, not recomputed.
    assert payload.issuer == "NIC"
    assert payload.seller_gstin == "37ARZPT4384Q1MT"
    assert payload.buyer_gstin == "29AWGPV7107B1Z1"
    assert payload.doc_no == "Test-00df1"
    assert payload.doc_type == "INV"
    assert payload.doc_date == "14/07/2025"
    assert payload.item_count == 1
    assert payload.main_hsn == "010190"
    assert payload.irn.startswith("d9476807f5496dea9f") and len(payload.irn) == 64
    assert payload.irn_date == "2025-07-14 12:44:00"


def test_same_token_is_rejected_with_a_different_key():
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
    other_pem = other.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with pytest.raises(QrSignatureError):
        verify_signed_qr(TOKEN, other_pem)


def test_tampered_payload_is_rejected():
    header, body, sig = TOKEN.split(".")
    tampered = ".".join([header, body[:-4] + ("AAAA" if body[-4:] != "AAAA" else "BBBB"), sig])
    with pytest.raises(QrSignatureError):
        verify_signed_qr(tampered, NIC_SAMPLE_KEY)


def test_qr_image_in_nic_pdf_decodes_to_a_nic_token():
    # The printed QR image in NIC's PDF is NOT the text sample above: it is an
    # older (2020) token signed under a different key id that the PDF does not
    # publish. Values below are read from that image, checked by hand.
    from docflow.qr import read_qr_tokens

    tokens = read_qr_tokens(NIC / "Qrcode_procedure.pdf")

    assert len(tokens) == 1
    header = jwt.get_unverified_header(tokens[0])
    assert header["alg"] == "RS256"
    assert header["kid"] == "115F4426617A7938BE1BA06DBEE91A427584EDAB"
    with pytest.raises(QrSignatureError):
        verify_signed_qr(tokens[0], NIC_SAMPLE_KEY)
