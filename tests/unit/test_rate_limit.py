import pytest
from starlette.requests import Request

from app import rate_limit


def test_rate_limit_uses_local_fallback_outside_production(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "test")
    rate_limit._LOCAL_COUNTER.clear()

    assert rate_limit.is_rate_limited("test-key", maximum=1, window=60) is False
    assert rate_limit.is_rate_limited("test-key", maximum=1, window=60) is True


def test_rate_limit_requires_redis_in_production(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "production")

    with pytest.raises(RuntimeError, match="REDIS_URL"):
        rate_limit.is_rate_limited("test-key", maximum=1, window=60)


def test_rate_limit_uses_atomic_redis_counter(monkeypatch):
    class FakePipeline:
        def __init__(self, owner):
            self.owner = owner

        def incr(self, _key):
            self.owner.count += 1

        def expire(self, _key, seconds):
            self.owner.expiration = seconds

        def execute(self):
            return [self.owner.count, True]

    class FakeRedis:
        def __init__(self):
            self.count = 0
            self.expiration = None

        def pipeline(self, transaction=True):
            assert transaction is True
            return FakePipeline(self)

    fake = FakeRedis()
    monkeypatch.setenv("REDIS_URL", "redis://test")
    monkeypatch.setattr(rate_limit, "_redis_client", lambda _url: fake)
    rate_limit._POOLS.clear()

    assert rate_limit.is_rate_limited("test-key", maximum=1, window=60) is False
    assert rate_limit.is_rate_limited("test-key", maximum=1, window=60) is True
    assert fake.expiration == 60


def _request(client_host, forwarded=None):
    headers = [] if forwarded is None else [(b"x-forwarded-for", forwarded.encode())]
    return Request({"type": "http", "client": (client_host, 1234), "headers": headers})


def test_client_ip_uses_forwarded_address_from_trusted_proxy(monkeypatch):
    from app.analytics_routes import _client_ip

    monkeypatch.setenv("TRUSTED_PROXY_HOSTS", "10.0.0.2")
    assert _client_ip(_request("10.0.0.2", "203.0.113.10, 10.0.0.2")) == "203.0.113.10"


def test_client_ip_falls_back_when_sender_is_not_trusted(monkeypatch):
    from app.analytics_routes import _client_ip

    monkeypatch.setenv("TRUSTED_PROXY_HOSTS", "10.0.0.2")
    assert _client_ip(_request("198.51.100.8", "203.0.113.10")) == "198.51.100.8"
