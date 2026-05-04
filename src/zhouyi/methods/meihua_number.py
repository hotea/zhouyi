from __future__ import annotations

from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.domain.services import (
    line_position_from_number,
    trigram_from_number,
)
from zhouyi.infra.repository import DataRepository
from zhouyi.methods.common import FinalizeResultParams, build_meihua_lines, finalize_result


class MeihuaNumberMethod:
    method_id = "meihua-number"
    version = "meihua_number_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        numbers = request.raw_numbers
        if len(numbers) not in {2, 3}:
            raise ValueError("meihua-number requires 2 or 3 numbers")

        upper_num, lower_num = numbers[0], numbers[1]
        moving_source = sum(numbers[:2]) if len(numbers) == 2 else numbers[2]
        upper = trigram_from_number(upper_num)
        lower = trigram_from_number(lower_num)
        moving_line = line_position_from_number(moving_source)
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
                        "type": "meihua-number",
                        "upper_number": upper_num,
                        "lower_number": lower_num,
                        "moving_source": moving_source,
                        "upper_trigram": upper.value,
                        "lower_trigram": lower.value,
                        "moving_line": moving_line,
                    }
                ],
                raw_inputs={"numbers": list(numbers)},
                raw_derivation={
                    "mode": "two-number" if len(numbers) == 2 else "three-number"
                },
            )
        )
