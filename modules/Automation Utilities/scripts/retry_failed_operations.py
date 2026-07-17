#!/usr/bin/env python3
"""
retry_failed_operations.py
--------------------
A simple @retry decorator: catches specified exceptions and retries the
wrapped function up to N times with a fixed delay between attempts.

This is the "basic" retry building block. For exponential backoff, see
retry_backoff.py. For a more configurable version (async support,
per-attempt callbacks, etc.), see retry_decorator.py.

Usage as a library:
    from retry_failed_operations import retry

    @retry(times=3, delay=1.0, exceptions=(ConnectionError,))
    def flaky_call():
        ...

Run directly for a demo:
    python retry_failed_operations.py
"""

import functools
import time


def retry(times=3, delay=1.0, exceptions=(Exception,)):
    """
    Decorator factory. Retries the wrapped function up to `times` times,
    waiting `delay` seconds between attempts, only for the given
    `exceptions`. Re-raises the last exception if all attempts fail.
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
                    print(f"[retry] Attempt {attempt}/{times} for '{func.__name__}' "
                          f"failed: {exc!r}")
                    if attempt < times:
                        time.sleep(delay)
            print(f"[retry] All {times} attempts failed for '{func.__name__}'.")
            raise last_exc
        return wrapper
    return decorator


if __name__ == "__main__":
    # Demo: a function that fails twice, then succeeds on the 3rd try.
    call_count = {"n": 0}

    @retry(times=4, delay=0.3, exceptions=(RuntimeError,))
    def unstable_operation():
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise RuntimeError(f"simulated failure #{call_count['n']}")
        return "success"

    print("Demo: retrying an operation that fails twice before succeeding.\n")
    result = unstable_operation()
    print(f"\nFinal result: {result}")
    print(f"Total calls made: {call_count['n']}")
