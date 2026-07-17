#!/usr/bin/env python3
"""
timeout_execution.py
--------------------
Kill/interrupt a function's execution if it runs longer than a given
threshold. Uses a background thread + a sentinel, since Python cannot
force-kill another thread; instead this races the target function
against a timer and raises TimeoutError in the caller if the timer
wins (the original call is left to finish in the background, which is
the standard trade-off for pure-Python timeouts on arbitrary code).

For truly killable timeouts (e.g. an infinite CPU-bound loop), run the
work in a separate process instead -- see multiprocessing_utils.py.

Usage as a library:
    from timeout_execution import timeout

    @timeout(seconds=2)
    def slow_function():
        ...

Run directly for a demo:
    python timeout_execution.py
"""

import functools
import threading


class TimeoutError_(TimeoutError):
    pass


def timeout(seconds):
    """
    Decorator factory. Runs the wrapped function in a daemon thread and
    raises TimeoutError_ in the calling thread if it doesn't finish
    within `seconds`. The background thread is not forcibly killed
    (Python has no safe API for that) -- it will keep running until it
    naturally returns, but the caller is freed to move on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = {}
            exc_holder = {}
            done = threading.Event()

            def target():
                try:
                    result["value"] = func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    exc_holder["exc"] = exc
                finally:
                    done.set()

            worker = threading.Thread(target=target, daemon=True)
            worker.start()
            finished_in_time = done.wait(timeout=seconds)

            if not finished_in_time:
                raise TimeoutError_(
                    f"'{func.__name__}' did not complete within {seconds}s"
                )
            if "exc" in exc_holder:
                raise exc_holder["exc"]
            return result["value"]
        return wrapper
    return decorator


if __name__ == "__main__":
    import time

    @timeout(seconds=1)
    def fast_task():
        time.sleep(0.3)
        return "fast task finished"

    @timeout(seconds=1)
    def slow_task():
        time.sleep(3)
        return "slow task finished"  # never reached in time

    print("Demo 1: a task that finishes within the timeout")
    print(" ->", fast_task())

    print("\nDemo 2: a task that exceeds the timeout")
    try:
        slow_task()
    except TimeoutError_ as e:
        print(" -> Caught expected error:", e)
