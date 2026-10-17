from datetime import date
from decimal import Decimal

import pytest

from docflow.parse import parse_amount, parse_date, parse_rate


@pytest.mark.parametrize(
    "printed, expected",
    [
        ("11,800.00", Decimal("11800.00")),
        ("Rs. 1,18,000.50", Decimal("118000.50")),  # Indian digit grouping
        ("₹ 250", Decimal("250")),
        ("INR 9,999.9", Decimal("9999.9")),
        ("(0.40)", Decimal("-0.40")),  # accounting negative
        ("-0.40", Decimal("-0.40")),
    ],
)
def test_amounts_as_printed_on_indian_invoices(printed, expected):
    assert parse_amount(printed) == expected


@pytest.mark.parametrize("printed", ["", "N/A", "12.3.4", "abc"])
def test_unparseable_amounts_return_none(printed):
    assert parse_amount(printed) is None


@pytest.mark.parametrize(
    "printed, expected",
    [
        ("03/10/2026", date(2026, 10, 3)),  # Indian invoices are day-first
        ("03-10-2026", date(2026, 10, 3)),
        ("3-Oct-2026", date(2026, 10, 3)),
        ("03 Oct 2026", date(2026, 10, 3)),
        ("03.10.2026", date(2026, 10, 3)),
        ("2026-10-03", date(2026, 10, 3)),
        ("03/10/26", date(2026, 10, 3)),
    ],
)
def test_dates_are_day_first(printed, expected):
    assert parse_date(printed) == expected


@pytest.mark.parametrize("printed", ["31/02/2026", "13/13/2026", "yesterday", ""])
def test_impossible_dates_return_none(printed):
    assert parse_date(printed) is None


@pytest.mark.parametrize("printed, expected", [("18%", Decimal("18")), ("9 %", Decimal("9")), ("2.5", Decimal("2.5"))])
def test_rates(printed, expected):
    assert parse_rate(printed) == expected
