from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from zhouyi.domain.enums import CalendarMode, LineState
from zhouyi.domain.models import CastRequest, CastResult, Hexagram, Interpretation
from zhouyi.infra.config import AppConfig, ConfigStore
from zhouyi.infra.repository import DataRepository
from zhouyi.infra.session_store import SessionStore
from zhouyi.interpret.pipeline import InterpretationPipeline
from zhouyi.methods.registry import build_method_registry

logger = logging.getLogger("zhouyi")


class ZhouyiApp:
    def __init__(
        self, session_dir: Path | None = None, config_path: Path | None = None
    ) -> None:
        self.repository = DataRepository()
        self.methods = build_method_registry(self.repository)
        self.interpreter = InterpretationPipeline(self.repository)
        self.sessions = SessionStore(session_dir)
        self.config_store = ConfigStore(config_path)
        self.config = self.config_store.load()

    def cast(
        self,
        method_name: str,
        request: CastRequest,
        save_session: bool | None = None,
        interpretation_profile: str = "balanced",
        language: str | None = None,
    ) -> tuple[CastResult, Interpretation]:
        logger.info("casting method=%s question=%s", method_name, request.question)
        method = self.methods.get(method_name)
        if method is None:
            raise ValueError(f"unknown method: {method_name!r}, available: {sorted(self.methods)}")
        result = method.cast(request)
        interpretation = self.interpreter.interpret(
            result,
            interpretation_profile,
            self.resolve_language(language),
        )
        should_save = (
            self.config.auto_save_sessions if save_session is None else save_session
        )
        if should_save:
            self.sessions.save(result, interpretation)
            logger.info("session saved: %s", result.session_id)
        return result, interpretation

    def methods_info(self) -> list[dict[str, str]]:
        return self.repository.list_methods_text()

    def methods_info_localized(self, language: str = "zh") -> list[dict[str, str]]:
        return self.repository.list_methods_text(language)

    def method_field_schema(
        self, language: str = "zh"
    ) -> dict[str, list[dict[str, str]]]:
        return self.repository.method_field_schema(language)

    def interpretation_profiles(self, language: str = "zh") -> list[dict[str, object]]:
        return self.repository.list_interpretation_profiles_text(language)

    def lookup_hexagram(self, index: int) -> Hexagram:
        return self.repository.get_hexagram_by_index(index)

    def lookup_trigram(self, trigram_name: str) -> dict[str, object]:
        return self.repository.get_trigram(
            self.repository.resolve_trigram_id(trigram_name)
        ).to_dict()

    def explain(self, session_id: str) -> dict[str, object]:
        return self.sessions.load_raw(session_id)

    def explain_localized(
        self, session_id: str, language: str = "zh"
    ) -> dict[str, object]:
        language = self.resolve_language(language)
        payload = self.explain(session_id)
        cast_result = self._cast_result_from_payload(payload["cast_result"])
        interpretation_payload = payload.get("interpretation") or {}
        profile_id = str(
            interpretation_payload.get("provenance", {}).get(
                "interpretation_profile", "balanced"
            )
        )
        interpretation = self.interpreter.interpret(cast_result, profile_id, language)
        return {
            "cast_result": cast_result.to_dict(),
            "interpretation": interpretation.to_dict(),
        }

    def recent_sessions(
        self, limit: int = 10, offset: int = 0
    ) -> list[dict[str, object]]:
        return self.sessions.list_recent(limit, offset)

    def recent_sessions_localized(
        self, limit: int = 10, language: str = "zh", offset: int = 0
    ) -> list[dict[str, object]]:
        language = self.resolve_language(language)
        items = self.recent_sessions(limit, offset)
        if language != "en":
            return items
        localized: list[dict[str, object]] = []
        for item in items:
            index = item.get("hexagram_index")
            name = item["hexagram"]
            if isinstance(index, int):
                name = self.lookup_hexagram(index).display_name(language)
            localized.append({**item, "hexagram": name})
        return localized

    def export(self, session_id: str, fmt: str, language: str | None = None) -> str:
        resolved_language = self.resolve_language(language)
        payload = self.explain_localized(session_id, resolved_language)
        if fmt == "json":
            return json.dumps(payload, ensure_ascii=False, indent=2)
        cast_result = payload["cast_result"]
        interpretation = payload.get("interpretation") or {}
        if fmt == "markdown":
            primary_name = (
                interpretation.get("primary_texts", {})
                .get("hexagram", {})
                .get("display_name", cast_result["primary_hexagram"]["name_zh"])
            )
            relating = interpretation.get("method_specific_analysis", {}).get(
                "relating_hexagram"
            )
            mutual = interpretation.get("method_specific_analysis", {}).get(
                "mutual_hexagram"
            )
            lines = [
                f"# {primary_name}",
                "",
                f"- Session: `{cast_result['session_id']}`",
                f"- Method: `{cast_result['method_id']}` / `{cast_result['method_version']}`",
                f"- Question: {cast_result['question'] or '-'}",
                f"- Primary: {'#' if resolved_language == 'en' else '第'}{cast_result['primary_hexagram']['king_wen_index']}{'' if resolved_language == 'en' else '卦'} {primary_name}",
                f"- Relating: {(relating or {}).get('name_en' if resolved_language == 'en' else 'name_zh', '-') if relating else '-'}",
                f"- Mutual: {(mutual or {}).get('name_en' if resolved_language == 'en' else 'name_zh', '-') if mutual else '-'}",
                "",
                "## Summary",
                "",
                interpretation.get("plain_language_summary", ""),
                "",
                "## Analysis",
                "",
                f"- Moving Rule: {interpretation.get('method_specific_analysis', {}).get('moving_line_rule', '-')}",
                f"- Body/Use: {interpretation.get('body_use_analysis', {}).get('relation_text', '-')}",
            ]
            return "\n".join(lines)
        raise ValueError(f"unsupported export format: {fmt}")

    def interpret_hexagram(
        self, index: int, line: int | None = None, language: str | None = None
    ) -> dict[str, object]:
        resolved_language = self.resolve_language(language)
        hexagram = self.lookup_hexagram(index)
        line_texts = (
            self.repository.get_line_texts(index, (line,), resolved_language)
            if line
            else []
        )
        return {
            "hexagram": hexagram.to_dict(),
            "primary_texts": self.repository.get_primary_texts(
                hexagram, resolved_language
            ),
            "line_texts": line_texts,
        }

    def config_view(self) -> dict[str, object]:
        return self.config.to_dict()

    def meihua_cases(self, language: str = "zh") -> list[dict[str, object]]:
        return self.repository.list_meihua_cases_text(language)

    def run_meihua_case(
        self, case_id: str, language: str | None = None
    ) -> dict[str, object]:
        resolved_language = self.resolve_language(language)
        case = next(
            (
                item
                for item in self.repository.list_meihua_cases()
                if item["case_id"] == case_id
            ),
            None,
        )
        if case is None:
            raise ValueError(f"unknown case: {case_id}")
        method = str(case["method"])
        data = case["input"]
        if method == "meihua-sound":
            request = CastRequest(
                extras={"count": data.get("count"), "hour": data.get("hour")}
            )
        elif method == "meihua-word":
            request = CastRequest(raw_text=str(data["text"]))
        else:
            request = CastRequest(extras=data)
        result, interpretation = self.cast(
            method,
            request,
            save_session=False,
            language=resolved_language,
        )
        return {
            "case": case,
            "cast_result": result.to_dict(),
            "interpretation": interpretation.to_dict(),
        }

    def _cast_result_from_payload(self, payload: dict[str, object]) -> CastResult:
        def build_hexagram(data: dict[str, object] | None):
            if data is None:
                return None
            return self.repository.build_hexagram_from_lines(
                tuple(LineState(value) for value in data["lines"])
            )

        result = CastResult(
            session_id=str(payload["session_id"]),
            question=payload.get("question"),
            method_id=str(payload["method_id"]),
            method_version=str(payload["method_version"]),
            created_at=datetime.fromisoformat(str(payload["created_at"])),
            timezone=str(payload["timezone"]),
            calendar_mode=CalendarMode(payload["calendar_mode"])
            if "calendar_mode" in payload and payload["calendar_mode"]
            else None,
            seed=payload.get("seed"),
            primary_hexagram=build_hexagram(payload["primary_hexagram"]),
            relating_hexagram=build_hexagram(payload.get("relating_hexagram")),
            mutual_hexagram=build_hexagram(payload.get("mutual_hexagram")),
            changing_lines=tuple(
                int(line) for line in payload.get("changing_lines", [])
            ),
            steps=list(payload.get("steps", [])),
            raw_inputs=dict(payload.get("raw_inputs", {})),
            raw_derivation=dict(payload.get("raw_derivation", {})),
            provenance=dict(payload.get("provenance", {})),
        )
        return result

    def config_init(self, force: bool = False) -> str:
        return str(self.config_store.init_default(force))

    def config_set(self, key: str, value: str) -> dict[str, object]:
        self.config = self.config_store.update(key, value)
        return self.config.to_dict()

    _CALENDAR_ALIASES: ClassVar[dict[str, str]] = {
        "lunar": "classical-lunisolar",
        "solar": "civil-simplified",
        "gregorian": "civil-simplified",
    }

    def resolve_calendar_mode(self, value: str | None) -> CalendarMode:
        if value is None:
            return self.config.calendar_mode
        mapped = self._CALENDAR_ALIASES.get(value, value)
        return CalendarMode(mapped)

    def resolve_export_format(self, value: str | None) -> str:
        return self.config.export_format.value if value is None else value

    def resolve_show_steps(self, value: bool | None) -> bool:
        return self.config.show_steps if value is None else value

    def resolve_language(self, value: str | None) -> str:
        if value is None:
            return self.config.language
        if value not in {"zh", "en"}:
            raise ValueError(f"language must be 'zh' or 'en', got: {value!r}")
        return value

    @staticmethod
    def calendar_mode(value: str) -> CalendarMode:
        return CalendarMode(value)
