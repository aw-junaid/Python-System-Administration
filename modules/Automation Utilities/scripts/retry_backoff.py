#!/usr/bin/env python3
"""
retry_backoff.py
--------------------
Retry decorator that progressively increases the delay between attempts
(exponential backoff), optionally with random jitter, to avoid a
"thundering herd" of clients all retrying at the exact same moment
against a struggling service.

For fixed-delay retries, see retry_failed_operations.py.
For a fully configurable sync/async retry with callbacks, see
retry_decorator.py.

Usage as a library:
    from retry_backoff import retry_with_backoff

    @retry_with_backoff(times=5, base_delay=0.5, max_delay=10, jitter=True)
    def call_flaky_service():
        ...

Run directly for a demo:
    python retry_backoff.py
"""

import functools
import random
import time


def retry_with_backoff(times=5, base_delay=0.5, max_delay=30.0,
                        multiplier=2.0, jitter=True, exceptions=(Exception,)):
    """
    Decorator factory. Retries up to `times` attempts. The delay before
    attempt N is `min(max_delay, base_delay * multiplier**(N-1))`, with
    up to 50% random jitter added/subtracted if `jitter=True` to spread
    out retries across many clients.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == times:
                        break
                    delay = min(max_delay, base_delay * (multiplier ** (attempt - 1)))
                    if jitter:
                        delay = delay * random.uniform(0.5, 1.5)
                    print(f"[retry_backoff] Attempt {attempt}/{times} for "
                          f"'{func.__name__}' failed: {exc!r} -- retrying in {delay:.2f}s")
                    time.sleep(delay)
            print(f"[retry_backoff] All {times} attempts failed for '{func.__name__}'.")
            raise last_exc
        return wrapper
    return decorator


if __name__ == "__main__":
    call_count = {"n": 0}

    @retry_with_backoff(times=5, base_delay=0.2, max_delay=3.0, jitter=False,
                         exceptions=(ConnectionError,))
    def unreliable_service():
        call_count["n"] += 1
        if call_count["n"] < 4:
            raise ConnectionError(f"service unavailable (attempt {call_count['n']})")
        return "connected"

    print("Demo: exponential backoff (0.2s, 0.4s, 0.8s, 1.6s...) with no jitter\n")
    result = unreliable_service()
    print(f"\nFinal result: {result}")
    print(f"Total calls made: {call_count['n']}")
