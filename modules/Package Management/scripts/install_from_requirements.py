#!/usr/bin/env python3
"""
install_from_requirements.py
--------------------
Reproduce an environment reliably from a requirements.txt (or similarly
formatted) lock file, via `pip install -r`.

Usage:
    python install_from_requirements.py requirements.txt
    python install_from_requirements.py requirements.txt --python ./myenv/bin/python
    python install_from_requirements.py requirements.txt --no-deps

Exit codes:
    0 -> installed successfully
    1 -> pip install failed
    2 -> requirements file not found / bad arguments
"""

import argparse
import subprocess
import sys
from pathlib import Path


def install_from_file(req_file, python_exe=sys.executable, no_deps=False, extra_index=None):
    cmd = [python_exe, "-m", "pip", "install", "-r", req_file]
    if no_deps:
        cmd.append("--no-deps")
    if extra_index:
        cmd.extend(["--extra-index-url", extra_index])

    print(f"[install-req] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr.strip()[-1500:])
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Install packages from a requirements.txt file.")
    parser.add_argument("requirements", help="Path to requirements.txt")
    parser.add_argument("--python", default=sys.executable, help="Path to target python interpreter")
    parser.add_argument("--no-deps", action="store_true", help="Do not install transitive dependencies")
    parser.add_argument("--extra-index", default=None, help="Extra package index URL")
    args = parser.parse_args()

    req_path = Path(args.requirements)
    if not req_path.is_file():
        print(f"[install-req] File not found: {req_path}")
        sys.exit(2)

    ok = install_from_file(str(req_path), python_exe=args.python, no_deps=args.no_deps,
                            extra_index=args.extra_index)
    if ok:
        print("[install-req] Environment reproduced successfully.")
    else:
        print("[install-req] Installation failed. See error output above.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
