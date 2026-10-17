"""Turn a digital PDF into a degraded, image-only "scan", deterministically by seed.

Own implementation instead of augraphy (fewer heavy dependencies on Windows, and every
effect is explicit). Levels: light = office scanner; heavy = poor phone/fax copy.
"""

import io
from pathlib import Path

import cv2
import numpy as np
import pymupdf
import pypdfium2 as pdfium
from PIL import Image

DPI = 200
LEVELS = {
    "light": {"skew": 1.0, "blur": 0.6, "noise": 6.0, "contrast": 1.0, "speckle": 0.0, "down": 1.0, "jpeg": 75},
    "heavy": {"skew": 3.0, "blur": 1.1, "noise": 14.0, "contrast": 0.75, "speckle": 0.0015, "down": 0.7, "jpeg": 45},
}


def degrade(src_pdf: Path, dst_pdf: Path, level: str, seed: int, rotate90: bool = False) -> dict:
    p = LEVELS[level]
    rng = np.random.default_rng(seed)
    pages = []
    meta = {"level": level, "seed": seed, "rotate90": rotate90, "dpi": DPI, "skew_deg": []}
    for page in pdfium.PdfDocument(str(src_pdf)):
        img = np.array(page.render(scale=DPI / 72).to_pil().convert("L"), dtype=np.float32)
        h, w = img.shape
        angle = float(rng.uniform(-p["skew"], p["skew"]))
        meta["skew_deg"].append(round(angle, 2))
        m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        img = cv2.warpAffine(img, m, (w, h), borderValue=255.0)
        if p["down"] < 1.0:
            small = cv2.resize(img, (int(w * p["down"]), int(h * p["down"])), interpolation=cv2.INTER_AREA)
            img = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
        img = cv2.GaussianBlur(img, (0, 0), p["blur"])
        img = (img - 128) * p["contrast"] + 128 + (1 - p["contrast"]) * 40
        img = img + rng.normal(0, p["noise"], img.shape)
        if p["speckle"]:
            mask = rng.random(img.shape) < p["speckle"]
            img[mask] = rng.choice([0.0, 255.0], size=int(mask.sum()))
        img = np.clip(img, 0, 255).astype(np.uint8)
        if rotate90:
            img = np.rot90(img, k=-1).copy()
        buf = io.BytesIO()
        Image.fromarray(img).save(buf, format="JPEG", quality=p["jpeg"])
        pages.append((buf.getvalue(), img.shape[1], img.shape[0]))
    # PyMuPDF with fixed metadata and no new /ID, so the same seed gives byte-identical files.
    out = pymupdf.open()
    for jpeg, w, h in pages:
        page = out.new_page(width=w * 72 / DPI, height=h * 72 / DPI)
        page.insert_image(page.rect, stream=jpeg)
    out.set_metadata({"title": "SYNTHETIC scanned test document (DocFlow)", "creationDate": "", "modDate": "", "producer": "DocFlow synth"})
    dst_pdf.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst_pdf, garbage=4, deflate=True, no_new_id=True)
    return meta
