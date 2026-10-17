"""Verify the signed QR code on GST e-invoices (IRP), offline.

The QR encodes an RS256 JWT whose `data` claim is itself a JSON string, so the
payload is parsed twice. Source: NIC, "QR Code procedure",
https://einvoice1.gst.gov.in/Documents/Qrcode_procedure.pdf
"""

import base64
import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import jwt
import pypdfium2 as pdfium
import zxingcpp
from cryptography import x509
from cryptography.hazmat.primitives import serialization

RENDER_DPI = 300


def read_qr_tokens(pdf_path: Path) -> list[str]:
    """Render every page and return the text of each QR code found."""
    tokens = []
    pdf = pdfium.PdfDocument(str(pdf_path))
    for page in pdf:
        image = page.render(scale=RENDER_DPI / 72).to_pil()
        for result in zxingcpp.read_barcodes(image, formats=zxingcpp.BarcodeFormat.QRCode):
            tokens.append(result.text)
    return tokens


class QrSignatureError(Exception):
    """The QR token's signature does not verify against the given public key."""


@dataclass(frozen=True)
class QrPayload:
    issuer: str
    seller_gstin: str
    buyer_gstin: str
    doc_no: str
    doc_type: str
    doc_date: str
    total_value: float
    item_count: int
    main_hsn: str
    irn: str
    irn_date: str


class QrStatus(StrEnum):
    VERIFIED = "VERIFIED"  # signature valid under a key held in the selected trust store
    INVALID_SIGNATURE = "INVALID_SIGNATURE"  # we hold the key and the signature fails: tampered or forged
    UNKNOWN_KEY = "UNKNOWN_KEY"  # signed under a key we do not hold: cannot verify (not an accusation)
    WRONG_ISSUER = "WRONG_ISSUER"  # e.g. a test-signed token presented in nic mode
    UNREADABLE = "UNREADABLE"  # a QR was found but it is not a well-formed signed token
    NO_QR = "NO_QR"


# Trust stores are folders under trust/ and are never mixed. nic: production IRP-1 and IRP-2 certificates;
# nic-sandbox: the NIC sandbox (its issuer string is our best reading of NIC's docs; a mismatch shows as WRONG_ISSUER, never VERIFIED).
ISSUERS = {"nic": "NIC", "nic-sandbox": "NIC Sandbox", "test": "DOCFLOW-TEST-NOT-NIC"}
TRUST_ROOT = Path(__file__).resolve().parents[2] / "trust"
_JWT = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


@dataclass
class QrResult:
    status: QrStatus
    trust: str
    kid: str | None = None
    payload: QrPayload | None = None
    detail: str = ""


@dataclass
class TrustStore:
    """One trust store per mode (never both), so a test-signed QR can never pass in nic mode."""

    mode: str
    keys: dict[str, bytes]  # kid (upper-case SHA-1 hex of the signing certificate) -> PEM public key
    unkeyed: list[bytes] = field(default_factory=list)  # bare keys published without a certificate (no derivable kid)

    @classmethod
    def load(cls, mode: str) -> "TrustStore":
        if mode not in ISSUERS:
            raise ValueError(f"trust mode must be one of {sorted(ISSUERS)}")
        folder = TRUST_ROOT / mode
        keys: dict[str, bytes] = {}
        for cert_file in sorted(folder.glob("*.cert.pem")) + sorted(folder.glob("*.cer")):
            raw = cert_file.read_bytes()
            cert = x509.load_pem_x509_certificate(raw) if b"BEGIN" in raw else x509.load_der_x509_certificate(raw)
            kid = hashlib.sha1(cert.public_bytes(serialization.Encoding.DER)).hexdigest().upper()
            keys[kid] = cert.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        unkeyed = [p.read_bytes() for p in sorted(folder.glob("*.pub.pem"))]
        return cls(mode=mode, keys=keys, unkeyed=unkeyed)

    def _unkeyed_match(self, token: str) -> bytes | None:
        for key in self.unkeyed:
            try:
                verify_signed_qr(token, key)
                return key
            except (QrSignatureError, KeyError, ValueError):
                continue
        return None

    def verify(self, token: str) -> QrResult:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as exc:
            return QrResult(QrStatus.UNREADABLE, self.mode, detail=str(exc))
        kid = (header.get("kid") or "").upper()
        if not kid and header.get("x5t"):
            pad = "=" * (-len(header["x5t"]) % 4)
            kid = base64.urlsafe_b64decode(header["x5t"] + pad).hex().upper()
        key = self.keys.get(kid) or self._unkeyed_match(token)
        if key is None:
            return QrResult(QrStatus.UNKNOWN_KEY, self.mode, kid=kid, detail=f"no key with kid {kid} in the '{self.mode}' trust store")
        try:
            payload = verify_signed_qr(token, key)
        except QrSignatureError as exc:
            return QrResult(QrStatus.INVALID_SIGNATURE, self.mode, kid=kid, detail=str(exc))
        if payload.issuer != ISSUERS[self.mode]:
            return QrResult(QrStatus.WRONG_ISSUER, self.mode, kid=kid, payload=payload, detail=f"issuer '{payload.issuer}' in '{self.mode}' mode")
        return QrResult(QrStatus.VERIFIED, self.mode, kid=kid, payload=payload)


