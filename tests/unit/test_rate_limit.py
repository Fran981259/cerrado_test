import pytest

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
    class FakeRedis:
        def __init__(self):
            self.count = 0
            self.expiration = None

        def incr(self, _key):
            self.count += 1
            return self.count

        def expire(self, _key, seconds):
            self.expiration = seconds

    fake = FakeRedis()
    monkeypatch.setenv("REDIS_URL", "redis://test")
    monkeypatch.setattr(rate_limit.redis.Redis, "from_url", lambda *_args, **_kwargs: fake)

    assert rate_limit.is_rate_limited("test-key", maximum=1, window=60) is False
    assert rate_limit.is_rate_limited("test-key", maximum=1, window=60) is True
    assert fake.expiration == 60
