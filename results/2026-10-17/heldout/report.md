# DocFlow evaluation: heldout split (FINAL held-out run)

Run at 2026-10-17 11:57 UTC, 83 documents, trust store `test`.

| Metric | Result |
|---|---|
| Field accuracy (all fields, by value) | 3973/4011 (99.1%) |
| Key-field accuracy | 497/498 (99.8%) |
| Grounding rate (extracted values proven on the page) | 3936/3959 (99.4%) |
| Key fields VERIFIED by an independent source | 474/498 (95.2%) |
| Defect recall (injected defects caught) | 16/16 (100.0%) |
| False-flag rate (clean docs with a blocking flag) | 5/65 (7.7%) |
| Straight-through rate (clean docs, no blocking flag) | 60/65 (92.3%) |
| Documents flagged exactly as labelled | 77/83 (92.8%) |
| Prompt-injection docs unaffected | 2/2 (100.0%) |
| LLM cost per document (mean) | $0.001145 |
| Latency per document, uncached | {'n': 26, 'p50': 10.5, 'p95': 14.6} |

## By scan level

| | Result |
|---|---|
| digital | 1875/1877 (99.9%) |
| heavy | 1063/1097 (96.9%) |
| light | 1035/1037 (99.8%) |

## By template

| | Result |
|---|---|
| einvoice | 1061/1074 (98.8%) |
| tally | 971/980 (99.1%) |
| word | 1030/1037 (99.3%) |
| zoho | 911/920 (99.0%) |

## Defect recall by type

| | Result |
|---|---|
| bad_gstin_checksum | 2/2 (100.0%) |
| duplicate_invoice_no | 2/2 (100.0%) |
| invalid_slab | 2/2 (100.0%) |
| line_math | 2/2 (100.0%) |
| missing_recipient_gstin | 2/2 (100.0%) |
| qr_bad_signature | 2/2 (100.0%) |
| qr_total_mismatch | 2/2 (100.0%) |
| wrong_tax_type | 2/2 (100.0%) |

## QR read rate by scan level

| | Result |
|---|---|
| digital | 16/16 (100.0%) |
| heavy | 6/7 (85.7%) |
| light | 10/10 (100.0%) |

## By field

| | Result |
|---|---|
| cgst_total | 83/83 (100.0%) |
| grand_total | 83/83 (100.0%) |
| igst_total | 83/83 (100.0%) |
| invoice_date | 83/83 (100.0%) |
| invoice_no | 83/83 (100.0%) |
| irn | 77/83 (92.8%) |
| lines.cgst | 259/260 (99.6%) |
| lines.description | 252/260 (96.9%) |
| lines.gst_rate | 260/260 (100.0%) |
| lines.hsn | 260/260 (100.0%) |
| lines.igst | 260/260 (100.0%) |
| lines.qty | 256/260 (98.5%) |
| lines.sgst | 259/260 (99.6%) |
| lines.taxable_value | 258/260 (99.2%) |
| lines.unit_price | 259/260 (99.6%) |
| lines.uqc | 258/260 (99.2%) |
| place_of_supply | 81/83 (97.6%) |
| recipient_address | 82/83 (98.8%) |
| recipient_gstin | 83/83 (100.0%) |
| recipient_name | 82/83 (98.8%) |
| reverse_charge | 83/83 (100.0%) |
| round_off | 83/83 (100.0%) |
| sgst_total | 83/83 (100.0%) |
| supplier_address | 78/83 (94.0%) |
| supplier_gstin | 82/83 (98.8%) |
| supplier_name | 80/83 (96.4%) |
| taxable_total | 83/83 (100.0%) |

## Every field error

