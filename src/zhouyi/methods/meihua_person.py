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


PERSON_TRIGRAM = {
    "man": "qian",
    "woman": "kun",
    "elder": "gen",
    "child": "zhen",
    "official": "kan",
    "scholar": "li",
    "merchant": "dui",
    "farmer": "xun",
}


class MeihuaPersonMethod:
    method_id = "meihua-person"
    version = "meihua_person_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        person_type = str(request.extras.get("person_type", "man"))
        count = int(request.extras.get("count", 1))
        if person_type not in PERSON_TRIGRAM:
            raise ValueError(f"unsupported person type: {person_type}")
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
                        "type": "meihua-person",
                        "person_type": person_type,
                        "count": count,
                        "hour": hour,
                        "upper_trigram": upper.value,
                        "lower_trigram": lower.value,
                        "moving_line": moving_line,
                    }
                ],
                raw_inputs={
                    "person_type": person_type,
                    "count": count,
                    "hour": request.extras.get("hour"),
                },
                raw_derivation={"person_trigram": PERSON_TRIGRAM[person_type]},
                created_at=dt,
            )
        )
