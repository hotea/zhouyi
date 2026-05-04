from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from zhouyi.api import api
from zhouyi.domain.models import CastRequest
from zhouyi.infra.session_store import SessionStore
from zhouyi.methods.meihua_number import MeihuaNumberMethod
from zhouyi.methods.meihua_sound import MeihuaSoundMethod
from zhouyi.methods.meihua_word import MeihuaWordMethod
from zhouyi.web.server import web, CSRF_COOKIE_NAME, _generate_csrf_token


class TestMeihuaNumberEdgeCases:
    def test_zero_number(self, repository):
        method = MeihuaNumberMethod(repository)
        request = CastRequest(raw_numbers=(0, 0))
        with pytest.raises(ValueError, match="positive"):
            method.cast(request)

    def test_negative_number(self, repository):
        method = MeihuaNumberMethod(repository)
        request = CastRequest(raw_numbers=(-3, -5))
        with pytest.raises(ValueError, match="positive"):
            method.cast(request)

    def test_large_number(self, repository):
        method = MeihuaNumberMethod(repository)
        request = CastRequest(raw_numbers=(999999, 888888))
        result = method.cast(request)
        assert result is not None

    def test_wrong_count(self, repository):
        method = MeihuaNumberMethod(repository)
        with pytest.raises(ValueError):
            method.cast(CastRequest(raw_numbers=(1,)))
        with pytest.raises(ValueError):
            method.cast(CastRequest(raw_numbers=(1, 2, 3, 4)))


class TestMeihuaSoundEdgeCases:
    def test_empty_text_and_no_count(self, repository):
        method = MeihuaSoundMethod(repository)
        with pytest.raises(ValueError):
            method.cast(CastRequest(raw_text=""))

    def test_count_zero(self, repository):
        method = MeihuaSoundMethod(repository)
        with pytest.raises(ValueError):
            method.cast(CastRequest(extras={"count": 0}))


class TestMeihuaWordEdgeCases:
    def test_empty_text(self, repository):
        method = MeihuaWordMethod(repository)
        with pytest.raises(ValueError):
            method.cast(CastRequest(raw_text=""))

    def test_whitespace_only(self, repository):
        method = MeihuaWordMethod(repository)
        with pytest.raises(ValueError):
            method.cast(CastRequest(raw_text="   "))


class TestSessionStoreSecurity:
    def test_path_traversal_blocked(self, tmp_path):
        store = SessionStore(base_dir=tmp_path)
        with pytest.raises(ValueError):
            store.session_path("../../../etc/passwd")

    def test_invalid_session_id_format(self, tmp_path):
        store = SessionStore(base_dir=tmp_path)
        with pytest.raises(ValueError):
            store.session_path("abc")

    def test_valid_session_id(self, tmp_path):
        store = SessionStore(base_dir=tmp_path)
        path = store.session_path("a" * 12)
        assert path.name == "a" * 12 + ".json"


class TestAPIEdgeCases:
    def test_invalid_datetime(self):
        client = TestClient(api)
        response = client.post(
            "/cast/meihua-time",
            json={
                "question": "test",
                "datetime_value": "not-a-datetime",
                "language": "zh",
            },
        )
        assert response.status_code == 422

    def test_invalid_method(self):
        client = TestClient(api)
        response = client.post(
            "/cast/nonexistent",
            json={"question": "test", "language": "zh"},
        )
        assert response.status_code == 422


class TestWebEdgeCases:
    def _csrf_post(self, client: TestClient, data: dict) -> object:
        home = client.get("/")
        cookie = home.cookies.get(CSRF_COOKIE_NAME, "")
        token = _generate_csrf_token()
        data["csrf_token"] = token
        return client.post("/cast", data=data, cookies={CSRF_COOKIE_NAME: cookie})

    def test_invalid_numbers(self):
        client = TestClient(web)
        response = self._csrf_post(client, {
            "method": "meihua-number",
            "numbers": "abc def",
            "lang": "zh",
        })
        assert response.status_code == 422

    def test_negative_count(self):
        client = TestClient(web)
        response = self._csrf_post(client, {
            "method": "meihua-object",
            "count": "-1",
            "lang": "zh",
        })
        assert response.status_code == 422
