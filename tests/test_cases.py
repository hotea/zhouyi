from zhouyi.app import ZhouyiApp


def test_cases_list_available() -> None:
    cases = ZhouyiApp().meihua_cases()
    assert len(cases) >= 4


def test_cases_list_localize_to_english() -> None:
    cases = ZhouyiApp().meihua_cases("en")
    assert any(item["title"] == "Watching Plum Blossoms Divination" for item in cases)


def test_run_known_case() -> None:
    data = ZhouyiApp().run_meihua_case("jinri-dongjing")
    assert data["cast_result"]["changing_lines"] == [6]


def test_run_known_case_localizes_to_english() -> None:
    data = ZhouyiApp().run_meihua_case("jinri-dongjing", "en")
    assert (
        data["interpretation"]["primary_texts"]["hexagram"]["display_name"]
        == "Radiance"
    )
    assert data["interpretation"]["provenance"]["language"] == "en"
