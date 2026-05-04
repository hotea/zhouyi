from __future__ import annotations

from uuid import uuid4

from zhouyi.domain.enums import Element, LineState, TrigramId


GENERATION_ORDER = {
    Element.WOOD: Element.FIRE,
    Element.FIRE: Element.EARTH,
    Element.EARTH: Element.METAL,
    Element.METAL: Element.WATER,
    Element.WATER: Element.WOOD,
}

CONTROL_ORDER = {
    Element.WOOD: Element.EARTH,
    Element.EARTH: Element.WATER,
    Element.WATER: Element.FIRE,
    Element.FIRE: Element.METAL,
    Element.METAL: Element.WOOD,
}


TRIGRAM_NUMBER_MAP = {
    1: TrigramId.QIAN,
    2: TrigramId.DUI,
    3: TrigramId.LI,
    4: TrigramId.ZHEN,
    5: TrigramId.XUN,
    6: TrigramId.KAN,
    7: TrigramId.GEN,
    8: TrigramId.KUN,
}


TRIGRAM_LINES = {
    TrigramId.QIAN: (1, 1, 1),
    TrigramId.DUI: (1, 1, 0),
    TrigramId.LI: (1, 0, 1),
    TrigramId.ZHEN: (1, 0, 0),
    TrigramId.XUN: (0, 1, 1),
    TrigramId.KAN: (0, 1, 0),
    TrigramId.GEN: (0, 0, 1),
    TrigramId.KUN: (0, 0, 0),
}


LINES_TO_TRIGRAM = {value: key for key, value in TRIGRAM_LINES.items()}


def line_state_from_binary(binary_value: int, moving: bool = False) -> LineState:
    if binary_value not in {0, 1}:
        raise ValueError(f"invalid binary line: {binary_value}")
    if binary_value == 1:
        return LineState.OLD_YANG if moving else LineState.YOUNG_YANG
    return LineState.OLD_YIN if moving else LineState.YOUNG_YIN


def trigram_from_number(value: int) -> TrigramId:
    if value <= 0:
        raise ValueError(f"trigram number must be positive, got {value}")
    normalized = value % 8
    return TRIGRAM_NUMBER_MAP[normalized or 8]


def line_position_from_number(value: int) -> int:
    if value <= 0:
        raise ValueError(f"line position number must be positive, got {value}")
    normalized = value % 6
    return normalized or 6


def trigram_from_lines(lines: tuple[int, int, int]) -> TrigramId:
    try:
        return LINES_TO_TRIGRAM[lines]
    except KeyError as exc:
        raise ValueError(f"unknown trigram lines: {lines}") from exc


def changed_lines(lines: tuple[LineState, ...]) -> tuple[LineState, ...]:
    return tuple(line.changed for line in lines)


def binary_lines(lines: tuple[LineState, ...]) -> tuple[int, ...]:
    return tuple(1 if line.is_yang else 0 for line in lines)


def mutual_binary_lines(lines: tuple[LineState, ...]) -> tuple[int, ...]:
    binary = binary_lines(lines)
    return binary[1:4] + binary[2:5]


def body_use_from_moving_line(moving_line: int) -> tuple[str, str]:
    if moving_line < 1 or moving_line > 6:
        raise ValueError("moving line must be between 1 and 6")
    if moving_line <= 3:
        return ("upper", "lower")
    return ("lower", "upper")


def relation_key(body: Element, use: Element) -> str:
    if body == use:
        return "same"
    if GENERATION_ORDER[body] == use:
        return "body_generates_use"
    if GENERATION_ORDER[use] == body:
        return "use_generates_body"
    if CONTROL_ORDER[body] == use:
        return "body_controls_use"
    if CONTROL_ORDER[use] == body:
        return "use_controls_body"
    raise ValueError(f"unsupported element relation: {body} -> {use}")


def make_session_id() -> str:
    return uuid4().hex[:12]
