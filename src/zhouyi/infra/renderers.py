from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from zhouyi.domain.models import CastResult, Hexagram, Interpretation, _dump_value
from zhouyi.infra.i18n import t


def _line_glyph(value: int) -> str:
    if value in {7, 9}:
        return "_________ o" if value == 9 else "_________"
    return "___   ___ x" if value == 6 else "___   ___"


def _hexagram_visual(hexagram: Hexagram) -> str:
    rows = [_line_glyph(int(line)) for line in reversed(hexagram.lines)]
    return "\n".join(rows)


def _trigram_label(value: str, language: str = "zh") -> str:
    return value.capitalize() if language == "en" else value


def hexagram_table(hexagram: Hexagram, title: str, language: str = "zh") -> Table:
    table = Table(title=title)
    table.add_column(t(language, "item"))
    table.add_column(t(language, "value"))
    table.add_row(
        t(language, "hexagram"),
        f"#{hexagram.king_wen_index} {hexagram.display_name(language)} {hexagram.unicode_symbol}"
        if language == "en"
        else f"第{hexagram.king_wen_index}卦 {hexagram.display_name(language)} {hexagram.unicode_symbol}",
    )
    table.add_row(
        t(language, "upper_trigram"),
        _trigram_label(hexagram.upper_trigram.value, language),
    )
    table.add_row(
        t(language, "lower_trigram"),
        _trigram_label(hexagram.lower_trigram.value, language),
    )
    table.add_row(
        t(language, "line"), " ".join(str(int(line)) for line in hexagram.lines)
    )
    table.add_row(
        t(language, "changing_lines"),
        ("、".join(str(line) for line in hexagram.changing_lines)
         if language == "zh"
         else ", ".join(str(line) for line in hexagram.changing_lines))
        or t(language, "no"),
    )
    table.add_row(t(language, "image"), _hexagram_visual(hexagram))
    return table


def render_cast(
    console: Console,
    result: CastResult,
    interpretation: Interpretation | None,
    show_steps: bool = False,
    language: str = "zh",
) -> None:
    console.print(
        hexagram_table(
            result.primary_hexagram, t(language, "primary_hexagram"), language
        )
    )
    if result.relating_hexagram:
        console.print(
            hexagram_table(
                result.relating_hexagram, t(language, "relating_hexagram"), language
            )
        )
    if result.mutual_hexagram:
        console.print(
            hexagram_table(
                result.mutual_hexagram, t(language, "mutual_hexagram"), language
            )
        )

    meta = Table(title=t(language, "session"))
    meta.add_column(t(language, "item"))
    meta.add_column(t(language, "value"))
    meta.add_row("session", result.session_id)
    meta.add_row(t(language, "method"), f"{result.method_id} ({result.method_version})")
    meta.add_row(t(language, "question"), result.question or "-")
    meta.add_row(
        t(language, "seed"), str(result.seed) if result.seed is not None else "-"
    )
    console.print(meta)

    if interpretation:
        console.print(
            Panel.fit(
                interpretation.plain_language_summary, title=t(language, "summary")
            )
        )
        primary = interpretation.primary_texts.get("hexagram", {})
        if primary.get("judgment") or primary.get("image") or primary.get("tuan"):
            text = "\n".join(
                part
                for part in [
                    str(primary.get("judgment") or ""),
                    str(primary.get("tuan") or ""),
                    str(primary.get("image") or ""),
                ]
                if part
            )
            console.print(Panel.fit(text, title=t(language, "classic_texts")))
        if interpretation.line_texts:
            focused = Table(title=t(language, "selected_texts"))
            focused.add_column(t(language, "line"))
            focused.add_column(t(language, "value"))
            focused.add_column(t(language, "line_image"))
            for item in interpretation.line_texts:
                focused.add_row(
                    str(item["line"]), str(item["text"]), str(item.get("image") or "-")
                )
            console.print(focused)
        body_use = interpretation.body_use_analysis
        body_table = Table(title=t(language, "body_use"))
        body_table.add_column(t(language, "item"))
        body_table.add_column(t(language, "value"))
        body_table.add_row(
            t(language, "body"),
            f"{body_use['body_trigram']['display_name']} ({body_use['body_side_label']})",
        )
        body_table.add_row(
            t(language, "use"),
            f"{body_use['use_trigram']['display_name']} ({body_use['use_side_label']})",
        )
        body_table.add_row(t(language, "relation"), str(body_use["relation_text"]))
        console.print(body_table)

    if show_steps:
        console.print_json(json.dumps(_dump_value(result.steps), ensure_ascii=False))


def render_methods(
    console: Console, methods: list[dict[str, str]], language: str = "zh"
) -> None:
    table = Table(title=t(language, "methods"))
    table.add_column("ID")
    table.add_column("Version")
    table.add_column("Description")
    for item in methods:
        table.add_row(item["id"], item["version"], item["description"])
    console.print(table)


def render_lookup_hexagram(
    console: Console, hexagram: Hexagram, language: str = "zh"
) -> None:
    console.print(hexagram_table(hexagram, t(language, "hexagram"), language))
    console.print(
        Panel.fit(hexagram.display_summary(language), title=t(language, "summary"))
    )


def render_config(
    console: Console, config: dict[str, object], language: str = "zh"
) -> None:
    table = Table(title=t(language, "config"))
    table.add_column("Key")
    table.add_column("Value")
    for key, value in config.items():
        table.add_row(str(key), str(value))
    console.print(table)


def render_lookup_trigram(
    console: Console, trigram: dict[str, object], language: str = "zh"
) -> None:
    table = Table(title=t(language, "trigram"))
    table.add_column(t(language, "item"))
    table.add_column(t(language, "value"))
    for key, value in trigram.items():
        table.add_row(
            str(key),
            json.dumps(value, ensure_ascii=False)
            if isinstance(value, (list, dict))
            else str(value),
        )
    console.print(table)


def render_sessions(
    console: Console, sessions: list[dict[str, object]], language: str = "zh"
) -> None:
    table = Table(title=t(language, "recent_sessions"))
    table.add_column(t(language, "session"))
    table.add_column(t(language, "created"))
    table.add_column(t(language, "method"))
    table.add_column(t(language, "hexagram"))
    table.add_column(t(language, "question"))
    for item in sessions:
        table.add_row(
            str(item["session_id"]),
            str(item["created_at"]),
            str(item["method_id"]),
            str(item["hexagram"]),
            str(item["question"] or "-"),
        )
    console.print(table)
