"""Bank statement Checks S1-S6 (research note 04, section 4).

Balances are checked against the PRINTED previous balance, so one wrong row is reported
where it happens (and on the row after it, whose arithmetic it also breaks).
"""

from collections import Counter
from decimal import Decimal

from docflow.checks import CheckInfo
from docflow.models import Field, Flag, Severity
from docflow.money import fmt_inr
from docflow.narration import classify, extract_reference
from docflow.parse import parse_amount, parse_date

B, W = Severity.BLOCKING, Severity.WARNING
CENT = Decimal("0.01")
SRC = "research note 04, section 4 (balance-chain invariant)"
STATEMENT_CATALOGUE = [
    CheckInfo("S1", B, "Balance chain: previous balance - debit + credit = printed balance, on every row.", SRC),
    CheckInfo("S2", B, "Opening balance + total credits - total debits = closing balance.", SRC),
    CheckInfo("S3", B, "Each transaction has exactly one of debit or credit.", SRC),
    CheckInfo("S4", B, "Each transaction date lies inside the statement period.", SRC),
    CheckInfo("S5", W, "UPI/IMPS rows carry a 12-digit RRN; NEFT a 16-character UTR; RTGS a 22-character UTR.", "RBI FAQ (RTGS UTR), bank formats; research note 04"),
    CheckInfo("S6", W, "Possible duplicate row (same date, amount, direction and reference).", "DocFlow"),
]


def _t(f: Field | None) -> str | None:
    return f.text.strip() if f is not None and f.text and f.text.strip() else None


def _amt(f: Field | None) -> Decimal | None:
    return parse_amount(_t(f))


def run_statement_checks(fields: dict[str, Field], lines: list[dict[str, Field]]) -> list[Flag]:
    flags: list[Flag] = []
    prev = _amt(fields.get("opening_balance"))
    total_dr = total_cr = Decimal(0)
    start, end = parse_date(_t(fields.get("period_from"))), parse_date(_t(fields.get("period_to")))
    seen: Counter = Counter()
    for i, ln in enumerate(lines):
        n = i + 1
        dr, cr, bal = _amt(ln.get("debit")), _amt(ln.get("credit")), _amt(ln.get("balance"))
        if (dr is None) == (cr is None):
            flags.append(Flag("S3", B, f"Row {n}: has {'both a debit and a credit' if dr is not None else 'neither a debit nor a credit'}.",
                              (f"lines.{i}.debit", f"lines.{i}.credit")))
        total_dr += dr or 0
        total_cr += cr or 0
        if prev is not None and bal is not None and (dr is not None or cr is not None):
            expected = prev - (dr or 0) + (cr or 0)
            if abs(expected - bal) > CENT:
                flags.append(Flag("S1", B, f"Row {n}: previous balance {fmt_inr(prev)} - debit {fmt_inr(dr or 0)} + credit {fmt_inr(cr or 0)} = {fmt_inr(expected)}, but the statement prints {fmt_inr(bal)}.",
                                  (f"lines.{i}.balance",)))
        if bal is not None:
            prev = bal
        d = parse_date(_t(ln.get("txn_date")))
        if d and start and end and not (start <= d <= end):
            flags.append(Flag("S4", B, f"Row {n}: date {d:%d.%m.%Y} is outside the statement period {start:%d.%m.%Y} to {end:%d.%m.%Y}.", (f"lines.{i}.txn_date",)))
        narration = _t(ln.get("narration")) or ""
        channel = classify(narration)
        ref = extract_reference(narration, channel)
        if channel in ("UPI", "IMPS", "NEFT", "RTGS") and ref is None:
            want = {"UPI": "a 12-digit RRN", "IMPS": "a 12-digit RRN", "NEFT": "a 16-character UTR", "RTGS": "a 22-character UTR"}[channel]
            flags.append(Flag("S5", W, f"Row {n}: {channel} narration does not carry {want}; matching this row to the books will need a human.", (f"lines.{i}.narration",)))
        key = (d, dr, cr, ref or _t(ln.get("ref_col")))
        seen[key] += 1
        if seen[key] == 2:
            flags.append(Flag("S6", W, f"Row {n}: same date, amount and reference as an earlier row; possible duplicate entry.", (f"lines.{i}.narration",)))
    opening, closing = _amt(fields.get("opening_balance")), _amt(fields.get("closing_balance"))
    if opening is not None and closing is not None and lines:
        expected = opening + total_cr - total_dr
        if abs(expected - closing) > CENT:
            flags.append(Flag("S2", B, f"Opening {fmt_inr(opening)} + credits {fmt_inr(total_cr)} - debits {fmt_inr(total_dr)} = {fmt_inr(expected)}, but closing balance is {fmt_inr(closing)}.",
                              ("opening_balance", "closing_balance")))
    return flags
