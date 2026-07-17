#!/usr/bin/env python3
"""
parallel_execution.py
--------------------
Map a function over an iterable concurrently using
concurrent.futures.ThreadPoolExecutor -- ideal for I/O-bound work
(network calls, file I/O) where threads spend most of their time
waiting rather than computing.

For CPU-bound work that needs to bypass the GIL, use
multiprocessing_utils.py instead.

Usage as a library:
    from parallel_execution import parallel_map

    results = parallel_map(fetch_url, list_of_urls, max_workers=8)

Run directly for a demo:
    python parallel_execution.py
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def parallel_map(func, items, max_workers=4, on_error=None):
    """
    Run `func(item)` for every item in `items` concurrently.
    Returns a list of results in the SAME ORDER as the input items.
    If a call raises and `on_error` is given, `on_error(item, exc)` is
    called and that slot is filled with None; otherwise the exception
    propagates.
    """
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(func, item): idx for idx, item in enumerate(items)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                if on_error is not None:
                    on_error(items[idx], exc)
                    results[idx] = None
                else:
                    raise
    return results


if __name__ == "__main__":
    def simulated_io_task(n):
        time.sleep(0.3)  # pretend this is a network request
        return n * n

    items = list(range(1, 9))

    print(f"Demo: squaring {len(items)} numbers, each simulating 0.3s of I/O\n")
    start = time.monotonic()
    results = parallel_map(simulated_io_task, items, max_workers=8)
    elapsed = time.monotonic() - start

    print(f"Input:   {items}")
    print(f"Results: {results}")
    print(f"\nElapsed: {elapsed:.2f}s (sequential would take ~{0.3*len(items):.1f}s)")