def verify_document_qr(pdf_path: Path, store: TrustStore) -> QrResult:
    tokens = [t for t in read_qr_tokens(pdf_path) if _JWT.match(t.strip())]
    if not tokens:
        return QrResult(QrStatus.NO_QR, store.mode)
    return store.verify(tokens[0].strip())


def verify_signed_qr(token: str, public_key_pem: bytes) -> QrPayload:
    try:
        claims = jwt.decode(token, public_key_pem, algorithms=["RS256"])
    except jwt.InvalidTokenError as exc:
        raise QrSignatureError(str(exc)) from exc

    data = json.loads(claims["data"])
    return QrPayload(
        issuer=claims["iss"],
        seller_gstin=data["SellerGstin"],
        buyer_gstin=data["BuyerGstin"],
        doc_no=data["DocNo"],
        doc_type=data["DocTyp"],
        doc_date=data["DocDt"],
        total_value=data["TotInvVal"],
        item_count=data["ItemCnt"],
        main_hsn=data["MainHsnCode"],
        irn=data["Irn"],
        irn_date=data["IrnDt"],
    )


# ---------------------------------------------------------------- Checks Q1-Q3, B3

def _irn_recipe(seller_gstin: str, doc_date, doc_type: str, doc_no: str) -> str:
    start = doc_date.year if doc_date.month >= 4 else doc_date.year - 1
    return hashlib.sha256(f"{seller_gstin}{start}-{(start + 1) % 100:02d}{doc_type}{doc_no}".encode()).hexdigest()


