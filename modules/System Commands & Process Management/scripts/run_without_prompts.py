#!/usr/bin/env python3
"""
run_without_prompts.py

Purpose:
    Run an external script/command non-interactively (no prompts), by
    feeding it empty/default input and using flags that suppress
    confirmation prompts where possible.

Usage:
    python run_without_prompts.py "some_command_that_might_prompt"

    If no command is given, a safe built-in demo runs instead.

Expected Output:
    Command executes without waiting for interactive input.
    STDOUT / STDERR / Exit Code are printed.

Caution:
    - Feeding blank input automatically means you will NOT see or be
      able to respond to confirmation prompts (e.g. "Are you sure? [y/N]").
      Only use this on commands you trust and understand, since it can
      auto-accept destructive actions if the target command defaults to
      "yes" on empty input.
    - Prefer commands that support a native "--yes" / "--non-interactive"
      / "--force" flag instead of relying on blank stdin, when available.
"""

import subprocess
import sys


def run_without_prompt(command: str) -> None:
    print(f"Running non-interactively: {command}\n")
    result = subprocess.run(
        command,
        shell=True,
        input="",           # empty stdin so any prompt gets a blank line
        capture_output=True,
        text=True,
        timeout=30
    )
    print("STDOUT:")
    print(result.stdout if result.stdout else "(no output)")
    print("STDERR:")
    print(result.stderr if result.stderr else "(no errors)")
    print(f"Exit Code: {result.returncode}")


def main():
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = "echo Running without prompts demo"
    run_without_prompt(command)


if __name__ == "__main__":
    main()
