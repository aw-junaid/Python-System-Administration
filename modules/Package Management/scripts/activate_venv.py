#!/usr/bin/env python3
"""
activate_venv.py
--------------------
A subprocess cannot change the activation state of your parent shell
(that is a shell-only concept), so this script instead LOCATES the
correct interpreter and activation script inside bin/ (POSIX) or
Scripts/ (Windows) and prints the exact command you need to run.

Usage:
    python activate_venv.py myenv
    python activate_venv.py myenv --run "pip -V"   # run a command using that venv's python

Exit codes:
    0 -> venv found and info printed (or command ran successfully)
    1 -> venv / interpreter not found, or --run command failed
"""

import argparse
import subprocess
import sys
from pathlib import Path


def locate_interpreter(venv_dir):
    venv_dir = Path(venv_dir)
    if sys.platform == "win32":
        py = venv_dir / "Scripts" / "python.exe"
        activate = venv_dir / "Scripts" / "activate.bat"
        activate_cmd = str(activate)
    else:
        py = venv_dir / "bin" / "python"
        activate = venv_dir / "bin" / "activate"
        activate_cmd = f"source {activate}"
    return py, activate, activate_cmd


def main():
    parser = argparse.ArgumentParser(
        description="Locate a venv's interpreter and print its activation command."
    )
    parser.add_argument("path", help="Path to the virtual environment directory")
    parser.add_argument("--run", metavar="CMD",
                         help="Run CMD using this venv's python -m pip / python directly, e.g. 'pip -V'")
    args = parser.parse_args()

    py, activate, activate_cmd = locate_interpreter(args.path)

    if not py.exists():
        print(f"[activate] No interpreter found at {py}. Did you create the venv with create_venv.py?")
        sys.exit(1)

    print(f"[activate] Interpreter: {py}")
    if activate.exists():
        print(f"[activate] To activate this venv in your shell, run:\n    {activate_cmd}")
    else:
        print("[activate] No activate script found (unusual) -- you can still call the interpreter directly.")

    if args.run:
        full_cmd = [str(py)] + args.run.split()
        print(f"[activate] Running inside venv: {' '.join(full_cmd)}")
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
