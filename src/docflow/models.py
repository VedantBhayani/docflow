"""Core types. Vocabulary follows GLOSSARY.md (Source Document, Field, Evidence, Check, Flag)."""

from dataclasses import dataclass, field
from enum import StrEnum


@dataclass(frozen=True)
class Word:
    id: str  # "w17", unique within a Source Document, in reading order
    text: str
    page: int  # 0-based
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1 normalised to 0..1 of the page
    confidence: float = 1.0  # 1.0 for text-layer words; OCR score otherwise


@dataclass
class Page:
    index: int
    width: float
    height: float
    source: str  # "pdf_text" | "ocr"
    words: list[Word]
    mean_confidence: float = 1.0
    transform: dict | None = None  # OCR pages: {"quarter_turns", "deskew_deg", "dpi"} to reproduce the evidence image


@dataclass
class Document:
    path: str
    sha256: str
    pages: list[Page]

    def words(self) -> list[Word]:
        return [w for p in self.pages for w in p.words]


class FieldStatus(StrEnum):
    VERIFIED = "VERIFIED"  # grounded and agrees with an independent source
    GROUNDED = "GROUNDED"  # the referenced words spell the value
    UNGROUNDED = "UNGROUNDED"  # the referenced words do not spell the value
    CONFLICT = "CONFLICT"  # sources disagree
    MISSING = "MISSING"


@dataclass(frozen=True)
class Evidence:
    page: int
    bbox: tuple[float, float, float, float]


@dataclass
class Field:
    name: str
    text: str | None  # exactly as printed on the Source Document
    status: FieldStatus
    word_ids: list[str] = field(default_factory=list)
    evidence: Evidence | None = None
    match_score: float = 0.0
    sources: list[str] = field(default_factory=list)
    conflicts: dict[str, str] = field(default_factory=dict)  # source -> the value that source read instead


class Severity(StrEnum):
    BLOCKING = "BLOCKING"
    WARNING = "WARNING"


@dataclass(frozen=True)
class Flag:
    check_id: str
    severity: Severity
    message: str
    fields: tuple[str, ...] = ()
