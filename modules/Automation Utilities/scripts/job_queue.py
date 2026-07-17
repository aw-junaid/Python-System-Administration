#!/usr/bin/env python3
"""
job_queue.py
--------------------
Minimal task-queue orchestration helpers for Redis-backed job queues
(the most common lightweight setup). Provides an enqueue/dequeue API
that mirrors what you'd do with RabbitMQ (via `pika`) or Celery, but
without those heavier dependencies.

Requires a running Redis server and the `redis` package:
    pip install redis

If `redis` is not installed, this script still runs its demo using an
in-memory fallback queue so you can see the API/behavior, but that
fallback is single-process only and NOT a substitute for real Redis in
production (no persistence, no multi-process sharing).

Usage as a library (with real Redis):
    from job_queue import RedisJobQueue

    q = RedisJobQueue(queue_name="emails", redis_url="redis://localhost:6379/0")
    q.enqueue({"to": "user@example.com", "subject": "Hi"})

    job = q.dequeue(timeout=5)
    if job:
        send_email(job)

Run directly for a demo:
    python job_queue.py
"""

import json
import time
import queue as _queue

try:
    import redis  # type: ignore
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisJobQueue:
    """A simple FIFO job queue backed by a Redis list (LPUSH/BRPOP)."""

    def __init__(self, queue_name="default", redis_url="redis://localhost:6379/0"):
        if not REDIS_AVAILABLE:
            raise RuntimeError(
                "The 'redis' package is not installed. Run: pip install redis"
            )
        self.queue_name = queue_name
        self.client = redis.from_url(redis_url)

    def enqueue(self, job: dict):
        """Push a JSON-serializable job onto the queue."""
        self.client.lpush(self.queue_name, json.dumps(job))

    def dequeue(self, timeout=0):
        """
        Block up to `timeout` seconds (0 = wait forever) for a job.
        Returns the deserialized job dict, or None if timed out.
        """
        result = self.client.brpop(self.queue_name, timeout=timeout)
        if result is None:
            return None
        _, raw = result
        return json.loads(raw)

    def queue_length(self):
        return self.client.llen(self.queue_name)


class InMemoryJobQueue:
    """
    Single-process fallback with the same enqueue/dequeue API, used only
    when `redis` isn't installed (e.g. for this script's demo, or quick
    local testing). Not shared across processes -- use RedisJobQueue for
    anything real.
    """

    def __init__(self, queue_name="default"):
        self.queue_name = queue_name
        self._q = _queue.Queue()

    def enqueue(self, job: dict):
        self._q.put(json.dumps(job))

    def dequeue(self, timeout=0):
        try:
            raw = self._q.get(timeout=timeout if timeout else None)
        except _queue.Empty:
            return None
        return json.loads(raw)

    def queue_length(self):
        return self._q.qsize()


def get_job_queue(queue_name="default", redis_url="redis://localhost:6379/0"):
    """Factory: returns a real RedisJobQueue if redis is available and
    reachable, otherwise falls back to InMemoryJobQueue with a warning."""
    if REDIS_AVAILABLE:
        try:
            q = RedisJobQueue(queue_name, redis_url)
            q.client.ping()
            return q
        except Exception as exc:
            print(f"[job_queue] Could not reach Redis at {redis_url} ({exc}). "
                  f"Falling back to in-memory queue.")
    else:
        print("[job_queue] 'redis' package not installed. "
              "Falling back to in-memory queue. Run: pip install redis")
    return InMemoryJobQueue(queue_name)


if __name__ == "__main__":
    print("Demo: enqueue 5 jobs, then process them via dequeue()\n")

    q = get_job_queue(queue_name="demo-jobs")

    for i in range(1, 6):
        q.enqueue({"job_id": i, "task": "send_report", "created": time.time()})
    print(f"Enqueued 5 jobs. Queue length: {q.queue_length()}\n")

    processed = 0
    while True:
        job = q.dequeue(timeout=1)
        if job is None:
            break
        print(f"  processed job {job['job_id']} ({job['task']})")
        processed += 1

    print(f"\nProcessed {processed} job(s). Queue length now: {q.queue_length()}")
