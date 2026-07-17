#!/usr/bin/env python3
"""
logging_best_practices.py

Demonstrates proper use of Python's `logging` module: appropriate log
levels (DEBUG/INFO/WARNING/ERROR/CRITICAL), a console handler AND a
rotating file handler, structured formatting, and avoiding `print()`
for anything other than final user-facing output.

Usage:
    python logging_best_practices.py
    python logging_best_practices.py --log-file automation.log --verbose

Expected output:
    Console output showing INFO-and-above messages by default (or
    DEBUG-and-above with --verbose), plus a rotating log file
    (default: automation.log) containing ALL levels including DEBUG,
    each line timestamped and tagged with its level and logger name.
    The script simulates a small backup task to show realistic
    level usage: DEBUG for internals, INFO for milestones, WARNING
    for recoverable issues, ERROR for failures, CRITICAL for
    unrecoverable failures.
"""

import argparse
import logging
import logging.handlers
import os
import random
import sys


def build_logger(log_file: str, verbose: bool) -> logging.Logger:
    logger = logging.getLogger("automation")
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter what's shown
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler: INFO by default, DEBUG if --verbose was passed.
    # Rule of thumb: console/operators see INFO+, files keep DEBUG for
    # later troubleshooting.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler: keeps full DEBUG history without growing
    # forever (5 files x 1MB each).
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def simulate_backup_task(logger: logging.Logger, files):
    """A small fake automation task demonstrating each log level's purpose."""
    logger.info("Backup task started for %d file(s).", len(files))

    backed_up = 0
    for f in files:
        logger.debug("Preparing to back up file: %s", f)  # low-level internal detail

        if f.endswith(".tmp"):
            logger.warning("Skipping temp file (recoverable, non-fatal): %s", f)
            continue

        # Simulate an occasional transient failure
        if random.random() < 0.2:
            logger.error("Failed to copy file (will be retried by caller): %s", f)
            continue

        logger.debug("Copied %s successfully.", f)
        backed_up += 1

    if backed_up == 0:
        logger.critical("No files were backed up at all — backup job effectively failed.")
    else:
        logger.info("Backup task finished: %d/%d file(s) backed up.", backed_up, len(files))


def main():
    parser = argparse.ArgumentParser(description="Demonstrate logging best practices with a simulated backup task.")
    parser.add_argument("--log-file", default="automation.log", help="Path to the rotating log file (default: automation.log)")
    parser.add_argument("--verbose", action="store_true", help="Show DEBUG-level messages on the console too")
    args = parser.parse_args()

    logger = build_logger(args.log_file, args.verbose)

    sample_files = ["report.csv", "cache.tmp", "database.sql", "session.tmp", "photos.zip"]
    simulate_backup_task(logger, sample_files)

    print()
    print(f"Full DEBUG-level log written to: {os.path.abspath(args.log_file)}")
    print("Run again with --verbose to also see DEBUG messages on the console.")


if __name__ == "__main__":
    main()
