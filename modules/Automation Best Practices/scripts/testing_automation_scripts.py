#!/usr/bin/env python3
"""
testing_automation_scripts.py

Demonstrates writing unit tests for automation code that shells out
via `subprocess`, using `pytest` and `unittest.mock` to avoid actually
running real commands during tests (fast, reliable, no side effects).

Contains BOTH the automation function under test AND its pytest test
cases in one file, so you can see the pattern end-to-end.

Usage:
    # Run the automation function directly (executes a real command):
    python testing_automation_scripts.py

    # Run the unit tests (does NOT execute real commands — subprocess
    # is mocked out):
    pip install pytest
    pytest testing_automation_scripts.py -v

Expected output:
    Running the script directly prints the real disk-free percentage
    for the current directory. Running `pytest` instead runs 4 test
    cases (success, non-zero exit code, command-not-found, and timeout)
    that all pass in well under a second, without touching the real
    filesystem/network — because `subprocess.run` is mocked.
"""

import shutil
import subprocess
import sys


def get_disk_usage_percent(path: str = ".") -> int:
    """
    A small automation function that wraps `subprocess` to call the
    'df' command (falls back to shutil on platforms without df) and
    returns disk usage as a percentage. This is the function under test.
    """
    try:
        result = subprocess.run(
            ["df", "-P", path],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except FileNotFoundError:
        # 'df' isn't available (e.g. some Windows environments) — fall back.
        total, used, _free = shutil.disk_usage(path)
        return int(used / total * 100)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"'df' command failed with exit code {e.returncode}: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"'df' command timed out: {e}") from e

    # Parse the second line, second-to-last column: "Capacity" e.g. "42%"
    lines = result.stdout.strip().splitlines()
    if len(lines) < 2:
        raise RuntimeError(f"Unexpected 'df' output: {result.stdout!r}")
    fields = lines[1].split()
    capacity_str = fields[4].rstrip("%")
    return int(capacity_str)


def main():
    try:
        pct = get_disk_usage_percent(".")
        print(f"Disk usage for current path: {pct}%")
    except RuntimeError as e:
        print(f"Could not determine disk usage: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pytest test cases below. Pytest auto-discovers any function starting
# with `test_` in this file when you run: pytest testing_automation_scripts.py
# ---------------------------------------------------------------------------

try:
    import pytest
    from unittest.mock import patch, MagicMock
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


if HAS_PYTEST:

    def _fake_completed_process(stdout, returncode=0):
        cp = MagicMock()
        cp.stdout = stdout
        cp.returncode = returncode
        return cp

    def test_get_disk_usage_percent_success():
        """subprocess.run is mocked — no real 'df' command is executed."""
        fake_output = (
            "Filesystem     512-blocks      Used Available Capacity Mounted on\n"
            "/dev/disk1s1   500000000  210000000 290000000      42% /\n"
        )
        with patch("subprocess.run", return_value=_fake_completed_process(fake_output)) as mock_run:
            result = get_disk_usage_percent("/")
            assert result == 42
            mock_run.assert_called_once()
            # Verify the command that WOULD have been run, without running it.
            called_args = mock_run.call_args[0][0]
            assert called_args[0] == "df"

    def test_get_disk_usage_percent_command_fails():
        """A non-zero exit code should raise a clear RuntimeError."""
        error = subprocess.CalledProcessError(returncode=1, cmd=["df"], stderr="df: permission denied")
        with patch("subprocess.run", side_effect=error):
            with pytest.raises(RuntimeError, match="exit code 1"):
                get_disk_usage_percent("/restricted")

    def test_get_disk_usage_percent_command_missing_falls_back():
        """If 'df' isn't found, the function should fall back to shutil, not crash."""
        with patch("subprocess.run", side_effect=FileNotFoundError("df: command not found")):
            with patch("shutil.disk_usage", return_value=(1000, 500, 500)):
                result = get_disk_usage_percent(".")
                assert result == 50

    def test_get_disk_usage_percent_timeout():
        """A hung command should raise a RuntimeError, not hang the test suite."""
        timeout_error = subprocess.TimeoutExpired(cmd=["df"], timeout=5)
        with patch("subprocess.run", side_effect=timeout_error):
            with pytest.raises(RuntimeError, match="timed out"):
                get_disk_usage_percent(".")


if __name__ == "__main__":
    main()
