"""GSTIN validation, checks G1-G5 (research note 01, section G).

G5 (Luhn mod 36) has no official publication; it is confirmed empirically on
74/74 bank-published GSTINs. See .scratch/docflow/research/01-gst-invoice-rules.md.
"""

import re

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_FORMAT = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$")
# GST state-code master (einvoice1.gst.gov.in/Others/MasterCodes): 01-38 except 28, plus 97.
STATE_CODES = frozenset({f"{n:02d}" for n in range(1, 39) if n != 28} | {"97"})
_PAN_HOLDER_TYPES = set("ABCFGHLJPT")


def check_char(first14: str) -> str:
    total = 0
    for i, ch in enumerate(first14.upper()):
        product = _ALPHABET.index(ch) * (1 if i % 2 == 0 else 2)
        total += product // 36 + product % 36
    return _ALPHABET[(36 - total % 36) % 36]


def normalise(gstin: str) -> str:
    return re.sub(r"\s+", "", gstin).upper()


def validate_gstin(gstin: str) -> list[str]:
    """Failed check IDs, in order. Empty list means valid."""
    g = normalise(gstin)
    if not _FORMAT.match(g):
        return ["G1"]
    failures = []
    if g[:2] not in STATE_CODES:
        failures.append("G2")
    if g[5] not in _PAN_HOLDER_TYPES:
        failures.append("G3")
    if g[12] == "0":
        failures.append("G4")
    if check_char(g[:14]) != g[14]:
        failures.append("G5")
    return failures
