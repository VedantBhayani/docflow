# Run log

What was run, on what, and what came out. This includes the things that failed or changed.

## 2026-10-17: Day-1 smoke tests (build ticket 01)

**Machine:** Windows 10, Intel64 Family 6 Model 142 (8th-gen Core class), CPU only. Python 3.12.11 via uv.
**Versions:** mistralai 3.2.0, rapidocr 3.10.0, onnxruntime 1.31.0, pymupdf 1.28.2, pypdfium2, zxing-cpp 3.1.1, pyjwt 2.15.1. Full record: `results/smoke/2026-10-17.json`.
**Command:** `uv run python -m docflow.smoke`, plus `uv run pytest`.

| Check | Result | Notes |
|---|---|---|
| Mistral structured output | **PASS** | `mistral-small-2603` (confirmed by `models.retrieve` as "Mistral Small 4", 262k context) returned the exact expected fields through `chat.parse` in 0.8 s, using 91 prompt and 49 completion tokens. |
| RapidOCR word boxes | **PASS** | 3 NIC pages at 300 dpi: median **6.08 s/page**, max 7.55 s. 436 word boxes. Read "Signed QR Code" correctly. |
| NIC sample QR, offline verification | **PASS** | NIC's published text sample (kid `4DE1544A…`) verifies with NIC's published key. A random key and a tampered payload are both rejected. |
| QR decode from PDF (zxing-cpp) | **PASS** | It decodes the QR image in NIC's PDF. See finding 3. |
| Secrets | **PASS** | The API key appears in no file except `.env`, which is gitignored (checked by scanning every file). |

### Findings that changed the plan

1. **The research had the wrong model IDs.** The API IDs are `mistral-small-2603` and `ministral-14b-2512`, not the pricing-page slugs. DocFlow pins the dated IDs, never `-latest`, so evaluation runs can be reproduced.
2. **OCR is slower than budgeted.** The original budget was 5 s/page, which was a guess. One run passed at 4.77 s and the next failed. A repeated measurement gave a median of 6–7.5 s at 300 dpi; lower dpi barely helped (5.4 s at 150 dpi). Decision: keep 300 dpi, because accuracy matters more than speed. Cache OCR output per page, so evaluation reruns cost nothing. Reset the budget to a ≤ 10 s median. This is a deliberate, recorded change, not a moved goalpost: a full uncached evaluation run of about 155 scanned pages takes about 20 min, which is acceptable.
3. **NIC's QR image is not its text sample.** The QR picture in NIC's PDF is a 2020 token (kid `115F4426…`) that the key printed in the same PDF cannot verify. Design consequence (build ticket 06): when no key in the trust store matches the token's key ID, report `UNKNOWN_KEY` as a warning, never "signature invalid". Calling a genuine invoice tampered because we lack its key would be a false accusation.

### Not yet verified

- INR/USD rate for ₹-per-document reporting (it's set when cost is first computed, with the date and source).
- The C7 rate-slab list against Notification 9/2025-CTR (build ticket 03).
- The NIC production key files (build ticket 06).

## 2026-10-17: Synthetic invoice set (build ticket 04)

**Command:** `uv run python -m docflow.synth invoices --seed 7` writes 120 invoices to `data/synthetic/invoices/` (26 MB) plus `manifest.json`.

**Composition:**
- 4 templates × 30.
- 60 digital, 32 light scans, 28 heavy scans.
- 48 with a QR code (40%), signed with the DocFlow TEST key.
- 31 defect documents across 10 types: GSTIN check digit, wrong tax type, line arithmetic, invalid slab, missing recipient GSTIN, prompt injection, QR total mismatch, QR bad signature (rogue key under the test key's ID), rotated page, and 2 duplicate pairs.
- Split: 37 dev / 83 held-out. Every defect type appears in both splits, and duplicate pairs stay together.

**Label integrity:** proved by `tests/test_synth_dataset.py`, 9 tests.
- Every truth value is printed on its digital page.
- The Check engine run on truth values gives exactly each document's expected blocking flags.
- QR codes decode from the page and verify; the rogue key fails.
- Scans have no text layer.
- The same seed reproduces byte-identical PDFs and truth files.

**Deviation from spec:** scan degradation is DocFlow's own seeded OpenCV code, not augraphy. This avoided a heavy dependency on Windows and keeps every effect explicit. Light = ±1° skew, blur 0.6, noise 6, JPEG 75. Heavy = ±3° skew, 0.7× resample, blur 1.1, noise 14, contrast 0.75, speckle, JPEG 45. I checked page renders by eye: the heavy scans are degraded but still legible to a human.
