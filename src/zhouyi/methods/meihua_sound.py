from __future__ import annotations

from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.domain.services import line_position_from_number, trigram_from_number
from zhouyi.infra.repository import DataRepository
from zhouyi.methods.common import (
    FinalizeResultParams,
    build_meihua_lines,
    finalize_result,
    resolve_meihua_datetime,
    resolve_meihua_hour,
)


class MeihuaSoundMethod:
    method_id = "meihua-sound"
    version = "meihua_sound_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        dt = resolve_meihua_datetime(request)
        raw_count = request.extras.get("count")
        count = (
            int(raw_count)
            if raw_count is not None
            else len("".join((request.raw_text or "").split()))
        )
        if count <= 0:
            raise ValueError("meihua-sound requires --count or non-empty --sentence")
        hour = resolve_meihua_hour(request, dt)
        upper = trigram_from_number(count)
        lower = trigram_from_number(count + hour)
        moving_line = line_position_from_number(count + hour)
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
                        "type": "meihua-sound",
                        "count": count,
                        "hour": hour,
                        "upper_trigram": upper.value,
                        "lower_trigram": lower.value,
                        "moving_line": moving_line,
                    }
                ],
                raw_inputs={"count": count, "hour": request.extras.get("hour")},
                raw_derivation={"sentence": request.raw_text},
                created_at=dt,
            )
        )
