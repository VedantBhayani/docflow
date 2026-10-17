from docflow.models import Field, FieldStatus
from docflow.pipeline import INVOICE_KEY_FIELDS, evidence_flags


def F(name, status, text="x"):
    return Field(name=name, text=text, status=status)


def ids(flags):
    return sorted(f.check_id for f in flags)


def test_grounded_and_verified_fields_raise_nothing():
    fields = {"invoice_no": F("invoice_no", FieldStatus.GROUNDED), "grand_total": F("grand_total", FieldStatus.VERIFIED)}
    assert evidence_flags(fields, [], INVOICE_KEY_FIELDS) == []


def test_ungrounded_field_is_e1_even_if_not_key():
    fields = {"recipient_name": F("recipient_name", FieldStatus.UNGROUNDED)}
    assert ids(evidence_flags(fields, [], INVOICE_KEY_FIELDS)) == ["E1"]


def test_ungrounded_line_value_is_e1():
    lines = [{"igst": F("lines.0.igst", FieldStatus.UNGROUNDED)}]
    flags = evidence_flags({}, lines, INVOICE_KEY_FIELDS)
    assert ids(flags) == ["E1"] and flags[0].fields == ("lines.0.igst",)


def test_missing_key_field_is_e2_but_missing_optional_field_is_not():
    fields = {"grand_total": F("grand_total", FieldStatus.MISSING, None), "round_off": F("round_off", FieldStatus.MISSING, None)}
    assert ids(evidence_flags(fields, [], INVOICE_KEY_FIELDS)) == ["E2"]


def test_conflict_with_the_rule_extractor_is_e3():
    f = F("supplier_gstin", FieldStatus.CONFLICT)
    f.conflicts["rules"] = "27AAACU2414K1ZF"
    flags = evidence_flags({"supplier_gstin": f}, [], INVOICE_KEY_FIELDS)
    assert ids(flags) == ["E3"] and "27AAACU2414K1ZF" in flags[0].message


def test_conflict_only_with_the_qr_is_left_to_q2():
    f = F("grand_total", FieldStatus.CONFLICT)
    f.conflicts["qr"] = "2705.0"
    assert evidence_flags({"grand_total": f}, [], INVOICE_KEY_FIELDS) == []


def test_ungrounded_non_checked_field_is_only_a_warning():
    fields = {"irn": F("irn", FieldStatus.UNGROUNDED), "supplier_address": F("supplier_address", FieldStatus.UNGROUNDED)}
    flags = evidence_flags(fields, [{"description": F("lines.0.description", FieldStatus.UNGROUNDED)}], INVOICE_KEY_FIELDS)
    assert {f.severity for f in flags} == {"WARNING"} and len(flags) == 3


def test_ungrounded_value_that_feeds_a_check_is_blocking():
    fields = {"igst_total": F("igst_total", FieldStatus.UNGROUNDED)}
    flags = evidence_flags(fields, [{"taxable_value": F("lines.0.taxable_value", FieldStatus.UNGROUNDED)}], INVOICE_KEY_FIELDS)
    assert {f.severity for f in flags} == {"BLOCKING"} and len(flags) == 2
