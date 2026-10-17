# DocFlow evaluation: statements heldout split (FINAL held-out run)

Run at 2026-10-17 12:03 UTC, 20 documents, trust store `test`.

| Metric | Result |
|---|---|
| Field accuracy (all fields, by value) | 8895/9486 (93.8%) |
| Key-field accuracy | n/a |
| Grounding rate (extracted values proven on the page) | 7140/7141 (100.0%) |
| Key fields VERIFIED by an independent source | n/a |
| Defect recall (injected defects caught) | 8/8 (100.0%) |
| False-flag rate (clean docs with a blocking flag) | 3/12 (25.0%) |
| Straight-through rate (clean docs, no blocking flag) | 9/12 (75.0%) |
| Documents flagged exactly as labelled | 17/20 (85.0%) |
| Prompt-injection docs unaffected | n/a |
| LLM cost per document (mean) | $0.001125 |
| Latency per document, uncached | {'n': 20, 'p50': 3.54, 'p95': 87.67} |

## By scan level

| | Result |
|---|---|
| digital | 6534/6549 (99.8%) |
| heavy | 1431/2003 (71.4%) |
| light | 930/934 (99.6%) |

## By template

| | Result |
|---|---|
| dash | 1594/1645 (96.9%) |
| initbr | 2403/2482 (96.8%) |
| kotak | 730/1178 (62.0%) |
| mmt | 649/653 (99.4%) |
| signed | 1830/1834 (99.8%) |
| slash | 1689/1694 (99.7%) |

## Defect recall by type

| | Result |
|---|---|
| both_dr_cr | 2/2 (100.0%) |
| broken_chain | 2/2 (100.0%) |
| closing_mismatch | 2/2 (100.0%) |
| date_outside_period | 2/2 (100.0%) |

## QR read rate by scan level

| | Result |
|---|---|

## By field

| | Result |
|---|---|
| account_holder | 20/20 (100.0%) |
| account_number | 20/20 (100.0%) |
| bank_name | 0/20 (0.0%) |
| closing_balance | 20/20 (100.0%) |
| lines.balance | 1390/1500 (92.7%) |
| lines.credit | 1452/1500 (96.8%) |
| lines.debit | 1450/1500 (96.7%) |
| lines.narration | 1319/1500 (87.9%) |
| lines.ref_col | 1289/1375 (93.7%) |
| lines.txn_date | 1406/1500 (93.7%) |
| lines.value_date | 469/471 (99.6%) |
| opening_balance | 20/20 (100.0%) |
| period_from | 20/20 (100.0%) |
| period_to | 20/20 (100.0%) |

## Every field error

