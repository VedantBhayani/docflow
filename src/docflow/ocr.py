"""OCR route for pages without a text layer: orient, deskew, read words with boxes.

Evidence boxes on OCR pages refer to the corrected (rotated + deskewed) page image.
The transform is recorded so the review UI can reproduce that exact image.
Results are cached per (document, page, OCR version) and committed, like the LLM cache.
"""

import json
from pathlib import Path

import cv2
import numpy as np
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "data" / "ocr_cache"
OCR_VERSION = "rapidocr3.10-300dpi-deskew-v1"
DPI = 300
POOR_SCAN_CONFIDENCE = 0.80
_engine = None


def _ocr():
    global _engine
    if _engine is None:
        from rapidocr import RapidOCR

        _engine = RapidOCR()
    return _engine


def render(pdf_path: Path, page_index: int, dpi: int = DPI) -> np.ndarray:
    return np.array(pdfium.PdfDocument(str(pdf_path))[page_index].render(scale=dpi / 72).to_pil().convert("L"))


def estimate_skew(img: np.ndarray, max_deg: float = 4.0, step: float = 0.2) -> float:
    """Angle (degrees) that makes text lines horizontal, by maximising the row-profile variance."""
    small = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)
    ink = (small < 160).astype(np.float32)
    h, w = ink.shape
    best, best_angle = -1.0, 0.0
    for angle in np.arange(-max_deg, max_deg + 1e-9, step):
        m = cv2.getRotationMatrix2D((w / 2, h / 2), float(angle), 1.0)
        profile = cv2.warpAffine(ink, m, (w, h), borderValue=0.0).sum(axis=1)
        score = float(np.var(profile))
        if score > best:
            best, best_angle = score, float(angle)
    return round(best_angle, 2)


def rotate(img: np.ndarray, angle: float) -> np.ndarray:
    h, w = img.shape
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, m, (w, h), borderValue=255)


def apply_transform(img: np.ndarray, quarter_turns: int, angle: float) -> np.ndarray:
    img = np.rot90(img, k=quarter_turns).copy() if quarter_turns else img
    return rotate(img, angle) if angle else img


def _read(img: np.ndarray) -> list[dict]:
    out = _ocr()(img, return_word_box=True)
    if not out.txts:
        return []  # nothing readable; RapidOCR then returns a sentinel ('', 1.0, None) that must not count as a word
    h, w = img.shape
    words = []
    for line in out.word_results or ():
        for item in line:
            if len(item) != 3:  # RapidOCR emits empty entries on pages with nothing readable
                continue
            text, score, box = item
            xs, ys = [p[0] for p in box], [p[1] for p in box]
            words.append({"text": text, "confidence": round(float(score), 4),
                          "bbox": (max(min(xs), 0) / w, max(min(ys), 0) / h, min(max(xs), w) / w, min(max(ys), h) / h)})
    return words


def _orientation(img: np.ndarray) -> int:
    """Quarter turns (np.rot90 k) to make a landscape scan of a portrait page upright."""
    if img.shape[1] <= img.shape[0]:
        return 0
    best_k, best_score = 0, -1.0
    small = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
    for k in (1, 3):
        words = _read(np.rot90(small, k=k).copy())
        score = sum(w["confidence"] for w in words)
        if score > best_score:
            best_k, best_score = k, score
    return best_k


def ocr_page(pdf_path: Path, page_index: int, doc_sha256: str) -> dict:
    """Words (normalised boxes, confidence), mean confidence and the applied transform."""
    key = f"{doc_sha256}-p{page_index}-{OCR_VERSION}"
    cached = CACHE / f"{key}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    img = render(pdf_path, page_index)
    k = _orientation(img)
    upright = np.rot90(img, k=k).copy() if k else img
    angle = estimate_skew(upright)
    corrected = rotate(upright, angle) if angle else upright
    words = _read(corrected)
    mean = round(sum(w["confidence"] for w in words) / len(words), 4) if words else 0.0
    result = {"ocr_version": OCR_VERSION, "dpi": DPI, "quarter_turns": k, "deskew_deg": angle,
              "width": corrected.shape[1], "height": corrected.shape[0], "mean_confidence": mean, "words": words}
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(result), encoding="utf-8")
    return result
