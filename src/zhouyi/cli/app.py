from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime

import click
import typer
from rich.console import Console
import uvicorn

from zhouyi.app import ZhouyiApp
from zhouyi.domain.enums import CalendarMode
from zhouyi.domain.models import CastRequest
from zhouyi.infra.renderers import (
    render_config,
    render_cast,
    render_lookup_hexagram,
    render_lookup_trigram,
    render_methods,
    render_sessions,
)

app = typer.Typer(
    help="Zhouyi CLI", no_args_is_help=True, pretty_exceptions_enable=False
)
cast_app = typer.Typer(
    help="Cast hexagrams", no_args_is_help=True, pretty_exceptions_enable=False
)
meihua_app = typer.Typer(
    help="Meihua casting methods", no_args_is_help=True, pretty_exceptions_enable=False
)
lookup_app = typer.Typer(
    help="Lookup classic data", no_args_is_help=True, pretty_exceptions_enable=False
)
config_app = typer.Typer(
    help="Manage config", no_args_is_help=True, pretty_exceptions_enable=False
)
console = Console()


def _service() -> ZhouyiApp:
    return ZhouyiApp()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _print_json(payload: object) -> None:
    console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))


def _run_action(action: Callable[[], None]) -> None:
    try:
        action()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def methods(
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        language = service.resolve_language(lang)
        data = service.methods_info_localized(language)
        if json_output:
            _print_json(data)
            return
        render_methods(console, data, language)

    _run_action(action)


@app.command()
def profiles(
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        language = service.resolve_language(lang)
        data = service.interpretation_profiles(language)
        if json_output:
            _print_json(data)
            return
        render_config(
            console,
            {item["profile_id"]: item["summary_style"] for item in data},
            language,
        )

    _run_action(action)


@app.command()
def cases(
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        language = service.resolve_language(lang)
        data = service.meihua_cases(language)
        if json_output:
            _print_json(data)
            return
        render_config(
            console,
            {item["case_id"]: item["title"] for item in data},
            language,
        )

    _run_action(action)


@app.command()
def case(
    case_id: str,
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        data = service.run_meihua_case(case_id, service.resolve_language(lang))
        if json_output:
            _print_json(data)
            return
        console.print(data["interpretation"]["plain_language_summary"])

    _run_action(action)


@app.command()
def serve_api(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8864, "--port"),
) -> None:
    def action() -> None:
        uvicorn.run("zhouyi.api:api", host=host, port=port, reload=False)

    _run_action(action)


@app.command()
def serve_web(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8864, "--port"),
) -> None:
    def action() -> None:
        uvicorn.run("zhouyi.web.server:web", host=host, port=port, reload=False)

    _run_action(action)


@app.command()
def tui(lang: str | None = typer.Option(None, "--lang")) -> None:
    def action() -> None:
        from zhouyi.tui import run_tui

        service = _service()
        run_tui(service.resolve_language(lang))

    _run_action(action)


@app.command()
def sessions(
    limit: int = typer.Option(10, "--limit", min=1, max=100),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        language = service.resolve_language(lang)
        data = service.recent_sessions_localized(limit, language)
        if json_output:
            _print_json(data)
            return
        render_sessions(console, data, language)

    _run_action(action)


@config_app.command("show")
def config_show(
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        data = service.config_view()
        if json_output:
            _print_json(data)
            return
        render_config(console, data, service.resolve_language(lang))

    _run_action(action)


@config_app.command("init")
def config_init(force: bool = typer.Option(False, "--force")) -> None:
    def action() -> None:
        service = _service()
        console.print(service.config_init(force))

    _run_action(action)


@config_app.command("set")
def config_set(
    key: str, value: str, lang: str | None = typer.Option(None, "--lang")
) -> None:
    def action() -> None:
        service = _service()
        render_config(
            console, service.config_set(key, value), service.resolve_language(lang)
        )

    _run_action(action)


@lookup_app.command("hexagram")
def lookup_hexagram(
    index: int = typer.Argument(min=1, max=64),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        hexagram = service.lookup_hexagram(index)
        if json_output:
            _print_json(hexagram.to_dict())
            return
        render_lookup_hexagram(console, hexagram, service.resolve_language(lang))

    _run_action(action)


@lookup_app.command("trigram")
def lookup_trigram(
    name: str,
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        trigram = service.lookup_trigram(name)
        if json_output:
            _print_json(trigram)
            return
        render_lookup_trigram(console, trigram, service.resolve_language(lang))

    _run_action(action)


@cast_app.command("dayan")
def cast_dayan(
    question: str | None = typer.Option(None, "--question"),
    seed: int | None = typer.Option(None, "--seed"),
    show_steps: bool | None = typer.Option(None, "--show-steps/--no-show-steps"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        resolved_show_steps = service.resolve_show_steps(show_steps)
        result, interpretation = service.cast(
            "dayan",
            CastRequest(question=question, seed=seed, show_steps=resolved_show_steps),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console,
            result,
            interpretation,
            show_steps=resolved_show_steps,
            language=service.resolve_language(lang),
        )

    _run_action(action)


@meihua_app.command("time")
def cast_meihua_time(
    datetime_value: str | None = typer.Option(None, "--datetime"),
    calendar: str | None = typer.Option(None, "--calendar"),
    hour: str | None = typer.Option(None, "--hour"),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-time",
            CastRequest(
                question=question,
                calendar_mode=service.resolve_calendar_mode(calendar),
                datetime_value=_parse_datetime(datetime_value),
                extras={"hour": hour},
            ),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@meihua_app.command("number")
def cast_meihua_number(
    numbers: list[int] = typer.Argument(...),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-number",
            CastRequest(question=question, raw_numbers=tuple(numbers)),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@meihua_app.command("sound")
def cast_meihua_sound(
    count: int | None = typer.Option(None, "--count"),
    hour: str | None = typer.Option(None, "--hour"),
    sentence: str | None = typer.Option(None, "--sentence"),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-sound",
            CastRequest(
                question=question,
                raw_text=sentence,
                extras={"count": count, "hour": hour},
            ),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@meihua_app.command("word")
def cast_meihua_word(
    text: str = typer.Argument(...),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-word",
            CastRequest(question=question, raw_text=text),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@cast_app.command("coin")
def cast_coin(
    question: str | None = typer.Option(None, "--question"),
    seed: int | None = typer.Option(None, "--seed"),
    show_steps: bool | None = typer.Option(None, "--show-steps/--no-show-steps"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        resolved_show_steps = service.resolve_show_steps(show_steps)
        result, interpretation = service.cast(
            "coin",
            CastRequest(question=question, seed=seed, show_steps=resolved_show_steps),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console,
            result,
            interpretation,
            show_steps=resolved_show_steps,
            language=service.resolve_language(lang),
        )

    _run_action(action)


@meihua_app.command("object")
def cast_meihua_object(
    object_type: str = typer.Option("flower", "--object-type"),
    count: int = typer.Option(1, "--count"),
    hour: str | None = typer.Option(None, "--hour"),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-object",
            CastRequest(
                question=question,
                extras={"object_type": object_type, "count": count, "hour": hour},
            ),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@meihua_app.command("person")
def cast_meihua_person(
    person_type: str = typer.Option("man", "--person-type"),
    count: int = typer.Option(1, "--count"),
    hour: str | None = typer.Option(None, "--hour"),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-person",
            CastRequest(
                question=question,
                extras={"person_type": person_type, "count": count, "hour": hour},
            ),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@meihua_app.command("static")
def cast_meihua_static(
    item_type: str = typer.Option("stone", "--item-type"),
    count: int = typer.Option(1, "--count"),
    hour: str | None = typer.Option(None, "--hour"),
    question: str | None = typer.Option(None, "--question"),
    save: bool | None = typer.Option(None, "--save/--no-save"),
    profile: str = typer.Option("balanced", "--profile"),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        result, interpretation = service.cast(
            "meihua-static",
            CastRequest(
                question=question,
                extras={"item_type": item_type, "count": count, "hour": hour},
            ),
            save_session=save,
            interpretation_profile=profile,
            language=service.resolve_language(lang),
        )
        if json_output:
            _print_json(
                {
                    "cast_result": result.to_dict(),
                    "interpretation": interpretation.to_dict(),
                }
            )
            return
        render_cast(
            console, result, interpretation, language=service.resolve_language(lang)
        )

    _run_action(action)


@cast_app.command("guided")
def cast_guided(lang: str | None = typer.Option(None, "--lang")) -> None:
    def action() -> None:
        service = _service()
        language = service.resolve_language(lang)
        method = typer.prompt(
            "Method",
            type=click.Choice(
                [
                    "dayan",
                    "coin",
                    "meihua-time",
                    "meihua-number",
                    "meihua-sound",
                    "meihua-word",
                    "meihua-object",
                    "meihua-person",
                    "meihua-static",
                ]
            ),
            default="dayan",
        )
        question = typer.prompt("Question", default="", show_default=False) or None
        if method == "dayan":
            seed_text = typer.prompt("Seed (optional)", default="", show_default=False)
            result, interpretation = service.cast(
                "dayan",
                CastRequest(
                    question=question,
                    seed=int(seed_text) if seed_text else None,
                    show_steps=service.config.show_steps,
                ),
                language=language,
            )
        elif method == "coin":
            seed_text = typer.prompt("Seed (optional)", default="", show_default=False)
            result, interpretation = service.cast(
                "coin",
                CastRequest(
                    question=question, seed=int(seed_text) if seed_text else None
                ),
                language=language,
            )
        elif method == "meihua-time":
            dt_text = typer.prompt(
                "Datetime ISO (blank for now)", default="", show_default=False
            )
            hour = (
                typer.prompt("Hour branch (optional)", default="", show_default=False)
                or None
            )
            result, interpretation = service.cast(
                "meihua-time",
                CastRequest(
                    question=question,
                    calendar_mode=service.config.calendar_mode,
                    datetime_value=_parse_datetime(dt_text) if dt_text else None,
                    extras={"hour": hour},
                ),
                language=language,
            )
        elif method == "meihua-number":
            numbers = tuple(
                int(part)
                for part in typer.prompt(
                    "Numbers, separated by spaces", default="3 5"
                ).split()
            )
            result, interpretation = service.cast(
                "meihua-number",
                CastRequest(question=question, raw_numbers=numbers),
                language=language,
            )
        elif method == "meihua-sound":
            count_text = typer.prompt(
                "Count (blank to infer from sentence)", default="", show_default=False
            )
            sentence = (
                typer.prompt("Sentence (optional)", default="", show_default=False)
                or None
            )
            hour = (
                typer.prompt("Hour branch (optional)", default="", show_default=False)
                or None
            )
            result, interpretation = service.cast(
                "meihua-sound",
                CastRequest(
                    question=question,
                    raw_text=sentence,
                    extras={
                        "count": int(count_text) if count_text else None,
                        "hour": hour,
                    },
                ),
                language=language,
            )
        elif method == "meihua-word":
            text = typer.prompt("Text")
            result, interpretation = service.cast(
                "meihua-word",
                CastRequest(question=question, raw_text=text),
                language=language,
            )
        elif method == "meihua-object":
            object_type = typer.prompt("Object type", default="flower")
            count = int(typer.prompt("Count", default="1"))
            hour = typer.prompt("Hour branch", default="you")
            result, interpretation = service.cast(
                "meihua-object",
                CastRequest(
                    question=question,
                    extras={"object_type": object_type, "count": count, "hour": hour},
                ),
                language=language,
            )
        elif method == "meihua-person":
            person_type = typer.prompt("Person type", default="merchant")
            count = int(typer.prompt("Count", default="1"))
            hour = typer.prompt("Hour branch", default="zi")
            result, interpretation = service.cast(
                "meihua-person",
                CastRequest(
                    question=question,
                    extras={"person_type": person_type, "count": count, "hour": hour},
                ),
                language=language,
            )
        else:
            item_type = typer.prompt("Static item type", default="stone")
            count = int(typer.prompt("Count", default="1"))
            hour = typer.prompt("Hour branch", default="mao")
            result, interpretation = service.cast(
                "meihua-static",
                CastRequest(
                    question=question,
                    extras={"item_type": item_type, "count": count, "hour": hour},
                ),
                language=language,
            )
        render_cast(
            console,
            result,
            interpretation,
            show_steps=service.config.show_steps,
            language=language,
        )

    _run_action(action)


@app.command()
def interpret(
    hexagram: int = typer.Option(..., "--hexagram", min=1, max=64),
    line: int | None = typer.Option(None, "--line", min=1, max=6),
    json_output: bool = typer.Option(False, "--json"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        language = service.resolve_language(lang)
        data = service.interpret_hexagram(hexagram, line, language)
        if json_output:
            _print_json(data)
            return
        render_lookup_hexagram(console, service.lookup_hexagram(hexagram), language)
        if data["line_texts"]:
            console.print_json(
                json.dumps(data["line_texts"], ensure_ascii=False, indent=2)
            )

    _run_action(action)


@app.command()
def explain(
    session_id: str = typer.Argument(..., help="Session id, prefix, or 'latest'"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        _print_json(
            service.explain_localized(session_id, service.resolve_language(lang))
        )

    _run_action(action)


@app.command()
def export(
    session_id: str = typer.Argument(..., help="Session id, prefix, or 'latest'"),
    fmt: str | None = typer.Option(None, "--format"),
    lang: str | None = typer.Option(None, "--lang"),
) -> None:
    def action() -> None:
        service = _service()
        console.print(
            service.export(
                session_id,
                service.resolve_export_format(fmt),
                service.resolve_language(lang),
            )
        )

    _run_action(action)


cast_app.add_typer(meihua_app, name="meihua")
app.add_typer(cast_app, name="cast")
app.add_typer(lookup_app, name="lookup")
app.add_typer(config_app, name="config")


def run() -> None:
    app()
