from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from zhouyi.domain.enums import CalendarMode, OutputFormat


@dataclass(slots=True)
class AppConfig:
    calendar_mode: CalendarMode = CalendarMode.CIVIL_SIMPLIFIED
    export_format: OutputFormat = OutputFormat.JSON
    auto_save_sessions: bool = True
    show_steps: bool = False
    language: str = "zh"

    def to_dict(self) -> dict[str, object]:
        return {
            "calendar_mode": self.calendar_mode.value,
            "export_format": self.export_format.value,
            "auto_save_sessions": self.auto_save_sessions,
            "show_steps": self.show_steps,
            "language": self.language,
        }


class ConfigStore:
    def __init__(self, config_path: Path | None = None) -> None:
        configured = os.environ.get("ZHOUYI_CONFIG_FILE")
        self.path = (
            Path(configured)
            if configured
            else (config_path or (Path.home() / ".zhouyi-cli" / "config.json"))
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return AppConfig(
            calendar_mode=CalendarMode(
                payload.get("calendar_mode", CalendarMode.CIVIL_SIMPLIFIED.value)
            ),
            export_format=OutputFormat(
                payload.get("export_format", OutputFormat.JSON.value)
            ),
            auto_save_sessions=bool(payload.get("auto_save_sessions", True)),
            show_steps=bool(payload.get("show_steps", False)),
            language=str(payload.get("language", "zh")),
        )

    def save(self, config: AppConfig) -> Path:
        self.path.write_text(
            json.dumps(config.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return self.path

    def init_default(self, force: bool = False) -> Path:
        if self.path.exists() and not force:
            raise ValueError(f"config already exists: {self.path}")
        return self.save(AppConfig())

    def update(self, key: str, value: str) -> AppConfig:
        config = self.load()
        normalized = key.strip().replace("_", "-").lower()
        if normalized == "calendar-mode":
            config.calendar_mode = CalendarMode(value)
        elif normalized == "export-format":
            config.export_format = OutputFormat(value)
        elif normalized == "auto-save-sessions":
            config.auto_save_sessions = value.strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
        elif normalized == "show-steps":
            config.show_steps = value.strip().lower() in {"1", "true", "yes", "on"}
        elif normalized == "language":
            if value not in {"zh", "en"}:
                raise ValueError("language must be 'zh' or 'en'")
            config.language = value
        else:
            raise ValueError(f"unsupported config key: {key}")
        self.save(config)
        return config
