from __future__ import annotations

from zhouyi.domain.models import CastResult
from zhouyi.domain.services import body_use_from_moving_line, relation_key
from zhouyi.infra.i18n import t, tx
from zhouyi.infra.repository import DataRepository


def _determine_body_use(changing_lines: tuple[int, ...]) -> tuple[str, str]:
    if not changing_lines:
        return ("lower", "upper")
    lower_count = sum(1 for line in changing_lines if line <= 3)
    upper_count = sum(1 for line in changing_lines if line >= 4)
    if lower_count > upper_count:
        return ("upper", "lower")
    if upper_count > lower_count:
        return ("lower", "upper")
    return body_use_from_moving_line(changing_lines[-1])


def analyze_body_use(
    result: CastResult, repository: DataRepository, language: str = "zh"
) -> dict[str, object]:
    if not result.changing_lines:
        moving_line = None
        body_side, use_side = "lower", "upper"
    else:
        moving_line = result.changing_lines[0]
        body_side, use_side = _determine_body_use(result.changing_lines)

    body_trigram = (
        result.primary_hexagram.upper_trigram
        if body_side == "upper"
        else result.primary_hexagram.lower_trigram
    )
    use_trigram = (
        result.primary_hexagram.upper_trigram
        if use_side == "upper"
        else result.primary_hexagram.lower_trigram
    )
    body_info = repository.get_trigram(body_trigram)
    use_info = repository.get_trigram(use_trigram)
    key = relation_key(body_info.element, use_info.element)

    return {
        "moving_line": moving_line,
        "moving_count": len(result.changing_lines),
        "hexagram_editorial": repository.chinese_editorial(
            result.primary_hexagram.king_wen_index
        )
        if language == "zh"
        else result.primary_hexagram.display_summary(language),
        "body_side": body_side,
        "use_side": use_side,
        "body_side_label": t(language, f"body_side_{body_side}"),
        "use_side_label": t(language, f"body_side_{use_side}"),
        "body_trigram": {
            **body_info.to_dict(),
            "display_name": body_info.display_name(language),
            "display_image": body_info.display_image(language),
        },
        "use_trigram": {
            **use_info.to_dict(),
            "display_name": use_info.display_name(language),
            "display_image": use_info.display_image(language),
        },
        "relation": key,
        "relation_text": repository.meihua_rules[key]
        if language == "zh"
        else tx(language, key),
    }
