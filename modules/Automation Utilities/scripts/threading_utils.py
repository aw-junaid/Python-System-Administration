#!/usr/bin/env python3
"""
threading_utils.py
--------------------
Helpers for handling I/O-bound concurrent workloads safely with the
`threading` module directly (as opposed to parallel_execution.py, which
wraps ThreadPoolExecutor for simple map-style jobs). Includes:

  - a thread-safe Counter using a Lock
  - a worker-pool pattern using a Queue for producer/consumer workloads

Usage as a library:
    from threading_utils import SafeCounter, run_worker_pool

    counter = SafeCounter()
    counter.increment()

    run_worker_pool(worker_fn, work_items, num_workers=4)

Run directly for a demo:
    python threading_utils.py
"""

import queue
import threading
import time


class SafeCounter:
    """A counter safe to increment from multiple threads at once."""

    def __init__(self, start=0):
        self._value = start
        self._lock = threading.Lock()

    def increment(self, amount=1):
        with self._lock:
            self._value += amount
            return self._value

    @property
    def value(self):
        with self._lock:
            return self._value


def run_worker_pool(worker_fn, items, num_workers=4):
    """
    Classic producer/consumer pattern: put all `items` on a Queue, then
    start `num_workers` threads that each pull items off the queue and
    call `worker_fn(item)` until the queue is empty. Safe because Queue
    itself is thread-safe -- no manual locking needed for the handoff.
    Blocks until all items are processed.
    """
    q = queue.Queue()
    for item in items:
        q.put(item)

    def worker():
        while True:
            try:
                item = q.get_nowait()
            except queue.Empty:
                return
            try:
                worker_fn(item)
            finally:
                q.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(num_workers)]
    for t in threads:
        t.start()
    q.join()
    for t in threads:
        t.join()


if __name__ == "__main__":
    print("Demo 1: SafeCounter incremented from 10 threads, 1000 times each\n")
    counter = SafeCounter()

    def bump():
        for _ in range(1000):
            counter.increment()

    threads = [threading.Thread(target=bump) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Expected: 10000, Actual: {counter.value}  "
          f"({'correct -- no race condition' if counter.value == 10000 else 'MISMATCH'})")

    print("\nDemo 2: worker pool processing 10 items with 3 workers\n")
    processed = SafeCounter()

    def process_item(item):
        time.sleep(0.05)
        processed.increment()
        print(f"  processed item {item} on {threading.current_thread().name}")

    run_worker_pool(process_item, list(range(1, 11)), num_workers=3)
    print(f"\nTotal processed: {processed.value}")
