#!/usr/bin/env python3
"""
performance_optimization.py

Demonstrates profiling a script with `cProfile` to FIND bottlenecks
before optimizing (rather than guessing), then shows a concrete
before/after optimization for a common automation mistake (repeated
O(n) membership checks against a list vs. a set).

Usage:
    python performance_optimization.py

Expected output:
    Two cProfile reports printed to the console: one for a slow,
    unoptimized function and one for a fast, optimized version doing
    the same logical work. The report is sorted by cumulative time so
    the worst offender is at the top. A final summary line shows the
    measured wall-clock speedup. A file `profile_slow.prof` is also
    written, which you can inspect further with `snakeviz` or `pstats`.
"""

import cProfile
import io
import pstats
import time


DATA_SIZE = 20_000
LOOKUP_COUNT = 20_000


def slow_membership_checks():
    """
    Common automation anti-pattern: checking membership against a LIST
    in a loop is O(n) per check -> O(n*m) total. Easy to write by
    accident when processing e.g. "is this hostname in my allow-list?"
    for every line of a large log file.
    """
    allow_list = list(range(DATA_SIZE))  # a list, not a set
    found = 0
    for i in range(LOOKUP_COUNT):
        if i in allow_list:  # O(n) scan every time
            found += 1
    return found


def fast_membership_checks():
    """Same logical result, but using a set for O(1) average-case membership checks."""
    allow_set = set(range(DATA_SIZE))  # a set, not a list
    found = 0
    for i in range(LOOKUP_COUNT):
        if i in allow_set:  # O(1) average
            found += 1
    return found


def profile_function(func, label: str, save_to: str = None) -> float:
    """Run cProfile on `func`, print a sorted report, and return elapsed wall time."""
    profiler = cProfile.Profile()

    start = time.perf_counter()
    profiler.enable()
    func()
    profiler.disable()
    elapsed = time.perf_counter() - start

    print(f"\n{'=' * 60}\nProfile: {label}  (wall time: {elapsed:.4f}s)\n{'=' * 60}")
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(5)  # top 5 costliest calls
    print(stream.getvalue())

    if save_to:
        profiler.dump_stats(save_to)

    return elapsed


def main():
    print("Performance Optimization Demo (cProfile)")

    slow_time = profile_function(slow_membership_checks, "UNOPTIMIZED (list membership checks)", save_to="profile_slow.prof")
    fast_time = profile_function(fast_membership_checks, "OPTIMIZED (set membership checks)", save_to="profile_fast.prof")

    speedup = slow_time / fast_time if fast_time > 0 else float("inf")
    print("=" * 60)
    print(f"Summary: optimized version was ~{speedup:.1f}x faster "
          f"({slow_time:.4f}s -> {fast_time:.4f}s) for the same {LOOKUP_COUNT:,} lookups.")
    print("Detailed profiles saved to profile_slow.prof / profile_fast.prof")
    print("(Tip: inspect them visually with: pip install snakeviz && snakeviz profile_slow.prof)")


if __name__ == "__main__":
    main()
