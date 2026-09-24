import pytest
from fastapi import HTTPException

from app.security import require_api_key


def test_production_rejects_weak_operator_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PUBLISH_API_KEY", "short")

    with pytest.raises(HTTPException, match="fraca"):
        require_api_key("short")


def test_production_accepts_strong_operator_key(monkeypatch):
    key = "k" * 32
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PUBLISH_API_KEY", key)

    assert require_api_key(key) is None


def test_rotation_accepts_previous_key_during_transition(monkeypatch):
    current = "c" * 32
    previous = "p" * 32
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PUBLISH_API_KEY", current)
    monkeypatch.setenv("PUBLISH_API_KEY_PREVIOUS", previous)

    assert require_api_key(previous) is None
