#!/usr/bin/env python3
"""
multiprocessing_utils.py
--------------------
Parallelize CPU-bound work across real OS processes using
`multiprocessing`, bypassing the GIL entirely (unlike threading_utils.py
or parallel_execution.py, which are best for I/O-bound work since
Python threads can't run CPU-bound bytecode in parallel).

Usage as a library:
    from multiprocessing_utils import parallel_map_processes

    results = parallel_map_processes(cpu_heavy_func, items, workers=4)

Run directly for a demo (compares process-pool vs sequential timing):
    python multiprocessing_utils.py

Note: the worker function must be defined at module level (importable
by name) because multiprocessing pickles it to send to child processes
-- this is why the demo function below lives at the top of the file
rather than inside `if __name__ == "__main__":`.
"""

import time
from multiprocessing import Pool, cpu_count


def parallel_map_processes(func, items, workers=None):
    """
    Run `func(item)` for every item in `items`, distributed across a
    process pool. Returns results in the same order as the input.
    `workers` defaults to the machine's CPU count.
    """
    workers = workers or cpu_count()
    with Pool(processes=workers) as pool:
        return pool.map(func, items)


def _cpu_bound_work(n):
    """A deliberately expensive pure-CPU computation for the demo."""
    total = 0
    for i in range(n):
        total += i * i
    return total


if __name__ == "__main__":
    items = [3_000_000] * 8

    print(f"Demo: {len(items)} CPU-bound tasks (summing squares up to {items[0]:,})")
    print(f"Machine has {cpu_count()} CPU core(s) available.\n")

    start = time.monotonic()
    sequential_results = [_cpu_bound_work(n) for n in items]
    sequential_time = time.monotonic() - start
    print(f"Sequential: {sequential_time:.2f}s")

    start = time.monotonic()
    parallel_results = parallel_map_processes(_cpu_bound_work, items)
    parallel_time = time.monotonic() - start
    print(f"Multiprocessing (Pool): {parallel_time:.2f}s")

    assert sequential_results == parallel_results, "results should match"
    speedup = sequential_time / parallel_time if parallel_time > 0 else float("inf")
    print(f"\nResults match. Speedup: {speedup:.2f}x "
          f"(actual speedup depends on available CPU cores)")
