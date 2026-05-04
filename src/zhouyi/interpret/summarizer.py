from __future__ import annotations

from zhouyi.domain.models import CastResult
from zhouyi.infra.i18n import tx


def _trim_terminal_punctuation(text: str) -> str:
    return text.rstrip("。！？；，,.!?; ")


def _clean_selected_texts(selected_texts: list[str]) -> str:
    cleaned = [
        _trim_terminal_punctuation(text) for text in selected_texts if text.strip()
    ]
    return "; ".join(cleaned) if cleaned else ""


def summarize(
    result: CastResult,
    body_use_analysis: dict[str, object],
    decision_rule: str,
    selected_texts: list[str],
    language: str = "zh",
) -> str:
    spacer = " " if language == "en" else ""
    line_text = tx(language, "no_moving")
    if result.changing_lines:
        separator = ", " if language == "en" else "、"
        joined = separator.join(str(line) for line in result.changing_lines)
        line_text = tx(language, "moving_line_text").format(lines=joined)

    relating = tx(language, "no_relating")
    if result.relating_hexagram:
        relating = tx(language, "relating_text").format(
            index=result.relating_hexagram.king_wen_index,
            name=result.relating_hexagram.display_name(language),
        )

    focus = ""
    if selected_texts:
        focus = f"{tx(language, 'focus_prefix')}{_clean_selected_texts(selected_texts)}"

    summary = tx(language, "summary_text").format(
        index=result.primary_hexagram.king_wen_index,
        name=result.primary_hexagram.display_name(language),
        hexagram_editorial=_trim_terminal_punctuation(
            str(
                body_use_analysis.get(
                    "hexagram_editorial",
                    result.primary_hexagram.display_summary(language),
                )
            )
        ),
        line_text=f"{line_text}{spacer}",
        relating=f"{relating}{spacer}",
        decision_rule=decision_rule,
    )
    if focus:
        summary += f"{spacer}{focus}{'.' if language == 'en' else '。'}"
    summary += (" " if language == "en" else "") + tx(language, "body_use_text").format(
        relation_text=body_use_analysis["relation_text"]
    )
    return summary
