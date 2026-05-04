from fastapi.testclient import TestClient

from zhouyi.api import api


client = TestClient(api)


def test_api_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_cast() -> None:
    response = client.post(
        "/cast/meihua-number",
        json={
            "raw_numbers": [3, 5],
            "save_session": False,
            "interpretation_profile": "balanced",
            "language": "en",
        },
    )
    assert response.status_code == 200
    assert response.json()["cast_result"]["method_id"] == "meihua-number"
    assert response.json()["language"] == "en"


def test_api_cases() -> None:
    response = client.get("/cases")
    assert response.status_code == 200
    assert any(item["case_id"] == "guanmei-zhan" for item in response.json()["items"])


def test_api_profiles_localize_to_english() -> None:
    response = client.get("/profiles?lang=en")
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "en"
    assert any(item["name"] == "Classic Reading" for item in payload["items"])


def test_api_cases_localize_to_english() -> None:
    response = client.get("/cases?lang=en")
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "en"
    assert any(
        item["title"] == "Watching Plum Blossoms Divination"
        for item in payload["items"]
    )


def test_api_sessions_localize_to_english() -> None:
    cast_response = client.post(
        "/cast/meihua-number",
        json={
            "raw_numbers": [3, 5],
            "save_session": True,
            "interpretation_profile": "balanced",
        },
    )
    assert cast_response.status_code == 200
    session_id = cast_response.json()["cast_result"]["session_id"]

    sessions_response = client.get("/sessions?lang=en")
    assert sessions_response.status_code == 200
    sessions_payload = sessions_response.json()
    assert sessions_payload["language"] == "en"
    assert any(item["hexagram"] == "Holding" for item in sessions_payload["items"])

    detail_response = client.get(f"/sessions/{session_id}?lang=en")
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["language"] == "en"
    assert (
        detail_payload["interpretation"]["primary_texts"]["hexagram"]["display_name"]
        == "Holding"
    )


def test_api_methods_meta() -> None:
    response = client.get("/methods?lang=en")
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "en"
    assert "field_schema" in payload
    assert any(item["id"] == "coin" for item in payload["items"])


def test_api_openapi_includes_cast_request_schema() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    payload = response.json()
    assert "CastPayloadModel" in payload["components"]["schemas"]
    assert payload["paths"]["/cast/{method_name}"]["post"]["requestBody"]
