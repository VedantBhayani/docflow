"""Verify the signed QR code on GST e-invoices (IRP), offline.

The QR encodes an RS256 JWT whose `data` claim is itself a JSON string, so the
payload is parsed twice. Source: NIC, "QR Code procedure",
https://einvoice1.gst.gov.in/Documents/Qrcode_procedure.pdf
"""

import json
from dataclasses import dataclass
from pathlib import Path

import jwt
import pypdfium2 as pdfium
import zxingcpp

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
