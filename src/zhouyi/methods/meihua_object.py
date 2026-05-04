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


OBJECT_TRIGRAM = {
    "flower": "dui",
    "flowering_plant": "xun",
    "tree": "zhen",
    "metal": "qian",
    "stone": "gen",
    "water": "kan",
    "book": "li",
    "earth": "kun",
}


class MeihuaObjectMethod:
    method_id = "meihua-object"
    version = "meihua_object_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        object_type = str(request.extras.get("object_type", "flower"))
        count = int(request.extras.get("count", 1))
        if object_type not in OBJECT_TRIGRAM:
            raise ValueError(f"unsupported object type: {object_type}")
        dt = resolve_meihua_datetime(request)
        hour = resolve_meihua_hour(request, dt)
        upper_num = count
        lower_num = count + hour
        upper = trigram_from_number(upper_num)
        lower = trigram_from_number(lower_num)
        moving_line = line_position_from_number(lower_num)
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
                        "type": "meihua-object",
                        "object_type": object_type,
                        "count": count,
                        "hour": hour,
                        "upper_trigram": upper.value,
                        "lower_trigram": lower.value,
                        "moving_line": moving_line,
                    }
                ],
                raw_inputs={
                    "object_type": object_type,
                    "count": count,
                    "hour": request.extras.get("hour"),
                },
                raw_derivation={"object_trigram": OBJECT_TRIGRAM[object_type]},
                created_at=dt,
            )
        )