| Doc | Field | Got | Truth | Status |
|---|---|---|---|---|
| stmt-0001 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0004 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0004379-SAHYADRI LOGISTICS P. ZZBKN26070137214` | `NEFT CR-ZZBK0004379-SAHYADRI LOGISTICS P-ZZBKN26070137214` | GROUNDED |
| stmt-0004 | lines.value_date | `02/07/26.` | `02/07/26` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-677997760719-SARTHI STATIONERS-ZENITH- XXXX X9956-ADVANCE` | `IMPS-677997760719-SARTHI STATIONERS-ZENITH-XXXXXX9956-ADVANCE` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-638034663242-TRIKON.LOGISTICS E-ZENITH- XXX0XXX2628-ADVANCE` | `IMPS-638034663242-TRIKON LOGISTICS E-ZENITH-XXXXXX2628-ADVANCE` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-TRIKON OFFICE SUPP-tikon@okzz-ZZBK0006225- 693772427352-PURCHASE` | `UPI-TRIKON OFFICE SUPP-trikon@okzz-ZZBK0006225-693772427352-PURCHASE` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-660902240141-SAHYADRI FABRICATI-ZENITH- XXXX0X5413-ADVANCE` | `IMPS-660902240141-SAHYADRI FABRICATI-ZENITH-XXXXXX5413-ADVANCE` | GROUNDED |
| stmt-0004 | lines.ref_col | `66090224Q141` | `660902240141` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-NIMBUS IT SERVICES-nimbus@okzz-ZZBK0003780. 682864885540-PAYMENT` | `UPI-NIMBUS IT SERVICES-nimbus@okzz-ZZBK0003780-682864885540-PAYMENT` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-675809709226-ANVAY OFFICE SUPPL-ZENITH- XX XX5035-ADVANCE` | `IMPS-675809709226-ANVAY OFFICE SUPPL-ZENITH-XXXXXX5035-ADVANCE` | GROUNDED |
| stmt-0004 | lines.balance | `49.05.967.65.` | `49,05,987.65` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-NIMBUS PACKAGING T-rimbus@okzz-ZZBK0004977- 618733628338-PURCHASE` | `UPI-NIMBUS PACKAGING T-nimbus@okzz-ZZBK0004977-618733628338-PURCHASE` | GROUNDED |
| stmt-0004 | lines.balance | `39.75.391..17` | `39,75,391.17` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0005143-SHAKTI LOGISTICS LLP. ZZBKN26070978366` | `NEFT CR-ZZBK0005143-SHAKTI LOGISTICS LLP-ZZBKN26070978366` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-TRIKON LOGISTICS T-brikon@okzz-ZZBK0006121- 678008535976-PURCHASE` | `UPI-TRIKON LOGISTICS T-trikon@okzz-ZZBK0006121-678008535976-PURCHASE` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT DR-ZZBK0006564-TRIKON POLYMERS LLP. ZZBKN26071076605-VENDOR` | `NEFT DR-ZZBK0006564-TRIKON POLYMERS LLP-ZZBKN26071076605-VENDOR` | GROUNDED |
| stmt-0004 | lines.narration | `UP1-NIMBUS IT SERVICES-nimbus@okzz-ZZBK0003816- 668460448662-PAYMENT` | `UPI-NIMBUS IT SERVICES-nimbus@okzz-ZZBK0003816-668460448662-PAYMENT` | GROUNDED |
| stmt-0004 | lines.ref_col | `668480448662` | `668460448662` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-682864192862-SAHYADRI POLYMERS-ZENITH XX XXX8651-ADVANCE` | `IMPS-682864192862-SAHYADRI POLYMERS-ZENITH-XXXXXX8651-ADVANCE` | GROUNDED |
| stmt-0004 | lines.value_date | `12/07/26.` | `12/07/26` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0009691-SAHYADRI OFFICE SUPP. ZZBKN26071226846` | `NEFT CR-ZZBK0009691-SAHYADRI OFFICE SUPP-ZZBKN26071226846` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-TRIKON HARDWARE IN-tikon@okzz-ZZBK0006536- 655592708258-PAYMENT` | `UPI-TRIKON HARDWARE IN-trikon@okzz-ZZBK0006536-655592708258-PAYMENT` | GROUNDED |
| stmt-0004 | lines.ref_col | `655592706258` | `655592708258` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-NIMBUS STATIONERS-nimbus@okzz-ZZBK0009839 G99 ENT` | `UPI-NIMBUS STATIONERS-nimbus@okzz-ZZBK0009839-699038094152-PAYMENT` | GROUNDED |
| stmt-0004 | lines.narration | `UP1-SHAKTI PACKAGING T-shaksi@okzz-ZZBK0003565- 692746350229-PURCHASE` | `UPI-SHAKTI PACKAGING T-shakti@okzz-ZZBK0003565-692746350229-PURCHASE` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-SHAKTI FABRICATION-shaki@okzz-ZZBK0007112- 635175021498-PAYMENT` | `UPI-SHAKTI FABRICATION-shakti@okzz-ZZBK0007112-635175021498-PAYMENT` | GROUNDED |
| stmt-0004 | lines.narration | `RTGS CR-ZZBK0003986-SHAKTI OFFICE SUPP. ZZBKRC2026071444480593` | `RTGS CR-ZZBK0003986-SHAKTI OFFICE SUPP-ZZBKRC2026071444480593` | GROUNDED |
| stmt-0004 | lines.narration | `UP1-VISTAR TEXTILES PV-vistargokzz-ZZBK0003761- 674791191747-PURCHASE` | `UPI-VISTAR TEXTILES PV-vistar@okzz-ZZBK0003761-674791191747-PURCHASE` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT DR-ZZBK0002759-PRAGATI IT SERVICES. ZZBKN26071576366-VENDOR` | `NEFT DR-ZZBK0002759-PRAGATI IT SERVICES-ZZBKN26071576366-VENDOR` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-ANVAY FABRICATION-amvay@okzz-ZZBK0008075- 661898146280-PURCHASE` | `UPI-ANVAY FABRICATION-anvay@okzz-ZZBK0008075-661898146280-PURCHASE` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0006811-MEGHDOOT OFFICE SUPP. ZZBKN26071665779` | `NEFT CR-ZZBK0006811-MEGHDOOT OFFICE SUPP-ZZBKN26071665779` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0007141-MEGHDOOT PACKAGING P. ZZBKN26071686341` | `NEFT CR-ZZBK0007141-MEGHDOOT PACKAGING P-ZZBKN26071686341` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-628379984651-TRIKON IT SERVICES-ZENITH- XXXXXXX1813-ADVANCE` | `IMPS-628379984651-TRIKON IT SERVICES-ZENITH-XXXXXX1813-ADVANCE` | GROUNDED |
| stmt-0004 | lines.credit | `77.64.1.30` | `77,641.30` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-MEGHDOOT STATIONER-meghdoot@okzz- ZZBK0008852-875738371949-PAYMENT` | `UPI-MEGHDOOT STATIONER-meghdoot@okzz-ZZBK0008852-675738371949-PAYMENT` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0005564-VISTAR OFFICE SUPPLL ZZBKN26071873264` | `NEFT CR-ZZBK0005564-VISTAR OFFICE SUPPLI-ZZBKN26071873264` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-669747698192-SHAKTI LOGISTICS E-ZENITH- XX XXX9281-ADVANCE` | `IMPS-669747698192-SHAKTI LOGISTICS E-ZENITH-XXXXXX9281-ADVANCE` | GROUNDED |
| stmt-0004 | lines.narration | `UP1-KAVERi ELECTRICALS-kaven@okzz-ZZBK0008842- 621587710167-PURCHASE` | `UPI-KAVERI ELECTRICALS-kaveri@okzz-ZZBK0008842-621587710167-PURCHASE` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-SHAKT1 HARDWARE TR-shaks@okzz-ZZBK0003677. 687718090696-PURCHASE` | `UPI-SHAKTI HARDWARE TR-shakti@okzz-ZZBK0003677-687718090696-PURCHASE` | GROUNDED |
| stmt-0004 | lines.debit | `3.175..19` | `3,175.19` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-SARTHI IT SERVICES-sarthi@okzz-ZZBK0004089 679336538032-PAYMENT` | `UPI-SARTHI IT SERVICES-sarthi@okzz-ZZBK0004089-679336538032-PAYMENT` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-SARTHI IT SERVICES-sarthi@okzz-ZZBK0001017. 614747504967-PURCHASE` | `UPI-SARTHI IT SERVICES-sarthi@okzz-ZZBK0001017-614747504967-PURCHASE` | GROUNDED |
| stmt-0004 | lines.balance | `25.27.797 42` | `25,27,797.42` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0002978-TRIKON FABRICATION P. ZZBKN26072254381` | `NEFT CR-ZZBK0002978-TRIKON FABRICATION P-ZZBKN26072254381` | GROUNDED |
| stmt-0004 | lines.ref_col | `2 C22 4947` | `ZZBKN26072364947` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-646454521763-KAVERI TEXTILES TR-ZENITH XXXXXX1396-ADVANCE` | `IMPS-646454521763-KAVERI TEXTILES TR-ZENITH-XXXXXX1396-ADVANCE` | GROUNDED |
| stmt-0004 | lines.narration | `NEFT CR-ZZBK0005762-VISTAR IT SERVICES L ZZBKN26072774101` | `NEFT CR-ZZBK0005762-VISTAR IT SERVICES I-ZZBKN26072774101` | GROUNDED |
| stmt-0004 | lines.narration | `IMPS-612547083104-KAVERI PACKAGING P-ZENITH- XXXXX8361-ADVANCE` | `IMPS-612547083104-KAVERI PACKAGING P-ZENITH-XXXXXX8361-ADVANCE` | GROUNDED |
| stmt-0004 | lines.narration | `UPI-MEGHDOOT POLYMERS-meghdool@okzz- ZZBK0009694-610357717517-PAYMENT` | `UPI-MEGHDOOT POLYMERS-meghdoot@okzz-ZZBK0009694-610357717517-PAYMENT` | GROUNDED |
| stmt-0005 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0006 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0008 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0008 | lines.narration | `DEP ZZBK/kaveri@okzz/PAYMENT` | `DEP TFR UPI/CR/616315010655/KAVERI HARDWARE IN/ZZBK/kaveri@okzz/PAYMENT` | GROUNDED |
| stmt-0008 | lines.ref_col | `65` | `616315010655` | GROUNDED |
| stmt-0009 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0011 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0012 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0014 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0015 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0019 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0019 | lines.txn_date | `23 08 Ju| 2026` | `01 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `CHQ PAID VISTAR IT SERVICES I` | `IMPS-677896929368-NIMBUS HARDWARE IN` | GROUNDED |
| stmt-0019 | lines.ref_col | `596827` | `IMPS-677896929368` | GROUNDED |
| stmt-0019 | lines.debit | `8,87.034.18` | `None` | GROUNDED |
| stmt-0019 | lines.credit | `None` | `579.61` | MISSING |
| stmt-0019 | lines.balance | `-1.58.998.51` | `12,99,608.87` | GROUNDED |
| stmt-0019 | lines.txn_date | `45 14 Jul 2026` | `01 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `RTGS ZZBKRC2026071456868469 MEGHDOOT OFFICE SU` | `UPI/KAVERI FABRICATION/617753863917/PURCHASE` | GROUNDED |
| stmt-0019 | lines.ref_col | `ZZBKRC2026071456868469` | `UPI-607885211910` | GROUNDED |
| stmt-0019 | lines.debit | `None` | `4,686.23` | MISSING |
| stmt-0019 | lines.credit | `3.23.459.00` | `None` | GROUNDED |
| stmt-0019 | lines.balance | `11.47.970.07` | `12,94,922.64` | GROUNDED |
| stmt-0019 | lines.txn_date | `46 14 .Jua| 2026` | `01 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `NEFT ZZBKN26071443867 KAVERI IT SERVICES` | `NEFT ZZBKN26070174879 AARAV IT SERVICES` | GROUNDED |
| stmt-0019 | lines.ref_col | `ZZBKN26071443867` | `ZZBKN26070174879` | GROUNDED |
| stmt-0019 | lines.credit | `1.71.556.52` | `4,75,088.48` | GROUNDED |
| stmt-0019 | lines.balance | `-9.76.413.55` | `17,70,011.12` | GROUNDED |
| stmt-0019 | lines.txn_date | `47 14 Ju| 2026` | `01 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `Int.Pd: 8653076:14-07-2026` | `Int.Pd:4715937:01-07-2026` | GROUNDED |
| stmt-0019 | lines.credit | `667.01` | `610.51` | GROUNDED |
| stmt-0019 | lines.balance | `-9.75.746.54` | `17,70,621.63` | GROUNDED |
| stmt-0019 | lines.txn_date | `48 14 Jk 2026` | `02 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `IMPS-611849138281-AARAV ELECTRICALS` | `RTGS ZZBKRC2026070203643206 UDAAN IT SERVICES` | GROUNDED |
| stmt-0019 | lines.ref_col | `IMPS-611849138281` | `ZZBKRC2026070203643206` | GROUNDED |
| stmt-0019 | lines.credit | `69.841.99` | `33,840.40` | GROUNDED |
| stmt-0019 | lines.balance | `-9.05.904.55` | `18,04,462.03` | GROUNDED |
| stmt-0019 | lines.txn_date | `49 15 J 2026` | `02 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `SMS CHGS` | `RTGS ZZBKRC2026070238106930 MEGHDOOT PACKAGING` | GROUNDED |
| stmt-0019 | lines.ref_col | `None` | `ZZBKRC2026070238106930` | MISSING |
| stmt-0019 | lines.debit | `17.70` | `None` | GROUNDED |
| stmt-0019 | lines.credit | `None` | `2,37,658.30` | MISSING |
| stmt-0019 | lines.balance | `-9.05.922.25` | `20,42,120.33` | GROUNDED |
| stmt-0019 | lines.txn_date | `50 15 Jul 2026` | `03 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `UPI/SHAKTI HARDWARE EN/629657044802/PURCHASE` | `NEFT ZZBKN26070359879 NIMBUS OFFICE SUPP` | GROUNDED |
| stmt-0019 | lines.ref_col | `UPI-669908056133` | `ZZBKN26070359879` | GROUNDED |
| stmt-0019 | lines.debit | `4.38.405.06` | `4,069.82` | GROUNDED |
| stmt-0019 | lines.balance | `-13.44.327.31` | `20,38,050.51` | GROUNDED |
| stmt-0019 | lines.txn_date | `51 15 Jul 2026` | `03 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `NEFT ZZBKN26071520555 PRAGATI FABRICATIO` | `UPI/SARTHI FABRICATION/637076941872/PAYMENT` | GROUNDED |
| stmt-0019 | lines.ref_col | `ZZBKN26071520555` | `UPI-814593875280` | GROUNDED |
| stmt-0019 | lines.credit | `60.822.23` | `4,221.41` | GROUNDED |
| stmt-0019 | lines.balance | `-12.83.505.08` | `20,42,271.92` | GROUNDED |
| stmt-0019 | lines.txn_date | `52 15 Jul 2026` | `03 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `NEFT ZZBKN26071518124 SAHYADRI FABRICATI` | `CHQ PAID SARTHI HARDWARE ENTE` | GROUNDED |
| stmt-0019 | lines.ref_col | `ZZBKN26071518124` | `857871` | GROUNDED |
| stmt-0019 | lines.debit | `3.707.54` | `4,52,469.47` | GROUNDED |
| stmt-0019 | lines.balance | `-12.87.212.62` | `15,89,802.45` | GROUNDED |
| stmt-0019 | lines.txn_date | `53 16 Jul 2026` | `04 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `UPVANVAY PACKAGING LL/667166229540/PURCHASE` | `CHQ PAID MEGHDOOT OFFICE SUPP` | GROUNDED |
| stmt-0019 | lines.ref_col | `UPI-166655892328` | `933767` | GROUNDED |
| stmt-0019 | lines.debit | `34.832.91` | `6,92,604.73` | GROUNDED |
| stmt-0019 | lines.balance | `-13.22.045.53` | `8,97,197.72` | GROUNDED |
| stmt-0019 | lines.txn_date | `67 20 Jul 2026` | `04 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `NEFT ZZBKN26072019844 KAVERI POLYMERS IN` | `CHQ PAID AARAV HARDWARE ENTER` | GROUNDED |
| stmt-0019 | lines.ref_col | `ZZBKN26072019844` | `721193` | GROUNDED |
| stmt-0019 | lines.debit | `None` | `25,620.34` | MISSING |
| stmt-0019 | lines.credit | `6.91.149.40` | `None` | GROUNDED |
| stmt-0019 | lines.balance | `1.36.196.58` | `8,71,577.38` | GROUNDED |
| stmt-0019 | lines.txn_date | `68 22 Ja| 2026` | `04 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `IMPS-653615693365-PRAGATI IT SERVICE` | `IMPS-663608260203-KAVERI ELECTRICALS` | GROUNDED |
| stmt-0019 | lines.ref_col | `MPS-653615693365` | `IMPS-663608260203` | GROUNDED |
| stmt-0019 | lines.credit | `3.31.736.85` | `5,20,161.72` | GROUNDED |
| stmt-0019 | lines.balance | `4.67.933.43` | `13,91,739.10` | GROUNDED |
| stmt-0019 | lines.txn_date | `69 22 Jul 2026` | `04 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `UPIKAVERI HARDWARE LL/688115571775/PURCHASE` | `NEFT ZZBKN26070416936 ANVAY OFFICE SUPPL` | GROUNDED |
| stmt-0019 | lines.ref_col | `UPL-321161073714` | `ZZBKN26070416936` | GROUNDED |
| stmt-0019 | lines.debit | `84.345.72` | `None` | GROUNDED |
| stmt-0019 | lines.credit | `None` | `72,109.20` | MISSING |
| stmt-0019 | lines.balance | `3.83.587.71` | `14,63,848.30` | GROUNDED |
| stmt-0019 | lines.txn_date | `89 .28 Jμ| 2026` | `04 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `SMS CHGS` | `UPI/PRAGATI IT SERVICE/658548435428/PURCHASE` | GROUNDED |
| stmt-0019 | lines.ref_col | `None` | `UPI-556017212849` | MISSING |
| stmt-0019 | lines.debit | `17.70` | `19,323.70` | GROUNDED |
| stmt-0019 | lines.balance | `-9.68.747.60.` | `14,44,524.60` | GROUNDED |
| stmt-0019 | lines.txn_date | `90. 28 2026` | `05 Jul 2026` | GROUNDED |
| stmt-0019 | lines.narration | `CHQ PAID ANVAY OFFICE SUPPLIE` | `UPI/VISTAR HARDWARE IN/693524324628/PAYMENT` | GROUNDED |
| stmt-0019 | lines.ref_col | `036902` | `UPI-865526582878` | GROUNDED |
| stmt-0019 | lines.debit | `62.343.00` | `None` | GROUNDED |
| stmt-0019 | lines.credit | `None` | `58,937.09` | MISSING |
| stmt-0019 | lines.balance | `-10.31.090.60` | `15,03,461.69` | GROUNDED |
| stmt-0019 | lines.txn_date | `None` | `05 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26070521251 UDAAN LOGISTICS IN` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26070521251` | ABSENT |
| stmt-0019 | lines.debit | `None` | `3,98,698.99` | ABSENT |
| stmt-0019 | lines.balance | `None` | `11,04,762.70` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `06 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26070693305 ANVAY STATIONERS T` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26070693305` | ABSENT |
| stmt-0019 | lines.debit | `None` | `7,69,690.22` | ABSENT |
| stmt-0019 | lines.balance | `None` | `3,35,072.48` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `06 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/MEGHDOOT HARDWARE/627836214054/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-243733832720` | ABSENT |
| stmt-0019 | lines.credit | `None` | `3,08,412.64` | ABSENT |
| stmt-0019 | lines.balance | `None` | `6,43,485.12` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `06 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SHAKTI PACKAGING E/663787037850/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-957724805525` | ABSENT |
| stmt-0019 | lines.credit | `None` | `84,027.93` | ABSENT |
| stmt-0019 | lines.balance | `None` | `7,27,513.05` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `07 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/UDAAN ELECTRICALS/633921782910/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-982509097375` | ABSENT |
| stmt-0019 | lines.credit | `None` | `4,690.08` | ABSENT |
| stmt-0019 | lines.balance | `None` | `7,32,203.13` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `08 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SARTHI OFFICE SUPP/673012885691/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-634062057559` | ABSENT |
| stmt-0019 | lines.debit | `None` | `4,149.76` | ABSENT |
| stmt-0019 | lines.balance | `None` | `7,28,053.37` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `08 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `SMS CHGS` | ABSENT |
| stmt-0019 | lines.debit | `None` | `17.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `7,28,035.67` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `08 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID VISTAR IT SERVICES I` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `596827` | ABSENT |
| stmt-0019 | lines.debit | `None` | `8,87,034.18` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-1,58,998.51` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `08 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID VISTAR LOGISTICS TRA` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `374565` | ABSENT |
| stmt-0019 | lines.debit | `None` | `1,988.63` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-1,60,987.14` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `09 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26070975540 KAVERI PACKAGING E` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26070975540` | ABSENT |
| stmt-0019 | lines.credit | `None` | `58,633.28` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-1,02,353.86` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `09 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID VISTAR FABRICATION P` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `149159` | ABSENT |
| stmt-0019 | lines.debit | `None` | `4,736.25` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-1,07,090.11` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `09 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/AARAV IT SERVICES/668311847494/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-659939857090` | ABSENT |
| stmt-0019 | lines.debit | `None` | `2,95,796.28` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,02,886.39` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `10 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SARTHI LOGISTICS E/643443856209/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-424785494554` | ABSENT |
| stmt-0019 | lines.debit | `None` | `2,587.57` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,05,473.96` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `10 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SARTHI IT SERVICES/646979247249/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-878104954691` | ABSENT |
| stmt-0019 | lines.credit | `None` | `4,458.68` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,01,015.28` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `11 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `SMS CHGS` | ABSENT |
| stmt-0019 | lines.debit | `None` | `17.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,01,032.98` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `11 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/MEGHDOOT PACKAGING/614819978945/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-770637241041` | ABSENT |
| stmt-0019 | lines.debit | `None` | `62,808.04` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,63,841.02` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `11 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/NIMBUS POLYMERS PV/648114558864/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-494764125128` | ABSENT |
| stmt-0019 | lines.debit | `None` | `3,14,676.33` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-7,78,517.35` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `11 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071132208 TRIKON HARDWARE TR` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071132208` | ABSENT |
| stmt-0019 | lines.credit | `None` | `3,16,343.77` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,62,173.58` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `11 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID SAHYADRI POLYMERS PV` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `378666` | ABSENT |
| stmt-0019 | lines.debit | `None` | `4,40,757.19` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,02,930.77` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `12 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-670274946694-SHAKTI POLYMERS LL` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-670274946694` | ABSENT |
| stmt-0019 | lines.credit | `None` | `1,531.07` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,01,399.70` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `12 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID TRIKON IT SERVICES L` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `366455` | ABSENT |
| stmt-0019 | lines.debit | `None` | `55,048.55` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,56,448.25` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `12 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/ANVAY STATIONERS T/688529356816/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-202820824299` | ABSENT |
| stmt-0019 | lines.credit | `None` | `3,21,800.76` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,34,647.49` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `12 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071247622 ANVAY HARDWARE LLP` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071247622` | ABSENT |
| stmt-0019 | lines.debit | `None` | `717.08` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,35,364.57` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `13 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `SMS CHGS` | ABSENT |
| stmt-0019 | lines.debit | `None` | `17.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,35,382.27` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `13 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071312689 KAVERI POLYMERS IN` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071312689` | ABSENT |
| stmt-0019 | lines.credit | `None` | `13,963.14` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,21,419.13` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `13 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-689568159239-ANVAY LOGISTICS PV` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-689568159239` | ABSENT |
| stmt-0019 | lines.credit | `None` | `1,32,685.49` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,88,733.64` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071434100 MEGHDOOT FABRICATI` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071434100` | ABSENT |
| stmt-0019 | lines.debit | `None` | `8,33,728.25` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,22,461.89` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SAHYADRI STATIONER/619269819381/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-197525298314` | ABSENT |
| stmt-0019 | lines.credit | `None` | `2,108.34` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,20,353.55` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/UDAAN FABRICATION/628798026799/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-665103838790` | ABSENT |
| stmt-0019 | lines.debit | `None` | `1,51,075.52` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-14,71,429.07` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `RTGS ZZBKRC2026071456868469 MEGHDOOT OFFICE SU` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKRC2026071456868469` | ABSENT |
| stmt-0019 | lines.credit | `None` | `3,23,459.00` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-11,47,970.07` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071443867 KAVERI IT SERVICES` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071443867` | ABSENT |
| stmt-0019 | lines.credit | `None` | `1,71,556.52` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,76,413.55` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `Int.Pd:8653076:14-07-2026` | ABSENT |
| stmt-0019 | lines.credit | `None` | `667.01` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,75,746.54` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `14 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-611849138281-AARAV ELECTRICALS` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-611849138281` | ABSENT |
| stmt-0019 | lines.credit | `None` | `69,841.99` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,05,904.55` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `15 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `SMS CHGS` | ABSENT |
| stmt-0019 | lines.debit | `None` | `17.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,05,922.25` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `15 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SHAKTI HARDWARE EN/629657044802/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-669908056133` | ABSENT |
| stmt-0019 | lines.debit | `None` | `4,38,405.06` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,44,327.31` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `15 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071520555 PRAGATI FABRICATIO` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071520555` | ABSENT |
| stmt-0019 | lines.credit | `None` | `60,822.23` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-12,83,505.08` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `15 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071518124 SAHYADRI FABRICATI` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071518124` | ABSENT |
| stmt-0019 | lines.debit | `None` | `3,707.54` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-12,87,212.62` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `16 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/ANVAY PACKAGING LL/667166229540/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-166655892328` | ABSENT |
| stmt-0019 | lines.debit | `None` | `34,832.91` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,22,045.53` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `16 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/VISTAR OFFICE SUPP/637278729990/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-576422230667` | ABSENT |
| stmt-0019 | lines.credit | `None` | `532.81` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,21,512.72` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `16 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/UDAAN ELECTRICALS/693131441822/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-595462187901` | ABSENT |
| stmt-0019 | lines.debit | `None` | `21,864.45` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,43,377.17` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `16 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `RTGS ZZBKRC2026071615587943 ANVAY HARDWARE PVT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKRC2026071615587943` | ABSENT |
| stmt-0019 | lines.credit | `None` | `8,92,818.30` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,50,558.87` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `16 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SHAKTI STATIONERS/672740768684/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-337735548835` | ABSENT |
| stmt-0019 | lines.credit | `None` | `12,011.67` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,38,547.20` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `17 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-629028876736-KAVERI IT SERVICES` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-629028876736` | ABSENT |
| stmt-0019 | lines.credit | `None` | `15,147.43` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,23,399.77` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `17 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26071798076 ANVAY TEXTILES ENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26071798076` | ABSENT |
| stmt-0019 | lines.credit | `None` | `2,290.92` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,21,108.85` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `17 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/NIMBUS PACKAGING P/624348225193/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-756503084212` | ABSENT |
| stmt-0019 | lines.credit | `None` | `4,493.59` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,16,615.26` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `18 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SHAKTI OFFICE SUPP/660864086179/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-820999703429` | ABSENT |
| stmt-0019 | lines.credit | `None` | `4,753.63` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,11,861.63` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `18 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/MEGHDOOT TEXTILES/694614258966/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-802360671445` | ABSENT |
| stmt-0019 | lines.credit | `None` | `1,536.62` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-4,10,325.01` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `18 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-621423853578-ANVAY PACKAGING TR` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-621423853578` | ABSENT |
| stmt-0019 | lines.credit | `None` | `83,115.38` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-3,27,209.63` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `19 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID SHAKTI HARDWARE INDU` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `164251` | ABSENT |
| stmt-0019 | lines.debit | `None` | `3,53,115.30` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,80,324.93` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `20 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `SMS CHGS` | ABSENT |
| stmt-0019 | lines.debit | `None` | `17.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,80,342.63` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `20 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/MEGHDOOT IT SERVIC/686258382419/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-946594438650` | ABSENT |
| stmt-0019 | lines.credit | `None` | `1,25,389.81` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-5,54,952.82` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `20 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072019844 KAVERI POLYMERS IN` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072019844` | ABSENT |
| stmt-0019 | lines.credit | `None` | `6,91,149.40` | ABSENT |
| stmt-0019 | lines.balance | `None` | `1,36,196.58` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `22 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-653615693365-PRAGATI IT SERVICE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-653615693365` | ABSENT |
| stmt-0019 | lines.credit | `None` | `3,31,736.85` | ABSENT |
| stmt-0019 | lines.balance | `None` | `4,67,933.43` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `22 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/KAVERI HARDWARE LL/688115571775/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-321161073714` | ABSENT |
| stmt-0019 | lines.debit | `None` | `84,345.72` | ABSENT |
| stmt-0019 | lines.balance | `None` | `3,83,587.71` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `22 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID SARTHI FABRICATION L` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `522056` | ABSENT |
| stmt-0019 | lines.debit | `None` | `6,70,952.47` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-2,87,364.76` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `22 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072232359 MEGHDOOT POLYMERS` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072232359` | ABSENT |
| stmt-0019 | lines.credit | `None` | `4,062.32` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-2,83,302.44` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `23 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `Int.Pd:4051752:23-07-2026` | ABSENT |
| stmt-0019 | lines.credit | `None` | `846.62` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-2,82,455.82` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `23 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072378684 KAVERI TEXTILES TR` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072378684` | ABSENT |
| stmt-0019 | lines.debit | `None` | `2,30,750.80` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-5,13,206.62` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `24 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/UDAAN TEXTILES LLP/672187542972/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-257597731102` | ABSENT |
| stmt-0019 | lines.credit | `None` | `1,206.89` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-5,11,999.73` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `24 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `Int.Pd:3739137:24-07-2026` | ABSENT |
| stmt-0019 | lines.credit | `None` | `791.78` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-5,11,207.95` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `25 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID MEGHDOOT HARDWARE EN` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `626663` | ABSENT |
| stmt-0019 | lines.debit | `None` | `7,07,915.54` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-12,19,123.49` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `25 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/MEGHDOOT IT SERVIC/612972426903/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-252049960245` | ABSENT |
| stmt-0019 | lines.debit | `None` | `83,733.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-13,02,857.19` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072731225 TRIKON OFFICE SUPP` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072731225` | ABSENT |
| stmt-0019 | lines.debit | `None` | `1,03,977.86` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-14,06,835.05` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `IMPS-686348289691-SARTHI TEXTILES PV` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `IMPS-686348289691` | ABSENT |
| stmt-0019 | lines.credit | `None` | `7,97,237.38` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,09,597.67` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `RTGS ZZBKRC2026072746640434 AARAV FABRICATION` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKRC2026072746640434` | ABSENT |
| stmt-0019 | lines.credit | `None` | `9,793.80` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-5,99,803.87` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072794081 UDAAN OFFICE SUPPL` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072794081` | ABSENT |
| stmt-0019 | lines.debit | `None` | `40,733.43` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,40,537.30` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SARTHI OFFICE SUPP/687143735152/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-937197334333` | ABSENT |
| stmt-0019 | lines.debit | `None` | `49,791.81` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,90,329.11` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SARTHI PACKAGING I/660068608114/PAYMENT` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-559798493342` | ABSENT |
| stmt-0019 | lines.credit | `None` | `8,362.91` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-6,81,966.20` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `27 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072737123 SHAKTI IT SERVICES` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072737123` | ABSENT |
| stmt-0019 | lines.debit | `None` | `71,260.41` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-7,53,226.61` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `28 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072841981 PRAGATI ELECTRICAL` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072841981` | ABSENT |
| stmt-0019 | lines.debit | `None` | `27,421.08` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-7,80,647.69` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `28 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `NEFT ZZBKN26072875133 SARTHI TEXTILES TR` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `ZZBKN26072875133` | ABSENT |
| stmt-0019 | lines.credit | `None` | `4,405.48` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-7,76,242.21` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `28 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/VISTAR ELECTRICALS/678604309578/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-267450938434` | ABSENT |
| stmt-0019 | lines.debit | `None` | `425.62` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-7,76,667.83` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `28 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `UPI/SAHYADRI LOGISTICS/613039115808/PURCHASE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `UPI-204695586980` | ABSENT |
| stmt-0019 | lines.debit | `None` | `1,92,062.07` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,68,729.90` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `28 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `SMS CHGS` | ABSENT |
| stmt-0019 | lines.debit | `None` | `17.70` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-9,68,747.60` | ABSENT |
| stmt-0019 | lines.txn_date | `None` | `28 Jul 2026` | ABSENT |
| stmt-0019 | lines.narration | `None` | `CHQ PAID ANVAY OFFICE SUPPLIE` | ABSENT |
| stmt-0019 | lines.ref_col | `None` | `036902` | ABSENT |
| stmt-0019 | lines.debit | `None` | `62,343.00` | ABSENT |
| stmt-0019 | lines.balance | `None` | `-10,31,090.60` | ABSENT |
| stmt-0020 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0021 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0022 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0024 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0024 | lines.balance | `9.66.818.33` | `9,66,618.33` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/655852603382/VISTAR ELECTRICALS/PAYMENT ZENITH` | `UPI/P2M/655852603382/VISTAR ELECTRICALS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `NEFT/ZZBKN26090277918/TRIKON FABRICATIONVENDOR PAYMENT` | `NEFT/ZZBKN26090277918/TRIKON FABRICATION/VENDOR PAYMENT` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/672950881648/ANVAY LOGISTICS INPURCHASE/ ZENITH` | `UPI/P2A/672950881648/ANVAY LOGISTICS IN/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `4.47.542.96` | `-4,47,542.96` | GROUNDED |
| stmt-0024 | lines.balance | `4.14.047.54` | `-4,14,047.54` | GROUNDED |
| stmt-0024 | lines.balance | `4.14.062.54` | `-4,14,062.54` | GROUNDED |
| stmt-0024 | lines.txn_date | `0-9 26` | `04-09-2026` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/647647689732/SHAKTI POLYMERS PV/PURCHASE/ ZENITH` | `UPI/P2A/647647689732/SHAKTI POLYMERS PV/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/622540370381/VISTAR PACKAGING P/PAYMENT/ ZENITH` | `UPI/P2M/622540370381/VISTAR PACKAGING P/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `.15.59.796.00` | `-15,59,796.00` | GROUNDED |
| stmt-0024 | lines.txn_date | `05--02026` | `05-09-2026` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2M/644004601340/AARAV OFFICE SUPPL/PAYMENT/ ZENITH` | `UPI/P2M/644004601340/AARAV OFFICE SUPPL/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/657267972010/SARTHI STATIONERS/PURCHASE/ ZENITH` | `UPI/P2A/657267972010/SARTHI STATIONERS/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `.15.28.171.95` | `-15,28,171.95` | GROUNDED |
| stmt-0024 | lines.narration | `CREDIT INTERÉST` | `CREDIT INTEREST` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/642721185371/MEGHDOOT HARDWARE/PURCHASE/ ZENITH` | `UPI/P2A/642721185371/MEGHDOOT HARDWARE/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/621008716478/VISTAR POLYMERS PV/PAYMENT/ ZENITH` | `UPI/P2M/621008716478/VISTAR POLYMERS PV/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `NEFT/ZZBKN26090714509/UDAAN TEXTILES PVT/VENDOR: PAYMENT` | `NEFT/ZZBKN26090714509/UDAAN TEXTILES PVT/VENDOR PAYMENT` | GROUNDED |
| stmt-0024 | lines.narration | `NEFT/ZZBKN26090725257/MEGHDOOT FABRICATIVENDOR PAYMENT` | `NEFT/ZZBKN26090725257/MEGHDOOT FABRICATI/VENDOR PAYMENT` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/663216969583/UDAAN IT SERVICES/PURCHASE/ ZENITH` | `UPI/P2A/663216969583/UDAAN IT SERVICES/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2M/681288248878/ANVAY POLYMERS LLP/PAYMENT/ ZENITH` | `UPI/P2M/681288248878/ANVAY POLYMERS LLP/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `2.69.778.86` | `-2,69,778.86` | GROUNDED |
| stmt-0024 | lines.balance | `-15.072.66.9736` | `-15,072.66` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/666267826847/ANVAY TEXTILES LLP/PAYMENT/ ZENITH` | `UPI/P2M/666267826847/ANVAY TEXTILES LLP/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `.18.763.24` | `-18,763.24` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/637234791813/PRAGATI TEXTILES E/PAYMENT/ ZENITH` | `UPI/P2M/637234791813/PRAGATI TEXTILES E/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.txn_date | `.09-09-2026` | `09-09-2026` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2M/658107328098/UDAAN ELECTRICALS/PAYMENT/ ZENITH` | `UPI/P2M/658107328098/UDAAN ELECTRICALS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2A/678230104792/MEGHDOOT LOGISTICS/PURCHASE/ ZENITH` | `UPI/P2A/678230104792/MEGHDOOT LOGISTICS/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `NEFT/ZZBKN26091087258/UDAAN FABRICATIONVENDOR PAYMENT` | `NEFT/ZZBKN26091087258/UDAAN FABRICATION/VENDOR PAYMENT` | GROUNDED |
| stmt-0024 | lines.balance | `.7.18.271.14` | `-7,18,271.14` | GROUNDED |
| stmt-0024 | lines.balance | `~2.77.998.84` | `-2,77,998.84` | GROUNDED |
| stmt-0024 | lines.balance | `.2.28.726.54` | `-2,28,726.54` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/636679485647/AARAV OFFICE SUPPL/PAYMENT/ ZENITH` | `UPI/P2M/636679485647/AARAV OFFICE SUPPL/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/637772744374/SARTHI STATIONERS/PURCHASE/ ZENITH` | `UPI/P2A/637772744374/SARTHI STATIONERS/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2A/669715890661/AARAV HARDWARE TRA/PURCHASE/ ZENITH` | `UPI/P2A/669715890661/AARAV HARDWARE TRA/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/621912858266/UDAAN STATIONERS E/PAYMENT/ ZENITH` | `UPI/P2M/621912858266/UDAAN STATIONERS E/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/660309954254/PRAGATI STATIONERS/PAYMENT/ ZENITH` | `UPI/P2M/660309954254/PRAGATI STATIONERS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2A/698477658797/PRAGATI PACKAGING/PURCHASE/ ZENITH` | `UPI/P2A/698477658797/PRAGATI PACKAGING/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `1,87.497 25` | `1,87,497.25` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2A/677216320467/SHAKTI ELECTRICALS/PURCHASE/ ZENITH` | `UPI/P2A/677216320467/SHAKTI ELECTRICALS/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/627983110879/SARTHI ELECTRICALS/PAYMENT/ ZENITH` | `UPI/P2M/627983110879/SARTHI ELECTRICALS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2M/622087420467/AARAV PACKAGING TR/PAYMENT/ ZENITH` | `UPI/P2M/622087420467/AARAV PACKAGING TR/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/639792290147/PRAGATI OFFICE SUP/PURCHASE/ ZENITH` | `UPI/P2A/639792290147/PRAGATI OFFICE SUP/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/667683916903/ANVAY FABRICATION/PAYMENT/ ZENITH.` | `UPI/P2M/667683916903/ANVAY FABRICATION/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.txn_date | `17-09-2026.` | `17-09-2026` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/686183274766/SAHYADRI STATIONER/PAYMENT/ ZENITH` | `UPI/P2M/686183274766/SAHYADRI STATIONER/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `CHQ PAID/105157/KAVERI IT SERVICES1` | `CHQ PAID/105157/KAVERI IT SERVICES I` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2M/628945042412/MEGHDOOT IT SERVIC/PAYMENT7 ZENITH` | `UPI/P2M/628945042412/MEGHDOOT IT SERVIC/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/696310225116/TRIKON IT SERVICES/PAYMENT/ ZENITH` | `UPI/P2M/696310225116/TRIKON IT SERVICES/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/643840085716/SAHYADRI POLYMERS/PAYMENT7 ZENITH` | `UPI/P2M/643840085716/SAHYADRI POLYMERS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2M/695201168031/SAHYADRI LOGISTICS/PAYMENT/ ZENITH` | `UPI/P2M/695201168031/SAHYADRI LOGISTICS/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.ref_col | `459614.` | `459614` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/690173332661/AARAV OFFICE SUPPL/PURCHASE/ ZENITH` | `UPI/P2A/690173332661/AARAV OFFICE SUPPL/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/622500896263/AARAV HARDWARE LLP/PURCHASE/ ZENITH` | `UPI/P2A/622500896263/AARAV HARDWARE LLP/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `11.58.363.60` | `11,58,383.60` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/642962798233/AARAV HARDWARE LLP/PAYMENT/ ZENITH` | `UPI/P2M/642962798233/AARAV HARDWARE LLP/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/629570899447/SARTHI OFFICE SUPP/PURCHASE/ ZENITH` | `UPI/P2A/629570899447/SARTHI OFFICE SUPP/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `NEFT/ZZBKN26092188564/MEGHDOOT STATIONERVENDOR PAYMENT` | `NEFT/ZZBKN26092188564/MEGHDOOT STATIONER/VENDOR PAYMENT` | GROUNDED |
| stmt-0024 | lines.balance | `.5.47.340.23` | `-5,47,340.23` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2M/670701781098/SHAKTI IT SERVICES/PAYMENT ZENITH` | `UPI/P2M/670701781098/SHAKTI IT SERVICES/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `5.46.874.21` | `-5,46,874.21` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2M/681480815601/PRAGATI POLYMERS L/PAYMENT/ ZENITH` | `UPI/P2M/681480815601/PRAGATI POLYMERS L/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/668009516389/SAHYADRI ELECTRICA/PAYMENT/ 2ENIITH` | `UPI/P2M/668009516389/SAHYADRI ELECTRICA/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/619740636869/TRIKON TEXTILES PV/PAYMENT/ ZENITH` | `UPI/P2M/619740636869/TRIKON TEXTILES PV/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/622665130289/SARTHI PACKAGING P/PAYMENT7 ZENITH` | `UPI/P2M/622665130289/SARTHI PACKAGING P/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/693664536215/ANVAY STATIONERS I/PURCHASE ZENITH` | `UPI/P2A/693664536215/ANVAY STATIONERS I/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPIP2A/674088435522/SARTHI IT SERVICES/PURCHASE/ ZENITH` | `UPI/P2A/674088435522/SARTHI IT SERVICES/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPVP2M/643197815036/SHAKTI IT SERVICES/PAYMENT/ ZENITH` | `UPI/P2M/643197815036/SHAKTI IT SERVICES/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.balance | `1.66.818.50:` | `1,66,818.50` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/610835018707/ANVAY HARDWARE LLP/PURCHASE/ ZENITH` | `UPI/P2A/610835018707/ANVAY HARDWARE LLP/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2M/645509002215/KAVERI PACKAGING I/PAYMENT/ ZENITH` | `UPI/P2M/645509002215/KAVERI PACKAGING I/PAYMENT/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `UPUP2A/616570441630/ANVAY LOGISTICS LL/PURCHASE/ ZENITH` | `UPI/P2A/616570441630/ANVAY LOGISTICS LL/PURCHASE/ZENITH` | GROUNDED |
| stmt-0024 | lines.narration | `NEFT/ZZBKN26092829202/AUDAAN FABRICATION/ZENITH` | `NEFT/ZZBKN26092829202/UDAAN FABRICATION/ZENITH` | GROUNDED |
| stmt-0025 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0026 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0027 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0029 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |
| stmt-0030 | bank_name | `Zenith Co-operative Bank Ltd` | `Zenith Co-operative Bank Ltd (SYNTHETIC)` | GROUNDED |

## Every flag outcome that differs from its label

| Doc | Scan | Defect | Blocking flags | Expected |
|---|---|---|---|---|
| stmt-0004 | heavy | - | E1, S1, S2, S3 | - |
| stmt-0019 | heavy | - | S1, S2, S4 | - |
| stmt-0024 | heavy | - | S1, S4 | - |

## Statement Lines (the contract Recon consumes)

| | Result |
|---|---|
| Fully correct (channel, ref, direction, amount, cheque) | 1354/1500 (90.3%) |
| UTR/RRN references correct | 1043/1163 (89.7%) |
| dash | 224/232 (96.6%) |
| initbr | 362/409 (88.5%) |
| kotak | 104/194 (53.6%) |
| mmt | 125/125 (100.0%) |
| signed | 301/301 (100.0%) |
| slash | 238/239 (99.6%) |
