from __future__ import annotations

from datetime import datetime

from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.domain.services import (
    line_position_from_number,
    trigram_from_number,
)
from zhouyi.infra.calendar import resolve_calendar_point
from zhouyi.infra.repository import DataRepository
from zhouyi.methods.common import FinalizeResultParams, build_meihua_lines, finalize_result


class MeihuaTimeMethod:
    method_id = "meihua-time"
    version = "meihua_time_v1"

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def cast(self, request: CastRequest) -> CastResult:
        dt = request.datetime_value or datetime.now().astimezone()
        explicit_hour = request.extras.get("hour")
        point = resolve_calendar_point(dt, request.calendar_mode, explicit_hour)
        upper_sum = point.year + point.month + point.day
        lower_sum = upper_sum + point.hour
        moving_sum = lower_sum
        upper = trigram_from_number(upper_sum)
        lower = trigram_from_number(lower_sum)
        moving_line = line_position_from_number(moving_sum)
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
                        "type": "meihua-time",
                        "calendar": point.label,
                        "year": point.year,
                        "month": point.month,
                        "day": point.day,
                        "hour": point.hour,
                        "upper_sum": upper_sum,
                        "lower_sum": lower_sum,
                        "moving_sum": moving_sum,
                        "upper_trigram": upper.value,
                        "lower_trigram": lower.value,
                        "moving_line": moving_line,
                    }
                ],
                raw_inputs={
                    "datetime": dt.isoformat(),
                    "calendar_mode": request.calendar_mode.value,
                    "hour": explicit_hour,
                },
                raw_derivation={
                    "calendar_point": {
                        "year": point.year,
                        "month": point.month,
                        "day": point.day,
                        "hour": point.hour,
                        "label": point.label,
                    }
                },
                created_at=dt if dt.tzinfo else dt.astimezone(),
            )
        )
