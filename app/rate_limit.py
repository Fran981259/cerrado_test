"""Rate limit compartilhado para endpoints públicos."""

import os
import time

import redis

_LOCAL_COUNTER: dict[str, tuple[float, int]] = {}


def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def _local_limit(key: str, maximum: int, window: int) -> bool:
    now = time.time()
    started_at, count = _LOCAL_COUNTER.get(key, (now, 0))
    if now - started_at >= window:
        _LOCAL_COUNTER[key] = (now, 1)
        return False
    count += 1
    _LOCAL_COUNTER[key] = (started_at, count)
    return count > maximum


def is_rate_limited(key: str, maximum: int, window: int) -> bool:
    """Incrementa o contador compartilhado e informa se o limite foi excedido."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        if _is_production():
            raise RuntimeError("REDIS_URL obrigatório para rate limit em produção")
        return _local_limit(key, maximum, window)
    try:
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        count = int(client.incr(key))
        if count == 1:
            client.expire(key, window)
        return count > maximum
    except redis.RedisError as error:
        if _is_production():
            raise RuntimeError("Rate limit compartilhado indisponível") from error
        return _local_limit(key, maximum, window)
