from __future__ import annotations

from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.domain.services import (
    line_position_from_number,
    trigram_from_number,
)
from zhouyi.infra.repository import DataRepository
from zhouyi.methods.common import FinalizeResultParams, build_meihua_lines, finalize_result


class MeihuaWordMethod:
    method_id = "meihua-word"
    version = "meihua_word_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        if not request.raw_text:
            raise ValueError("meihua-word requires text input")

        text = "".join(request.raw_text.split())
        count = len(text)
        if count == 0:
            raise ValueError("text must not be empty")

        midpoint = count // 2
        if count % 2 == 0:
            upper_count = midpoint
            lower_count = midpoint
            split_mode = "equal"
        else:
            upper_count = midpoint
            lower_count = count - midpoint
            split_mode = "less-upper-more-lower"

        upper = trigram_from_number(upper_count or count)
        lower = trigram_from_number(lower_count or count)
        moving_line = line_position_from_number(count)
        lines = build_meihua_lines(self.repository, upper, lower, moving_line)

        return finalize_result(
            FinalizeResultParams(
                repository=self.repository,
                request=request,
                method_id=self.method_id,
                method_version=self.version,
                lines=lines,
                steps=[
                    {
                        "type": "meihua-word",
                        "text": text,
                        "character_count": count,
                        "split_mode": split_mode,
                        "upper_count": upper_count,
                        "lower_count": lower_count,
                        "upper_trigram": upper.value,
                        "lower_trigram": lower.value,
                        "moving_line": moving_line,
                    }
                ],
                raw_inputs={"text": text},
                raw_derivation={"character_count": count},
            )
        )
