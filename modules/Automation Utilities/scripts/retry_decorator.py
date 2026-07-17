#!/usr/bin/env python3
"""
retry_decorator.py
--------------------
A more configurable @retry annotation than retry_failed_operations.py:
supports both sync and async functions, a custom on_failure callback
per attempt, and an optional predicate to decide whether a *result*
(not just an exception) counts as a failure worth retrying.

For plain fixed-delay retries, see retry_failed_operations.py.
For exponential backoff, see retry_backoff.py.

Usage as a library:
    from retry_decorator import retry

    @retry(times=3, delay=0.5, exceptions=(IOError,))
    def read_flaky_file():
        ...

    @retry(times=3, delay=0.5, result_ok=lambda r: r is not None)
    async def fetch_async():
        ...

Run directly for a demo:
    python retry_decorator.py
"""

import asyncio
import functools
import inspect
import time


def retry(times=3, delay=1.0, exceptions=(Exception,), result_ok=None, on_failure=None):
    """
    Decorator factory usable on both sync and async callables.

    times       -- max attempts
    delay       -- seconds to wait between attempts
    exceptions  -- exception types that trigger a retry
    result_ok   -- optional callable(result) -> bool; if it returns
                   False, the result is treated as a failure and retried
                   even though no exception was raised
    on_failure  -- optional callable(attempt, exc_or_result) called after
                   each failed attempt, useful for logging/metrics
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exc = None
                for attempt in range(1, times + 1):
                    try:
                        result = await func(*args, **kwargs)
                        if result_ok is not None and not result_ok(result):
                            if on_failure:
                                on_failure(attempt, result)
                            if attempt < times:
                                await asyncio.sleep(delay)
                            continue
                        return result
                    except exceptions as exc:
                        last_exc = exc
                        if on_failure:
                            on_failure(attempt, exc)
                        if attempt < times:
                            await asyncio.sleep(delay)
                if last_exc:
                    raise last_exc
                raise RuntimeError(f"'{func.__name__}' never returned an acceptable result")
            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    result = func(*args, **kwargs)
                    if result_ok is not None and not result_ok(result):
                        if on_failure:
                            on_failure(attempt, result)
                        if attempt < times:
                            time.sleep(delay)
                        continue
                    return result
                except exceptions as exc:
                    last_exc = exc
                    if on_failure:
                        on_failure(attempt, exc)
                    if attempt < times:
                        time.sleep(delay)
            if last_exc:
                raise last_exc
            raise RuntimeError(f"'{func.__name__}' never returned an acceptable result")
        return sync_wrapper
    return decorator


if __name__ == "__main__":
    def log_failure(attempt, info):
        print(f"[retry_decorator] attempt {attempt} did not succeed: {info!r}")

    counter = {"n": 0}

    @retry(times=4, delay=0.2, result_ok=lambda r: r == "ready", on_failure=log_failure)
    def poll_status():
        counter["n"] += 1
        return "pending" if counter["n"] < 3 else "ready"

    print("Demo 1 (sync, result-based retry): polling until status == 'ready'\n")
    print("Result:", poll_status())

    async def async_demo():
        attempts = {"n": 0}

        @retry(times=3, delay=0.2, exceptions=(ValueError,), on_failure=log_failure)
        async def flaky_async_call():
            attempts["n"] += 1
            if attempts["n"] < 2:
                raise ValueError("simulated async failure")
            return "async success"

        return await flaky_async_call()

    print("\nDemo 2 (async, exception-based retry):\n")
    result = asyncio.run(async_demo())
    print("Result:", result)
