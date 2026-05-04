from __future__ import annotations

import threading
import time

import pytest

from zhouyi.domain.models import CastRequest
from zhouyi.methods.dayan_zhu_xi import DayanZhuXiMethod
from zhouyi.methods.meihua_number import MeihuaNumberMethod
from zhouyi.methods.meihua_time import MeihuaTimeMethod


class TestPerformance:
    def test_dayan_performance(self, repository):
        method = DayanZhuXiMethod(repository)
        request = CastRequest(seed=42, show_steps=False)
        start = time.perf_counter()
        for _ in range(100):
            method.cast(request)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0

    def test_meihua_time_performance(self, repository):
        method = MeihuaTimeMethod(repository)
        request = CastRequest()
        start = time.perf_counter()
        for _ in range(1000):
            method.cast(request)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0

    def test_meihua_number_performance(self, repository):
        method = MeihuaNumberMethod(repository)
        request = CastRequest(raw_numbers=(3, 5))
        start = time.perf_counter()
        for _ in range(1000):
            method.cast(request)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0


class TestConcurrency:
    def test_repository_cached_property_thread_safe(self, repository):
        results = []
        errors = []

        def access():
            try:
                _ = repository.hexagram_lookup
                results.append(True)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=access) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
        assert len(results) == 10

    def test_session_store_concurrent_save(self, tmp_path):
        from datetime import datetime

        from zhouyi.domain.models import CastResult, Hexagram, LineState
        from zhouyi.domain.enums import TrigramId
        from zhouyi.infra.session_store import SessionStore

        store = SessionStore(base_dir=tmp_path)
        hexagram = Hexagram(
            lines=tuple([LineState.YOUNG_YANG] * 6),
            king_wen_index=1,
            name_zh="乾",
            unicode_symbol="",
            upper_trigram=TrigramId.QIAN,
            lower_trigram=TrigramId.QIAN,
            summary="",
        )
        result = CastResult(
            session_id="a" * 12,
            question=None,
            method_id="test",
            method_version="v1",
            created_at=datetime.now(),
            timezone="UTC",
            calendar_mode=None,
            seed=None,
            primary_hexagram=hexagram,
            relating_hexagram=None,
            mutual_hexagram=None,
            changing_lines=(),
            steps=[],
            raw_inputs={},
        )
        errors = []

        def save():
            try:
                store.save(result)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=save) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0


class TestEndToEnd:
    def test_full_flow(self, tmp_path):
        from zhouyi.app import ZhouyiApp

        app = ZhouyiApp(session_dir=tmp_path)
        result, interpretation = app.cast(
            "meihua-number",
            CastRequest(raw_numbers=(3, 5)),
            save_session=True,
        )
        assert result.session_id
        assert result.primary_hexagram

        sessions = app.recent_sessions(limit=1)
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == result.session_id

        payload = app.explain(result.session_id)
        assert "cast_result" in payload
        assert "interpretation" in payload

        md = app.export(result.session_id, "markdown", language="zh")
        assert result.primary_hexagram.name_zh in md

        json_str = app.export(result.session_id, "json", language="zh")
        assert result.session_id in json_str
