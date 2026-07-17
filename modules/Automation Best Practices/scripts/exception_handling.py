#!/usr/bin/env python3
"""
exception_handling.py

Demonstrates proper exception handling: catching SPECIFIC exception
types instead of a bare `except:`, preserving tracebacks with
`raise ... from e`, and only handling the errors you actually expect.

Usage:
    python exception_handling.py

Expected output:
    The script runs four small "automation tasks" (read a missing file,
    divide by zero, convert bad data, and write to a location without
    permission). Each failure is caught by a SPECIFIC exception handler
    and printed as a clear, actionable message — instead of crashing
    with an unhandled traceback or silently swallowing the error with
    a bare `except:`. A final summary line shows how many tasks
    succeeded vs. failed.
"""

import json
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("exception_handling_demo")


# ---------------------------------------------------------------------------
# ANTI-PATTERN (shown only as a comment, never executed):
#
#   try:
#       do_something()
#   except:                # <-- catches EVERYTHING, including
#       pass                #     KeyboardInterrupt and SystemExit,
#                            #     and hides real bugs. Avoid this.
#
# GOOD PATTERN: catch the specific exception(s) you expect and know
# how to recover from, and let unexpected exceptions propagate.
# ---------------------------------------------------------------------------


def read_config_file(path: str) -> dict:
    """Read and parse a JSON config file, handling only expected failures."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Config file not found at '%s'; using defaults.", path)
        return {}
    except json.JSONDecodeError as e:
        logger.error("Config file '%s' contains invalid JSON: %s", path, e)
        raise ValueError(f"Could not parse config file: {path}") from e
    except PermissionError:
        logger.error("No permission to read config file '%s'.", path)
        raise


def divide_metrics(total: float, count: int) -> float:
    """Compute an average, handling only the specific error we expect."""
    try:
        return total / count
    except ZeroDivisionError:
        logger.warning("Count was zero; returning 0.0 instead of dividing.")
        return 0.0
    except TypeError as e:
        logger.error("Invalid types passed to divide_metrics: %s", e)
        raise


def parse_int_setting(raw_value: str) -> int:
    """Convert a string setting to int, handling only bad-format input."""
    try:
        return int(raw_value)
    except ValueError as e:
        logger.error("Setting %r is not a valid integer.", raw_value)
        raise ValueError(f"Expected an integer, got: {raw_value!r}") from e


def write_report(path: str, content: str) -> None:
    """Write a report file, handling only permission/path errors."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except PermissionError:
        logger.error("No permission to write to '%s'.", path)
        raise
    except FileNotFoundError:
        logger.error("Directory for '%s' does not exist.", path)
        raise
    except OSError as e:
        # Catch-all for OS-level issues (disk full, invalid path, etc.)
        # Still specific to OSError, not a bare except.
        logger.error("OS error while writing '%s': %s", path, e)
        raise


def run_task(name: str, func, *args, **kwargs) -> bool:
    """Run a task, printing success/failure without hiding unexpected errors."""
    try:
        result = func(*args, **kwargs)
        logger.info("Task %-22s -> OK (result=%r)", name, result)
        return True
    except (FileNotFoundError, ValueError, PermissionError, OSError) as e:
        # We explicitly know these can happen and how to report them.
        logger.info("Task %-22s -> HANDLED FAILURE (%s: %s)", name, type(e).__name__, e)
        return False
    # NOTE: anything other than the exceptions above (e.g. a bug causing a
    # KeyError we didn't anticipate) is intentionally NOT caught here, so
    # it surfaces as a real traceback instead of being hidden.


def main():
    print("Exception Handling Demo")
    print("=" * 40)

    results = []
    results.append(run_task("read_missing_config", read_config_file, "/nonexistent/config.json"))
    results.append(run_task("divide_by_zero", divide_metrics, 100, 0))
    results.append(run_task("parse_bad_int", parse_int_setting, "not-a-number"))
    results.append(run_task("write_to_bad_path", write_report, "/root/forbidden/report.txt", "data"))

    succeeded = sum(1 for r in results if r)
    print("=" * 40)
    print(f"Summary: {succeeded}/{len(results)} tasks completed without needing a handled failure.")
    print("(All failures above were caught by SPECIFIC exception types, not a bare 'except:'.)")


if __name__ == "__main__":
    main()
