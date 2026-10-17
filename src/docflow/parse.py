"""Deterministic interpretation of printed text. The LLM never converts values; this does.

Indian invoices print dates day-first and may use lakh grouping (1,18,000.50).
Anything ambiguous or malformed returns None rather than a guess.
"""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

_CURRENCY = re.compile(r"(?i)(?<![a-z])(rs\.?|inr)(?![a-z])|₹")
_AMOUNT = re.compile(r"^-?\d+(\.\d+)?$")
_OCR_DOTTED = re.compile(r"^-?\d{1,3}([.,]\d{2,3})*\.\d{2,3}([.,]\d{2,3})*\.\d{2}$")  # 22.014.48, 3.25,635.05
_DATE_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d-%b-%Y", "%d %b %Y", "%d-%B-%Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]


def parse_amount(text: str | None) -> Decimal | None:
    if not text:
        return None
    raw = text.strip()
    if re.search(r"[.,]\d{2}[.,]$", raw):  # stray OCR dot after a 2-decimal amount: "17.70."
        raw = raw[:-1]
    s = _CURRENCY.sub("", raw).strip()
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(" ", "")
    if _OCR_DOTTED.match(s):  # OCR read thousand-separator commas as dots: only the last dot is decimal
        head, _, frac = s.rpartition(".")
        s = head.replace(".", "").replace(",", "") + "." + frac
    s = s.replace(",", "")
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
    s = re.sub(r"(?<=\d)[~_](?=\d)", "-", s)  # OCR noise: '~' or '_' between digits can only be a separator
    if "-" in s and "/" in s:
        s = s.replace("/", "-")
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
