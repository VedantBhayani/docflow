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


def test_conflict_is_e3():
    fields = {"supplier_gstin": F("supplier_gstin", FieldStatus.CONFLICT)}
    assert ids(evidence_flags(fields, [], INVOICE_KEY_FIELDS)) == ["E3"]
