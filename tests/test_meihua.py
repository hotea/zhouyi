from datetime import datetime

from zhouyi.domain.enums import CalendarMode
from zhouyi.domain.models import CastRequest
from zhouyi.infra.repository import DataRepository
from zhouyi.interpret.pipeline import InterpretationPipeline
from zhouyi.methods.meihua_number import MeihuaNumberMethod
from zhouyi.methods.meihua_sound import MeihuaSoundMethod
from zhouyi.methods.meihua_time import MeihuaTimeMethod
from zhouyi.methods.meihua_word import MeihuaWordMethod


def test_meihua_number_two_number_mode() -> None:
    repo = DataRepository()
    result = MeihuaNumberMethod(repo).cast(CastRequest(raw_numbers=(3, 5)))
    assert result.primary_hexagram.upper_trigram.value == "li"
    assert result.primary_hexagram.lower_trigram.value == "xun"
    assert result.changing_lines == (2,)


def test_meihua_time_uses_year_month_day_hour_rule() -> None:
    repo = DataRepository()
    result = MeihuaTimeMethod(repo).cast(
        CastRequest(
            datetime_value=datetime.fromisoformat("2026-03-31T21:30:00+08:00"),
            calendar_mode=CalendarMode.CIVIL_SIMPLIFIED,
        )
    )
    step = result.steps[0]
    assert step["upper_sum"] == 2060
    assert step["hour"] == 12
    assert step["lower_sum"] == 2072
    assert step["moving_line"] == 2


def test_meihua_sound_sentence_can_supply_count() -> None:
    repo = DataRepository()
    result = MeihuaSoundMethod(repo).cast(
        CastRequest(raw_text="今日动静如何", extras={"count": None, "hour": "you"})
    )
    assert result.primary_hexagram.king_wen_index > 0
    assert len(result.steps) == 1


def test_meihua_word_uses_character_count() -> None:
    repo = DataRepository()
    result = MeihuaWordMethod(repo).cast(CastRequest(raw_text="今日动静如何"))
    assert result.steps[0]["character_count"] == 6
    assert result.changing_lines == (6,)


def test_summary_does_not_duplicate_terminal_punctuation() -> None:
    repo = DataRepository()
    result = MeihuaNumberMethod(repo).cast(CastRequest(raw_numbers=(3, 5)))
    interpretation = InterpretationPipeline(repo).interpret(result)
    assert "。。" not in interpretation.plain_language_summary


def test_chinese_summary_uses_editorial_and_richer_moving_rule() -> None:
    repo = DataRepository()
    result = MeihuaNumberMethod(repo).cast(CastRequest(raw_numbers=(3, 5)))
    interpretation = InterpretationPipeline(repo).interpret(result, language="zh")
    assert "适合把散乱材料炼成可用成果" in interpretation.plain_language_summary
    assert "一爻发动" in interpretation.method_specific_analysis["moving_line_rule"]
