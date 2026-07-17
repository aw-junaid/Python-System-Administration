#!/usr/bin/env python3
"""
generate_warnings.py
---------------------
Demonstrates how to generate warning messages in Python using the
built-in `warnings` module (different from logging warnings).

Usage:
    python3 generate_warnings.py
"""

import warnings


def divide(a, b):
    if b == 0:
        warnings.warn("Division by zero attempted, returning None", RuntimeWarning)
        return None
    return a / b


def deprecated_function():
    warnings.warn(
        "deprecated_function() is deprecated, use new_function() instead",
        DeprecationWarning,
        stacklevel=2,
    )


def main():
    # Make sure warnings are always shown (Python hides duplicates by default)
    warnings.simplefilter("always")

    print("Result:", divide(10, 2))
    print("Result:", divide(10, 0))  # triggers RuntimeWarning

    deprecated_function()  # triggers DeprecationWarning

    # Custom warning category example
    class DiskSpaceWarning(UserWarning):
        pass

    warnings.warn("Disk space is running low", DiskSpaceWarning)


if __name__ == "__main__":
    main()
