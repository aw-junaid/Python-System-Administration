#!/usr/bin/env python3
"""
cache_results.py
--------------------
Memoize function return values two ways:

  1. In-process, via functools.lru_cache (fast, zero setup, but cache is
     lost when the process exits and isn't shared across processes).
  2. Cross-process, via a Redis-backed cache decorator (persists between
     runs and is shared across workers, at the cost of needing a Redis
     server + the `redis` package).

Usage as a library:
    from cache_results import memoize_lru, memoize_redis

    @memoize_lru(maxsize=256)
    def expensive_calc(n):
        ...

    @memoize_redis(ttl_seconds=60)
    def expensive_api_call(user_id):
        ...

Run directly for a demo:
    python cache_results.py
"""

import functools
import json
import time

try:
    import redis  # type: ignore
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


def memoize_lru(maxsize=128):
    """Thin, explicit wrapper around functools.lru_cache for consistency
    with the other decorators in this file (and to make intent obvious
    at the call site)."""
    def decorator(func):
        return functools.lru_cache(maxsize=maxsize)(func)
    return decorator


def memoize_redis(ttl_seconds=300, redis_url="redis://localhost:6379/0", key_prefix=None):
    """
    Cache a function's return value in Redis, keyed by its arguments,
    for `ttl_seconds`. Falls back to an in-process dict (with the same
    TTL behavior) if redis isn't installed/reachable, so the decorator
    is always safe to use.
    """
    def decorator(func):
        prefix = key_prefix or func.__name__
        local_cache = {}
        client = None
        if REDIS_AVAILABLE:
            try:
                client = redis.from_url(redis_url)
                client.ping()
            except Exception:
                client = None

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{json.dumps([args, kwargs], sort_keys=True, default=str)}"

            if client is not None:
                cached = client.get(cache_key)
                if cached is not None:
                    return json.loads(cached)
                result = func(*args, **kwargs)
                client.setex(cache_key, ttl_seconds, json.dumps(result))
                return result

            # in-process fallback with manual TTL
            now = time.monotonic()
            if cache_key in local_cache:
                value, expires_at = local_cache[cache_key]
                if now < expires_at:
                    return value
            result = func(*args, **kwargs)
            local_cache[cache_key] = (result, now + ttl_seconds)
            return result

        return wrapper
    return decorator


if __name__ == "__main__":
    call_count = {"lru": 0, "redis": 0}

    @memoize_lru(maxsize=32)
    def slow_square(n):
        call_count["lru"] += 1
        time.sleep(0.2)
        return n * n

    print("Demo 1: functools.lru_cache-based memoization\n")
    print("First call (n=5):", slow_square(5), f"(function body ran {call_count['lru']}x)")
    print("Second call (n=5):", slow_square(5), f"(function body ran {call_count['lru']}x -- cached)")

    @memoize_redis(ttl_seconds=5)
    def slow_lookup(user_id):
        call_count["redis"] += 1
        time.sleep(0.2)
        return {"user_id": user_id, "name": f"user-{user_id}"}

    print("\nDemo 2: Redis-backed memoization (falls back to in-process if no Redis)\n")
    if not REDIS_AVAILABLE:
        print("[note] 'redis' package not installed -- using in-process TTL fallback for this demo.")
    print("First call (id=42):", slow_lookup(42), f"(function body ran {call_count['redis']}x)")
    print("Second call (id=42):", slow_lookup(42), f"(function body ran {call_count['redis']}x -- cached)")
