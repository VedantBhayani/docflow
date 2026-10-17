# DocFlow evaluation: dev split

Run at 2026-10-17 08:11 UTC, 37 documents, trust store `test`.

| Metric | Result |
|---|---|
| Field accuracy (all fields, by value) | 1796/1809 (99.3%) |
| Key-field accuracy | 222/222 (100.0%) |
| Grounding rate (extracted values proven on the page) | 1781/1785 (99.8%) |
| Key fields VERIFIED by an independent source | 208/222 (93.7%) |
| Defect recall (injected defects caught) | 9/9 (100.0%) |
| False-flag rate (clean docs with a blocking flag) | 0/27 (0.0%) |
| Straight-through rate (clean docs, no blocking flag) | 27/27 (100.0%) |
| Documents flagged exactly as labelled | 37/37 (100.0%) |
| Prompt-injection docs unaffected | 1/1 (100.0%) |
| LLM cost per document (mean) | $0.001153 |
| Latency per document, uncached | n/a: every LLM call came from cache, so timings would not be real |

## By scan level

| | Result |
|---|---|
| digital | 942/943 (99.9%) |
| heavy | 340/349 (97.4%) |
| light | 514/517 (99.4%) |

## By template

| | Result |
|---|---|
| einvoice | 389/396 (98.2%) |
| tally | 539/540 (99.8%) |
| word | 409/413 (99.0%) |
| zoho | 459/460 (99.8%) |

## Defect recall by type

| | Result |
|---|---|
| bad_gstin_checksum | 1/1 (100.0%) |
| duplicate_invoice_no | 2/2 (100.0%) |
| invalid_slab | 1/1 (100.0%) |
| line_math | 1/1 (100.0%) |
| missing_recipient_gstin | 1/1 (100.0%) |
| qr_bad_signature | 1/1 (100.0%) |
| qr_total_mismatch | 1/1 (100.0%) |
| wrong_tax_type | 1/1 (100.0%) |

## QR read rate by scan level

| | Result |
|---|---|
| digital | 8/8 (100.0%) |
| heavy | 2/3 (66.7%) |
| light | 4/4 (100.0%) |

## By field

| | Result |
|---|---|
| cgst_total | 37/37 (100.0%) |
| grand_total | 37/37 (100.0%) |
| igst_total | 37/37 (100.0%) |
| invoice_date | 37/37 (100.0%) |
| invoice_no | 37/37 (100.0%) |
| irn | 34/37 (91.9%) |
| lines.cgst | 118/118 (100.0%) |
| lines.description | 115/118 (97.5%) |
| lines.gst_rate | 118/118 (100.0%) |
| lines.hsn | 118/118 (100.0%) |
| lines.igst | 118/118 (100.0%) |
| lines.qty | 117/118 (99.2%) |
| lines.sgst | 118/118 (100.0%) |
| lines.taxable_value | 118/118 (100.0%) |
| lines.unit_price | 117/118 (99.2%) |
| lines.uqc | 116/118 (98.3%) |
| place_of_supply | 37/37 (100.0%) |
| recipient_address | 36/37 (97.3%) |
| recipient_gstin | 37/37 (100.0%) |
| recipient_name | 37/37 (100.0%) |
| reverse_charge | 37/37 (100.0%) |
| round_off | 37/37 (100.0%) |
| sgst_total | 37/37 (100.0%) |
| supplier_address | 37/37 (100.0%) |
| supplier_gstin | 37/37 (100.0%) |
| supplier_name | 35/37 (94.6%) |
| taxable_total | 37/37 (100.0%) |

## Every field error

| Doc | Field | Got | Truth | Status |
|---|---|---|---|---|
| inv-0003 | recipient_address | `Unit 228, Business Park, Hyderabad, Telangana Sl` | `Unit 228, Business Park, Hyderabad, Telangana` | GROUNDED |
| inv-0056 | irn | `0b8159c2ce71et2d4e68b2984e9d3` | `0b8159c2ce71ef2d4e68b2984e9d3438de06f542e0807ffbcaf11709001d4c4b` | GROUNDED |
| inv-0078 | supplier_name | `Nimbus Logistics Pvt Ltd` | `Nimbus Logistics Industries Pvt Ltd` | UNGROUNDED |
| inv-0089 | lines.description | `Corugated cartons 5-ply` | `Corrugated cartons 5-ply` | GROUNDED |
| inv-0089 | lines.description | `2 Hand sanitiser 500 ml` | `Hand sanitiser 500 ml` | GROUNDED |
| inv-0089 | lines.description | `3. Ergonomic office chair` | `Ergonomic office chair` | GROUNDED |
| inv-0106 | lines.qty | `100.00 NOS` | `100.00` | GROUNDED |
| inv-0106 | lines.uqc | `None` | `NOS` | MISSING |
| inv-0115 | irn | `d523b9d1c5dbf79843563e4db88131097d8e8e04620487425c229039` | `d523b9d1c5dbf79843563ef4db8813f04cb018c97d8e8e0462d487428c229039` | UNGROUNDED |
| inv-0119 | supplier_name | `Pragati Packaging Traders.` | `Pragati Packaging Traders` | GROUNDED |
| inv-0119 | irn | `743e316a11de23984732dc44e20100b` | `743e316a11de23984732dc44e20100ba96302c110e0e40137e5b5c83241ad4ed` | GROUNDED |
| inv-0119 | lines.uqc | `90.28` | `BTL` | GROUNDED |
| inv-0119 | lines.unit_price | `1.083.36` | `90.28` | GROUNDED |

## Every flag outcome that differs from its label

| Doc | Scan | Defect | Blocking flags | Expected |
|---|---|---|---|---|
| none | | | | |
