from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from zhouyi.domain.enums import CalendarMode, Element, LineState, TrigramId


def _dump_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_dump_value(item) for item in value]
    if isinstance(value, list):
        return [_dump_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _dump_value(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


@dataclass(slots=True, frozen=True)
class TrigramInfo:
    trigram_id: TrigramId
    name_zh: str
    number: int
    element: Element
    symbol: str
    lines: tuple[int, int, int]
    image: str
    name_en: str | None = None
    image_en: str | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.number <= 8:
            raise ValueError(f"trigram number must be 1-8, got {self.number}")
        if not all(b in {0, 1} for b in self.lines):
            raise ValueError(f"trigram lines must be 0 or 1, got {self.lines}")

    def display_name(self, language: str = "zh") -> str:
        if language == "en" and self.name_en:
            return self.name_en
        return self.name_zh

    def display_image(self, language: str = "zh") -> str:
        if language == "en" and self.image_en:
            return self.image_en
        return self.image

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigram_id": self.trigram_id.value,
            "name_zh": self.name_zh,
            "name_en": self.name_en,
            "number": self.number,
            "element": self.element.value,
            "symbol": self.symbol,
            "lines": list(self.lines),
            "image": self.image,
            "image_en": self.image_en,
        }


@dataclass(slots=True, frozen=True)
class Hexagram:
    lines: tuple[LineState, ...]
    king_wen_index: int
    name_zh: str
    unicode_symbol: str
    upper_trigram: TrigramId
    lower_trigram: TrigramId
    summary: str
    name_en: str | None = None
    summary_en: str | None = None

    def __post_init__(self) -> None:
        if len(self.lines) != 6:
            raise ValueError(f"hexagram must have exactly 6 lines, got {len(self.lines)}")
        if not 1 <= self.king_wen_index <= 64:
            raise ValueError(f"king_wen_index must be 1-64, got {self.king_wen_index}")

    def display_name(self, language: str = "zh") -> str:
        if language == "en" and self.name_en:
            return self.name_en
        return self.name_zh

    def display_summary(self, language: str = "zh") -> str:
        if language == "en" and self.summary_en:
            return self.summary_en
        return self.summary

    @property
    def changing_lines(self) -> tuple[int, ...]:
        return tuple(
            index for index, line in enumerate(self.lines, start=1) if line.is_moving
        )

    @property
    def binary_lines(self) -> tuple[int, ...]:
        return tuple(1 if line.is_yang else 0 for line in self.lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lines": [int(line) for line in self.lines],
            "binary_lines": list(self.binary_lines),
            "king_wen_index": self.king_wen_index,
            "name_zh": self.name_zh,
            "name_en": self.name_en,
            "unicode_symbol": self.unicode_symbol,
            "upper_trigram": self.upper_trigram.value,
            "lower_trigram": self.lower_trigram.value,
            "changing_lines": list(self.changing_lines),
            "summary": self.summary,
            "summary_en": self.summary_en,
        }


@dataclass(slots=True)
class CastRequest:
    question: str | None = None
    calendar_mode: CalendarMode = CalendarMode.CIVIL_SIMPLIFIED
    datetime_value: datetime | None = None
    raw_numbers: tuple[int, ...] = ()
    raw_text: str | None = None
    seed: int | None = None
    show_steps: bool = False
    interactive_inputs: dict[str, Any] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "calendar_mode": self.calendar_mode.value,
            "datetime_value": _dump_value(self.datetime_value),
            "raw_numbers": list(self.raw_numbers),
            "raw_text": self.raw_text,
            "seed": self.seed,
            "show_steps": self.show_steps,
            "interactive_inputs": _dump_value(self.interactive_inputs),
            "extras": _dump_value(self.extras),
        }


@dataclass(slots=True)
class CastResult:
    session_id: str
    question: str | None
    method_id: str
    method_version: str
    created_at: datetime
    timezone: str
    calendar_mode: CalendarMode | None
    seed: int | None
    primary_hexagram: Hexagram
    relating_hexagram: Hexagram | None
    mutual_hexagram: Hexagram | None
    changing_lines: tuple[int, ...]
    steps: list[dict[str, Any]]
    raw_inputs: dict[str, Any]
    raw_derivation: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "question": self.question,
            "method_id": self.method_id,
            "method_version": self.method_version,
            "created_at": self.created_at.isoformat(),
            "timezone": self.timezone,
            "calendar_mode": self.calendar_mode.value if self.calendar_mode else None,
            "seed": self.seed,
            "primary_hexagram": self.primary_hexagram.to_dict(),
            "relating_hexagram": self.relating_hexagram.to_dict()
            if self.relating_hexagram
            else None,
            "mutual_hexagram": self.mutual_hexagram.to_dict()
            if self.mutual_hexagram
            else None,
            "changing_lines": list(self.changing_lines),
            "steps": _dump_value(self.steps),
            "raw_inputs": _dump_value(self.raw_inputs),
            "raw_derivation": _dump_value(self.raw_derivation),
            "provenance": _dump_value(self.provenance),
        }


@dataclass(slots=True)
class Interpretation:
    primary_texts: dict[str, Any]
    line_texts: list[dict[str, Any]]
    method_specific_analysis: dict[str, Any]
    body_use_analysis: dict[str, Any]
    timing_notes: list[str]
    plain_language_summary: str
    confidence_notes: list[str]
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_texts": _dump_value(self.primary_texts),
            "line_texts": _dump_value(self.line_texts),
            "method_specific_analysis": _dump_value(self.method_specific_analysis),
            "body_use_analysis": _dump_value(self.body_use_analysis),
            "timing_notes": list(self.timing_notes),
            "plain_language_summary": self.plain_language_summary,
            "confidence_notes": list(self.confidence_notes),
            "provenance": _dump_value(self.provenance),
        }


@dataclass(slots=True, frozen=True)
class InterpretationProfile:
    profile_id: str
    name: str
    summary_style: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "summary_style": self.summary_style,
        }
