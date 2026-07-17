#!/usr/bin/env python3
"""
rate_limiting.py
--------------------
A token-bucket rate limiter to throttle API calls (or any repeated
operation) to at most `rate` events per `per_seconds`, while still
allowing short bursts up to the bucket's capacity.

Usage as a library:
    from rate_limiting import TokenBucket

    limiter = TokenBucket(rate=5, per_seconds=1.0, capacity=5)

    for request in requests:
        limiter.acquire()   # blocks until a token is available
        send(request)

    # or as a decorator:
    from rate_limiting import rate_limited

    @rate_limited(rate=2, per_seconds=1.0)
    def call_api():
        ...

Run directly for a demo:
    python rate_limiting.py
"""

import functools
import threading
import time


class TokenBucket:
    def __init__(self, rate, per_seconds=1.0, capacity=None):
        """
        rate        -- tokens added per `per_seconds`
        per_seconds -- time window the rate applies to
        capacity    -- max tokens the bucket can hold (defaults to `rate`,
                       i.e. no more than one window's worth of burst)
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.capacity = capacity if capacity is not None else rate
        self._tokens = float(self.capacity)
        self._lock = threading.Lock()
        self._last_refill = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        added = elapsed * (self.rate / self.per_seconds)
        if added > 0:
            self._tokens = min(self.capacity, self._tokens + added)
            self._last_refill = now

    def try_acquire(self, tokens=1):
        """Non-blocking: returns True if tokens were available and consumed."""
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def acquire(self, tokens=1):
        """Blocking: waits until enough tokens are available, then consumes them."""
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                deficit = tokens - self._tokens
                wait_time = deficit / (self.rate / self.per_seconds)
            time.sleep(max(wait_time, 0.001))


def rate_limited(rate, per_seconds=1.0, capacity=None):
    """Decorator: throttle calls to a function using a shared TokenBucket."""
    bucket = TokenBucket(rate=rate, per_seconds=per_seconds, capacity=capacity)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bucket.acquire()
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    print("Demo: allowing 3 calls/second, firing 8 calls back-to-back\n")

    @rate_limited(rate=3, per_seconds=1.0)
    def call_api(n):
        print(f"  call {n} executed at t={time.monotonic() - start:.2f}s")

    start = time.monotonic()
    for i in range(1, 9):
        call_api(i)
    print("\nNotice calls are spaced out once the initial burst capacity is used.")
