#!/usr/bin/env python3
"""
export_requirements.py
--------------------
Equivalent of `pip freeze`, scoped to a specific project/venv interpreter,
written out to a requirements.txt-style file.

Usage:
    python export_requirements.py                       # freeze current interpreter to requirements.txt
    python export_requirements.py --output deps.txt
    python export_requirements.py --python ./myenv/bin/python --output requirements.txt

Exit codes:
    0 -> exported successfully
    1 -> pip freeze failed
"""

import argparse
import subprocess
import sys


def freeze(python_exe):
    cmd = [python_exe, "-m", "pip", "freeze"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print("[export] pip freeze failed:")
        print(result.stderr.strip())
        sys.exit(1)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description="Export requirements.txt from an environment.")
    parser.add_argument("--output", default="requirements.txt", help="Output file path")
    parser.add_argument("--python", default=sys.executable, help="Path to target python interpreter")
    args = parser.parse_args()

    print(f"[export] Freezing packages from: {args.python}")
    contents = freeze(args.python)

    lines = [l for l in contents.splitlines() if l.strip()]
    with open(args.output, "w") as f:
        f.write(contents)

    print(f"[export] Wrote {len(lines)} package pin(s) to {args.output}")
    sys.exit(0)


if __name__ == "__main__":
    main()
