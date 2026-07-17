#!/usr/bin/env python3
"""
retry_strategies.py

Demonstrates a production-style retry strategy: exponential backoff
WITH random jitter (to avoid "thundering herd" retries), a maximum
attempt cap, only retrying on specific transient exceptions, and
designing the retried operation to be IDEMPOTENT (safe to run more
than once) using an idempotency key.

Usage:
    python retry_strategies.py
    python retry_strategies.py --max-attempts 5 --base-delay 0.5

Expected output:
    The script simulates calling a flaky "remote API" a few times.
    You will see log lines for each attempt, the increasing (jittered)
    delay between retries, and a final SUCCESS or "giving up after N
    attempts" message. It also demonstrates that calling the
    idempotent operation twice with the same idempotency key only
    performs the underlying action once.
"""

import argparse
import functools
import logging
import random
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("retry_demo")


class TransientError(Exception):
    """Represents a retryable, temporary failure (e.g. network blip, 503)."""


class PermanentError(Exception):
    """Represents a non-retryable failure (e.g. 400 Bad Request, bad auth)."""


def retry_with_backoff(max_attempts=5, base_delay=0.3, max_delay=8.0, retry_on=(TransientError,)):
    """
    Decorator implementing exponential backoff with full jitter.

    Only exceptions listed in `retry_on` trigger a retry; anything else
    (e.g. PermanentError) is raised immediately, since retrying a
    permanent failure just wastes time and can mask real bugs.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    if attempt >= max_attempts:
                        logger.error("Giving up after %d attempts: %s", attempt, e)
                        raise
                    # Exponential backoff with FULL JITTER:
                    # delay = random value between 0 and min(max_delay, base * 2^attempt)
                    exp_delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    jittered_delay = random.uniform(0, exp_delay)
                    logger.warning(
                        "Attempt %d/%d failed (%s). Retrying in %.2fs...",
                        attempt, max_attempts, e, jittered_delay,
                    )
                    time.sleep(jittered_delay)
                    attempt += 1
        return wrapper
    return decorator


@retry_with_backoff(max_attempts=5, base_delay=0.3, retry_on=(TransientError,))
def call_flaky_api(success_probability=0.4):
    """Simulates a remote call that fails transiently most of the time."""
    if random.random() < success_probability:
        return {"status": "ok", "data": 42}
    raise TransientError("simulated 503 Service Unavailable")


# ---------------------------------------------------------------------------
# Idempotency demo: retries are only SAFE if the underlying action can be
# repeated without side effects (e.g. creating a duplicate charge/order).
# The common pattern is an "idempotency key" that lets the receiving
# system recognize and dedupe a repeated request.
# ---------------------------------------------------------------------------

_processed_requests = {}  # simulates a server-side dedupe store, keyed by idempotency key


def create_order_idempotent(order_payload: dict, idempotency_key: str) -> dict:
    """
    Simulates a POST /orders call that is safe to retry: if the same
    idempotency_key was already processed, return the cached result
    instead of creating a duplicate order.
    """
    if idempotency_key in _processed_requests:
        logger.info("Idempotency key %s already processed — returning cached result, no duplicate created.", idempotency_key)
        return _processed_requests[idempotency_key]

    logger.info("Processing NEW order for idempotency key %s ...", idempotency_key)
    result = {"order_id": f"ORD-{len(_processed_requests) + 1:04d}", "payload": order_payload}
    _processed_requests[idempotency_key] = result
    return result


def main():
    parser = argparse.ArgumentParser(description="Demonstrate retry with exponential backoff, jitter, and idempotency.")
    parser.add_argument("--max-attempts", type=int, default=5, help="Max retry attempts (default: 5)")
    parser.add_argument("--base-delay", type=float, default=0.3, help="Base delay in seconds for backoff (default: 0.3)")
    args = parser.parse_args()

    global call_flaky_api
    call_flaky_api = retry_with_backoff(
        max_attempts=args.max_attempts, base_delay=args.base_delay, retry_on=(TransientError,)
    )(call_flaky_api.__wrapped__)

    print("Part 1: Retry with exponential backoff + jitter")
    print("-" * 50)
    try:
        result = call_flaky_api(success_probability=0.4)
        print(f"SUCCESS: {result}")
    except TransientError as e:
        print(f"FAILED after all retries: {e}")

    print()
    print("Part 2: Idempotent retry (safe to call twice with same key)")
    print("-" * 50)
    key = "order-abc-123"
    first = create_order_idempotent({"item": "widget", "qty": 2}, key)
    print(f"First call result:  {first}")
    second = create_order_idempotent({"item": "widget", "qty": 2}, key)  # simulates a retried request
    print(f"Retry call result:  {second}")
    print(f"Same order returned both times: {first == second} (no duplicate order was created)")


if __name__ == "__main__":
    main()
