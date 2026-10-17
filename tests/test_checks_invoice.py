from docflow.checks import run_invoice_checks
from docflow.models import Field, FieldStatus

VALID_A = "27AAACU2414K1ZF"  # Axis Bank, published
VALID_B = "27AABCI8842G1ZF"  # IDBI Bank, published


def F(name, text):
    return Field(name=name, text=text, status=FieldStatus.GROUNDED)


def invoice(**over):
    """A correct inter-state invoice, hand-computed:
    line 1: 10 x 100.00 = 1,000.00 @18% -> IGST 180.00
    line 2: 2 x 250.25 = 500.50 @5%    -> IGST 25.03 (25.025 rounded half-up)
    taxable 1,500.50; IGST 205.03; pre-round 1,705.53; round-off -0.53; grand 1,705.00
    """
    fields = {
        "supplier_gstin": VALID_A, "recipient_gstin": VALID_B,
        "taxable_total": "1,500.50", "cgst_total": "0.00", "sgst_total": "0.00", "igst_total": "205.03",
        "round_off": "-0.53", "grand_total": "1,705.00",
    }
    fields.update(over.pop("fields", {}))
    lines = [
        {"qty": "10", "unit_price": "100.00", "taxable_value": "1,000.00", "gst_rate": "18%", "cgst": "0.00", "sgst": "0.00", "igst": "180.00"},
        {"qty": "2", "unit_price": "250.25", "taxable_value": "500.50", "gst_rate": "5%", "cgst": "0.00", "sgst": "0.00", "igst": "25.03"},
    ]
    for i, patch in over.pop("lines", {}).items():
        lines[i].update(patch)
    return (
        {k: F(k, v) for k, v in fields.items()},
        [{k: F(f"lines.{i}.{k}", v) for k, v in ln.items()} for i, ln in enumerate(lines)],
    )


def ids(flags):
    return sorted(f.check_id for f in flags)


def test_correct_invoice_raises_no_flags():
    assert ids(run_invoice_checks(*invoice())) == []


def test_bad_supplier_gstin_check_digit_is_g5():
    flags = run_invoice_checks(*invoice(fields={"supplier_gstin": "27AAACU2414K1ZH"}))
    assert ids(flags) == ["G5"]
    assert flags[0].fields == ("supplier_gstin",)


def test_both_gstins_are_checked():
    flags = run_invoice_checks(*invoice(fields={"recipient_gstin": "27AABCI8842G1Z"}))
    assert ids(flags) == ["G1"]
    assert flags[0].fields == ("recipient_gstin",)


def test_line_tax_not_equal_to_taxable_times_rate_is_c6():
    # 1,000.00 @18% must be 180.00; 190.00 is off by 10 (> max(1, 0.5%)).
    flags = run_invoice_checks(*invoice(lines={0: {"igst": "190.00"}}, fields={"igst_total": "215.03", "round_off": "0.47", "grand_total": "1,716.00"}))
    assert "C6" in ids(flags)
    assert any("lines.0" in f for fl in flags for f in fl.fields)


def test_rounding_within_one_rupee_is_tolerated():
    # 180.90 vs 180.00: within Rs 1 tolerance on the line.
    flags = run_invoice_checks(*invoice(lines={0: {"igst": "180.90"}}, fields={"igst_total": "205.93", "round_off": "0.57", "grand_total": "1,707.00"}))
    assert "C6" not in ids(flags)


def test_totals_not_matching_sum_of_lines_is_c6():
    flags = run_invoice_checks(*invoice(fields={"taxable_total": "1,600.50", "round_off": "-0.53", "grand_total": "1,805.00"}))
    assert "C6" in ids(flags)


def test_grand_total_not_reconciling_is_c6():
    flags = run_invoice_checks(*invoice(fields={"grand_total": "1,750.00"}))
    assert ids(flags) == ["C6"]


def test_round_off_of_a_rupee_or_more_is_c6():
    flags = run_invoice_checks(*invoice(fields={"round_off": "1.47", "grand_total": "1,707.00"}))
    assert "C6" in ids(flags)


def test_qty_times_price_mismatch_is_a_warning_not_blocking():
    flags = run_invoice_checks(*invoice(lines={0: {"qty": "11"}}))
    assert ids(flags) == ["C6Q"]
    assert flags[0].severity == "WARNING"
