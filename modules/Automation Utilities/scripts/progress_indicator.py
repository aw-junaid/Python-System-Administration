#!/usr/bin/env python3
"""
progress_indicator.py
--------------------
A dependency-free iterable wrapper that prints a percentage-complete
progress bar as you iterate, similar in spirit to `tqdm` but with zero
external dependencies.

Usage as a library:
    from progress_indicator import progress

    for item in progress(my_list, label="Processing"):
        do_work(item)

Run directly for a demo:
    python progress_indicator.py
"""

import sys
import time


def progress(iterable, label="Progress", bar_width=30, stream=sys.stdout):
    """
    Wrap any sized iterable. Prints a live-updating progress bar of the
    form: "Label [####------] 40% (4/10)" and a newline once complete.
    """
    try:
        total = len(iterable)
    except TypeError:
        iterable = list(iterable)
        total = len(iterable)

    if total == 0:
        stream.write(f"{label}: nothing to do\n")
        return

    for index, item in enumerate(iterable, start=1):
        yield item
        pct = index / total
        filled = int(bar_width * pct)
        bar = "#" * filled + "-" * (bar_width - filled)
        stream.write(f"\r{label} [{bar}] {pct*100:5.1f}% ({index}/{total})")
        stream.flush()
        if index == total:
            stream.write("\n")


if __name__ == "__main__":
    print("Demo: iterating over 20 items with a live progress bar\n")
    for _ in progress(range(20), label="Working"):
        time.sleep(0.05)
    print("Done.")
