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
