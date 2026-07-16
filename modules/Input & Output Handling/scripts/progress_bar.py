#!/usr/bin/env python3
"""
Topic: Display Progress Bars

Shows two approaches:
1. A manually implemented text progress bar (no dependencies).
2. A progress bar using the third-party 'tqdm' library (if installed).

Requires (optional): tqdm  (see requirements.txt)

Usage:
    python progress_bar.py

Expected Output:
    A manual progress bar filling up, followed by a tqdm progress bar
    (or a message saying tqdm is not installed).
"""

import sys
import time


def manual_progress_bar(total: int = 30, delay: float = 0.03) -> None:
    print("Manual progress bar:")
    for i in range(total + 1):
        percent = int((i / total) * 100)
        filled = int((i / total) * 30)
        bar = "#" * filled + "-" * (30 - filled)
        sys.stdout.write(f"\r[{bar}] {percent}%")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def tqdm_progress_bar(total: int = 30, delay: float = 0.03) -> None:
    try:
        from tqdm import tqdm
    except ImportError:
        print("\ntqdm is not installed. Install it with: pip install tqdm")
        return

    print("\ntqdm progress bar:")
    for _ in tqdm(range(total)):
        time.sleep(delay)


def main() -> None:
    manual_progress_bar()
    tqdm_progress_bar()


if __name__ == "__main__":
    main()
