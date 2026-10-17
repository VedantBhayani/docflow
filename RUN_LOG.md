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

## 2026-10-17: E-invoice QR in the pipeline (ticket 06) and the evaluation harness (ticket 10)

**QR verification:**
- **Separate trust stores:** `trust/test/` (DocFlow test certificate) and `trust/nic/` (currently only the key printed in NIC's QR procedure PDF). The private test key moved out of the trust store into `tests/fixtures/keys/`.
- **Statuses:**
  - VERIFIED
  - INVALID_SIGNATURE: Q1, blocking
  - UNKNOWN_KEY: Q1, warning, never an accusation
  - WRONG_ISSUER: Q1, blocking
  - UNREADABLE: Q1, warning
- **Q2:** a verified QR is compared with the printed GSTINs, doc no, date, total (±₹1), line count and main HSN.
- **Q3:** printed IRN vs the QR's IRN, but only when the printed IRN is well-formed (64 hex characters). A garbled print is a warning.
- **Q3R:** the IRN recipe check, a warning (canonicalisation unverified).
- **B3:** IRN more than 30 days after the invoice date, a warning.

**Dataset corrections made while building this (labels and realism, not pipeline tuning):**
1. **Label fix:** bad-GSTIN defect documents that carry a QR now expect Q2 as well, because the signed QR holds the true GSTIN and does contradict the print.
2. **QR print size:** raised from 1.5 in to 2 × 2 in, the minimum print size recommended for e-invoice QR codes. At 1.5 in no heavy-scan QR could be decoded (0/10, even with binarisation); at 2 in, 8/10 decode. Digital 24/24, light 14/14. Header layouts shifted to fit.

**Evaluation harness** (`python -m docflow.evaluate --split dev`): scores fields by value and checks every flag outcome against its label, running A3 as a batch per split. Held-out requires `--final` and each run is logged in `results/heldout_runs.log`. Latency is only reported from uncached runs.

**Dev result (37 documents, digital + scans), after the Q3-readability fix:**
- Field accuracy 99.3% (1796/1809); key fields 100% (222/222); grounding rate 99.8%.
- Defect recall 9/9; false flags 0/27; flagged exactly as labelled 37/37.
- QR read on dev scans: light 4/4, heavy 2/3.
- **Change made after looking at dev:** Q3 was falsely accusing a genuine heavy scan whose 6.5 pt IRN OCR had garbled; it now requires a well-formed IRN first.

**Not done:** downloading NIC's production public keys from einvoice1.gst.gov.in. That is a file download and needs the user's approval. Until then, real e-invoices verify as UNKNOWN_KEY (warning), never as tampered.

## 2026-10-17: Bank statement tracer (build ticket 08)

**Generator** (`docflow.synth.statement`): fictional "Zenith Co-operative Bank (SYNTHETIC)" in an HDFC-like dash-narration layout.
- Channels: UPI, IMPS, NEFT, RTGS, cheque, charges, interest. Each line's expected channel, reference, cheque number, direction and amount are in the truth file.
- Narrations wrap onto extra lines as on real statements; page 2 carries a "BALANCE B/F" row; the last page has a summary box.

**Deterministic parts:**
- Narration channel classification and UTR/RRN extraction (only from the channel's own segment; IFSC never taken as UTR; line-wrapped UTRs rejoined).
- Checks S1–S6.
- The Statement Line contract (JSONL/CSV) that Recon consumes.

**What happened on the tracer** (2 statements of 30 lines each; these were used for tuning, so they are **not** part of any reported result):

| Step | Statement Lines fully correct | Fix |
|---|---|---|
| plain serialisation, prompt v1 | 3 / 30 | — |
| table-aware serialisation + prompt v2 | 30 / 30 | Rows under the detected table header are emitted cell by cell with `<empty>` markers, so an amount's column is never lost. Before this, rows with only a withdrawal or only a deposit came out with debit = amount and credit = balance. |
| + statement balance rules | 30 / 30, clean statement CLEAN | The LLM kept taking page 2's "BALANCE B/F" as the opening balance. Carry-forward rows on later pages are now rejected, and a label-anchored rule reads opening and closing from the summary box. |

**Bugs found and fixed while inspecting output, not just tests:**
1. `counterparty_hint` returned "CHQ PAID": `\b` had become a literal backspace character through shell quoting. Fixed and tested; bank charges and interest now have no counterparty.
2. Line evidence covered only the balance cell; it is now the whole row.

Broken-chain twin: S1 on exactly the broken row and the row after it (whose arithmetic it also breaks), and nothing else.

## 2026-10-17: Statement breadth (build ticket 09)

**Set:** 30 statements, **6 layouts × 5**: dash (HDFC-like), slash (SBI-like), mmt (ICICI-like), kotak (Kotak-like), initbr (Axis-like: cheque column, OPENING BALANCE row, branch column after the balance, GST on its own row), and signed (stress: a cash-credit/overdraft account with one Amount column, a Dr/Cr indicator and balances printed "45,000.00 Dr"; plus a UPI reversal pair and a bounced cheque with a return charge and GST).
- Stratified: every layout has 2 defects, 1–2 scans and at least one clean digital statement. Before this, a random draw left "dash" with no clean statement, so its false-flag rate could not be measured.
- 10 scanned (5 light, 5 heavy), 12 single-defect statements (3 per type), 1–6 pages (about 30% are 90–120 transactions long). Split 10 dev / 20 held-out.
- `both_dr_cr` is never put on the signed layout, because a single Amount column cannot print both sides.

**Deterministic table parser** (`statement_table.py`) instead of the LLM for rows: header roles by keyword, words assigned to columns by position, wrapped narrations joined, B/F, opening and total rows recognised. A signed Amount column is split by its Dr/Cr cell; an unreadable side leaves both empty, so S3 flags the row.

**OCR repairs found on dev scans** (general, not layout-specific):
- `OPENING.BALANCE`, where OCR glued the words with a dot, ended page 1's table early. Carry and opening rows now match across `.` and `_`.
- `67.64.203.63~2671`: OCR glued a balance to the next column's value. Split at ingest.
- `:` read as a separator inside amounts (`1.780:16`) is repaired. A bare `12:30` (a time) is still not an amount.
- `45,000.00 Dr` parses as −45,000.00. Paise are required, so `5 Cr` (five crore) is not read as a balance side.

**Consistency check, disclosed:** the table parser and label rules were checked against truth on **all 20 digital statements, including held-out**. This is a generator/label-integrity check: 8,122/8,122 cells matched and nothing was tuned from it. Scan checks were run on dev only.

**Dev result (new set):**
- Statement Lines fully correct 503/518 (**97.1%**); references 96.1%; fields 98.7%; grounding 100%.
- Defects caught 4/4; flagged exactly as labelled 9/10.
- The one false flag is the heavy-scan initbr statement. OCR read `02-04-2026` as `2028` (S4) and misread one amount (S1); human review is the right outcome there.
- `bank_name` misses the "(SYNTHETIC)" suffix on every statement. This is header LLM behaviour and is left as is.

**Feature freeze on statements** after this (re-scope 2026-10-17: fresher internship, stop overbuilding).

## 2026-10-17: NIC public keys installed (ticket 06 completed)

Downloaded with the user's approval from https://einvoice1.gst.gov.in. Index files: `PubKeysEinv1.json`, `PubKeysEinv2.json`, `PubKeysSb.json`. Ten zips went into an empty scratch folder; their members were listed before extracting (only .pem and .cer files).
- `trust/nic/`: 8 production certificates (IRP-1 2020–2027, IRP-2 2023–2027) normalised to DER, plus one bare key (`ProdPubKey3`, 2020–2022, published without a certificate, so it has no derivable kid and is tried only when no kid matches).
- `trust/nic-sandbox/`: 2 sandbox certificates, kept as a separate trust mode that is never mixed with production.
- `SOURCES.json` in each folder records the URL, GenPeriod, zip SHA-256, certificate validity and fetch date. A test checks that the store loads exactly what SOURCES.json lists.

**Findings:**
- NIC's own printed QR in `Qrcode_procedure.pdf` (Sept 2020, kid `115F4426…`) now **VERIFIES** against NIC's production certificate `prodpubkey1`. That makes it a real IRP-signed token verified offline.
- Kid `4DE1544A…`, which the text sample is signed under and which I had labelled "probably sandbox", is actually the **production** IRP-1 certificate for 06/09/2024 – 03/06/2026. The old note was wrong; the superseded loose sample key was removed.
- The sandbox issuer string (`NIC Sandbox`) is my best reading of the docs. If it is wrong, the result shows as WRONG_ISSUER, never VERIFIED.

## 2026-10-17: FINAL held-out evaluation (ticket 10)

Run once at commit `b2628f0`, after the statement feature freeze. An earlier attempt at ~17:10 was killed externally (it took the background shell with it) before writing any report or score. Its partial LLM calls were cached and reused, and no result was seen before this run.

**Invoices** (83 held-out, 42 scanned; `results/2026-10-17/heldout/`):

| Metric | Held-out | Dev |
|---|---|---|
| Field accuracy | 99.1% (3973/4011) | 99.3% |
| Key-field accuracy | 99.8% (497/498) | 100% |
| Grounding rate | 99.4% | 99.8% |
| Defect recall | 16/16 | 9/9 |
| False-flag rate | **5/65 (7.7%)** | 0/27 |
| Flagged exactly as labelled | 77/83 (92.8%) | 37/37 |
| QR read (digital / light / heavy) | 16/16 · 10/10 · 6/7 | |

Mislabelled outcomes (6), diagnosed afterwards and **not tuned**:
- **inv-0027, inv-0055** (heavy): OCR shifted line-item columns, raising C4/C6 or A11/C6.
- **inv-0088** (heavy): OCR read the GSTIN `…M1Z1` as `…MIZ1`. G5 caught it, **but the field was marked VERIFIED**, because the rule extractor read the same OCR text. On scans the LLM and the rule extractor share one OCR source, so their agreement is not independent evidence.
- **inv-0118** (heavy): OCR changed 2 of the 64 IRN characters, so Q3 claimed an IRN mismatch. This is a false accusation on a scan.
- **inv-0120** (heavy): E1 fired on one ungrounded value.
- **inv-0042** (digital, duplicate defect): A3 was caught correctly, plus an extra E1.

**Statements** (20 held-out, 7 scanned; `results/2026-10-17/statements-heldout/`):

| Metric | Held-out | Dev |
|---|---|---|
| Statement Lines fully correct | **90.3% (1354/1500)** | 97.1% |
| References correct | 89.7% | 96.1% |
| Fields by value | 93.8% (digital 99.8%, light 99.6%, **heavy 71.4%**) | 98.7% |
| Grounding rate | 100% | 100% |
| Defect recall | 8/8 | 4/4 |
| False-flag rate | **3/12 (25%)**, all heavy scans | 1/6 |
| Latency per document, uncached | p50 3.5 s, p95 88 s (multi-page heavy scans) | |

**Worst case: stmt-0019** (kotak, heavy, 0/90 lines). The narrow `#` column sits next to Date. On a 2°-skewed heavy scan, OCR merged them (`45 14 Jul 2026`) and misread the month (`Ju|`), so most rows had no parseable date and only 15 of 90 were recognised. The S-checks then flagged the statement, which is the safe direction, but its lines are unusable.

**Honest summary:** digital and lightly scanned documents are close to perfect, and every injected defect was caught. Heavily degraded scans are where DocFlow is weak. They usually end up flagged for review rather than passed silently, but not always for the right reason.

## 2026-10-17: HTTP API, review demo, n8n intake (tickets 11, 12, 14)

- **API:** `POST /extract`, `GET /health`, 10 MB limit, 415 for a non-PDF, 422 for an unreadable PDF without exposing internals. 7 tests.
- **Demo:** `demo/app.py`, standalone. Modern Streamlit pins pillow<13, which conflicts with the OCR stack, so the demo has its own requirements and reads exported results. Checked in the browser: evidence highlight on digital and deskewed scans, flagged statement rows clickable, Excel export with Fields, Lines and Flags sheets.
- **n8n 2.43.7** (npm global, Node 24.11.1). The first install was killed mid-download along with the other background jobs, not by an n8n error. The clean retry took 10 minutes and installed 2,297 packages. The workflow was imported and published by CLI. End-to-end test with the API in test trust mode (the synthetic QR codes are test-signed):

| Dropped in | Routed to | Register row |
|---|---|---|
| clean e-invoice (inv-0095) | `processed/` | CLEAN, QR VERIFIED |
| tampered-QR invoice (inv-0031) | `review/` | NEEDS REVIEW, Q2 "grand_total printed 40,699.00 vs QR 41699.0" |
| `notes.txt` | `failed/` | FAILED, 415 "Only PDF files are accepted." |
| broken-chain statement (stmt-0002) | `review/` | NEEDS REVIEW, S1 rows 31 and 32 |
| invoice with the API stopped | `failed/` | FAILED, `connect ECONNREFUSED 127.0.0.1:8000` |

Each document took about 3 s (LLM cache warm). `n8n/sample-register.xlsx` is the register from this run (synthetic data only).
