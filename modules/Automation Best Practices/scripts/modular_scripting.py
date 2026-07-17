#!/usr/bin/env python3
"""
modular_scripting.py

Demonstrates breaking a "monolithic" automation script into small,
reusable, independently-testable functions and a class — instead of
one giant script with everything inline. Builds a small system report
by composing focused functions, each with a single responsibility.

Usage:
    python modular_scripting.py

Expected output:
    A short system report printed to the console (platform, Python
    version, CPU count, disk usage of the current drive, and current
    working directory), assembled by a `SystemReportBuilder` class
    that delegates each piece of data collection to its own small
    function. You can reuse `gather_platform_info()`,
    `gather_python_info()`, etc. independently in other scripts, and
    unit test each one in isolation.
"""

import os
import platform
import shutil
from dataclasses import dataclass, field
from typing import Callable, Dict


# ---------------------------------------------------------------------------
# ANTI-PATTERN (shown only as a comment):
#
#   def main():
#       print(platform.system())
#       print(platform.release())
#       print(f"CPUs: {os.cpu_count()}")
#       total, used, free = shutil.disk_usage("/")
#       print(f"Disk free: {free // (1024**3)} GB")
#       ... 200 more lines, all inline, nothing reusable or testable ...
#
# GOOD PATTERN: small, focused, independently-testable functions,
# composed together by a coordinating class or function.
# ---------------------------------------------------------------------------


def gather_platform_info() -> Dict[str, str]:
    """Single responsibility: describe the OS/platform."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
    }


def gather_python_info() -> Dict[str, str]:
    """Single responsibility: describe the Python runtime."""
    return {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
    }


def gather_cpu_info() -> Dict[str, int]:
    """Single responsibility: describe CPU resources."""
    return {"logical_cpus": os.cpu_count() or 0}


def gather_disk_info(path: str = ".") -> Dict[str, int]:
    """Single responsibility: describe disk usage for a given path."""
    total, used, free = shutil.disk_usage(path)
    gb = 1024 ** 3
    return {
        "total_gb": round(total / gb, 1),
        "used_gb": round(used / gb, 1),
        "free_gb": round(free / gb, 1),
    }


def gather_cwd_info() -> Dict[str, str]:
    """Single responsibility: describe the current working directory."""
    return {"cwd": os.getcwd()}


@dataclass
class SystemReportBuilder:
    """
    Coordinates independent data-gathering functions into one report.
    Each 'section' is a (name, function) pair — new sections can be
    added without touching the gathering functions themselves, and
    each function can be unit tested completely on its own.
    """

    sections: Dict[str, Callable[[], dict]] = field(default_factory=lambda: {
        "Platform": gather_platform_info,
        "Python": gather_python_info,
        "CPU": gather_cpu_info,
        "Disk (current path)": gather_disk_info,
        "Working Directory": gather_cwd_info,
    })

    def build(self) -> Dict[str, dict]:
        return {name: fn() for name, fn in self.sections.items()}

    def render_text(self) -> str:
        report = self.build()
        lines = ["System Report", "=" * 40]
        for section, data in report.items():
            lines.append(f"\n[{section}]")
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)


def main():
    builder = SystemReportBuilder()
    print(builder.render_text())
    print()
    print("Each section above came from its own small, reusable function —")
    print("e.g. gather_disk_info() can be imported and reused in other scripts.")


if __name__ == "__main__":
    main()
