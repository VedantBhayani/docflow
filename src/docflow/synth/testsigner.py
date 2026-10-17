"""Sign synthetic e-invoice QR payloads with DocFlow's own TEST key. Never NIC's.

The test key pair lives in trust/test/ and is committed on purpose: it is a published
test key, worthless outside this repo, and the issuer is DOCFLOW-TEST-NOT-NIC. A
separate "rogue" key is used to make bad-signature defects under the same key ID.
"""

import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[3]
TEST_DIR = ROOT / "trust" / "test"
ROGUE_DIR = ROOT / "tests" / "fixtures" / "keys"  # outside every trust store
TEST_ISSUER = "DOCFLOW-TEST-NOT-NIC"


def _make_keypair(cn: str) -> tuple[bytes, bytes]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    cert = (
        x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number()).not_valid_before(start).not_valid_after(start.replace(year=2036))
        .sign(key, hashes.SHA256())
    )
    key_pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return key_pem, cert.public_bytes(serialization.Encoding.PEM)


def ensure_keys() -> None:
    """Create the test and rogue key pairs once; they are then committed and reused."""
    for folder, stem, cn in [(TEST_DIR, "DOCFLOW-TEST-ONLY", "DocFlow TEST signer - NOT NIC/IRP"),
                             (ROGUE_DIR, "ROGUE-NOT-TRUSTED", "DocFlow ROGUE signer - for bad-signature tests")]:
        if (folder / f"{stem}.cert.pem").exists():
            continue
        folder.mkdir(parents=True, exist_ok=True)
        key_pem, cert_pem = _make_keypair(cn)
        (folder / f"{stem}.key.pem").write_bytes(key_pem)
        (folder / f"{stem}.cert.pem").write_bytes(cert_pem)


def thumbprint(cert_pem: bytes) -> tuple[str, str]:
    """(kid, x5t) the way IRP headers carry them: SHA-1 of the DER certificate, hex and base64url."""
    der = x509.load_pem_x509_certificate(cert_pem).public_bytes(serialization.Encoding.DER)
    digest = hashlib.sha1(der).digest()
    return digest.hex().upper(), base64.urlsafe_b64encode(digest).decode().rstrip("=")


def irn(seller_gstin: str, fy: str, doc_type: str, doc_no: str) -> str:
    """IRN recipe published by NIC: SHA-256 of supplier GSTIN + FY (YYYY-YY) + doc type + doc number."""
    return hashlib.sha256(f"{seller_gstin}{fy}{doc_type}{doc_no}".encode()).hexdigest()


def sign_payload(data: dict, rogue: bool = False) -> str:
    """Signed QR token with the test key's kid/x5t. rogue=True signs with an untrusted key under the same kid."""
    ensure_keys()
    cert_pem = (TEST_DIR / "DOCFLOW-TEST-ONLY.cert.pem").read_bytes()
    key_dir, stem = (ROGUE_DIR, "ROGUE-NOT-TRUSTED") if rogue else (TEST_DIR, "DOCFLOW-TEST-ONLY")
    key_pem = (key_dir / f"{stem}.key.pem").read_bytes()
    kid, x5t = thumbprint(cert_pem)
    claims = {"iss": TEST_ISSUER, "data": json.dumps(data, separators=(",", ":"))}
    return jwt.encode(claims, key_pem, algorithm="RS256", headers={"kid": kid, "x5t": x5t, "typ": "JWT"})
