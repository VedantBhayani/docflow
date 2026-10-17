"""Deterministic channel classification and reference extraction for bank narrations.

Patterns come from research note 04 (per-bank templates from open-source statement
parsers). Rule adopted from those parsers: extract a reference only for channels whose
narration is built around one, and only from that channel's own segment; pulling digit
runs out of cheque, interest or mandate rows creates false matches downstream.
"""

import re

RRN = re.compile(r"^\d{12}$")
NEFT_UTR = re.compile(r"^[A-Z]{4}[A-Z0-9]\d{7,}[A-Z0-9]*$")
RTGS_UTR = re.compile(r"^[A-Z]{4}R[A-Z0-9](?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{8}$")
IFSC = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")

_CHANNELS = [  # order matters: anchored and more specific prefixes first
    ("CHEQUE", re.compile(r"^\s*CLG\s*/|\bCHQ\b|\bCHEQUE\b|\bCLG\b|\bINWARD CLG\b")),
    ("IMPS", re.compile(r"\bMMT\s*/\s*IMPS\b|\bIMPS\b")),
    ("UPI", re.compile(r"\bUPI\b")),
    ("RTGS", re.compile(r"\bRTGS\b")),
    ("NEFT", re.compile(r"\bNEFT\b")),
    ("INTEREST", re.compile(r"\bINT\.?\s*PD\b|\bINTEREST\b")),
    ("CHARGE", re.compile(r"\bCHGS?\b|\bCHARGES?\b|\bFEE\b|\bAMC\b|\bGST\b")),
    ("CASH", re.compile(r"\bCASH\b|\bATM\b")),
]


def classify(narration: str) -> str:
    n = re.sub(r"\s+", " ", narration.upper())
    for channel, pattern in _CHANNELS:
        if pattern.search(n):
            return channel
    return "OTHER"


def _segments(n: str) -> list[str]:
    """Narrations are delimited by '-', '/', '*' or spaces depending on the bank; references never contain these."""
    return [s.strip(",.") for s in re.split(r"[-/*\s]+", n) if s.strip(",.")]


def _rejoin_wrapped(n: str) -> str:
    """A PDF line wrap can insert one space inside a long reference ('ZZBKN2610150 0126')."""
    return re.sub(r"([A-Z]{4}[A-Z0-9]\d{5,})\s(\d{1,6})\b", r"\1\2", n)


def extract_reference(narration: str, channel: str) -> str | None:
    n = _rejoin_wrapped(re.sub(r"\s+", " ", narration.upper().strip()))
    segs = _segments(n)
    if channel in ("UPI", "IMPS"):
        # The RRN is the first 12-digit segment after the channel keyword.
        start = next((i for i, s in enumerate(segs) if re.search(rf"\b{channel}\b", s)), None)
        if start is None:
            return None
        for s in segs[start + 1 :]:
            if RRN.match(s):
                return s
        return None
    if channel == "RTGS":
        for s in segs:
            if RTGS_UTR.match(s):
                return s
        return None
    if channel == "NEFT":
        if re.match(r"^\s*BIL\s*/", n):
            return None  # ICICI net-banking: the id is the bank's own transfer id, not the UTR (research note 04)
        for s in segs:
            if IFSC.match(s):
                continue
            if NEFT_UTR.match(s) and len(s) == 16:
                return s
        return None
    return None


CLG_CHEQUE = re.compile(r"^\s*CLG\s*/[^/]+/(\d{6})\b")


def extract_cheque(narration: str) -> str | None:
    """Cheque serial from a clearing narration (CLG/<payer>/<serial>/...) for layouts without a cheque column."""
    m = CLG_CHEQUE.match(narration.upper())
    return m.group(1) if m else None
