#!/usr/bin/env python3
"""
log_warnings_errors.py
------------------------
Logs WARNING and ERROR level messages, each tagged with a custom error
code, to a log file for later inspection.

Usage:
    python3 log_warnings_errors.py
"""

import logging
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "warnings_errors.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] [code=%(error_code)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_FILE,
    filemode="a",
)

logger = logging.getLogger("warnings_errors_demo")


def log_warning(message, error_code="W000"):
    logger.warning(message, extra={"error_code": error_code})


def log_error(message, error_code="E000"):
    logger.error(message, extra={"error_code": error_code})


def main():
    log_warning("Disk usage above 80%", error_code="W101")
    log_warning("Response time degraded", error_code="W102")
    log_error("Failed to connect to database", error_code="E201")
    log_error("Unhandled exception in worker thread", error_code="E202")

    print(f"Warnings and errors logged to: {LOG_FILE}")


if __name__ == "__main__":
    main()
