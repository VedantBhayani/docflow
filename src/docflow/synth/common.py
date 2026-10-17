"""Shared synthetic-data helpers: fictional parties, valid GSTINs, GST arithmetic.

Everything here is fictional. Names are assembled from neutral word lists and every
document is marked SYNTHETIC, so nothing can pass for a real company's invoice.
"""

import random
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from docflow.gstin import check_char

TWO = Decimal("0.01")

STATES = {  # GST state code -> name (subset of the GST state-code master)
    "24": "Gujarat", "27": "Maharashtra", "29": "Karnataka", "33": "Tamil Nadu",
    "07": "Delhi", "09": "Uttar Pradesh", "19": "West Bengal", "36": "Telangana",
}
CITIES = {
    "24": ["Ahmedabad", "Gandhinagar", "Surat", "Vadodara"], "27": ["Mumbai", "Pune", "Nagpur"],
    "29": ["Bengaluru", "Mysuru"], "33": ["Chennai", "Coimbatore"], "07": ["New Delhi"],
    "09": ["Noida", "Lucknow"], "19": ["Kolkata"], "36": ["Hyderabad"],
}
_FIRST = ["Aarav", "Nimbus", "Sahyadri", "Kaveri", "Vistar", "Pragati", "Shakti", "Udaan", "Anvay", "Trikon", "Meghdoot", "Sarthi"]
_SECOND = ["Packaging", "Office Supplies", "Electricals", "Logistics", "Fabrication", "Stationers", "Hardware", "Polymers", "Textiles", "IT Services"]
_SUFFIX = ["Pvt Ltd", "LLP", "Traders", "Enterprises", "Industries Pvt Ltd"]

# (description, HSN/SAC, unit, typical unit price) - post 22.09.2025 slabs applied by the caller.
CATALOGUE = [
    ("Corrugated cartons 5-ply", "48191010", "NOS", 42),
    ("A4 copier paper 75 GSM (ream)", "48025690", "PAC", 285),
    ("LED panel light 18W", "94051900", "NOS", 610),
    ("Ergonomic office chair", "94013000", "NOS", 7450),
    ("Stretch wrap film 23 micron", "39201012", "KGS", 168),
    ("Copper cable 2.5 sq mm (90 m)", "85444999", "ROL", 3120),
    ("Annual IT support services", "998713", "OTH", 18500),
    ("Freight charges", "996511", "OTH", 2400),
    ("Steel shelving unit", "94032090", "NOS", 5300),
    ("Hand sanitiser 500 ml", "38089400", "BTL", 95),
]


@dataclass(frozen=True)
class Party:
    name: str
    address: str
    state_code: str
    gstin: str


def money(x) -> Decimal:
    return Decimal(x).quantize(TWO, rounding=ROUND_HALF_UP)


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


def make_gstin(rng: random.Random, state_code: str, name: str) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pan = "".join(rng.choice(letters) for _ in range(3)) + "C" + name[0].upper() + f"{rng.randint(0, 9999):04d}" + rng.choice(letters)
    body = f"{state_code}{pan}{rng.randint(1, 3)}Z"
    return body + check_char(body)


def make_party(rng: random.Random, state_code: str) -> Party:
    name = f"{rng.choice(_FIRST)} {rng.choice(_SECOND)} {rng.choice(_SUFFIX)}"
    city = rng.choice(CITIES[state_code])
    address = f"Unit {rng.randint(1, 240)}, {rng.choice(['Industrial Estate', 'Trade Centre', 'Business Park', 'MIDC Road'])}, {city}, {STATES[state_code]}"
    return Party(name=name, address=address, state_code=state_code, gstin=make_gstin(rng, state_code, name))
