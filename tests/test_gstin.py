import pytest

from docflow.gstin import check_char, validate_gstin

# Real GSTINs published by the banks themselves (research note 01, worked examples).
AXIS_MH = "27AAACU2414K1ZF"
IDBI_MH = "27AABCI8842G1ZF"


@pytest.mark.parametrize("gstin", [AXIS_MH, IDBI_MH])
def test_bank_published_gstins_are_valid(gstin):
    assert validate_gstin(gstin) == []


def test_check_char_matches_published_worked_example():
    assert check_char(AXIS_MH[:14]) == "F"


def test_wrong_check_character_fails_g5():
    assert validate_gstin("27AAACU2414K1ZH") == ["G5"]


def test_single_character_typo_in_body_is_caught():
    # One OCR-style swap (0 -> O would break format; use a digit change instead).
    assert "G5" in validate_gstin("27AAACU2415K1ZF")


def test_bad_format_short_circuits():
    assert validate_gstin("27AAACU2414K1Z") == ["G1"]


def test_unknown_state_code_fails_g2():
    # 28 (old Andhra Pradesh) is not in the GST state-code master.
    body = "28AAACU2414K1Z"
    assert "G2" in validate_gstin(body + check_char(body))


def test_bad_pan_holder_type_fails_g3():
    # 4th PAN character must be a holder type (C, P, H, F, A, T, B, L, J, G).
    body = "27AAAXU2414K1Z"
    assert "G3" in validate_gstin(body + check_char(body))


def test_entity_number_zero_fails_g4():
    body = "27AAACU2414K0Z"
    assert "G4" in validate_gstin(body + check_char(body))


def test_spaces_and_lowercase_are_normalised():
    assert validate_gstin(" 27aaacu2414k1zf ") == []
