"""Every invoice Check in spec section 6 (non-QR) gets a passing and a failing case.

Base invoice is intra-state Maharashtra (27 -> 27), hand-computed:
  line 1: 4 x 1,250.00 = 5,000.00 @18%: CGST 450.00 + SGST 450.00
  line 2 (service, SAC 998713): 1 x 2,000.00 = 2,000.00 @18%: CGST 180.00 + SGST 180.00
  taxable 7,000.00; CGST 630.00; SGST 630.00; pre-round 8,260.00; grand 8,260.00
"""

from datetime import date

import pytest

from docflow.gstin import check_char
from docflow.checks import CATALOGUE, catalogue_markdown, check_duplicates, run_invoice_checks
from docflow.models import Field, FieldStatus

SUP = "27AAACU2414K1ZF"  # Axis Bank (Maharashtra), bank-published
REC = "27AABCI8842G1ZF"  # IDBI Bank (Maharashtra), bank-published
GUJ = "24AAACU2414K1Z" + check_char("24AAACU2414K1Z")  # valid, fictional, Gujarat


def F(name, text):
    return Field(name=name, text=text, status=FieldStatus.GROUNDED if text is not None else FieldStatus.MISSING)


def make(fields=None, lines=None, drop=()):
    base = {
        "supplier_name": "Vistar Hardware Pvt Ltd", "supplier_address": "Unit 4, MIDC Road, Pune, Maharashtra", "supplier_gstin": SUP,
        "recipient_name": "Kaveri Logistics LLP", "recipient_address": "Unit 9, Trade Centre, Mumbai, Maharashtra", "recipient_gstin": REC,
        "invoice_no": "DFTEST-2627-0101", "invoice_date": "03/10/2026", "place_of_supply": "Maharashtra (27)", "reverse_charge": "No",
        "taxable_total": "7,000.00", "cgst_total": "630.00", "sgst_total": "630.00", "igst_total": "0.00", "round_off": "0.00", "grand_total": "8,260.00",
    }
    base.update(fields or {})
    for k in drop:
        base[k] = None
    ls = [
        {"description": "Steel shelving unit", "hsn": "94032090", "qty": "4", "uqc": "NOS", "unit_price": "1,250.00", "taxable_value": "5,000.00",
         "gst_rate": "18%", "cgst": "450.00", "sgst": "450.00", "igst": "0.00"},
        {"description": "Annual IT support services", "hsn": "998713", "qty": "1", "uqc": "OTH", "unit_price": "2,000.00", "taxable_value": "2,000.00",
         "gst_rate": "18%", "cgst": "180.00", "sgst": "180.00", "igst": "0.00"},
    ]
    for i, patch in (lines or {}).items():
        ls[i].update(patch)
    return {k: F(k, v) for k, v in base.items()}, [{k: F(f"lines.{i}.{k}", v) for k, v in ln.items()} for i, ln in enumerate(ls)]


def ids(flags):
    return sorted({f.check_id for f in flags})


def sev(flags, check_id):
    return {f.severity for f in flags if f.check_id == check_id}


def test_base_invoice_is_clean():
    assert run_invoice_checks(*make()) == []


@pytest.mark.parametrize("missing, check_id", [
    ("supplier_name", "A1"), ("supplier_address", "A1"), ("supplier_gstin", "A1"),
    ("recipient_name", "A5"), ("recipient_address", "A5"), ("recipient_gstin", "A5"),
    ("invoice_no", "A2"), ("invoice_date", "A4"), ("grand_total", "A10"), ("taxable_total", "A11"),
])
def test_mandatory_particular_missing(missing, check_id):
    flags = run_invoice_checks(*make(drop=(missing,)))
    assert check_id in ids(flags)
    assert sev(flags, check_id) == {"BLOCKING"}


@pytest.mark.parametrize("bad", ["DFTEST/2627/0101/EXTRA", "INV 0101", "INV#0101"])
def test_invoice_number_format_a2(bad):
    assert "A2" in ids(run_invoice_checks(*make(fields={"invoice_no": bad})))


def test_unparseable_date_a4():
    assert "A4" in ids(run_invoice_checks(*make(fields={"invoice_date": "31/02/2026"})))


def test_line_without_rate_a12_and_without_tax_a13():
    flags = run_invoice_checks(*make(lines={0: {"gst_rate": None}}))
    assert "A12" in ids(flags)
    flags = run_invoice_checks(*make(lines={0: {"cgst": None, "sgst": None, "igst": None}}))
    assert "A13" in ids(flags)


def test_intra_state_charging_igst_is_c2():
    # Same totals, but charged as IGST on an intra-state supply.
    flags = run_invoice_checks(*make(
        fields={"cgst_total": "0.00", "sgst_total": "0.00", "igst_total": "1,260.00"},
        lines={0: {"cgst": "0.00", "sgst": "0.00", "igst": "900.00"}, 1: {"cgst": "0.00", "sgst": "0.00", "igst": "360.00"}},
    ))
    assert "C2" in ids(flags) and sev(flags, "C2") == {"BLOCKING"}


def test_inter_state_charging_cgst_sgst_is_c3():
    flags = run_invoice_checks(*make(fields={"recipient_gstin": GUJ, "place_of_supply": "Gujarat (24)"}))
    assert "C3" in ids(flags)


