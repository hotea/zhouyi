from zhouyi.app import ZhouyiApp
from zhouyi.domain.models import CastRequest


def test_interpretation_profiles_are_available() -> None:
    app = ZhouyiApp()
    profiles = app.interpretation_profiles()
    assert {item["profile_id"] for item in profiles} == {
        "classic",
        "balanced",
        "modern",
    }


def test_interpretation_profiles_localize_to_english() -> None:
    app = ZhouyiApp()
    profiles = app.interpretation_profiles("en")
    assert any(item["name"] == "Classic Reading" for item in profiles)
    assert any("plain-language" in item["summary_style"] for item in profiles)


def test_classic_profile_prefers_classic_text() -> None:
    app = ZhouyiApp()
    _, interpretation = app.cast(
        "meihua-number",
        CastRequest(raw_numbers=(3, 5)),
        save_session=False,
        interpretation_profile="classic",
    )
    assert interpretation.provenance["interpretation_profile"] == "classic"
