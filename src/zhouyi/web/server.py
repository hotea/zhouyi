from __future__ import annotations

import hashlib
import secrets
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from zhouyi.app import ZhouyiApp
from zhouyi.domain.models import CastRequest
from zhouyi.infra.i18n import LABELS

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

web = FastAPI(title="Zhouyi Web", version="0.2.0")
web.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

VALID_WEB_METHODS = {
    "dayan", "coin",
    "meihua-time", "meihua-number", "meihua-word",
    "meihua-sound", "meihua-object", "meihua-person", "meihua-static",
}

CSRF_COOKIE_NAME = "zhouyi_csrf"
CSRF_SECRET = secrets.token_hex(32)


def _generate_csrf_token() -> str:
    return hashlib.sha256(CSRF_SECRET.encode()).hexdigest()[:32]


def _validate_csrf(request: Request, submitted: str) -> None:
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token or not submitted:
        raise HTTPException(status_code=403, detail="missing CSRF token")
    expected = _generate_csrf_token()
    if cookie_token != expected or submitted != expected:
        raise HTTPException(status_code=403, detail="invalid CSRF token")


@lru_cache(maxsize=1)
def _get_app() -> ZhouyiApp:
    return ZhouyiApp()


def _line_visual(line: int) -> dict[str, object]:
    return {
        "is_yang": line in {7, 9},
        "is_moving": line in {6, 9},
        "marker": "o" if line == 9 else ("x" if line == 6 else ""),
        "raw": line,
    }


def _line_visuals(lines: list[int]) -> list[dict[str, object]]:
    return [_line_visual(line) for line in reversed(lines)]


def _transition_rows(
    primary_lines: list[int], relating_lines: list[int] | None
) -> list[dict[str, object]] | None:
    if not relating_lines:
        return None
    rows: list[dict[str, object]] = []
    for line_number, (before, after) in zip(
        range(6, 0, -1),
        zip(reversed(primary_lines), reversed(relating_lines)),
        strict=False,
    ):
        rows.append(
            {
                "line": line_number,
                "before": _line_visual(before),
                "after": _line_visual(after),
                "changed": before != after,
            }
        )
    return rows


def _visualize_result(payload: dict[str, object]) -> dict[str, object]:
    cast_result = payload["cast_result"]
    return {
        "primary": _line_visuals(cast_result["primary_hexagram"]["lines"]),
        "relating": _line_visuals(cast_result["relating_hexagram"]["lines"])
        if cast_result.get("relating_hexagram")
        else None,
        "mutual": _line_visuals(cast_result["mutual_hexagram"]["lines"])
        if cast_result.get("mutual_hexagram")
        else None,
        "transition": _transition_rows(
            cast_result["primary_hexagram"]["lines"],
            cast_result["relating_hexagram"]["lines"]
            if cast_result.get("relating_hexagram")
            else None,
        ),
    }


def _parse_numbers(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split() if part.strip())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"invalid numbers: {exc}") from exc


def _parse_seed(value: str) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"invalid seed: {exc}") from exc


def _parse_count(value: str) -> int:
    if not value:
        return 1
    try:
        count = int(value)
        if count < 0:
            raise HTTPException(status_code=422, detail="count must be non-negative")
        return count
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"invalid count: {exc}") from exc


def _set_csrf_cookie(response: Response) -> str:
    token = _generate_csrf_token()
    response.set_cookie(CSRF_COOKIE_NAME, token, httponly=False, samesite="strict")
    return token


@web.get("/", response_class=HTMLResponse)
def home(request: Request, lang: str = "zh") -> HTMLResponse:
    app = _get_app()
    language = app.resolve_language(lang)
    csrf_token = _generate_csrf_token()
    response = templates.TemplateResponse(
        request,
        "index.html",
        {
            "lang": language,
            "labels": LABELS[language],
            "methods": app.methods_info_localized(language),
            "field_schema": app.method_field_schema(language),
            "profiles": app.interpretation_profiles(language),
            "sessions": app.recent_sessions_localized(6, language),
            "result": None,
            "visuals": None,
            "form": None,
            "csrf_token": csrf_token,
        },
    )
    response.set_cookie(CSRF_COOKIE_NAME, csrf_token, httponly=False, samesite="strict")
    return response


