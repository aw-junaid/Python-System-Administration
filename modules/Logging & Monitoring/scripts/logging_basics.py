#!/usr/bin/env python3
"""
logging_basics.py
------------------
Introduction to Python's built-in `logging` module: setting up a logger,
choosing a log level, and formatting messages.

Usage:
    python3 logging_basics.py
"""

import logging

# 1. Basic configuration: level, format, output destination
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 2. Create a named logger (best practice instead of using the root logger)
logger = logging.getLogger("logging_basics_demo")


def main():
    logger.debug("This is a DEBUG message - detailed diagnostic info")
    logger.info("This is an INFO message - confirms things work as expected")
    logger.warning("This is a WARNING message - something unexpected happened")
    logger.error("This is an ERROR message - a serious problem occurred")
    logger.critical("This is a CRITICAL message - the program may be unable to continue")

    # Logging with variables
    user = "ahmad"
    logger.info("User '%s' logged in successfully", user)


if __name__ == "__main__":
    main()
