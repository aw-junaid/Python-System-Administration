#!/usr/bin/env python3
"""
install_packages.py
--------------------
Auto-provision Python packages using `pip install` run inside a subprocess.

Usage:
    python install_packages.py requests flask "django>=4.0"
    python install_packages.py --user requests
    python install_packages.py --python /path/to/venv/bin/python requests

Exit codes:
    0  -> all packages installed successfully
    1  -> one or more packages failed to install
    2  -> bad arguments / nothing to install
"""

import argparse
import subprocess
import sys


def build_pip_command(python_exe, packages, user_flag, upgrade_flag, extra_index):
    cmd = [python_exe, "-m", "pip", "install"]
    if user_flag:
        cmd.append("--user")
    if upgrade_flag:
        cmd.append("--upgrade")
    if extra_index:
        cmd.extend(["--extra-index-url", extra_index])
    cmd.extend(packages)
    return cmd


def install_packages(packages, python_exe=sys.executable, user_flag=False,
                      upgrade_flag=False, extra_index=None):
    """Install a list of package specifiers. Returns (succeeded, failed) lists."""
    succeeded, failed = [], []

    for pkg in packages:
        cmd = build_pip_command(python_exe, [pkg], user_flag, upgrade_flag, extra_index)
        print(f"[install] Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            print(f"[install] TIMEOUT while installing '{pkg}'")
            failed.append(pkg)
            continue
        except FileNotFoundError:
            print(f"[install] ERROR: interpreter '{python_exe}' not found")
            failed.append(pkg)
            continue

        if result.returncode == 0:
            print(f"[install] OK: {pkg}")
            succeeded.append(pkg)
        else:
            print(f"[install] FAILED: {pkg}")
            print(result.stderr.strip()[-800:])  # last part of stderr is usually the reason
            failed.append(pkg)

    return succeeded, failed


def main():
    parser = argparse.ArgumentParser(description="Install Python packages via pip.")
    parser.add_argument("packages", nargs="*", help="Package specifiers, e.g. requests 'flask>=2.0'")
    parser.add_argument("--user", action="store_true", help="Install into user site-packages")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade if already installed")
    parser.add_argument("--python", default=sys.executable, help="Path to target python interpreter")
    parser.add_argument("--extra-index", default=None, help="Extra package index URL (private repos, etc.)")
    args = parser.parse_args()

    if not args.packages:
        print("No packages specified. Example: python install_packages.py requests flask")
        sys.exit(2)

    succeeded, failed = install_packages(
        args.packages,
        python_exe=args.python,
        user_flag=args.user,
        upgrade_flag=args.upgrade,
        extra_index=args.extra_index,
    )

    print("\n--- Summary ---")
    print(f"Succeeded ({len(succeeded)}): {', '.join(succeeded) or 'none'}")
    print(f"Failed    ({len(failed)}): {', '.join(failed) or 'none'}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
