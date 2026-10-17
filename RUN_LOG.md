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
- ~~The C7 rate-slab list~~: verified 2026-10-17 from Notification 9/2025-IT(R) (build ticket 03; see research note 01 addendum).
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

## 2026-10-17: Rule extractor and the first dev-split diagnosis (build ticket 07)

**Rule extractor** (`docflow.rules`): regexes and label anchors for both GSTINs, invoice no, date, taxable total and grand total. It abstains whenever a field is ambiguous.
- Dev, digital documents: 0 wrong out of 112 values produced; it abstained on 2 of 114.
- **Held-out peek, disclosed:** I measured rule precision on the held-out digital documents once, without changing any rule afterwards. Result: 0 wrong out of 240 values produced, abstained on 6 of 246 (the missing-GSTIN defects and the injected "grand total as 0.00" note). The pipeline's LLM path has not been run on held-out.
- Agreement upgrades a field to VERIFIED; disagreement makes it CONFLICT (flag E3, showing both values).

**Dev diagnosis, digital only** (scans need ticket 05). Changes made **after looking at dev errors**:

| Step | Field errors (dev, digital) | Change |
|---|---|---|
| prompt v2, plain serialisation | 27 / 924 (97.1%) | none yet |
| prompt v3 + column-gap markers | 1 / 932 (99.9%) | Serialisation inserts ` \| ` at gaps > 1.2% of page width. Prompt v3 explains it, asks for every word of multi-word values, and adds `irn`. |
| + evidence completion | 1 / 932 | Grounding extends an incomplete word pointer to adjacent words on the same row, but only if that spells the value **exactly**. This removed false E1 flags on correct values such as "5 %". |

- Root cause of the 27 errors: plain serialisation hid column boundaries. Numbers inside descriptions ("23 micron", "500 ml") were read as HSN codes, and side-by-side Supplier/Recipient blocks merged.
- Remaining error: the recipient address on the missing-GSTIN defect document picked up the table header word "Sl". It is a real error and counts against accuracy. Grounding cannot catch it because the LLM pointed at the word it copied.
- Blocking flags matched labels on every dev digital document except the 2 duplicates, which only `process_batch` checks (the diagnosis script calls `process`).

## 2026-10-17: OCR route for scans (build ticket 05)

`docflow.ocr` handles pages with no text layer:
- Landscape pages are oriented by trying 90° and 270° and keeping the higher OCR confidence.
- Pages are deskewed by maximising the row-profile variance over ±4°. Tests recover known rotations within 0.3°.
- RapidOCR reads the page at 300 dpi and returns word boxes. P1 (poor scan) fires when mean confidence < 0.80.
- OCR results are cached per (document, page, OCR version) in `data/ocr_cache/`, which is committed, and the transform is recorded so the review UI can reproduce the image the boxes refer to.
- RapidOCR returns a fake `('', 1.0, None)` "word" with confidence 1.0 when it reads nothing. That is now guarded, and a pure-noise test page proves P1 fires.

**Dev iterations on scans** (all changes general OCR rules, made **while looking at dev scans**):

| Step | Light: fields / flags as labelled | Heavy: fields / flags as labelled | Change |
|---|---|---|---|
| first run | 99.0% / 4 of 11 | 85.2% / 0 of 7 | — |
| + value-based scoring, E1 severity, glued-label split | 99.2% / 11 of 11 | 96.8% / 1 of 7 | `GSTIN:07…` split at ingest; E1 is a warning for fields no Check uses (IRN, names, addresses) |
| + OCR amount repair, numeric grounding, GSTIN normalisation | 99.2% / 11 of 11 | 97.7% / 7 of 7 | `22.014.48` and `3.25,635.05` read as amounts; an amount field grounds on exact numeric equality with a printed word; non-alphanumerics stripped from GSTINs |

- The digital dev split is unchanged at 931/932.
- **These dev numbers are optimistic by construction:** I changed code after looking at these 18 scans. The held-out run is the real test.
- **Known residual:** the IRN, printed at 6.5 pt, is often garbled by OCR on scans. It raises an E1 warning, not a block, and the QR carries the IRN anyway.
