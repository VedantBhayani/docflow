# DocFlow evaluation: statements dev split

Run at 2026-10-17 11:10 UTC, 10 documents, trust store `test`.

| Metric | Result |
|---|---|
| Field accuracy (all fields, by value) | 3187/3230 (98.7%) |
| Key-field accuracy | n/a |
| Grounding rate (extracted values proven on the page) | 2627/2627 (100.0%) |
| Key fields VERIFIED by an independent source | n/a |
| Defect recall (injected defects caught) | 4/4 (100.0%) |
| False-flag rate (clean docs with a blocking flag) | 1/6 (16.7%) |
| Straight-through rate (clean docs, no blocking flag) | 5/6 (83.3%) |
| Documents flagged exactly as labelled | 9/10 (90.0%) |
| Prompt-injection docs unaffected | n/a |
| LLM cost per document (mean) | $0.001108 |
| Latency per document, uncached | {'n': 10, 'p50': 3.72, 'p95': 4.79} |

## By scan level

| | Result |
|---|---|
| digital | 1708/1713 (99.7%) |
| heavy | 431/466 (92.5%) |
| light | 1048/1051 (99.7%) |

## By template

| | Result |
|---|---|
| dash | 526/539 (97.6%) |
| initbr | 254/277 (91.7%) |
| kotak | 1056/1059 (99.7%) |
| mmt | 496/497 (99.8%) |
| signed | 318/319 (99.7%) |
| slash | 537/539 (99.6%) |

## Defect recall by type

| | Result |
|---|---|
| both_dr_cr | 1/1 (100.0%) |
| broken_chain | 1/1 (100.0%) |
| closing_mismatch | 1/1 (100.0%) |
| date_outside_period | 1/1 (100.0%) |

## QR read rate by scan level

| | Result |
|---|---|

## By field

| | Result |
|---|---|
| account_holder | 9/10 (90.0%) |
| account_number | 10/10 (100.0%) |
| bank_name | 0/10 (0.0%) |
| closing_balance | 10/10 (100.0%) |
| lines.balance | 516/518 (99.6%) |
| lines.credit | 518/518 (100.0%) |
| lines.debit | 518/518 (100.0%) |
| lines.narration | 489/518 (94.4%) |
| lines.ref_col | 420/420 (100.0%) |
| lines.txn_date | 517/518 (99.8%) |
| lines.value_date | 150/150 (100.0%) |
| opening_balance | 10/10 (100.0%) |
| period_from | 10/10 (100.0%) |
| period_to | 10/10 (100.0%) |

## Every field error

