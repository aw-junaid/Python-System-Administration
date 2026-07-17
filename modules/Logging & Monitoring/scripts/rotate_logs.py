#!/usr/bin/env python3
"""
rotate_logs.py
-----------------
Demonstrates automatic log rotation using RotatingFileHandler.
When the log file reaches a set size, it is rotated (renamed) and a
fresh file is started, keeping a limited number of backups.

Usage:
    python3 rotate_logs.py
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "rotating.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("rotate_logs_demo")
logger.setLevel(logging.INFO)

# Rotate when file reaches ~1 KB, keep 3 backup files (rotating.log.1, .2, .3)
handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1024,
    backupCount=3,
)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    # Write enough log lines to trigger multiple rotations
    for i in range(200):
        logger.info("Log entry number %d - sample log rotation test message", i)

    print(f"Rotating logs written to: {LOG_DIR}/")
    print("Check the folder - you should see rotating.log, rotating.log.1, .2, .3")


if __name__ == "__main__":
    main()
