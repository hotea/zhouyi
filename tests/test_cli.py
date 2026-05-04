import json

from typer.testing import CliRunner

from zhouyi.cli.app import app


runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Zhouyi CLI" in result.stdout


def test_methods_json() -> None:
    result = runner.invoke(app, ["methods", "--json"])
    assert result.exit_code == 0
    assert "dayan" in result.stdout


def test_meihua_number_json() -> None:
    result = runner.invoke(app, ["cast", "meihua", "number", "3", "5", "--json"])
    assert result.exit_code == 0
    assert '"method_id": "meihua-number"' in result.stdout


def test_sessions_command() -> None:
    runner.invoke(app, ["cast", "meihua", "number", "3", "5", "--json"])
    result = runner.invoke(app, ["sessions", "--json"])
    assert result.exit_code == 0
    assert '"session_id"' in result.stdout


def test_config_and_latest_alias(tmp_path) -> None:
    env = {
        "ZHOUYI_SESSION_DIR": str(tmp_path / "sessions"),
        "ZHOUYI_CONFIG_FILE": str(tmp_path / "config.json"),
    }
    init_result = runner.invoke(app, ["config", "init", "--force"], env=env)
    assert init_result.exit_code == 0

    set_result = runner.invoke(
        app,
        ["config", "set", "calendar-mode", "classical-lunisolar"],
        env=env,
    )
    assert set_result.exit_code == 0

    show_result = runner.invoke(app, ["config", "show", "--json"], env=env)
    assert show_result.exit_code == 0
    show_payload = json.loads(show_result.stdout)
    assert show_payload["calendar_mode"] == "classical-lunisolar"

    cast_result = runner.invoke(
        app, ["cast", "meihua", "number", "3", "5", "--json"], env=env
    )
    assert cast_result.exit_code == 0

    explain_result = runner.invoke(app, ["explain", "latest"], env=env)
    assert explain_result.exit_code == 0
    assert '"method_id": "meihua-number"' in explain_result.stdout


def test_explain_and_export_localize_to_english(tmp_path) -> None:
    env = {
        "ZHOUYI_SESSION_DIR": str(tmp_path / "sessions"),
        "ZHOUYI_CONFIG_FILE": str(tmp_path / "config.json"),
    }
    cast_result = runner.invoke(
        app, ["cast", "meihua", "number", "3", "5", "--json"], env=env
    )
    assert cast_result.exit_code == 0

    explain_result = runner.invoke(app, ["explain", "latest", "--lang", "en"], env=env)
    assert explain_result.exit_code == 0
    explain_payload = json.loads(explain_result.stdout)
    assert (
        explain_payload["interpretation"]["primary_texts"]["hexagram"]["display_name"]
        == "Holding"
    )

    export_result = runner.invoke(
        app,
        ["export", "latest", "--format", "markdown", "--lang", "en"],
        env=env,
    )
    assert export_result.exit_code == 0
    assert "# Holding" in export_result.stdout


def test_no_save_does_not_create_session(tmp_path) -> None:
    env = {
        "ZHOUYI_SESSION_DIR": str(tmp_path / "sessions"),
        "ZHOUYI_CONFIG_FILE": str(tmp_path / "config.json"),
    }
    result = runner.invoke(
        app,
        ["cast", "meihua", "number", "3", "5", "--no-save", "--json"],
        env=env,
    )
    assert result.exit_code == 0

    sessions_result = runner.invoke(app, ["sessions", "--json"], env=env)
    assert sessions_result.exit_code == 0
    assert json.loads(sessions_result.stdout) == []


def test_interpret_json_includes_classic_texts(tmp_path) -> None:
    env = {"ZHOUYI_CONFIG_FILE": str(tmp_path / "config.json")}
    result = runner.invoke(
        app, ["interpret", "--hexagram", "49", "--line", "1", "--json"], env=env
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert (
        payload["primary_texts"]["hexagram"]["judgment"]
        == "革：己日乃孚。元亨利贞，悔亡。"
    )
    assert payload["primary_texts"]["hexagram"]["tuan"] is not None
    assert payload["line_texts"][0]["source"] == "specific"
    assert payload["line_texts"][0]["image"] is not None


def test_interpret_json_localizes_to_english() -> None:
    result = runner.invoke(
        app, ["interpret", "--hexagram", "49", "--line", "1", "--json", "--lang", "en"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["primary_texts"]["hexagram"]["display_name"] == "Skinning"
    assert payload["primary_texts"]["hexagram"]["judgment"].startswith("Ge:")
    assert payload["line_texts"][0]["source"] == "translated"
    assert payload["line_texts"][0]["image"] is not None


def test_case_command_english_summary_has_no_double_space_before_focus() -> None:
    result = runner.invoke(app, ["case", "jinri-dongjing", "--json", "--lang", "en"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert (
        ".  Current focus:" not in payload["interpretation"]["plain_language_summary"]
    )


def test_profiles_command() -> None:
    result = runner.invoke(app, ["profiles", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert {item["profile_id"] for item in payload} == {"classic", "balanced", "modern"}


def test_methods_command_in_english() -> None:
    result = runner.invoke(app, ["methods", "--lang", "en"])
    assert result.exit_code == 0
    assert "Methods" in result.stdout
    assert "Dayan divination" in result.stdout


def test_cases_command() -> None:
    result = runner.invoke(app, ["cases", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any(item["case_id"] == "guanmei-zhan" for item in payload)


def test_case_command_localizes_to_english() -> None:
    result = runner.invoke(app, ["case", "jinri-dongjing", "--json", "--lang", "en"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert (
        payload["interpretation"]["primary_texts"]["hexagram"]["display_name"]
        == "Radiance"
    )


def test_coin_command_json() -> None:
    result = runner.invoke(app, ["cast", "coin", "--seed", "7", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["cast_result"]["method_id"] == "coin"
