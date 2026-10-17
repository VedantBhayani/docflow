"""Grounding: prove each extracted value is printed where the LLM says it is.

Exact (whitespace-insensitive) match for numbers, IDs and dates. Fuzzy matching is
allowed only for free text, because a one-digit difference in a long amount still
scores above 90% similarity.
"""

import re

from rapidfuzz import fuzz

from docflow.models import Evidence, Field, FieldStatus, Word

FREE_TEXT_FIELDS = {"supplier_name", "recipient_name", "description", "place_of_supply", "supplier_address", "recipient_address", "narration"}
FUZZY_MIN = 90.0


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s).casefold()


def _whole_word_subspan(words: list[Word], value: str) -> list[Word] | None:
    """The contiguous run of whole words that spells the value exactly, if any."""
    texts = [_norm(w.text) for w in words]
    for i in range(len(texts)):
        joined = ""
        for j in range(i, len(texts)):
            joined += texts[j]
            if joined == value:
                return words[i : j + 1]
            if len(joined) >= len(value):
                break
    return None


def _id_num(word_id: str) -> int | None:
    return int(word_id[1:]) if word_id[1:].isdigit() else None


def _complete_span(words: list[Word], value: str, index: dict[str, Word], reach: int = 3) -> list[Word] | None:
    """Extend an incomplete pointer to adjacent words on the same visual row, if that spells the value exactly."""
    nums = [_id_num(w.id) for w in words]
    if None in nums:
        return None
    lo, hi = min(nums), max(nums)
    row_cy = (words[0].bbox[1] + words[0].bbox[3]) / 2
    height = words[0].bbox[3] - words[0].bbox[1]

    def same_row(n: int) -> Word | None:
        w = index.get(f"w{n}")
        if w is None or w.page != words[0].page or abs((w.bbox[1] + w.bbox[3]) / 2 - row_cy) > height / 2:
            return None
        return w

    for left in range(0, reach + 1):
        for right in range(0, reach + 1):
            if left == right == 0:
                continue
            span = [same_row(n) for n in range(lo - left, hi + right + 1)]
            if all(span) and _norm(" ".join(w.text for w in span)) == value:
                return span
    return None


def _union(words: list[Word]) -> Evidence:
    page = words[0].page
    same = [w for w in words if w.page == page]
    return Evidence(
        page=page,
        bbox=(min(w.bbox[0] for w in same), min(w.bbox[1] for w in same), max(w.bbox[2] for w in same), max(w.bbox[3] for w in same)),
    )


def ground_ref(name: str, text: str | None, word_ids: list[str], index: dict[str, Word]) -> Field:
    if text is None or not text.strip():
        return Field(name=name, text=None, status=FieldStatus.MISSING, sources=["llm"])
    words = [index[i] for i in word_ids if i in index]
    if not words or len(words) != len(word_ids):
        return Field(name=name, text=text, status=FieldStatus.UNGROUNDED, word_ids=word_ids, sources=["llm"])

    printed = _norm(" ".join(w.text for w in words))
    value = _norm(text)
    base = name.split(".")[-1]
    if printed == value:
        score = 100.0
    elif sub := _whole_word_subspan(words, value):
        score = 95.0  # span also covers a label such as "GSTIN:"; evidence is the value's own words
        words = sub
    elif full := _complete_span(words, value, index):
        score = 90.0  # pointer was incomplete; the exact value is printed in the adjacent words
        words, word_ids = full, [w.id for w in full]
    elif base in FREE_TEXT_FIELDS and fuzz.ratio(printed, value) >= FUZZY_MIN:
        score = round(fuzz.ratio(printed, value), 1)
    else:
        return Field(name=name, text=text, status=FieldStatus.UNGROUNDED, word_ids=word_ids, evidence=_union(words), sources=["llm"])
    return Field(name=name, text=text, status=FieldStatus.GROUNDED, word_ids=word_ids, evidence=_union(words), match_score=score, sources=["llm"])
