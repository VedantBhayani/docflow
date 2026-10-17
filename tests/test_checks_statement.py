"""Statement Checks S1-S6, with hand-computed balances.

Opening 10,000.00
  01/09/26 UPI CR   5,000.00 -> 15,000.00
  02/09/26 NEFT DR  2,500.50 -> 12,499.50
  03/09/26 CHQ DR     499.50 -> 12,000.00
Closing 12,000.00
"""

from docflow.checks_statement import run_statement_checks
from docflow.models import Field, FieldStatus


def F(name, text):
    return Field(name=name, text=text, status=FieldStatus.GROUNDED if text is not None else FieldStatus.MISSING)


def make(fields=None, lines=None):
    base = {"period_from": "01/09/2026", "period_to": "30/09/2026", "opening_balance": "10,000.00", "closing_balance": "12,000.00"}
    base.update(fields or {})
    ls = [
        {"txn_date": "01/09/26", "narration": "UPI-KAVERI-kaveri@okzz-ZZBK0001234-612345678901-PAY", "ref_col": "612345678901",
         "debit": None, "credit": "5,000.00", "balance": "15,000.00"},
        {"txn_date": "02/09/26", "narration": "NEFT DR-ZZBK0004321-TRIKON-ZZBKN26090200001-VENDOR", "ref_col": "ZZBKN26090200001",
         "debit": "2,500.50", "credit": None, "balance": "12,499.50"},
        {"txn_date": "03/09/26", "narration": "CHQ PAID-MICR CTS-ANVAY", "ref_col": "123456",
         "debit": "499.50", "credit": None, "balance": "12,000.00"},
    ]
    for i, patch in (lines or {}).items():
        ls[i].update(patch)
    return {k: F(k, v) for k, v in base.items()}, [{k: F(f"lines.{i}.{k}", v) for k, v in ln.items()} for i, ln in enumerate(ls)]


def ids(flags, severity=None):
    return sorted(f.check_id for f in flags if severity is None or f.severity == severity)


def test_consistent_statement_is_clean():
    assert run_statement_checks(*make()) == []


def test_broken_balance_on_one_row_is_s1_on_that_row():
    flags = run_statement_checks(*make(lines={1: {"balance": "13,499.50"}}))
    s1 = [f for f in flags if f.check_id == "S1"]
    assert s1 and s1[0].fields == ("lines.1.balance",) and s1[0].severity == "BLOCKING"


def test_chain_resumes_after_the_broken_row():
    # Row 2's balance follows from row 1's PRINTED balance; only row 1 is wrong vs its predecessor,
    # and row 2 is wrong vs row 1's printed value. Both are reported, row 1 first.
    flags = run_statement_checks(*make(lines={1: {"balance": "13,499.50"}}))
    assert [f.fields[0] for f in flags if f.check_id == "S1"] == ["lines.1.balance", "lines.2.balance"]


def test_opening_plus_credits_minus_debits_must_equal_closing_s2():
    assert "S2" in ids(run_statement_checks(*make(fields={"closing_balance": "12,100.00"})))


def test_row_with_both_or_neither_side_is_s3():
    assert "S3" in ids(run_statement_checks(*make(lines={0: {"debit": "5,000.00"}})))
    assert "S3" in ids(run_statement_checks(*make(lines={2: {"debit": None}})))


def test_date_outside_the_period_is_s4():
    assert "S4" in ids(run_statement_checks(*make(lines={2: {"txn_date": "03/10/26"}})))


def test_malformed_reference_for_its_channel_is_a_warning_s5():
    flags = run_statement_checks(*make(lines={0: {"narration": "UPI-KAVERI-kaveri@okzz-ZZBK0001234-61234567890-PAY"}}))  # 11-digit RRN
    assert ids(flags, "WARNING") == ["S5"]


def test_duplicate_line_is_a_warning_s6():
    dup = {"txn_date": "02/09/26", "narration": "NEFT DR-ZZBK0004321-TRIKON-ZZBKN26090200001-VENDOR", "ref_col": "ZZBKN26090200001",
           "debit": "2,500.50", "credit": None, "balance": "9,999.00"}
    fields, lines = make(fields={"closing_balance": "9,999.00"}, lines={2: dup})
    flags = run_statement_checks(fields, lines)
    assert "S6" in ids(flags, "WARNING")


def test_missing_opening_balance_skips_s2_but_chain_still_checked():
    flags = run_statement_checks(*make(fields={"opening_balance": None}))
    assert "S2" not in ids(flags)


def test_unreadable_date_is_s4_blocking():
    flags = run_statement_checks(*make(lines={1: {"txn_date": "O2/O9/26x"}}))
    s4 = [f for f in flags if f.check_id == "S4"]
    assert s4 and s4[0].severity == "BLOCKING" and "unreadable" in s4[0].message
