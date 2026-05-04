from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from pathlib import Path

from zhouyi.domain.models import CastResult, Interpretation

logger = logging.getLogger("zhouyi")

_SESSION_ID_PATTERN = re.compile(r"^[a-f0-9]{12}$")


class SessionStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        configured = os.environ.get("ZHOUYI_SESSION_DIR")
        self.base_dir = (
            base_dir or Path(configured)
            if configured
            else (base_dir or (Path.home() / ".zhouyi-cli" / "sessions"))
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _validate_session_id(self, session_id: str) -> None:
        if not _SESSION_ID_PATTERN.match(session_id):
            raise ValueError(f"invalid session id format: {session_id}")

    def session_path(self, session_id: str) -> Path:
        self._validate_session_id(session_id)
        return self.base_dir / f"{session_id}.json"

    def resolve_session_ref(self, session_ref: str) -> str:
        normalized = session_ref.strip()
        if normalized == "latest":
            recent = self.list_recent(1)
            if not recent:
                raise ValueError("no saved sessions found")
            return str(recent[0]["session_id"])
        self._validate_session_id(normalized)
        exact = self.session_path(normalized)
        if exact.exists():
            return normalized
        matches = sorted(self.base_dir.glob(f"{normalized}*.json"))
        if len(matches) == 1:
            return matches[0].stem
        if len(matches) > 1:
            raise ValueError(f"session prefix is ambiguous: {session_ref}")
        raise ValueError(f"session not found: {session_ref}")

    def save(
        self, result: CastResult, interpretation: Interpretation | None = None
    ) -> Path:
        payload = {
            "cast_result": result.to_dict(),
            "interpretation": interpretation.to_dict() if interpretation else None,
        }
        path = self.session_path(result.session_id)
        fd, tmp_path = tempfile.mkstemp(
            dir=self.base_dir, suffix=".json.tmp", prefix=result.session_id
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return path

    def load_raw(self, session_ref: str) -> dict[str, object]:
        path = self.session_path(self.resolve_session_ref(session_ref))
        return json.loads(path.read_text(encoding="utf-8"))

    def list_recent(
        self, limit: int = 10, offset: int = 0
    ) -> list[dict[str, object]]:
        items = sorted(
            self.base_dir.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        result: list[dict[str, object]] = []
        for path in items[offset : offset + limit]:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                cast_result = payload["cast_result"]
                result.append(
                    {
                        "session_id": cast_result["session_id"],
                        "created_at": cast_result["created_at"],
                        "method_id": cast_result["method_id"],
                        "hexagram": cast_result["primary_hexagram"]["name_zh"],
                        "hexagram_index": cast_result["primary_hexagram"]["king_wen_index"],
                        "question": cast_result.get("question"),
                    }
                )
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                logger.warning("skipping corrupted session file %s: %s", path, exc)
        return result