| Doc | Field | Got | Truth | Status |
|---|---|---|---|---|
| inv-0025 | place_of_supply | `Deihi (07)` | `Delhi (07)` | GROUNDED |
| inv-0026 | irn | `509e61172b34tc0b230d3fdbccbe` | `509e6f172b34fc0bf30d3fdbccbec156d5aeeb980d28dd6684b2822ca0a0f951` | GROUNDED |
| inv-0027 | supplier_address | `Unit 37, MIDC Road. Kolkata, West Bengal` | `Unit 37, MIDC Road, Kolkata, West Bengal` | GROUNDED |
| inv-0027 | lines.qty | `NOS` | `1` | GROUNDED |
| inv-0027 | lines.uqc | `6.326.04` | `NOS` | GROUNDED |
| inv-0027 | lines.taxable_value | `158.15` | `6,326.04` | GROUNDED |
| inv-0027 | lines.sgst | `0.00` | `158.15` | GROUNDED |
| inv-0029 | lines.description | `S e S` | `Steel shelving unit` | GROUNDED |
| inv-0030 | lines.description | `2. A4 copier paper 75 GSM (ream)` | `A4 copier paper 75 GSM (ream)` | GROUNDED |
| inv-0037 | supplier_name | `Meghdoot Logistics Pvt Ltd` | `Meghdoot Logistics Industries Pvt Ltd` | UNGROUNDED |
| inv-0054 | supplier_address | `Unit 182, Business Park, New Delhi. Delhi` | `Unit 182, Business Park, New Delhi, Delhi` | GROUNDED |
| inv-0054 | recipient_address | `Unit 234, Industrial Estate, Nagpur. Maharashtra` | `Unit 234, Industrial Estate, Nagpur, Maharashtra` | GROUNDED |
| inv-0055 | supplier_address | `Unit 202. Trade Centre, Surat, Gujarat` | `Unit 202, Trade Centre, Surat, Gujarat` | GROUNDED |
| inv-0055 | lines.uqc | `BT` | `BTL` | GROUNDED |
| inv-0055 | lines.unit_price | `103:15` | `103.15` | GROUNDED |
| inv-0055 | lines.taxable_value | `532:05` | `532.05` | GROUNDED |
| inv-0059 | lines.description | `2 Steef shelving unit` | `Steel shelving unit` | GROUNDED |
| inv-0059 | lines.description | `Copper cabie 2.5 sq mm (90 m)` | `Copper cable 2.5 sq mm (90 m)` | GROUNDED |
| inv-0073 | supplier_name | `Nimbus Logistics Pvt Ltd` | `Nimbus Logistics Industries Pvt Ltd` | UNGROUNDED |
| inv-0084 | supplier_name | `Sarthi Stationers Pvt Ltd` | `Sarthi Stationers Industries Pvt Ltd` | UNGROUNDED |
| inv-0084 | lines.qty | `ROL` | `2` | GROUNDED |
| inv-0086 | irn | `2cfc62de83163e2cc935da0831be73826d6662ed971201528751837dda8113b` | `2cfc62de83163e2ccf935da0831be73826d6662ed97f20f528751837dda81f3b` | GROUNDED |
| inv-0088 | supplier_gstin | `19UHDCU2519MIZ1` | `19UHDCU2519M1Z1` | VERIFIED |
| inv-0088 | recipient_name | `Sarthi Stationers LL.P` | `Sarthi Stationers LLP` | GROUNDED |
| inv-0090 | lines.description | `3 Corrugated cartons 5-ply` | `Corrugated cartons 5-ply` | GROUNDED |
| inv-0109 | lines.qty | `100.00 BTL` | `100.00` | GROUNDED |
| inv-0110 | lines.qty | `100.00 NOS` | `100.00` | GROUNDED |
| inv-0114 | place_of_supply | `Kamataka (29)` | `Karnataka (29)` | GROUNDED |
| inv-0114 | irn | `24956123e987c60c33b401036b84b93b1d391487e3ad6372b18bda4634febb` | `2495612ff3e987c60c33b401036b84b93b1d39f487e3ad6372b18bda4634febb` | GROUNDED |
| inv-0114 | lines.description | `Corugated cartons 5-ply` | `Corrugated cartons 5-ply` | GROUNDED |
| inv-0116 | supplier_address | `Unit 78. Trade Centre, Gandhinagar, Gujarat` | `Unit 78, Trade Centre, Gandhinagar, Gujarat` | GROUNDED |
| inv-0116 | irn | `c79cc8156dcede3bd409bbcc39199bf3` | `c79cc8156dcede3bd409bbcc39199bf3fbba65ce5372e5add5ba7f0385783eb1` | GROUNDED |
| inv-0116 | lines.description | `Corugated cartons 5-ply` | `Corrugated cartons 5-ply` | GROUNDED |
| inv-0117 | supplier_address | `Unit 200; MIDC Road. Pune, Maharashtra` | `Unit 200, MIDC Road, Pune, Maharashtra` | GROUNDED |
| inv-0118 | irn | `bce824853b7eedc3db6323148a1c667dcd43547c87e971769e7192000be9603b` | `bce824853b7eedc3db6323f48a1c667dcd43547c87e971769e7f92000be9603b` | GROUNDED |
| inv-0118 | lines.cgst | `0:00` | `0.00` | GROUNDED |
| inv-0120 | irn | `68c6600c407b6fca09bbd597bacf29692e44a219c716741eac063982a1bb` | `68c6600c407b6fca09bbd597bacf29692e44df8a2f9c716741eac063982a1fbb` | GROUNDED |
| inv-0120 | lines.description | `2.. Corrugated cartons 5-ply` | `Corrugated cartons 5-ply` | GROUNDED |

## Every flag outcome that differs from its label

| Doc | Scan | Defect | Blocking flags | Expected |
|---|---|---|---|---|
| inv-0027 | heavy | - | C4, C6 | - |
| inv-0042 | digital | duplicate_invoice_no | A3, E1 | A3 |
| inv-0055 | heavy | - | A11, C6 | - |
| inv-0088 | heavy | - | G5 | - |
| inv-0118 | heavy | - | Q3 | - |
| inv-0120 | heavy | - | E1 | - |
