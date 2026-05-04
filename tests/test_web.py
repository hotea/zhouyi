from zhouyi.domain.models import CastRequest
from zhouyi.app import ZhouyiApp
from fastapi.testclient import TestClient
from zhouyi.web.server import web, CSRF_COOKIE_NAME, _generate_csrf_token

client = TestClient(web)


def _get_csrf_cookie() -> tuple[str, str]:
    response = client.get("/")
    assert response.status_code == 200
    cookie = response.cookies.get(CSRF_COOKIE_NAME)
    return cookie, _generate_csrf_token()


def test_web_home() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "现代简约的周易起卦与解卦工作台" in response.text


def test_web_home_english() -> None:
    response = client.get("/?lang=en")
    assert response.status_code == 200
    assert (
        "A modern minimal Yijing casting and interpretation workspace" in response.text
    )


def test_web_cast_form() -> None:
    cookie_token, form_token = _get_csrf_cookie()
    response = client.post(
        "/cast",
        data={
            "method": "meihua-number",
            "profile": "balanced",
            "question": "此事可行否",
            "numbers": "3 5",
            "csrf_token": form_token,
        },
        cookies={CSRF_COOKIE_NAME: cookie_token},
    )
    assert response.status_code == 200
    assert "结果" in response.text or "Result" in response.text
    assert "hexagram-stack" in response.text
    assert "figure-compare-card" in response.text


def test_web_session_detail(tmp_path) -> None:
    app = ZhouyiApp(session_dir=tmp_path)
    result, _ = app.cast(
        "meihua-number",
        CastRequest(raw_numbers=(3, 5), question="测试会话"),
        save_session=True,
    )
    session_id = result.session_id
    web_app = ZhouyiApp(session_dir=tmp_path)
    sessions = web_app.recent_sessions(limit=1)
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == session_id


def test_web_session_detail_localizes_saved_session_to_english(tmp_path) -> None:
    app = ZhouyiApp(session_dir=tmp_path)
    result, _ = app.cast(
        "meihua-number",
        CastRequest(raw_numbers=(3, 5), question="测试会话"),
        save_session=True,
    )
    session_id = result.session_id
    payload = app.explain_localized(session_id, "en")
    assert "cast_result" in payload
    assert "interpretation" in payload
    assert "The primary hexagram is" in payload["interpretation"]["plain_language_summary"]
