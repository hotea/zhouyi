from __future__ import annotations

import random
from datetime import datetime

from zhouyi.domain.enums import LineState
from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.domain.services import (
    changed_lines,
    line_state_from_binary,
    make_session_id,
    mutual_binary_lines,
)
from zhouyi.infra.repository import DataRepository
from zhouyi.infra.rng import build_random

YAO_MAP = {9: LineState.OLD_YANG, 8: LineState.YOUNG_YIN, 7: LineState.YOUNG_YANG, 6: LineState.OLD_YIN}


def _she_remainder(count: int) -> int:
    return (count - 1) % 4 + 1


class DayanZhuXiMethod:
    method_id = "dayan"
    version = "dayan_zhu_xi_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        rng = build_random(request.seed)
        lines: list[LineState] = []
        steps: list[dict[str, object]] = []
        for line_no in range(1, 7):
            line_value, line_steps = self._generate_line(rng)
            lines.append(line_value)
            if request.show_steps:
                steps.append({"line_no": line_no, **line_steps})
            else:
                steps.append({"line_no": line_no, "line_value": line_value})
        primary = self.repository.build_hexagram_from_lines(tuple(lines))
        relating_lines = changed_lines(tuple(lines))
        relating = (
            self.repository.build_hexagram_from_lines(relating_lines)
            if primary.changing_lines
            else None
        )
        mutual_binary = mutual_binary_lines(tuple(lines))
        mutual = self.repository.build_hexagram_from_lines(
            tuple(line_state_from_binary(bit) for bit in mutual_binary)
        )
        now = datetime.now().astimezone()
        return CastResult(
            session_id=make_session_id(),
            question=request.question,
            method_id=self.method_id,
            method_version=self.version,
            created_at=now,
            timezone=str(now.tzinfo),
            calendar_mode=None,
            seed=request.seed,
            primary_hexagram=primary,
            relating_hexagram=relating,
            mutual_hexagram=mutual,
            changing_lines=primary.changing_lines,
            steps=steps,
            raw_inputs={"seed": request.seed},
            raw_derivation={"total_steps": len(steps)},
            provenance={"request": request.to_dict()},
        )

    def _generate_line(self, rng: random.Random) -> tuple[LineState, dict[str, object]]:
        sticks = 49
        bian_steps: list[dict[str, object]] = []
        for bian_no in range(1, 4):
            left_total = rng.randint(1, sticks - 1)
            right_total = sticks - left_total
            guayi = 1
            right_after_guayi = right_total - guayi
            left_rem = _she_remainder(left_total)
            right_rem = _she_remainder(right_after_guayi)
            remainder = guayi + left_rem + right_rem
            sticks -= remainder
            bian_steps.append(
                {
                    "bian_no": bian_no,
                    "left_total": left_total,
                    "right_total": right_total,
                    "guayi": guayi,
                    "left_rem": left_rem,
                    "right_rem": right_rem,
                    "remainder": remainder,
                    "remaining": sticks,
                }
            )
        yao_value = sticks // 4
        line_value = YAO_MAP[yao_value]
        return line_value, {"line_value": line_value, "yao": yao_value, "steps": bian_steps}