def check_document_qr(qr: QrResult, fields: dict, lines: list[dict]) -> list:
    """Q1 signature, Q2 QR vs printed fields, Q3 printed IRN, B3 IRN date. Mutates field status:
    a verified QR upgrades agreeing fields to VERIFIED and marks contradicted ones CONFLICT."""
    from datetime import datetime

    from docflow.gstin import normalise as norm_gstin
    from docflow.models import FieldStatus, Flag, Severity
    from docflow.parse import parse_amount, parse_date

    B, W = Severity.BLOCKING, Severity.WARNING
    if qr.status == QrStatus.NO_QR:
        return []
    if qr.status == QrStatus.UNKNOWN_KEY:
        return [Flag("Q1", W, f"E-invoice QR is signed under key {qr.kid}, which is not in the '{qr.trust}' trust store, so it cannot be verified. Not evidence of tampering.", ())]
    if qr.status == QrStatus.UNREADABLE:
        return [Flag("Q1", W, f"A QR code was found but it is not a valid signed e-invoice token ({qr.detail}).", ())]
    if qr.status == QrStatus.WRONG_ISSUER:
        return [Flag("Q1", B, f"E-invoice QR issuer is '{qr.payload.issuer}', not the expected issuer for '{qr.trust}' mode.", ())]
    if qr.status == QrStatus.INVALID_SIGNATURE:
        return [Flag("Q1", B, f"E-invoice QR signature does NOT verify against the held key {qr.kid}: the QR is tampered with or forged.", ())]

    p = qr.payload
    flags = []

    def text(name):
        f = fields.get(name)
        return f.text if f is not None and f.text and f.status != FieldStatus.UNGROUNDED else None

    def amount_eq(a, b):
        return a is not None and b is not None and abs(a - b) <= 1

    main_line = None
    taxables = [(parse_amount(ln["taxable_value"].text) if ln.get("taxable_value") else None) for ln in lines]
    if taxables and all(t is not None for t in taxables) and taxables.count(max(taxables)) == 1:
        main_line = lines[taxables.index(max(taxables))]
    comparisons = [
        ("supplier_gstin", p.seller_gstin, lambda v: norm_gstin(v) == norm_gstin(p.seller_gstin)),
        ("recipient_gstin", p.buyer_gstin, lambda v: norm_gstin(v) == norm_gstin(p.buyer_gstin)),
        ("invoice_no", p.doc_no, lambda v: v.strip().upper() == p.doc_no.strip().upper()),
        ("invoice_date", p.doc_date, lambda v: parse_date(v) == parse_date(p.doc_date)),
        ("grand_total", str(p.total_value), lambda v: amount_eq(parse_amount(v), parse_amount(str(p.total_value)))),
    ]
    mismatched = []
    for name, qr_value, same in comparisons:
        v = text(name)
        if v is None:
            continue  # not printed or not grounded: nothing to compare
        f = fields[name]
        if same(v):
            if f.status in (FieldStatus.GROUNDED, FieldStatus.VERIFIED):
                f.status = FieldStatus.VERIFIED
            if "qr" not in f.sources:
                f.sources.append("qr")
        else:
            f.status = FieldStatus.CONFLICT
            f.conflicts["qr"] = qr_value
            mismatched.append(f"{name} printed '{v}' vs QR '{qr_value}'")
    if lines and p.item_count != len(lines):
        mismatched.append(f"line count printed {len(lines)} vs QR {p.item_count}")
    if main_line is not None and main_line.get("hsn") and main_line["hsn"].text and re.sub(r"\D", "", main_line["hsn"].text) != re.sub(r"\D", "", p.main_hsn):
        mismatched.append(f"main HSN printed '{main_line['hsn'].text}' vs QR '{p.main_hsn}'")
    if mismatched:
        names = tuple(m.split(" ")[0] for m in mismatched if m.split(" ")[0] in fields)
        flags.append(Flag("Q2", B, "Signed e-invoice QR contradicts the printed invoice: " + "; ".join(mismatched) + ".", names))

    printed_irn = text("irn")
    clean_irn = re.sub(r"\s", "", printed_irn).lower() if printed_irn else None
    if clean_irn and not re.fullmatch(r"[0-9a-f]{64}", clean_irn):
        flags.append(Flag("Q3", W, f"Printed IRN is not fully readable ('{printed_irn}'), so it cannot be compared with the QR; the QR's IRN is '{p.irn}'.", ("irn",)))
    elif clean_irn and clean_irn != p.irn.lower():
        flags.append(Flag("Q3", B, f"Printed IRN '{printed_irn}' differs from the IRN in the signed QR '{p.irn}'.", ("irn",)))
    doc_date = parse_date(p.doc_date)
    if doc_date and _irn_recipe(p.seller_gstin, doc_date, "INV", p.doc_no) != p.irn.lower():
        flags.append(Flag("Q3R", W, "IRN in the QR does not match SHA-256(GSTIN + FY + INV + DocNo); NIC's exact canonicalisation is unverified, so this is a warning.", ("irn",)))
    try:
        irn_dt = datetime.strptime(p.irn_date, "%Y-%m-%d %H:%M:%S").date()
        if doc_date and (irn_dt - doc_date).days > 30:
            flags.append(Flag("B3", W, f"IRN generated {(irn_dt - doc_date).days} days after the invoice date (30-day reporting limit for AATO >= Rs 10 Cr).", ("irn",)))
    except ValueError:
        pass
    return flags
