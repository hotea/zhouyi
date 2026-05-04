from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from zhouyi.domain.enums import CalendarMode, LineState, TrigramId
from zhouyi.domain.models import CastRequest, CastResult
from zhouyi.domain.services import (
    changed_lines,
    line_state_from_binary,
    make_session_id,
    mutual_binary_lines,
)
from zhouyi.infra.calendar import normalize_hour_input
from zhouyi.infra.repository import DataRepository


@dataclass
class FinalizeResultParams:
    repository: DataRepository
    request: CastRequest
    method_id: str
    method_version: str
    lines: tuple[LineState, ...]
    steps: list[dict[str, object]]
    raw_inputs: dict[str, object]
    raw_derivation: dict[str, object]
    created_at: datetime | None = None


def finalize_result(params: FinalizeResultParams) -> CastResult:
    now = params.created_at or datetime.now().astimezone()
    primary = params.repository.build_hexagram_from_lines(params.lines)
    relating_lines = changed_lines(params.lines)
    relating = (
        params.repository.build_hexagram_from_lines(relating_lines)
        if primary.changing_lines
        else None
    )
    mutual_binary = mutual_binary_lines(params.lines)
    mutual = params.repository.build_hexagram_from_lines(
        tuple(line_state_from_binary(bit) for bit in mutual_binary)
    )
    return CastResult(
        session_id=make_session_id(),
        question=params.request.question,
        method_id=params.method_id,
        method_version=params.method_version,
        created_at=now,
        timezone=str(now.tzinfo),
        calendar_mode=params.request.calendar_mode
        if isinstance(params.request.calendar_mode, CalendarMode)
        else None,
        seed=params.request.seed,
        primary_hexagram=primary,
        relating_hexagram=relating,
        mutual_hexagram=mutual,
        changing_lines=primary.changing_lines,
        steps=params.steps,
        raw_inputs=params.raw_inputs,
        raw_derivation=params.raw_derivation,
        provenance={"request": params.request.to_dict()},
    )


def build_meihua_lines(
    repository: DataRepository,
    upper: TrigramId,
    lower: TrigramId,
    moving_line: int,
) -> tuple[LineState, ...]:
    binary = (
        repository.get_trigram(lower).lines
        + repository.get_trigram(upper).lines
    )
    return tuple(
        line_state_from_binary(bit, idx == moving_line)
        for idx, bit in enumerate(binary, start=1)
    )


def resolve_meihua_datetime(request: CastRequest) -> datetime:
    dt = request.datetime_value or datetime.now().astimezone()
    return dt if dt.tzinfo else dt.astimezone()


def resolve_meihua_hour(request: CastRequest, dt: datetime) -> int:
    raw = request.extras.get("hour")
    if isinstance(raw, (int, float)):
        raw = int(raw)
    elif raw is not None:
        raw = str(raw)
    return normalize_hour_input(raw, dt)
