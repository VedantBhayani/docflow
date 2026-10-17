# DocFlow evaluation: statements dev split

Run at 2026-10-17 08:47 UTC, 11 documents, trust store `test`.

| Metric | Result |
|---|---|
| Field accuracy (all fields, by value) | 2281/2335 (97.7%) |
| Key-field accuracy | n/a |
| Grounding rate (extracted values proven on the page) | 1936/1936 (100.0%) |
| Key fields VERIFIED by an independent source | n/a |
| Defect recall (injected defects caught) | 4/4 (100.0%) |
| False-flag rate (clean docs with a blocking flag) | 2/7 (28.6%) |
| Straight-through rate (clean docs, no blocking flag) | 5/7 (71.4%) |
| Documents flagged exactly as labelled | 9/11 (81.8%) |
| Prompt-injection docs unaffected | n/a |
| LLM cost per document (mean) | $0.001119 |
| Latency per document, uncached | n/a: every LLM call came from cache, so timings would not be real |

## By scan level

| | Result |
|---|---|
| digital | 1339/1346 (99.5%) |
| heavy | 480/525 (91.4%) |
| light | 462/464 (99.6%) |

## By template

| | Result |
|---|---|
| dash | 322/343 (93.9%) |
| kotak | 852/856 (99.5%) |
| mmt | 410/436 (94.0%) |
| slash | 697/700 (99.6%) |

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
| account_holder | 11/11 (100.0%) |
| account_number | 11/11 (100.0%) |
| bank_name | 0/11 (0.0%) |
| closing_balance | 11/11 (100.0%) |
| lines.balance | 366/366 (100.0%) |
| lines.credit | 363/366 (99.2%) |
| lines.debit | 364/366 (99.5%) |
| lines.narration | 329/366 (89.9%) |
| lines.ref_col | 282/283 (99.6%) |
| lines.txn_date | 366/366 (100.0%) |
| lines.value_date | 145/145 (100.0%) |
| opening_balance | 11/11 (100.0%) |
| period_from | 11/11 (100.0%) |
| period_to | 11/11 (100.0%) |

## Every field error

