#!/usr/bin/env python3
"""
cross_platform_scripting.py

Demonstrates writing automation that works correctly on Windows,
macOS, and Linux without modification: using `pathlib` instead of
hardcoded `/` or `\\` path separators, `os.devnull` instead of a
hardcoded "/dev/null" or "NUL", detecting the OS only when truly
necessary, and handling line endings and environment variables in a
portable way.

Usage:
    python cross_platform_scripting.py

Expected output:
    A report showing: the detected OS, a correctly-joined path built
    with pathlib (using the right separator for your OS), the correct
    null device path for your OS, the path separator used in the PATH
    environment variable, and a demonstration of discarding subprocess
    output portably (redirecting to the OS null device) instead of a
    hardcoded Unix-only "/dev/null".
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# ANTI-PATTERN (never do this):
#
#   log_path = "logs" + "/" + "app.log"          # breaks on Windows
#   subprocess.run(["cmd"], stdout=open("/dev/null", "w"))  # breaks on Windows
#   config_path = "C:\\configs\\app.ini"          # breaks on Linux/macOS
#
# GOOD PATTERN: pathlib + os.devnull + os.pathsep, which adapt
# automatically to whatever OS the script is running on.
# ---------------------------------------------------------------------------


def build_portable_path() -> Path:
    """pathlib's `/` operator uses the correct separator for the current OS."""
    return Path("automation_workspace") / "logs" / "app.log"


def get_null_device() -> str:
    """os.devnull is '/dev/null' on Unix and 'nul' on Windows — never hardcode either."""
    return os.devnull


def get_path_separator() -> str:
    """os.pathsep is ':' on Unix and ';' on Windows (used to split $PATH / %PATH%)."""
    return os.pathsep


def run_command_discarding_output(command: list) -> int:
    """Run a command and discard its output, portably, using os.devnull."""
    with open(os.devnull, "w") as devnull:
        try:
            result = subprocess.run(command, stdout=devnull, stderr=devnull, timeout=5)
            return result.returncode
        except FileNotFoundError:
            return -1


def get_temp_dir_portable() -> Path:
    """Use tempfile for a portable temp directory instead of hardcoding /tmp."""
    import tempfile
    return Path(tempfile.gettempdir())


def detect_os_when_necessary() -> str:
    """
    Most code should be OS-agnostic via pathlib/os.*; only branch on the
    OS name for the rare cases that truly need it (e.g. choosing between
    'ping -c 1' on Unix vs 'ping -n 1' on Windows).
    """
    system = platform.system()
    if system == "Windows":
        ping_count_flag = "-n"
    else:
        ping_count_flag = "-c"
    return f"{system} detected -> would use 'ping {ping_count_flag} 1 host' for a single ping"


def main():
    print("Cross-Platform Scripting Demo")
    print("=" * 40)
    print(f"Detected OS:        {platform.system()} ({platform.platform()})")
    print(f"Path separator:     {os.sep!r}   (used by pathlib automatically)")
    print(f"PATH list sep:      {get_path_separator()!r}   (os.pathsep, splits $PATH / %PATH%)")
    print(f"Null device:        {get_null_device()!r}   (os.devnull)")
    print(f"Portable path:      {build_portable_path()}")
    print(f"Portable temp dir:  {get_temp_dir_portable()}")
    print(f"OS-specific branch: {detect_os_when_necessary()}")

    ping_target = "127.0.0.1"
    if platform.system() == "Windows":
        command = ["ping", "-n", "1", ping_target]
    else:
        command = ["ping", "-c", "1", ping_target]

    print(f"\nRunning a portable, output-discarding command: {' '.join(command)}")
    rc = run_command_discarding_output(command)
    if rc == 0:
        print("Command succeeded (output was discarded via os.devnull, not a hardcoded path).")
    elif rc == -1:
        print("'ping' not available in this environment — that's fine, the portability pattern still applies.")
    else:
        print(f"Command exited with code {rc}.")


if __name__ == "__main__":
    main()
