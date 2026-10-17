"""Indian-style money formatting for anything an auditor reads."""

from decimal import Decimal


def fmt_inr(x: Decimal) -> str:
    """Indian digit grouping: 1,18,000.50."""
    sign = "-" if x < 0 else ""
    whole, frac = f"{abs(x):.2f}".split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    return f"{sign}{whole}.{frac}"
