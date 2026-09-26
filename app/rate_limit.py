"""Rate limit compartilhado para endpoints públicos."""

import os
import time
from threading import Lock

import redis

_LOCAL_COUNTER: dict[str, tuple[float, int]] = {}
_POOL_LOCK = Lock()
_POOLS: dict[str, redis.ConnectionPool] = {}


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


def _redis_client(redis_url: str):
    """Return one pooled Redis client per configured URL."""
    with _POOL_LOCK:
        pool = _POOLS.get(redis_url)
        if pool is None:
            pool = redis.ConnectionPool.from_url(redis_url, decode_responses=True)
            _POOLS[redis_url] = pool
    return redis.Redis(connection_pool=pool)


def _atomic_increment(client, key: str, window: int) -> int:
    """Increment a counter and refresh its TTL in one Redis transaction."""
    pipe = client.pipeline(transaction=True)
    pipe.incr(key)
    pipe.expire(key, window)
    count, _ = pipe.execute()
    return int(count)


def is_rate_limited(key: str, maximum: int, window: int) -> bool:
    """Incrementa o contador compartilhado e informa se o limite foi excedido."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        if _is_production():
            raise RuntimeError("REDIS_URL obrigatório para rate limit em produção")
        return _local_limit(key, maximum, window)
    try:
        count = _atomic_increment(_redis_client(redis_url), key, window)
        return count > maximum
    except redis.RedisError as error:
        if _is_production():
            raise RuntimeError("Rate limit compartilhado indisponível") from error
        return _local_limit(key, maximum, window)
