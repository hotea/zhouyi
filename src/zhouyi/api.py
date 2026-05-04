from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Path, Query

from zhouyi.app import ZhouyiApp
from zhouyi.api_models import (
    CasesResponseModel,
    CastPayloadModel,
    CastResponseModel,
    HealthResponse,
    HexagramResponseModel,
    MethodsResponseModel,
    ProfilesResponseModel,
    SessionDetailResponseModel,
    SessionsResponseModel,
)
from zhouyi.domain.models import CastRequest

api = FastAPI(title="Zhouyi API", version="0.2.0")

VALID_METHODS = {
    "dayan", "coin",
    "meihua-time", "meihua-number", "meihua-word",
    "meihua-sound", "meihua-object", "meihua-person", "meihua-static",
}


@lru_cache(maxsize=1)
def get_app() -> ZhouyiApp:
    return ZhouyiApp()


@api.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return {"status": "ok"}


@api.get("/methods", response_model=MethodsResponseModel)
def methods(
    lang: Literal["zh", "en"] = "zh", app: ZhouyiApp = Depends(get_app)
) -> MethodsResponseModel:
    language = app.resolve_language(lang)
    return {
        "language": language,
        "items": app.methods_info_localized(language),
        "field_schema": app.method_field_schema(language),
    }


@api.get("/profiles", response_model=ProfilesResponseModel)
def profiles(
    lang: Literal["zh", "en"] = "zh", app: ZhouyiApp = Depends(get_app)
) -> ProfilesResponseModel:
    language = app.resolve_language(lang)
    return {
        "language": language,
        "items": app.interpretation_profiles(language),
    }


@api.get("/hexagrams/{index}", response_model=HexagramResponseModel)
def hexagram(
    index: int = Path(ge=1, le=64),
    lang: Literal["zh", "en"] = "zh",
    app: ZhouyiApp = Depends(get_app),
) -> HexagramResponseModel:
    language = app.resolve_language(lang)
    hexagram = app.lookup_hexagram(index)
    return {
        "language": language,
        "hexagram": hexagram.to_dict(),
        "primary_texts": app.repository.get_primary_texts(hexagram, language),
    }


@api.post("/cast/{method_name}", response_model=CastResponseModel)
def cast(
    method_name: str, payload: CastPayloadModel, app: ZhouyiApp = Depends(get_app)
) -> CastResponseModel:
    if method_name not in VALID_METHODS:
        raise HTTPException(
            status_code=422,
            detail=f"invalid method: {method_name!r}, must be one of {sorted(VALID_METHODS)}",
        )
    language = app.resolve_language(payload.language)
    try:
        datetime_value = (
            datetime.fromisoformat(payload.datetime_value)
            if payload.datetime_value
            else None
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"invalid datetime: {exc}") from exc
    request = CastRequest(
        question=payload.question,
        datetime_value=datetime_value,
        raw_numbers=tuple(payload.raw_numbers),
        raw_text=payload.raw_text,
        seed=payload.seed,
        show_steps=payload.show_steps,
        extras=payload.extras,
    )
    try:
        result, interpretation = app.cast(
            method_name,
            request,
            save_session=payload.save_session,
            interpretation_profile=payload.interpretation_profile,
            language=language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "language": language,
        "meta": {
            "method": method_name,
            "profile": payload.interpretation_profile,
        },
        "cast_result": result.to_dict(),
        "interpretation": interpretation.to_dict(),
    }


@api.get("/sessions", response_model=SessionsResponseModel)
def sessions(
    limit: int = Query(default=10, ge=1, le=100),
    lang: Literal["zh", "en"] = "zh",
    app: ZhouyiApp = Depends(get_app),
) -> SessionsResponseModel:
    language = app.resolve_language(lang)
    return {
        "language": language,
        "items": app.recent_sessions_localized(limit, language),
    }


@api.get("/sessions/{session_id}", response_model=SessionDetailResponseModel)
def session_detail(
    session_id: str, lang: Literal["zh", "en"] = "zh", app: ZhouyiApp = Depends(get_app)
) -> SessionDetailResponseModel:
    language = app.resolve_language(lang)
    payload = app.explain_localized(session_id, language)
    return {"language": language, **payload}


@api.get("/cases", response_model=CasesResponseModel)
def cases(
    lang: Literal["zh", "en"] = "zh", app: ZhouyiApp = Depends(get_app)
) -> CasesResponseModel:
    language = app.resolve_language(lang)
    return {"language": language, "items": app.meihua_cases(language)}