@web.post("/cast", response_class=HTMLResponse)
def cast(
    request: Request,
    method: str = Form(...),
    profile: str = Form("balanced"),
    question: str = Form(""),
    numbers: str = Form(""),
    text: str = Form(""),
    seed: str = Form(""),
    hour: str = Form(""),
    count: str = Form(""),
    object_type: str = Form("flower"),
    person_type: str = Form("merchant"),
    item_type: str = Form("stone"),
    lang: str = Form("zh"),
    csrf_token: str = Form(""),
) -> HTMLResponse:
    _validate_csrf(request, csrf_token)
    if method not in VALID_WEB_METHODS:
        raise HTTPException(status_code=422, detail=f"unsupported method: {method}")
    app = _get_app()
    language = app.resolve_language(lang)
    payload_question = question or None
    request_model = CastRequest(question=payload_question)
    if method == "meihua-number":
        request_model.raw_numbers = _parse_numbers(numbers)
    elif method == "meihua-word":
        request_model.raw_text = text or None
    elif method == "coin":
        request_model.seed = _parse_seed(seed)
    elif method == "meihua-object":
        request_model.extras = {
            "object_type": object_type,
            "count": _parse_count(count),
            "hour": hour or None,
        }
    elif method == "meihua-person":
        request_model.extras = {
            "person_type": person_type,
            "count": _parse_count(count),
            "hour": hour or None,
        }
    elif method == "meihua-static":
        request_model.extras = {
            "item_type": item_type,
            "count": _parse_count(count),
            "hour": hour or None,
        }
    elif method == "meihua-sound":
        request_model.raw_text = text or None
        request_model.extras = {
            "count": _parse_count(count),
            "hour": hour or None,
        }
    elif method == "meihua-time":
        request_model.extras = {
            "hour": hour or None,
        }
    elif method == "dayan":
        request_model.seed = _parse_seed(seed)

    try:
        result, interpretation = app.cast(
            method, request_model, interpretation_profile=profile, language=language
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    cast_result_dict = result.to_dict()
    interpretation_dict = interpretation.to_dict()
    new_csrf = _generate_csrf_token()
    response = templates.TemplateResponse(
        request,
        "index.html",
        {
            "lang": language,
            "labels": LABELS[language],
            "methods": app.methods_info_localized(language),
            "field_schema": app.method_field_schema(language),
            "profiles": app.interpretation_profiles(language),
            "sessions": app.recent_sessions_localized(6, language),
            "result": {
                "cast_result": cast_result_dict,
                "interpretation": interpretation_dict,
            },
            "visuals": _visualize_result(
                {
                    "cast_result": cast_result_dict,
                    "interpretation": interpretation_dict,
                }
            ),
            "form": {
                "method": method,
                "profile": profile,
                "question": question,
                "numbers": numbers,
                "text": text,
                "seed": seed,
                "hour": hour,
                "count": count,
                "object_type": object_type,
                "person_type": person_type,
                "item_type": item_type,
                "lang": language,
            },
            "csrf_token": new_csrf,
        },
    )
    response.set_cookie(CSRF_COOKIE_NAME, new_csrf, httponly=False, samesite="strict")
    return response


@web.get("/sessions/{session_id}", response_class=HTMLResponse)
def session_detail(request: Request, session_id: str, lang: str = "zh") -> HTMLResponse:
    app = _get_app()
    language = app.resolve_language(lang)
    payload = app.explain_localized(session_id, language)
    return templates.TemplateResponse(
        request,
        "session.html",
        {
            "lang": language,
            "labels": LABELS[language],
            "payload": payload,
            "visuals": _visualize_result(payload),
            "session_id": session_id,
        },
    )
