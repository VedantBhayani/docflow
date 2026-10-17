"""Channel and reference extraction from Indian bank narrations (research note 04, section 3).
Formats follow the published parser templates; names, banks and numbers are fictional."""

import pytest

from docflow.narration import classify, extract_reference


@pytest.mark.parametrize("narration, channel, ref", [
    # UPI: 12-digit RRN taken from the channel's own segment only
    ("UPI-KAVERI TRADERS-kaveri@okzz-ZZBK0001234-612345678901-INVOICE 42", "UPI", "612345678901"),
    ("UPI/CR/612345678902/VISTAR LLP/ZZBK/vistar@okzz/rent", "UPI", "612345678902"),
    ("UPI/P2M/612345678903/NIMBUS STORES/groceries/ZENITH", "UPI", "612345678903"),
    # IMPS
    ("IMPS-612345678904-SARTHI ENTERPRISES-ZENITH BANK-XXXXXXXX1234-advance", "IMPS", "612345678904"),
    ("MMT/IMPS/612345678905/salary/PRAGATI LLP/ZENITH", "IMPS", "612345678905"),
    # NEFT: 16-char UTR; the 11-char IFSC must never be taken as the UTR
    ("NEFT CR-ZZBK0004321-TRIKON PVT LTD-ZZBKN26101500123", "NEFT", "ZZBKN26101500123"),
    ("NEFT*ZZBK0004321*ZZBKN26101500124*UDAAN TRADERS", "NEFT", "ZZBKN26101500124"),
    ("NEFT DR-ZZBK0009999-ANVAY LLP-NETBANK,MUM-ZZBKN26101500125-payment", "NEFT", "ZZBKN26101500125"),
    # RTGS: 22-char UTR with embedded date
    ("RTGS/ZZBKRC2026101500000123/MEGHDOOT PVT LTD/ZENITH", "RTGS", "ZZBKRC2026101500000123"),
    ("RTGS CR-ZZBK0004321-SHAKTI INDUSTRIES-ZZBKRC2026101500000124", "RTGS", "ZZBKRC2026101500000124"),
])
def test_transfer_channels_and_their_references(narration, channel, ref):
    assert classify(narration) == channel
    assert extract_reference(narration, channel) == ref


@pytest.mark.parametrize("narration, channel", [
    ("CHQ PAID-MICR CTS-KAVERI TRADERS", "CHEQUE"),
    ("CLG/PRAGATI LLP/000123/ZZBK/15.10.2026ABC", "CHEQUE"),
    ("SMS CHGS QTR SEP26", "CHARGE"),
    ("MIN BAL CHGS", "CHARGE"),
    ("GST ON SMS CHGS", "CHARGE"),
    ("CREDIT INTEREST", "INTEREST"),
    ("Int.Pd:1234567:01-07-2026-30-09-2026", "INTEREST"),
    ("CASH DEPOSIT BY SELF", "CASH"),
    ("ATM WDL ZZBK GANDHINAGAR", "CASH"),
    ("ACH D- ZENITH MUTUAL FUND-SIP", "OTHER"),
])
def test_non_transfer_channels_have_no_narration_reference(narration, channel):
    assert classify(narration) == channel
    assert extract_reference(narration, channel) is None  # pulling digits out of these causes false matches downstream


def test_phone_or_account_digits_outside_the_ref_segment_are_ignored():
    # 12-digit account fragment appears before the RRN segment; only the RRN position counts.
    n = "IMPS-612345678906-ANVAY LLP-ZENITH-123456789012-refund"
    assert extract_reference(n, "IMPS") == "612345678906"


def test_utr_split_by_a_pdf_line_wrap_is_rejoined():
    assert extract_reference("NEFT CR-ZZBK0004321-TRIKON PVT LTD-ZZBKN2610150 0126", "NEFT") == "ZZBKN26101500126"


def test_unknown_layout_returns_no_reference_rather_than_a_guess():
    assert extract_reference("UPI-SOMEONE-noref", "UPI") is None


@pytest.mark.parametrize("narration, party", [
    ("CHQ PAID-MICR CTS-AARAV OFFICE SUPPLIES", "AARAV OFFICE SUPPLIES"),
    ("UPI-NIMBUS IT SERVICES-nimbus@okzz-ZZBK0001487-643320313538-PURCHASE", "NIMBUS IT SERVICES"),
    ("NEFT DR-ZZBK0004321-ANVAY LLP-NETBANK,MUM-ZZBKN26101500125-payment", "ANVAY LLP"),
    ("SMS CHGS QTR", None),  # bank charge: no counterparty but the bank
    ("CREDIT INTEREST TILL 06-SEP-2026", None),
    ("IMPS-612345678904-CREDIT INDIA LTD-ZENITH-XXXXXXXX1234-advance", "CREDIT INDIA LTD"),
])
def test_counterparty_hint(narration, party):
    from docflow.pipeline import _counterparty

    assert _counterparty(narration, classify(narration)) == party


def test_space_separated_neft_narration():
    assert extract_reference("NEFT ZZBKN26091500123 ANVAY TRADERS", "NEFT") == "ZZBKN26091500123"


def test_bank_internal_bil_id_is_not_a_utr():
    # ICICI-style net-banking transfer: the id is the bank's own transfer id, not the UTR
    assert extract_reference("BIL/NEFT/ZZ00012345/VENDOR/ANVAY LLP/ZENITH", "NEFT") is None


def test_cheque_number_from_a_clearing_narration():
    from docflow.narration import extract_cheque

    assert extract_cheque("CLG/PRAGATI LLP/000123/ZZBK/15.10.2026") == "000123"
    assert extract_cheque("CHQ PAID-MICR CTS-ANVAY") is None
