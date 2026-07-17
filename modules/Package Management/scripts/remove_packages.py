#!/usr/bin/env python3
"""
remove_packages.py
--------------------
Safely uninstall one or more Python packages via `pip uninstall`.

"Safely" here means:
  - Requires explicit confirmation (unless --yes is passed)
  - Refuses to uninstall a small protected list of critical packages
    (pip, setuptools, wheel) unless --force is given
  - Reports clearly which packages were removed vs skipped vs failed

Usage:
    python remove_packages.py requests flask
    python remove_packages.py requests --yes
    python remove_packages.py pip --force --yes

Exit codes:
    0 -> all requested removals succeeded (or nothing to do)
    1 -> one or more removals failed
    2 -> bad arguments
"""

import argparse
import subprocess
import sys

PROTECTED = {"pip", "setuptools", "wheel"}


def confirm(packages):
    names = ", ".join(packages)
    reply = input(f"About to uninstall: {names}\nProceed? [y/N]: ").strip().lower()
    return reply == "y"


def remove_packages(packages, python_exe=sys.executable, force=False):
    to_remove = []
    skipped = []

    for pkg in packages:
        if pkg.lower() in PROTECTED and not force:
            skipped.append(pkg)
        else:
            to_remove.append(pkg)

    if skipped:
        print(f"[remove] Skipping protected package(s) (use --force to override): {', '.join(skipped)}")

    succeeded, failed = [], []
    for pkg in to_remove:
        cmd = [python_exe, "-m", "pip", "uninstall", "-y", pkg]
        print(f"[remove] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"[remove] OK: {pkg}")
            succeeded.append(pkg)
        else:
            print(f"[remove] FAILED: {pkg}")
            print(result.stderr.strip()[-800:])
            failed.append(pkg)

    return succeeded, failed, skipped


def main():
    parser = argparse.ArgumentParser(description="Safely uninstall Python packages.")
    parser.add_argument("packages", nargs="*", help="Package names to remove")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    parser.add_argument("--force", action="store_true", help="Allow removing protected packages (pip, setuptools, wheel)")
    parser.add_argument("--python", default=sys.executable, help="Path to target python interpreter")
    args = parser.parse_args()

    if not args.packages:
        print("No packages specified. Example: python remove_packages.py requests flask")
        sys.exit(2)

    if not args.yes and not confirm(args.packages):
        print("Aborted, no changes made.")
        sys.exit(0)

    succeeded, failed, skipped = remove_packages(args.packages, python_exe=args.python, force=args.force)

    print("\n--- Summary ---")
    print(f"Removed ({len(succeeded)}): {', '.join(succeeded) or 'none'}")
    print(f"Failed  ({len(failed)}): {', '.join(failed) or 'none'}")
    print(f"Skipped ({len(skipped)}): {', '.join(skipped) or 'none'}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
