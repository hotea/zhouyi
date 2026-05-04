from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from lunardate import LunarDate

from zhouyi.domain.enums import CalendarMode


EARTHLY_BRANCH_HOURS = {
    "zi": 1,
    "chou": 2,
    "yin": 3,
    "mao": 4,
    "chen": 5,
    "si": 6,
    "wu": 7,
    "wei": 8,
    "shen": 9,
    "you": 10,
    "xu": 11,
    "hai": 12,
}


@dataclass(slots=True, frozen=True)
class CalendarPoint:
    year: int
    month: int
    day: int
    hour: int
    label: str
    is_leap_month: bool = False


def branch_hour_from_datetime(value: datetime) -> int:
    hour = value.hour
    if hour == 23 or hour < 1:
        return 1
    return ((hour + 1) // 2) + 1


def normalize_hour_input(value: str | int | None, dt: datetime) -> int:
    if value is None:
        return branch_hour_from_datetime(dt)
    if isinstance(value, int):
        if 1 <= value <= 12:
            return value
        raise ValueError("hour must be between 1 and 12")
    lowered = value.strip().lower()
    try:
        return EARTHLY_BRANCH_HOURS[lowered]
    except KeyError as exc:
        raise ValueError(f"unsupported earthly branch hour: {value}") from exc


def resolve_calendar_point(
    dt: datetime,
    mode: CalendarMode,
    explicit_hour: str | int | None = None,
) -> CalendarPoint:
    if mode == CalendarMode.CIVIL_SIMPLIFIED:
        hour = normalize_hour_input(explicit_hour, dt)
        return CalendarPoint(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=hour,
            label="civil-simplified",
        )

    lunar = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
    hour = normalize_hour_input(explicit_hour, dt)
    return CalendarPoint(
        year=lunar.year,
        month=lunar.month,
        day=lunar.day,
        hour=hour,
        label="classical-lunisolar",
        is_leap_month=getattr(lunar, "isLeapMonth", False),
    )