def test_unequal_cgst_and_sgst_is_c4():
    flags = run_invoice_checks(*make(
        fields={"sgst_total": "640.00", "grand_total": "8,270.00"},
        lines={0: {"sgst": "460.00"}},
    ))
    assert "C4" in ids(flags)


def test_rate_not_a_valid_goods_slab_after_reform_is_blocking_c7():
    # 12% was abolished for goods from 22.09.2025 (Notification 9/2025-IT(R)).
    flags = run_invoice_checks(*make(lines={0: {"gst_rate": "12%", "cgst": "300.00", "sgst": "300.00"}},
                                     fields={"cgst_total": "480.00", "sgst_total": "480.00", "grand_total": "7,960.00"}))
    assert "C7" in ids(flags) and sev(flags, "C7") == {"BLOCKING"}


def test_invalid_rate_on_a_service_line_is_only_a_warning():
    flags = run_invoice_checks(*make(lines={1: {"gst_rate": "12%", "cgst": "120.00", "sgst": "120.00"}},
                                     fields={"cgst_total": "570.00", "sgst_total": "570.00", "grand_total": "8,140.00"}))
    assert sev(flags, "C7") == {"WARNING"}


def test_pre_reform_dates_use_the_old_slabs_as_a_warning():
    twelve = {0: {"gst_rate": "12%", "cgst": "300.00", "sgst": "300.00"}}
    flags = run_invoice_checks(*make(fields={"invoice_date": "15/08/2025", "cgst_total": "480.00", "sgst_total": "480.00", "grand_total": "7,960.00"}, lines=twelve))
    assert "C7" not in ids(flags)  # 12% was a valid slab before 22.09.2025
    flags = run_invoice_checks(*make(fields={"invoice_date": "15/08/2025", "cgst_total": "730.00", "sgst_total": "730.00", "grand_total": "8,460.00"},
                                     lines={0: {"gst_rate": "22%", "cgst": "550.00", "sgst": "550.00"}}))
    assert sev(flags, "C7") == {"WARNING"}  # old slab list is not re-verified, so warning only


def test_short_hsn_is_a_warning_and_qr_raises_the_bar():
    flags = run_invoice_checks(*make(lines={0: {"hsn": "940"}}))
    assert sev(flags, "A7") == {"WARNING"}
    assert "A7" not in ids(run_invoice_checks(*make(lines={0: {"hsn": "9403"}})))
    assert "A7" in ids(run_invoice_checks(*make(lines={0: {"hsn": "9403"}}), has_qr=True))


def test_goods_line_without_qty_or_unit_is_a9_warning_but_services_are_exempt():
    assert sev(run_invoice_checks(*make(lines={0: {"uqc": None}})), "A9") == {"WARNING"}
    assert "A9" not in ids(run_invoice_checks(*make(lines={1: {"uqc": None, "qty": None}})))


def test_inter_state_without_place_of_supply_is_a14_warning():
    flags = run_invoice_checks(*make(fields={"recipient_gstin": GUJ, "place_of_supply": None,
                                             "cgst_total": "0.00", "sgst_total": "0.00", "igst_total": "1,260.00"},
                                     lines={0: {"cgst": "0.00", "sgst": "0.00", "igst": "900.00"}, 1: {"cgst": "0.00", "sgst": "0.00", "igst": "360.00"}}))
    assert sev(flags, "A14") == {"WARNING"}
    assert "C3" not in ids(flags)  # fell back to the recipient's state (24), which is inter-state: IGST is right


def test_reverse_charge_missing_a16_and_rcm_with_tax_c8():
    assert sev(run_invoice_checks(*make(drop=("reverse_charge",))), "A16") == {"WARNING"}
    assert sev(run_invoice_checks(*make(fields={"reverse_charge": "Yes"})), "C8") == {"WARNING"}


def test_duplicates_across_a_batch_are_a3():
    one = make()[0]
    two = make(fields={"invoice_date": "05/10/2026"})[0]  # same FY, same supplier, same number
    three = make(fields={"invoice_no": "DFTEST-2627-0102"})[0]
    flags = check_duplicates({"a.pdf": one, "b.pdf": two, "c.pdf": three})
    assert sorted(flags) == ["a.pdf", "b.pdf"]
    assert all(f.check_id == "A3" for fl in flags.values() for f in fl)


def test_same_number_in_a_different_financial_year_is_not_a_duplicate():
    one = make()[0]
    other_fy = make(fields={"invoice_date": "03/10/2025"})[0]
    assert check_duplicates({"a.pdf": one, "b.pdf": other_fy}) == {}


def test_catalogue_lists_every_check_with_source_and_renders_markdown():
    implemented = {"A1", "A2", "A3", "A4", "A5", "A7", "A9", "A10", "A11", "A12", "A13", "A14", "A16",
                   "C2", "C3", "C4", "C6", "C6Q", "C7", "C8", "G1", "G2", "G3", "G4", "G5", "E1", "E2", "E3"}
    assert implemented <= {c.id for c in CATALOGUE}
    assert all(c.source and c.description for c in CATALOGUE)
    md = catalogue_markdown()
    assert md.startswith("## Invoices") and "| C7 |" in md and "| S1 |" in md
