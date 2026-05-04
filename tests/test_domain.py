from zhouyi.domain.enums import Element, LineState, TrigramId
from zhouyi.domain.services import (
    body_use_from_moving_line,
    changed_lines,
    line_position_from_number,
    relation_key,
    trigram_from_number,
)


def test_trigram_mapping_matches_meihua_numbers() -> None:
    assert trigram_from_number(1) == TrigramId.QIAN
    assert trigram_from_number(8) == TrigramId.KUN
    assert trigram_from_number(16) == TrigramId.KUN


def test_line_position_uses_mod_six() -> None:
    assert line_position_from_number(6) == 6
    assert line_position_from_number(7) == 1


def test_changed_lines_only_flips_moving_lines() -> None:
    lines = (
        LineState.OLD_YIN,
        LineState.YOUNG_YANG,
        LineState.YOUNG_YIN,
        LineState.OLD_YANG,
        LineState.YOUNG_YIN,
        LineState.YOUNG_YANG,
    )
    assert changed_lines(lines) == (
        LineState.YOUNG_YANG,
        LineState.YOUNG_YANG,
        LineState.YOUNG_YIN,
        LineState.YOUNG_YIN,
        LineState.YOUNG_YIN,
        LineState.YOUNG_YANG,
    )


def test_body_use_rule_depends_on_first_moving_line() -> None:
    assert body_use_from_moving_line(2) == ("upper", "lower")
    assert body_use_from_moving_line(5) == ("lower", "upper")


def test_five_element_relation() -> None:
    assert relation_key(Element.WOOD, Element.FIRE) == "body_generates_use"
    assert relation_key(Element.METAL, Element.WOOD) == "body_controls_use"
