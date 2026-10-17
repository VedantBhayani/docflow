"""Deterministic interpretation of printed text. The LLM never converts values; this does.

Indian invoices print dates day-first and may use lakh grouping (1,18,000.50).
Anything ambiguous or malformed returns None rather than a guess.
"""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

_CURRENCY = re.compile(r"(?i)(?<![a-z])(rs\.?|inr)(?![a-z])|₹")
_AMOUNT = re.compile(r"^-?\d+(\.\d+)?$")
_DATE_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d-%b-%Y", "%d %b %Y", "%d-%B-%Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]


def parse_amount(text: str | None) -> Decimal | None:
    if not text:
        return None
    s = _CURRENCY.sub("", text).strip()
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "").replace(" ", "")
    if not _AMOUNT.match(s):
        return None
    try:
        value = Decimal(s)
    except InvalidOperation:
        return None
    return -value if negative else value


def parse_date(text: str | None) -> date | None:
    if not text:
        return None
    s = re.sub(r"\s+", " ", text.strip())
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_rate(text: str | None) -> Decimal | None:
    if not text:
        return None
    return parse_amount(text.replace("%", ""))