| Doc | Field | Got | Truth | Status |
|---|---|---|---|---|
| stmt-0002 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0003 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0003 | lines.narration | `NEFT CR-ZZBK0002642-SHAKT1 OFFICE SUPPLI- ZZBKN26070152640` | `NEFT CR-ZZBK0002642-SHAKTI OFFICE SUPPLI-ZZBKN26070152640` | GROUNDED |
| stmt-0003 | lines.narration | `UPI-ANVAY ELECTRICALS-anvay@okzz-ZZBK0008557. 678525483756-PAYMENT` | `UPI-ANVAY ELECTRICALS-anvay@okzz-ZZBK0008557-678525483756-PAYMENT` | GROUNDED |
| stmt-0003 | lines.narration | `IMPS-658820361672-MEGHDOOT FABRICATI-ZENITH- XXOXXX2089-ADVANCE` | `IMPS-658820361672-MEGHDOOT FABRICATI-ZENITH-XXXXXX2089-ADVANCE` | GROUNDED |
| stmt-0003 | lines.narration | `UPI-KAVERI HARDWARE EN-kaven@okzz-ZZBK0006671- 681046006078-PURCHASE` | `UPI-KAVERI HARDWARE EN-kaveri@okzz-ZZBK0006671-681046006078-PURCHASE` | GROUNDED |
| stmt-0003 | lines.narration | `NEFT CR-ZZBK0008857-MEGHDOOT HARDWARE IN ZZBKN26070836639` | `NEFT CR-ZZBK0008857-MEGHDOOT HARDWARE IN-ZZBKN26070836639` | GROUNDED |
| stmt-0003 | lines.narration | `NEFT DR-ZZBK0001696-SARTHI ELECTRICALS L ZZBKN26071246887-VENDOR` | `NEFT DR-ZZBK0001696-SARTHI ELECTRICALS I-ZZBKN26071246887-VENDOR` | GROUNDED |
| stmt-0003 | lines.narration | `UPI-ANVAY OFFICE SUPPL-anvay@2okzz-ZZBK0006642- 671591243031-PURCHASE` | `UPI-ANVAY OFFICE SUPPL-anvay@okzz-ZZBK0006642-671591243031-PURCHASE` | GROUNDED |
| stmt-0003 | lines.narration | `NEFT CR-ZZBK0009725-NIMBUS IT SERVICES L ZZBKN26072162562` | `NEFT CR-ZZBK0009725-NIMBUS IT SERVICES I-ZZBKN26072162562` | GROUNDED |
| stmt-0003 | lines.narration | `IMPS-667913921209-SAHYADRI PACKAGING-ZENITH- XX0X X2255-ADVANCE` | `IMPS-667913921209-SAHYADRI PACKAGING-ZENITH-XXXXXX2255-ADVANCE` | GROUNDED |
| stmt-0003 | lines.narration | `UPI-KAVERI HARDWARE PV-kaven okzz-ZZBK0008228- 643569626216-PAYMENT` | `UPI-KAVERI HARDWARE PV-kaveri@okzz-ZZBK0008228-643569626216-PAYMENT` | GROUNDED |
| stmt-0003 | lines.balance | `.15.44.936.52` | `15,44,936.52` | GROUNDED |
| stmt-0007 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0010 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0013 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0016 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0017 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0018 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0023 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0023 | account_holder | `Nimbus. Textiles Enterprises` | `Nimbus Textiles Enterprises` | GROUNDED |
| stmt-0023 | lines.txn_date | `02-04-2028` | `02-04-2026` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2M/656089713855/PRAGATI ELECTRICAL/PAYMENT/ ZENITH` | `UPI/P2M/658089713855/PRAGATI ELECTRICAL/PAYMENT/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2M/691416744268/VISTAR FABRICATION/PAYMENT/ ZENITH` | `UPI/P2M/691416744268/VISTAR FABRICATION/PAYMENT/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2M/683838043873/SHAKTI ELECTRICALS/PAYMENT/ ZENITH` | `UPI/P2M/683838043873/SHAKTI ELECTRICALS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPVP2A/664002716264/UDAAN HARDWARE PVT/PURCHASE/ ZENITH` | `UPI/P2A/664002716264/UDAAN HARDWARE PVT/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPIP2A/610891592095/KAVERI OFFICE SUPP/PURCHASE/ ZENITH` | `UPI/P2A/610891592095/KAVERI OFFICE SUPP/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPVP2M/610561072941/SHAKTI LOGISTICS UPAYMENT/ZENITH` | `UPI/P2M/610561072941/SHAKTI LOGISTICS I/PAYMENT/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `NEFT/ZZBKN26041260191/TRIKON TEXTILES INVENDOR PAYMENT` | `NEFT/ZZBKN26041260191/TRIKON TEXTILES IN/VENDOR PAYMENT` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2A/694988103412/MEGHDOOT OFFICE SU/PURCHASE/ ZENITH` | `UPI/P2A/694988103412/MEGHDOOT OFFICE SU/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPIP2A/689696104124/TRIKON FABRICATION/PURCHASE/ ZENITH` | `UPI/P2A/689696104124/TRIKON FABRICATION/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2A/639825316945/ANVAY PACKAGING PV/PURCHASE ZENITH` | `UPI/P2A/639825316945/ANVAY PACKAGING PV/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `NEFT/ZZBKN26041606141/SAHYADRI HARDWAREVENDOR PAYMENT` | `NEFT/ZZBKN26041606141/SAHYADRI HARDWARE/VENDOR PAYMENT` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2A/629199235059/ANVAY OFFICE SUPPL/PURCHASE/ ZENITH` | `UPI/P2A/629199235059/ANVAY OFFICE SUPPL/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2A/642152811142/SHAKTI TEXTILES PV/PURCHASE/ ZENITH` | `UPI/P2A/642152811142/SHAKTI TEXTILES PV/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `NEFT/ZZBKN26041902958/SAHYADRI FABRICATVZENITH` | `NEFT/ZZBKN26041902958/SAHYADRI FABRICATI/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2A/642806916552/PRAGATI OFFICE SUP/PURCHASE/ ZENITH` | `UPI/P2A/642806916552/PRAGATI OFFICE SUP/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.balance | `16:50.105.10` | `18,50,105.10` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2M/644274053025/UDAAN PACKAGING PV/PAYMENT/ ZENITH` | `UPI/P2M/644274053025/UDAAN PACKAGING PV/PAYMENT/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `NEFT/ZZBKN26042519410/TRIKON POLYMERS PVIZENITH` | `NEFT/ZZBKN26042519410/TRIKON POLYMERS PV/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPUP2A/670973727426/MEGHDOOT PACKAGING/PURCHASE/ ZENITH` | `UPI/P2A/670973727426/MEGHDOOT PACKAGING/PURCHASE/ZENITH` | GROUNDED |
| stmt-0023 | lines.narration | `UPVP2A/649624949276/ C/PURCHASE ZENITH` | `UPI/P2A/649624949276/MEGHDOOT IT SERVIC/PURCHASE/ZENITH` | GROUNDED |
| stmt-0028 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |

## Every flag outcome that differs from its label

| Doc | Scan | Defect | Blocking flags | Expected |
|---|---|---|---|---|
| stmt-0023 | heavy | - | S1, S4 | - |

## Statement Lines (the contract Recon consumes)

| | Result |
|---|---|
| Fully correct (channel, ref, direction, amount, cheque) | 503/518 (97.1%) |
| UTR/RRN references correct | 365/380 (96.1%) |
| dash | 75/75 (100.0%) |
| initbr | 30/45 (66.7%) |
| kotak | 173/173 (100.0%) |
| mmt | 98/98 (100.0%) |
| signed | 52/52 (100.0%) |
| slash | 75/75 (100.0%) |
