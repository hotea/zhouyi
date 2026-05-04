from __future__ import annotations

from typing import Protocol

from zhouyi.domain.models import CastRequest, CastResult


class CastingMethod(Protocol):
    method_id: str
    version: str

    def cast(self, request: CastRequest) -> CastResult: ...
