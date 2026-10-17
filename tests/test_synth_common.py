import random
from decimal import Decimal

from docflow.gstin import validate_gstin
from docflow.synth.common import fmt_inr, make_party


def test_generated_parties_have_valid_gstins_for_their_state():
    rng = random.Random(1)
    for state in ["24", "27", "29", "33", "07", "09", "19", "36"]:
        for _ in range(25):
            party = make_party(rng, state)
            assert validate_gstin(party.gstin) == [], party.gstin
            assert party.gstin[:2] == state


def test_indian_grouping():
    assert fmt_inr(Decimal("118000.50")) == "1,18,000.50"
    assert fmt_inr(Decimal("11800")) == "11,800.00"
    assert fmt_inr(Decimal("999.5")) == "999.50"
    assert fmt_inr(Decimal("12345678.9")) == "1,23,45,678.90"
