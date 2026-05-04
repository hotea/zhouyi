from __future__ import annotations

from zhouyi.domain.enums import LineState
from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.infra.repository import DataRepository
from zhouyi.infra.rng import build_random
from zhouyi.methods.common import FinalizeResultParams, finalize_result


class CoinMethod:
    method_id = "coin"
    version = "coin_three_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        randomizer = build_random(request.seed)
        lines: list[LineState] = []
        steps: list[dict[str, object]] = []
        for line_no in range(1, 7):
            tosses = [randomizer.choice([2, 3]) for _ in range(3)]
            total = sum(tosses)
            line = {
                6: LineState.OLD_YIN,
                7: LineState.YOUNG_YANG,
                8: LineState.YOUNG_YIN,
                9: LineState.OLD_YANG,
            }[total]
            lines.append(line)
            steps.append(
                {
                    "line_no": line_no,
                    "tosses": tosses,
                    "total": total,
                    "line_state": int(line),
                }
            )

        return finalize_result(
            FinalizeResultParams(
                repository=self.repository,
                request=request,
                method_id=self.method_id,
                method_version=self.version,
                lines=tuple(lines),
                steps=steps,
                raw_inputs={"seed": request.seed},
                raw_derivation={"mode": "three-coins"},
            )
        )
