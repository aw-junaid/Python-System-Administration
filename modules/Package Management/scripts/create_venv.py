#!/usr/bin/env python3
"""
create_venv.py
--------------------
Build an isolated Python virtual environment using the standard-library
`venv` module.

Usage:
    python create_venv.py myenv
    python create_venv.py myenv --python python3.11
    python create_venv.py myenv --with-pip-upgrade
    python create_venv.py myenv --clear     # wipe and recreate if it exists

Exit codes:
    0 -> venv created successfully
    1 -> creation failed
    2 -> bad arguments
"""

import argparse
import subprocess
import sys
import venv
from pathlib import Path


def create_venv(target_dir, clear=False, upgrade_pip=False):
    target_dir = Path(target_dir)
    print(f"[venv] Creating virtual environment at: {target_dir.resolve()}")

    builder = venv.EnvBuilder(
        system_site_packages=False,
        clear=clear,
        symlinks=(sys.platform != "win32"),
        with_pip=True,
        upgrade_deps=upgrade_pip,
    )
    try:
        builder.create(str(target_dir))
    except Exception as exc:
        print(f"[venv] FAILED: {exc}")
        return False

    # Report the interpreter path so the user knows what to run next
    if sys.platform == "win32":
        py_path = target_dir / "Scripts" / "python.exe"
    else:
        py_path = target_dir / "bin" / "python"

    print(f"[venv] Done. Interpreter located at: {py_path}")
    print("[venv] Use activate_venv.py to see the activation command for your shell.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Create an isolated Python virtual environment.")
    parser.add_argument("path", help="Directory to create the venv in, e.g. ./myenv")
    parser.add_argument("--clear", action="store_true", help="Delete contents of an existing venv dir first")
    parser.add_argument("--with-pip-upgrade", dest="upgrade_pip", action="store_true",
                         help="Upgrade pip/setuptools/wheel inside the new venv")
    args = parser.parse_args()

    if not args.path:
        print("You must specify a target directory. Example: python create_venv.py myenv")
        sys.exit(2)

    ok = create_venv(args.path, clear=args.clear, upgrade_pip=args.upgrade_pip)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
