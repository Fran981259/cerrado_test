"""Simulações offline dos caminhos de falha críticos."""

import json

import pytest
import requests


def test_api_health_returns_503_when_database_is_unavailable(monkeypatch) -> None:
    from app.main import health_check

    def fail_session():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("app.main.get_session", fail_session)
    response = health_check()
    assert response.status_code == 503
    assert json.loads(response.body) == {"status": "unhealthy", "database": "unavailable"}


def test_maintenance_health_degrades_when_database_fails(monkeypatch) -> None:
    from app.tasks.maintenance import system_health_check

    monkeypatch.setattr("app.database.get_session", lambda: (_ for _ in ()).throw(RuntimeError("db down")))
    result = system_health_check()
    assert result["status"] == "unhealthy"
    assert result["checks"]["database"].startswith("fail:")


def test_llm_network_failure_exhausts_bounded_retries(monkeypatch) -> None:
    from app.llm_client import LLMClient

    attempts = 0

    def fail_post(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1
        raise requests.ConnectionError("provider unavailable")

    monkeypatch.setattr("app.llm_client.requests.post", fail_post)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
    client = LLMClient(api_key="test", provider="openai")
    with pytest.raises(requests.ConnectionError):
        client._post_with_backoff("https://example.invalid", {})
    assert attempts == client.MAX_ATTEMPTS