| Doc | Field | Got | Truth | Status |
|---|---|---|---|---|
| stmt-0006 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0006 | lines.narration | `UPI-SAHYADRI TEXTILES-sahyadni@okzz-ZZBK0008854- 677286012422-PURCHASE` | `UPI-SAHYADRI TEXTILES-sahyadri@okzz-ZZBK0008854-677286012422-PURCHASE` | GROUNDED |
| stmt-0006 | lines.narration | `UPI-KAVERI FABRICATION-kaven@okzz-ZZBK0002983- 655080463696-PAYMENT` | `UPI-KAVERI FABRICATION-kaveri@okzz-ZZBK0002983-655080463696-PAYMENT` | GROUNDED |
| stmt-0006 | lines.narration | `UPL-KAVERI HARDWARE PV-kaven@okzz-ZZBK0008347- 677442672817-PAYMENT` | `UPI-KAVERI HARDWARE PV-kaveri@okzz-ZZBK0008347-677442672817-PAYMENT` | GROUNDED |
| stmt-0006 | lines.credit | `23 612` | `2,358.12` | GROUNDED |
| stmt-0006 | lines.narration | `UPI: TRIKON ELECTRICALS-trikon@okzz-ZZBK0004172- 610418286962-PURCHASE` | `UPI-TRIKON ELECTRICALS-trikon@okzz-ZZBK0004172-610418286962-PURCHASE` | GROUNDED |
| stmt-0006 | lines.narration | `UPI-NIMBUS TEXTILES TR-nimbus@okzz-ZZBK0004488. 625106015587-PAYMENT.` | `UPI-NIMBUS TEXTILES TR-nimbus@okzz-ZZBK0004488-625106015587-PAYMENT` | GROUNDED |
| stmt-0006 | lines.narration | `IMPS-676526425027-SAHYADRI OFFICE SU-ZENITH- XXXXX5141-ADVANCE` | `IMPS-676526425027-SAHYADRI OFFICE SU-ZENITH-XXXXXX5141-ADVANCE` | GROUNDED |
| stmt-0006 | lines.narration | `NÉFT DR-ZZBK0008637-SAHYADRI OFFICE SUPP. ZZBKN26051071916-VENDOR` | `NEFT DR-ZZBK0008637-SAHYADRI OFFICE SUPP-ZZBKN26051071916-VENDOR` | GROUNDED |
| stmt-0006 | lines.narration | `NEFT CR-ZZBK0004130-PRAGATI OFFICE: SUPPL- ZZBKN26051001479` | `NEFT CR-ZZBK0004130-PRAGATI OFFICE SUPPL-ZZBKN26051001479` | GROUNDED |
| stmt-0006 | lines.ref_col | `ZZBKN26051390623` | `ZZBKN26051390823` | GROUNDED |
| stmt-0006 | lines.narration | `IMPS-611243222731-TRIKON ELECTRICALS-ZENITH- XXX XX2238-ADVANCE` | `IMPS-611243222731-TRIKON ELECTRICALS-ZENITH-XXXXXX2238-ADVANCE` | GROUNDED |
| stmt-0006 | lines.narration | `UPI-SAHYADRI LOGISTICS-sahyadn@okzz-ZZBK0004740- G2 5ENT` | `UPI-SAHYADRI LOGISTICS-sahyadri@okzz-ZZBK0004740-628970755628-PAYMENT` | GROUNDED |
| stmt-0006 | lines.narration | `UPI-NIMBUS HARDWARE EN-nimbus@okzz-ZZBKD0007565- 657959264458-PURCHASE` | `UPI-NIMBUS HARDWARE EN-nimbus@okzz-ZZBK0007565-657959264458-PURCHASE` | GROUNDED |
| stmt-0006 | lines.narration | `RTGS CR-ZZBK0007945-TRIKON PACKAGING L ZZBKRC2026051763494990` | `RTGS CR-ZZBK0007945-TRIKON PACKAGING I-ZZBKRC2026051763494990` | GROUNDED |
| stmt-0006 | lines.narration | `UPI-AARAV IT SERVICES-aarav@okzz-ZZBK0008219. 666659938200-PAYMENT` | `UPI-AARAV IT SERVICES-aarav@okzz-ZZBK0008219-666659938200-PAYMENT` | GROUNDED |
| stmt-0006 | lines.narration | `NEFT DR-ZZBK0004519-UDAAN TEXTILES LLP. ZZBKN26052281684-VENDOR` | `NEFT DR-ZZBK0004519-UDAAN TEXTILES LLP-ZZBKN26052281684-VENDOR` | GROUNDED |
| stmt-0006 | lines.narration | `RTGS CR-ZZBK0004777-ANVAY HARDWARE ENT- ZZBKRC20260523117715Q1` | `RTGS CR-ZZBK0004777-ANVAY HARDWARE ENT-ZZBKRC2026052311771501` | GROUNDED |
| stmt-0006 | lines.narration | `NEFT CR-ZZBK0009926-NIMBUS ELECTRICALS T. ZZBKN26052483079` | `NEFT CR-ZZBK0009926-NIMBUS ELECTRICALS T-ZZBKN26052483079` | GROUNDED |
| stmt-0006 | lines.narration | `NEFT CR-ZZBK0002021-TRIKON TEXTILES LLP. ZZBKN26052505792` | `NEFT CR-ZZBK0002021-TRIKON TEXTILES LLP-ZZBKN26052505792` | GROUNDED |
| stmt-0006 | lines.narration | `NEFT DR-ZZBK0004269-PRAGATI STATIONERS P. ZZBKN26052706404-VENDOR` | `NEFT DR-ZZBK0004269-PRAGATI STATIONERS P-ZZBKN26052706404-VENDOR` | GROUNDED |
| stmt-0009 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0013 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0014 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0017 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0017 | lines.narration | `BILNEFT/ZZ97412020/VENDORUDAAN HARDWARE PVT/ZENITH` | `BIL/NEFT/ZZ97412020/VENDOR/UDAAN HARDWARE PVT/ZENITH` | GROUNDED |
| stmt-0017 | lines.narration | `UPVANVAY FABRICATION/anvay@okzz/PURCHASE/ZENITH/612345326824/ ICI319967479` | `UPI/ANVAY FABRICATION/anvay@okzz/PURCHASE/ZENITH/612345326824/ICI319967479` | GROUNDED |
| stmt-0017 | lines.narration | `UPIMEGHDOOT POLYMERS/meghdoot@okzz/PAYMENT/ZENITH/ 682323949002/1C1472771319` | `UPI/MEGHDOOT POLYMERS/meghdoot@okzz/PAYMENT/ZENITH/682323949002/ICI472771319` | GROUNDED |
| stmt-0017 | lines.narration | `UPUANVAY HARDWARE PVT/anvay@okzz/PURCHASE/ZENITH 672584229697AC1255017675` | `UPI/ANVAY HARDWARE PVT/anvay@okzz/PURCHASE/ZENITH/672584229697/ICI255017675` | GROUNDED |
| stmt-0017 | lines.credit | `17972°1` | `1,797.91` | GROUNDED |
| stmt-0017 | lines.narration | `UPIMEGHDOOT POLYMERS/meghdoot@okzz/PAYMENT/ZENITH 6225142129241C1167978362` | `UPI/MEGHDOOT POLYMERS/meghdoot@okzz/PAYMENT/ZENITH/622514212924/ICI167978362` | GROUNDED |
| stmt-0017 | lines.narration | `UPUKAVERI HARDWARE PVkaven@okzz/PURCHASE/ZENITH/636292681819 ICI865740135` | `UPI/KAVERI HARDWARE PV/kaveri@okzz/PURCHASE/ZENITH/636292681819/ICI865740135` | GROUNDED |
| stmt-0017 | lines.narration | `UPIMEGHDOOT PACKAGING/meghdoot@okzz/PAYMENT/ZENITH/ 681951444597/CI782045345` | `UPI/MEGHDOOT PACKAGING/meghdoot@okzz/PAYMENT/ZENITH/681951444597/ICI782045345` | GROUNDED |
| stmt-0017 | lines.narration | `CLG/UDAAN PACKAGING LL/698206/ZZBK/13 07 2026` | `CLG/UDAAN PACKAGING LL/698206/ZZBK/13.07.2026` | GROUNDED |
| stmt-0017 | lines.narration | `BILNEFT/ZZ60337541/VENDOR/TRIKON IT SERVICES/ZENITH` | `BIL/NEFT/ZZ60337541/VENDOR/TRIKON IT SERVICES/ZENITH` | GROUNDED |
| stmt-0017 | lines.narration | `UPVSAHYADRI LOGISTICS/sahyadn@okzz/PURCHASE/ZENITH 623204173839/1CI968134424` | `UPI/SAHYADRI LOGISTICS/sahyadri@okzz/PURCHASE/ZENITH/623204173839/ICI968134424` | GROUNDED |
| stmt-0017 | lines.narration | `CLG/UDAAN STATIONERS T/581870/ZZBK/14.07 2026` | `CLG/UDAAN STATIONERS T/581870/ZZBK/14.07.2026` | GROUNDED |
| stmt-0017 | lines.narration | `UPUPRAGATI STATIONERS/praga9@okzz/PURCHASE/ZENITH/688738821800/ ICI302367410` | `UPI/PRAGATI STATIONERS/pragati@okzz/PURCHASE/ZENITH/688738821800/ICI302367410` | GROUNDED |
| stmt-0017 | lines.debit | `4.356 04` | `4,356.04` | GROUNDED |
| stmt-0017 | lines.narration | `UPVVISTAR ELECTRICALS/vistar@okzz/PAYMENT/ZENITH/689593988234/ ICI233784603` | `UPI/VISTAR ELECTRICALS/vistar@okzz/PAYMENT/ZENITH/689593988234/ICI233784603` | GROUNDED |
| stmt-0017 | lines.credit | `27.294 23` | `27,294.23` | GROUNDED |
| stmt-0017 | lines.narration | `UPiNIMBUS ELECTRICALS/nimbus@okzz/PURCHASE/ZENITH/ 6219247055540CI212655512` | `UPI/NIMBUS ELECTRICALS/nimbus@okzz/PURCHASE/ZENITH/621924705554/ICI212655512` | GROUNDED |
| stmt-0017 | lines.narration | `BILNEFT/ZZ73576619/VENDOR/AARAV POLYMERS PVT/ZENITH` | `BIL/NEFT/ZZ73576619/VENDOR/AARAV POLYMERS PVT/ZENITH` | GROUNDED |
| stmt-0017 | lines.narration | `UPINIMBUS ELECTRICALS/nimbus@okzz/PURCHASE/ZENITH 687429301546/CI517097569` | `UPI/NIMBUS ELECTRICALS/nimbus@okzz/PURCHASE/ZENITH/687429301546/ICI517097569` | GROUNDED |
| stmt-0017 | lines.debit | `1.59.553:55` | `1,59,553.55` | GROUNDED |
| stmt-0017 | lines.narration | `UPIPRAGATI FABRICATIO/pragati@okzz/PAYMENT/ZENITH/674911610429 IC1689995001` | `UPI/PRAGATI FABRICATIO/pragati@okzz/PAYMENT/ZENITH/674911610429/ICI689995001` | GROUNDED |
| stmt-0017 | lines.narration | `BILNEFT/ZZ95761464/VENDOR/MEGHDOOT FABRICATVZENITH` | `BIL/NEFT/ZZ95761464/VENDOR/MEGHDOOT FABRICATI/ZENITH` | GROUNDED |
| stmt-0017 | lines.narration | `MMTAMPS/649232902128/ADVANCE/TRIKON FABRICATION/ZENITH` | `MMT/IMPS/649232902128/ADVANCE/TRIKON FABRICATION/ZENITH` | GROUNDED |
| stmt-0021 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0022 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0024 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0025 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0029 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0030 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |

## Every flag outcome that differs from its label

| Doc | Scan | Defect | Blocking flags | Expected |
|---|---|---|---|---|
| stmt-0006 | heavy | - | S1, S2 | - |
| stmt-0017 | heavy | - | S1, S2, S3 | - |

## Statement Lines (the contract Recon consumes)

| | Result |
|---|---|
| Fully correct (channel, ref, direction, amount, cheque) | 342/366 (93.4%) |
| UTR/RRN references correct | 263/280 (93.9%) |
| dash | 43/48 (89.6%) |
| kotak | 138/138 (100.0%) |
| mmt | 64/83 (77.1%) |
| slash | 97/97 (100.0%) |
