from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, Label, Select, Static

from zhouyi.app import ZhouyiApp
from zhouyi.domain.models import CastRequest


class ZhouyiTUI(App[None]):
    CSS = """
    #result { height: auto; margin: 1 2; }
    #method-select { margin: 1 2; }
    #input-area { margin: 1 2; }
    #method-help { height: auto; margin: 0 2; color: #888; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.app_core = ZhouyiApp()
        self.current_method: str = "dayan"
        self._method_descriptions: dict[str, str] = {}
        self._method_fields: dict[str, list[dict[str, str]]] = {}

    def compose(self) -> ComposeResult:
        methods = self.app_core.methods_info()
        options = [(m["description"], m["id"]) for m in methods]
        self._method_descriptions = {m["id"]: m["description"] for m in methods}
        self._method_fields = self.app_core.method_field_schema("zh")
        yield Label("Zhouyi TUI")
        yield Select(options, id="method-select", value="dayan")
        yield Static("", id="method-help")
        with Vertical(id="input-area"):
            yield Input(placeholder="question (optional)", id="question")
            yield Input(placeholder="seed / numbers / text", id="param")
            yield Input(placeholder="hour (optional)", id="hour")
            yield Input(placeholder="count (optional)", id="count")
        yield Button("Cast", id="cast-btn")
        yield Static("", id="result")

    def _update_help(self) -> None:
        desc = self._method_descriptions.get(self.current_method, "")
        fields = self._method_fields.get(self.current_method, [])
        field_text = " | ".join(
            f"{f['name']}: {f['help']}" for f in fields
        ) if fields else ""
        help_text = f"{desc}\n{field_text}" if field_text else desc
        self.query_one("#method-help", Static).update(help_text)

    def on_select_changed(self, event: Select.Changed) -> None:
        self.current_method = str(event.value)
        param_input = self.query_one("#param", Input)
        if self.current_method in {"dayan", "coin"}:
            param_input.placeholder = "seed (optional)"
        elif self.current_method == "meihua-number":
            param_input.placeholder = "numbers (space-separated)"
        elif self.current_method in {"meihua-word", "meihua-sound"}:
            param_input.placeholder = "text"
        else:
            param_input.placeholder = "seed / numbers / text"
        self._update_help()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "cast-btn":
            return
        question = self.query_one("#question", Input).value or None
        param = self.query_one("#param", Input).value
        hour = self.query_one("#hour", Input).value or None
        count_str = self.query_one("#count", Input).value
        request = CastRequest(question=question)
        method = self.current_method
        try:
            if method in {"dayan", "coin"}:
                request.seed = int(param) if param else None
            elif method == "meihua-number":
                request.raw_numbers = tuple(
                    int(part) for part in param.split() if part.strip()
                )
            elif method in {"meihua-word", "meihua-sound"}:
                request.raw_text = param or None
                if method == "meihua-sound":
                    request.extras = {
                        "count": int(count_str) if count_str else None,
                        "hour": hour,
                    }
            elif method in {"meihua-object", "meihua-person", "meihua-static"}:
                request.extras = {
                    "count": int(count_str) if count_str else 1,
                    "hour": hour,
                }
            result, interpretation = self.app_core.cast(
                method, request, save_session=False
            )
            lines = [
                f"Method: {result.method_id}",
                f"Primary: {result.primary_hexagram.display_name()}",
            ]
            if result.relating_hexagram:
                lines.append(
                    f"Relating: {result.relating_hexagram.display_name()}"
                )
            if result.mutual_hexagram:
                lines.append(f"Mutual: {result.mutual_hexagram.display_name()}")
            summary = interpretation.plain_language_summary
            lines.append(f"\nSummary:\n{summary}")
            self.query_one("#result", Static).update("\n".join(lines))
        except Exception as exc:
            self.query_one("#result", Static).update(f"Error: {exc}")


def run_tui(language: str = "zh") -> None:
    del language
    ZhouyiTUI().run()
