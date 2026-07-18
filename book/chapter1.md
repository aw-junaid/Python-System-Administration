## Chapter 1: Input & Output Handling

Every command-line tool is, at its core, a translator between the outside world and your code. Data comes in — from a file, a pipe, a keyboard, an environment variable, a config file in five different formats — and results go out, either as clean output for a human to read or as structured data for the next program in the pipeline to consume. Get this layer wrong and nothing else in your script matters: the fanciest algorithm is useless if it can't read its input or if its output can't be parsed by the next tool in the chain.

This chapter is a working reference for that layer. It covers the mechanics of getting data into a Python script (files, pipes, stdin, arguments, environment variables) and the mechanics of getting data and status back out (stdout, stderr, exit codes, formatted and colored output). It also covers the ecosystem tools that make command-line interfaces usable — `argparse` and `click` for structured argument parsing, `tqdm` for progress feedback, `rich`/`colorama` for readable output — and the format-specific readers (JSON, CSV, YAML, XML, TOML) that every sysadmin script eventually needs, plus the special case of reading files that are password-protected.

A note on scope: this chapter assumes Python 3.8+ on a POSIX-like shell (Linux/macOS), with Windows-specific notes called out where behavior diverges (line endings, path separators, `findstr` vs `grep`, PowerShell equivalents). Standard library is preferred wherever it's sufficient; third-party packages are used only where they meaningfully reduce code or add real capability (colored output, progress bars, YAML parsing — none of which stdlib does well).

### 1.1 Accept Input from a File

**Use case:** A sysadmin needs a script that can be pointed at any log file, config file, or data dump — `./tool.py /var/log/syslog` — without hardcoding a filename, so it works the same way across servers and cron jobs.

**Prerequisites**
```bash
# No third-party packages needed — pure standard library.
python3 --version   # 3.8+ recommended
# Works on Linux, macOS, and Windows (path separators handled by pathlib).
```

**Cautions:** Always validate the path exists and is readable before opening it — a missing file or a directory passed by mistake will raise an unhandled exception if you don't catch it. Be careful with encoding; log files from mixed sources may not be valid UTF-8.

**Script**
```python
#!/usr/bin/env python3
"""read_file_input.py - Read and process a file passed as a CLI argument."""
import sys
from pathlib import Path


def process_file(path: Path) -> None:
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print(f"Error: not a regular file: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            line_count = 0
            for line in f:
                line_count += 1
                print(f"{line_count:>5}: {line.rstrip()}")
        print(f"\nProcessed {line_count} lines from {path}", file=sys.stderr)
    except PermissionError:
        print(f"Error: permission denied reading {path}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-file>", file=sys.stderr)
        sys.exit(2)
    process_file(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_file_input.py

# Basic run
./read_file_input.py /etc/hosts

# On a large log file
./read_file_input.py /var/log/syslog

# Missing file (demonstrates error handling)
./read_file_input.py /tmp/does-not-exist.txt
```

**Sample output**
```text
$ ./read_file_input.py /etc/hosts
    1: 127.0.0.1 localhost
    2: ::1       localhost ip6-localhost ip6-loopback
    3: 192.168.1.10 server01

Processed 3 lines from /etc/hosts

$ ./read_file_input.py /tmp/does-not-exist.txt
Error: file not found: /tmp/does-not-exist.txt
```

**Variations / flags**
- Add `--tail N` to only print the last N lines (use `collections.deque(maxlen=N)`).
- Add `--binary` mode using `path.open("rb")` for non-text files.
- Wrap in `argparse` (see 1.10) once you need more than one flag.

**Common pitfalls**
- Forgetting `errors="replace"` and crashing on a non-UTF-8 byte in a log file.
- Passing a directory instead of a file — always check `is_file()`.
- Relative paths breaking when the script is run from cron with a different working directory — prefer absolute paths or resolve with `Path(...).resolve()`.

### 1.2 Accept Input from a Pipe

**Use case:** A sysadmin wants to filter or transform the output of another tool, e.g. `ps aux | ./filter_procs.py` to highlight processes over a memory threshold, without writing to a temp file first.

**Prerequisites**
```bash
# Pure standard library.
python3 --version   # 3.8+
# Linux/macOS: pipes are native shell syntax.
# Windows: works the same in PowerShell and cmd.exe with the | operator.
```

**Cautions:** A script that only works with a pipe will hang waiting for input if run interactively with nothing piped in — always detect whether stdin is a terminal (`sys.stdin.isatty()`) and give a helpful message instead of hanging silently.

**Script**
```python
#!/usr/bin/env python3
"""pipe_input.py - Read and process lines piped in from another command."""
import sys


def main() -> None:
    if sys.stdin.isatty():
        print("No piped input detected. Usage: some_command | ./pipe_input.py",
              file=sys.stderr)
        sys.exit(1)

    total = 0
    matches = 0
    for line in sys.stdin:
        total += 1
        line = line.rstrip("\n")
        if "ERROR" in line.upper():
            matches += 1
            print(f"[MATCH] {line}")

    print(f"\nScanned {total} lines, found {matches} matches.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x pipe_input.py

# Pipe log output through it
cat /var/log/syslog | ./pipe_input.py

# Chain with another filter
journalctl -u nginx --since today | ./pipe_input.py

# Running without a pipe (should show the usage message, not hang)
./pipe_input.py
```

**Sample output**
```text
$ printf "info: ok\nERROR: disk full\ninfo: ok\n" | ./pipe_input.py
[MATCH] ERROR: disk full

Scanned 3 lines, found 1 matches.

$ ./pipe_input.py
No piped input detected. Usage: some_command | ./pipe_input.py
```

**Variations / flags**
- Add `--pattern <regex>` so the match string is configurable instead of hardcoded.
- Add `--count-only` to suppress per-line output and just print the summary.
- Use `sys.stdin.buffer.read()` instead of line iteration for binary piped data.

**Common pitfalls**
- Not stripping the trailing newline before comparing/printing lines.
- Assuming stdin is always UTF-8 — piped output from other locales can raise `UnicodeDecodeError`; pass `errors="replace"` if you rewrap `sys.stdin`.
- Broken pipe errors (`BrokenPipeError`) when downstream commands like `head` close early — catch and exit cleanly rather than printing a traceback.

### 1.3 Capture and Process Command Output

**Use case:** A sysadmin needs to run `df -h`, `systemctl status`, or `docker ps` from inside a script and parse the results programmatically, e.g. to alert when disk usage crosses a threshold.

**Prerequisites**
```bash
# Pure standard library (subprocess module).
python3 --version   # 3.8+
# Linux/macOS: run any shell binary.
# Windows: substitute the command with a Windows equivalent (e.g. "wmic" or PowerShell cmdlets).
```

**Cautions:** Never pass untrusted input into `shell=True` commands — it opens a command-injection hole. Prefer passing the command as a list of arguments (`subprocess.run([...])`) so the shell isn't invoked at all. Always set a `timeout` for commands that could hang.

**Script**
```python
#!/usr/bin/env python3
"""capture_output.py - Run a command and process its captured output."""
import subprocess
import sys


def run_command(cmd: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result
    except FileNotFoundError:
        print(f"Error: command not found: {cmd[0]}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"Error: command timed out after {timeout}s: {' '.join(cmd)}",
              file=sys.stderr)
        sys.exit(1)


def main() -> None:
    result = run_command(["df", "-h"])

    if result.returncode != 0:
        print(f"Command failed (exit {result.returncode}): {result.stderr}",
              file=sys.stderr)
        sys.exit(result.returncode)

    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5:
            filesystem, size, used, avail, use_pct = parts[:5]
            pct = int(use_pct.rstrip("%"))
            flag = " <-- HIGH USAGE" if pct >= 80 else ""
            print(f"{filesystem:<20} {use_pct:>5} used of {size:<8}{flag}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x capture_output.py

# Basic run - parses `df -h` and flags high-usage volumes
./capture_output.py

# Try it against a different command by editing the run_command call, e.g.:
#   run_command(["systemctl", "is-active", "nginx"])
```

**Sample output**
```text
$ ./capture_output.py
/dev/sda1              42% used of 100G
/dev/sda2              87% used of 500G  <-- HIGH USAGE
tmpfs                    2% used of 8.0G
```

**Variations / flags**
- Add `--threshold N` (default 80) to make the alert cutoff configurable via argparse.
- Add `--json` to emit the parsed rows as JSON for downstream tooling (see 1.17).
- Use `subprocess.Popen` with streaming reads instead of `run()` when you need output as it arrives (e.g. tailing a long-running build).

**Common pitfalls**
- Using `shell=True` with string-interpolated user input — a classic injection vulnerability.
- Forgetting `text=True`, which leaves `stdout`/`stderr` as bytes instead of `str` and breaks `.splitlines()` string logic.
- Not checking `returncode` and treating a failed command's (empty or error) output as valid data.
- Command name differs across distros (e.g. `df` flags vary between GNU coreutils and BusyBox) — verify flags on the target platform.

### 1.4 Redirect Input/Output Streams

**Use case:** A sysadmin wants a long-running maintenance script to log everything it prints to a file automatically — even output from `print()` calls scattered through the code — without changing every call site or relying only on shell-level `> file.log` redirection.

**Prerequisites**
```bash
# Pure standard library (contextlib, sys).
python3 --version   # 3.8+
# Works identically on Linux/macOS/Windows.
```

**Cautions:** Redirecting `sys.stdout` inside a script affects every subsequent `print()` call for the rest of the process (or until restored) — always restore the original stream in a `finally` block, or use `contextlib.redirect_stdout` as a context manager so it's automatic.

**Script**
```python
#!/usr/bin/env python3
"""redirect_streams.py - Redirect stdout/stderr to log files inside a script."""
import contextlib
import sys
from pathlib import Path


def noisy_task() -> None:
    print("Starting maintenance task...")
    print("Step 1: checking disk space")
    print("Step 2: rotating logs")
    print("Warning: log directory nearly full", file=sys.stderr)
    print("Done.")


def main() -> None:
    out_log = Path("task_stdout.log")
    err_log = Path("task_stderr.log")

    with out_log.open("w") as out_f, err_log.open("w") as err_f:
        with contextlib.redirect_stdout(out_f), contextlib.redirect_stderr(err_f):
            noisy_task()

    # Back on the real terminal now - streams are automatically restored.
    print(f"Task complete. See {out_log} and {err_log} for details.")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x redirect_streams.py

# Run normally - output is captured into files, not the terminal
./redirect_streams.py

# Inspect the captured logs
cat task_stdout.log
cat task_stderr.log

# Compare with shell-level redirection (redirects only the OS-level stream)
./redirect_streams.py > shell_stdout.log 2> shell_stderr.log
```

**Sample output**
```text
$ ./redirect_streams.py
Task complete. See task_stdout.log and task_stderr.log for details.

$ cat task_stdout.log
Starting maintenance task...
Step 1: checking disk space
Step 2: rotating logs
Done.

$ cat task_stderr.log
Warning: log directory nearly full
```

**Variations / flags**
- Add `--append` to open the log files with `"a"` instead of `"w"` for continuous logging across runs.
- Combine with the `logging` module and a `logging.FileHandler` for rotation, timestamps, and log levels instead of manual redirection.
- Use `os.dup2()` at the file-descriptor level if you need to redirect output from C extensions or subprocesses too, not just Python's `print()`.

**Common pitfalls**
- Forgetting that `redirect_stdout` does not affect subprocess output written directly to the terminal's file descriptor — subprocess output needs `stdout=out_f` passed to `subprocess.run()` instead.
- Leaving streams redirected because an exception skipped the `with` block's exit — using the context manager (as above) avoids this; manual `sys.stdout = ...` assignment does not.
- Losing real-time visibility during long tasks since output no longer appears on the terminal — pair with periodic status prints to a third channel if needed.

### 1.5 Read from Standard Input (stdin)

**Use case:** A sysadmin wants one script that works both interactively (`./tool.py`, then type input) and non-interactively (`echo "data" | ./tool.py`), e.g. a quick text-transform utility used in ad-hoc terminal sessions and in automated pipelines alike.

**Prerequisites**
```bash
# Pure standard library (sys.stdin).
python3 --version   # 3.8+
# Identical behavior on Linux/macOS; Windows terminals support stdin the same way.
```

**Cautions:** Interactive stdin blocks waiting for `Ctrl+D` (Linux/macOS) or `Ctrl+Z` then Enter (Windows) to signal end-of-input if you read all of it at once with `.read()` — make sure the user-facing docs mention this so the script doesn't look "frozen."

**Script**
```python
#!/usr/bin/env python3
"""read_stdin.py - Read all of stdin and report basic stats about it."""
import sys


def main() -> None:
    print("Reading input (Ctrl+D / Ctrl+Z to end)...", file=sys.stderr)
    data = sys.stdin.read()

    lines = data.splitlines()
    words = data.split()

    print(f"Lines: {len(lines)}")
    print(f"Words: {len(words)}")
    print(f"Characters: {len(data)}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_stdin.py

# Interactive mode - type text, then press Ctrl+D (Linux/macOS) or Ctrl+Z+Enter (Windows)
./read_stdin.py

# Piped mode - no interaction needed
echo "the quick brown fox" | ./read_stdin.py

# From a file via shell redirection
./read_stdin.py < notes.txt
```

**Sample output**
```text
$ echo "the quick brown fox jumps" | ./read_stdin.py
Reading input (Ctrl+D / Ctrl+Z to end)...
Lines: 1
Words: 5
Characters: 26
```

**Variations / flags**
- Use `for line in sys.stdin:` instead of `.read()` to process line-by-line without waiting for full EOF (better for streaming/tailing scenarios).
- Add a `--strip-blank` flag to filter out empty lines before counting.
- Combine with `input()` for a simple line-at-a-time interactive prompt instead of bulk read.

**Common pitfalls**
- Calling `sys.stdin.read()` with nothing piped and no terminal input — the script hangs, and users think it crashed.
- Mixing `input()` and `sys.stdin.read()` in the same script — `input()` consumes one line at a time and the two approaches don't compose cleanly.
- Encoding issues on Windows where the console codepage isn't UTF-8 by default — set `PYTHONIOENCODING=utf-8` if special characters get mangled.

### 1.6 Write to Standard Output (stdout)

**Use case:** A sysadmin writes a tool that lists stale user accounts; it must print only clean, parseable data to stdout so it can be piped into `wc -l`, `grep`, or another script — with any diagnostics kept out of the way (see 1.7).

**Prerequisites**
```bash
# Pure standard library (print(), sys.stdout).
python3 --version   # 3.8+
# Behavior is identical across Linux/macOS/Windows terminals and pipes.
```

**Cautions:** Keep stdout reserved for the actual output data a downstream tool would consume. Status messages, progress indicators, and logs belong on stderr (1.7) — mixing them into stdout breaks anything piping your script's output into another program.

**Script**
```python
#!/usr/bin/env python3
"""write_stdout.py - Print clean, pipeable results to stdout."""
import sys

STALE_ACCOUNTS = ["jdoe", "asmith", "temp_contractor01"]


def main() -> None:
    print(f"Scanning for stale accounts...", file=sys.stderr)  # diagnostic -> stderr

    for account in STALE_ACCOUNTS:
        print(account)  # actual result -> stdout

    print(f"Found {len(STALE_ACCOUNTS)} stale accounts.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x write_stdout.py

# Run directly - both streams show up interleaved on the terminal
./write_stdout.py

# Pipe stdout only into another tool - stderr messages stay off to the side
./write_stdout.py | wc -l

# Redirect stdout to a file, let stderr still print to the terminal
./write_stdout.py > accounts.txt
```

**Sample output**
```text
$ ./write_stdout.py | wc -l
Scanning for stale accounts...
Found 3 stale accounts.
3

$ ./write_stdout.py > accounts.txt
Scanning for stale accounts...
Found 3 stale accounts.

$ cat accounts.txt
jdoe
asmith
temp_contractor01
```

**Variations / flags**
- Add `--quiet` to suppress even the stderr diagnostics for use in tight automation.
- Use `sys.stdout.write(...)` directly (no trailing newline) when building output that must match an exact byte format.
- Flush explicitly (`print(..., flush=True)`) when interleaving with a subprocess that writes to the same terminal, to avoid out-of-order output.

**Common pitfalls**
- Printing status/progress text to stdout "for convenience," which then corrupts anything piping the output (e.g. `| jq` failing on non-JSON lines mixed in).
- Buffering surprises when stdout is redirected to a file — Python fully buffers non-tty stdout by default, so output may appear delayed; use `flush=True` or `-u` (`python3 -u script.py`) if real-time visibility matters.
- Trailing whitespace or inconsistent newlines making downstream `diff` or exact-match comparisons fail.

### 1.7 Write to Standard Error (stderr)

**Use case:** A sysadmin's backup script needs to report warnings ("skipping locked file X") and fatal errors without polluting the actual file-list output that a wrapper script consumes downstream.

**Prerequisites**
```bash
# Pure standard library (sys.stderr).
python3 --version   # 3.8+
# Identical behavior on Linux/macOS/Windows.
```

**Cautions:** Use appropriate exit codes alongside stderr messages (0 = success, non-zero = failure) so calling scripts and cron can detect failure without parsing text. Don't rely on stderr messages alone for control flow.

**Script**
```python
#!/usr/bin/env python3
"""write_stderr.py - Demonstrate proper separation of errors/warnings vs results."""
import sys

FILES_TO_BACKUP = ["/etc/passwd", "/etc/shadow", "/nonexistent/file"]


def backup_file(path: str) -> bool:
    import os
    from pathlib import Path
    p = Path(path)
    if not p.exists():
        print(f"WARNING: skipping missing file: {path}", file=sys.stderr)
        return False
    if not os.access(p, os.R_OK):
        print(f"WARNING: skipping unreadable file: {path}", file=sys.stderr)
        return False
    print(path)  # result -> stdout
    return True


def main() -> None:
    success_count = 0
    for f in FILES_TO_BACKUP:
        if backup_file(f):
            success_count += 1

    if success_count == 0:
        print("ERROR: no files were backed up", file=sys.stderr)
        sys.exit(1)
    elif success_count < len(FILES_TO_BACKUP):
        print(f"NOTE: backed up {success_count}/{len(FILES_TO_BACKUP)} files "
              f"(some were skipped, see warnings above)", file=sys.stderr)
        sys.exit(0)  # partial success still counts as success here
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x write_stderr.py

# Run normally
./write_stderr.py

# Send only stdout to a results file, watch stderr live on the terminal
./write_stderr.py > backed_up_files.txt

# Send only stderr to a log file, see stdout results on the terminal
./write_stderr.py 2> errors.log

# Check exit status for automation
./write_stderr.py; echo "exit code: $?"
```

**Sample output**
```text
$ ./write_stderr.py
WARNING: skipping missing file: /nonexistent/file
/etc/passwd
/etc/shadow
NOTE: backed up 2/3 files (some were skipped, see warnings above)

$ ./write_stderr.py > backed_up_files.txt
WARNING: skipping missing file: /nonexistent/file
NOTE: backed up 2/3 files (some were skipped, see warnings above)

$ cat backed_up_files.txt
/etc/passwd
/etc/shadow
```

**Variations / flags**
- Add `--strict` so any skipped file causes a non-zero exit instead of a partial-success note.
- Route stderr through the `logging` module with levels (`WARNING`, `ERROR`) instead of raw `print()` for timestamped, filterable diagnostics.
- Add `--verbose` / `--quiet` flags to control how much goes to stderr without touching stdout at all.

**Common pitfalls**
- Using `print()` (which defaults to stdout) for error messages by mistake — always pass `file=sys.stderr` explicitly.
- Exiting with code 0 even when something failed, which makes cron/CI treat a broken run as successful.
- Forgetting that `2>&1` in a shell command merges the streams — if you need them separate for testing, don't merge them when validating this behavior.

### 1.8 Read Multiline Input

**Use case:** A sysadmin builds a script that accepts a multi-line block — e.g. pasting a list of hostnames or a chunk of config — directly at the terminal, ending with `Ctrl+D` or a typed sentinel like `END`, instead of requiring a file.

**Prerequisites**
```bash
# Pure standard library.
python3 --version   # 3.8+
# Ctrl+D signals EOF on Linux/macOS; Ctrl+Z then Enter on Windows.
```

**Cautions:** Clearly document the termination method to the user (EOF vs sentinel word) — this is one of the most common sources of "the script just hangs" confusion for new CLI tools.

**Script**
```python
#!/usr/bin/env python3
"""read_multiline.py - Accept multi-line input via EOF or a sentinel line."""
import sys


def read_until_eof() -> list[str]:
    print("Enter lines of text, then press Ctrl+D (Ctrl+Z+Enter on Windows):",
          file=sys.stderr)
    return [line.rstrip("\n") for line in sys.stdin]


def read_until_sentinel(sentinel: str = "END") -> list[str]:
    print(f"Enter lines of text, type '{sentinel}' on its own line to finish:",
          file=sys.stderr)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == sentinel:
            break
        lines.append(line)
    return lines


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "eof"

    if mode == "sentinel":
        lines = read_until_sentinel()
    else:
        lines = read_until_eof()

    print(f"\nReceived {len(lines)} lines:")
    for i, line in enumerate(lines, 1):
        print(f"{i}: {line}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_multiline.py

# EOF mode - type lines, then Ctrl+D
./read_multiline.py eof

# Sentinel mode - type lines, then "END" to finish
./read_multiline.py sentinel

# Also works piped, since EOF mode reads all of stdin
printf "host1\nhost2\nhost3\n" | ./read_multiline.py eof
```

**Sample output**
```text
$ printf "web01\nweb02\ndb01\n" | ./read_multiline.py eof
Enter lines of text, then press Ctrl+D (Ctrl+Z+Enter on Windows):

Received 3 lines:
1: web01
2: web02
3: db01
```

**Variations / flags**
- Add `--strip-empty` to drop blank lines from the collected block.
- Combine with 1.19/1.17 to parse the collected block as YAML/JSON once fully read.
- Add a max-line-count guard to avoid unbounded memory use on malformed/huge pastes.

**Common pitfalls**
- Using `input()` in a loop but forgetting to catch `EOFError`, which crashes the script when input ends via Ctrl+D instead of the sentinel.
- Sentinel word colliding with real data (e.g. a hostname literally named `END`) — pick an unlikely sentinel or make it configurable.
- Windows terminals sending `\r\n` line endings that leave a stray `\r` if you only strip `\n` — use `.rstrip()` without arguments, or `.rstrip("\r\n")`, when portability matters.

### 1.9 Handle Command-Line Arguments

**Use case:** A sysadmin needs a minimal one-off script — e.g. `./restart_service.py nginx` — where pulling in a full argument-parsing library would be overkill for a single required argument.

**Prerequisites**
```bash
# Pure standard library (sys.argv).
python3 --version   # 3.8+
# Identical behavior on Linux/macOS/Windows; sys.argv[0] is the script path on all platforms.
```

**Cautions:** `sys.argv` gives you no validation, type conversion, or `--help` text for free — for anything beyond one or two positional arguments, switch to `argparse` (1.10) or `click` (1.11) rather than hand-rolling parsing logic that will accumulate bugs.

**Script**
```python
#!/usr/bin/env python3
"""raw_argv.py - Handle command-line arguments manually via sys.argv."""
import sys


def main() -> None:
    args = sys.argv[1:]  # sys.argv[0] is the script name itself

    if not args:
        print(f"Usage: {sys.argv[0]} <service_name> [--force]", file=sys.stderr)
        sys.exit(2)

    service_name = args[0]
    force = "--force" in args

    print(f"Service to restart: {service_name}")
    print(f"Force mode: {force}")

    if service_name.startswith("--"):
        print("Error: expected a service name first, got a flag", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x raw_argv.py

# Basic positional argument
./raw_argv.py nginx

# With an extra flag
./raw_argv.py nginx --force

# No arguments (shows usage and exits non-zero)
./raw_argv.py
```

**Sample output**
```text
$ ./raw_argv.py nginx --force
Service to restart: nginx
Force mode: True

$ ./raw_argv.py
Usage: raw_argv.py <service_name> [--force]
```

**Variations / flags**
- Support `--` as an "end of options" marker so arguments starting with `-` after it are treated literally.
- Add simple manual flag/value pairs (`--timeout 30`) by scanning `args` with an index instead of iterating directly.
- Graduate to `argparse` (1.10) the moment you need more than 2-3 arguments or any type validation.

**Common pitfalls**
- Off-by-one errors from forgetting `sys.argv[0]` is the script name, not the first user argument.
- No built-in `--help`, so users have to read the source or a README to know the syntax.
- Silent misparsing of flags vs values (e.g. `--force` accidentally consumed as a service name) without careful manual checks.

### 1.10 Parse Command-Line Options using argparse

**Use case:** A sysadmin is writing a reusable disk-cleanup tool that needs typed options (`--min-size`, `--days`), a boolean flag (`--dry-run`), and proper `--help` text for teammates who didn't write it.

**Prerequisites**
```bash
# Pure standard library - no install needed.
python3 --version   # 3.8+
# Identical behavior on Linux/macOS/Windows.
```

**Cautions:** `argparse` exits the process directly (via `SystemExit`) on bad input or `--help` — that's usually desired for a CLI tool, but be aware of it if you're calling the parser from inside test code or a larger application.

**Script**
```python
#!/usr/bin/env python3
"""argparse_cli.py - Structured CLI parsing with argparse."""
import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find and optionally delete old large files."
    )
    parser.add_argument(
        "directory",
        help="Directory to scan",
    )
    parser.add_argument(
        "--min-size", type=int, default=100,
        help="Minimum file size in MB to consider (default: 100)",
    )
    parser.add_argument(
        "--days", type=int, default=30,
        help="Only consider files older than this many days (default: 30)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be deleted without deleting anything",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="Increase output verbosity (-v, -vv)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(f"Directory: {args.directory}")
    print(f"Min size: {args.min_size} MB")
    print(f"Older than: {args.days} days")
    print(f"Dry run: {args.dry_run}")
    print(f"Verbosity level: {args.verbose}")

    if args.dry_run:
        print("\n[DRY RUN] No files will actually be deleted.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x argparse_cli.py

# Auto-generated help
./argparse_cli.py --help

# Basic run with defaults
./argparse_cli.py /var/log

# Overriding options
./argparse_cli.py /var/log --min-size 500 --days 90 --dry-run

# Increasing verbosity
./argparse_cli.py /var/log -vv
```

**Sample output**
```text
$ ./argparse_cli.py /var/log --min-size 500 --days 90 --dry-run
Directory: /var/log
Min size: 500 MB
Older than: 90 days
Dry run: True
Verbosity level: 0

[DRY RUN] No files will actually be deleted.

$ ./argparse_cli.py --help
usage: argparse_cli.py [-h] [--min-size MIN_SIZE] [--days DAYS] [--dry-run]
                        [-v]
                        directory

Find and optionally delete old large files.

positional arguments:
  directory            Directory to scan
...
```

**Variations / flags**
- Add subcommands with `parser.add_subparsers()` for a multi-verb CLI (e.g. `tool.py scan` / `tool.py clean`).
- Use `type=argparse.FileType("r")` to have argparse open a file argument directly.
- Add `choices=[...]` to a flag to restrict it to a fixed set of valid values with automatic error messages.

**Common pitfalls**
- Forgetting `action="store_true"` on boolean flags and instead requiring `--dry-run true`, which is not how argparse booleans normally work.
- Mismatched dashes vs underscores — `--min-size` becomes `args.min_size` (dashes convert to underscores automatically).
- Not setting sensible `default=` values, leading to `None` checks scattered through the rest of the script.

### 1.11 Parse Command-Line Options using click

**Use case:** A sysadmin is building a small internal toolkit with several related subcommands (`tool.py backup`, `tool.py restore`, `tool.py verify`) and wants less boilerplate and nicer composition than argparse offers for multi-command tools.

**Prerequisites**
```bash
python3 -m pip install click
python3 -c "import click; print(click.__version__)"
# Works on Linux/macOS/Windows - pure Python package, no OS-specific dependencies.
```

**Cautions:** `click` is a third-party dependency — pin a version in `requirements.txt` for reproducible deployments, since CLI behavior (especially help formatting) can shift between major versions.

**Script**
```python
#!/usr/bin/env python3
"""click_cli.py - Structured, multi-command CLI using click."""
import click


@click.group()
@click.option("--verbose", is_flag=True, help="Enable verbose output.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """A small backup toolkit."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("source")
@click.option("--destination", "-d", default="/backups", show_default=True,
              help="Where to store the backup.")
@click.option("--compress/--no-compress", default=True,
              help="Compress the backup archive.")
@click.pass_context
def backup(ctx: click.Context, source: str, destination: str, compress: bool) -> None:
    """Back up SOURCE to the destination directory."""
    if ctx.obj["verbose"]:
        click.echo(f"[verbose] source={source} dest={destination} compress={compress}")
    click.echo(f"Backing up '{source}' to '{destination}' (compress={compress})")


@cli.command()
@click.argument("archive")
@click.option("--target", default=".", show_default=True, help="Restore location.")
def restore(archive: str, target: str) -> None:
    """Restore ARCHIVE to the target directory."""
    click.echo(f"Restoring '{archive}' into '{target}'")


if __name__ == "__main__":
    cli()
```

**How it works and how to run**
```bash
chmod +x click_cli.py

# Top-level help, listing subcommands
./click_cli.py --help

# Subcommand help
./click_cli.py backup --help

# Run a subcommand
./click_cli.py backup /var/www --destination /mnt/backups

# Boolean flag pair (--compress / --no-compress)
./click_cli.py backup /var/www --no-compress

# Global flag before the subcommand
./click_cli.py --verbose backup /var/www
```

**Sample output**
```text
$ ./click_cli.py --verbose backup /var/www --destination /mnt/backups
[verbose] source=/var/www dest=/mnt/backups compress=True
Backing up '/var/www' to '/mnt/backups' (compress=True)

$ ./click_cli.py restore backup-2026-01-01.tar.gz --target /srv/restore
Restoring 'backup-2026-01-01.tar.gz' into '/srv/restore'
```

**Variations / flags**
- Add `@click.option("--dry-run", is_flag=True)` to any subcommand for safe previewing, matching the pattern from 1.10.
- Use `click.confirm("Proceed?")` to add an interactive confirmation before destructive actions.
- Package the script as a proper console entry point via `setup.py`/`pyproject.toml` so it installs as a system-wide `backup-tool` command instead of `python3 click_cli.py`.

**Common pitfalls**
- Forgetting `@click.pass_context` when a subcommand needs access to group-level options like `--verbose`.
- Mixing up `click.echo()` (click's recommended, encoding-safe print) with plain `print()` — mostly interchangeable, but `click.echo()` handles some cross-platform edge cases (color stripping, Windows consoles) better.
- Not pinning the `click` version, which can cause subtle CLI help-text or option-parsing differences after an upgrade.

### 1.12 Parse Environment Variables

**Use case:** A sysadmin's deployment script needs an API token and target environment name (`API_TOKEN`, `DEPLOY_ENV`) without hardcoding secrets into the script or requiring them as visible command-line arguments (which would show up in shell history and `ps` output).

**Prerequisites**
```bash
# Pure standard library (os.environ).
python3 --version   # 3.8+
# Setting variables:
#   Linux/macOS (bash/zsh): export API_TOKEN=xyz
#   Windows (PowerShell):   $env:API_TOKEN = "xyz"
#   Windows (cmd.exe):      set API_TOKEN=xyz
```

**Cautions:** Never print secret environment variables (tokens, passwords) to stdout/stderr/logs. Provide clear errors when a required variable is missing rather than letting the script fail deep inside unrelated logic with a confusing `KeyError`.

**Script**
```python
#!/usr/bin/env python3
"""env_vars.py - Read required and optional configuration from the environment."""
import os
import sys


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        print(f"Error: required environment variable '{name}' is not set",
              file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    api_token = get_required_env("API_TOKEN")
    deploy_env = os.environ.get("DEPLOY_ENV", "staging")  # optional, with default
    debug = os.environ.get("DEBUG", "0") == "1"

    masked_token = api_token[:4] + "..." if len(api_token) > 4 else "***"
    print(f"Deploying to: {deploy_env}")
    print(f"API token (masked): {masked_token}")
    print(f"Debug mode: {debug}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x env_vars.py

# Missing required variable (should show a clear error, not a traceback)
./env_vars.py

# Setting it inline for a single run (Linux/macOS)
API_TOKEN=abc123456 DEPLOY_ENV=production ./env_vars.py

# Exporting for the current shell session, then running
export API_TOKEN=abc123456
export DEBUG=1
./env_vars.py
```

**Sample output**
```text
$ API_TOKEN=abc123456 DEPLOY_ENV=production ./env_vars.py
Deploying to: production
API token (masked): abc1...
Debug mode: False

$ ./env_vars.py
Error: required environment variable 'API_TOKEN' is not set
```

**Variations / flags**
- Load variables from a `.env` file with `python-dotenv` (`pip install python-dotenv`) for local development convenience, while still preferring real environment variables in production.
- Add type coercion helpers (e.g. `int(os.environ.get("PORT", "8080"))`) with try/except for numeric config values.
- Validate an allowed set of values for variables like `DEPLOY_ENV` (`staging`, `production`) and error clearly on typos.

**Common pitfalls**
- Using `os.environ["NAME"]` directly, which raises an unhandled `KeyError` (with a less friendly message) instead of a controlled error message.
- Logging or printing full secret values during debugging and leaving that code in place.
- Assuming environment variables persist between separate shell sessions or across a reboot — `export` is only session-scoped unless added to a shell profile or systemd unit file.

### 1.13 Interactive Command-Line Menus

**Use case:** A sysadmin builds an internal "ops console" script that junior team members run to pick from a small set of safe, pre-approved actions (restart a service, view logs, check disk space) without needing to remember exact flags.

**Prerequisites**
```bash
# Pure standard library (input()).
python3 --version   # 3.8+
# Works in any interactive terminal on Linux/macOS/Windows.
# (Third-party alternative for richer menus: pip install questionary)
```

**Cautions:** Menus assume an interactive terminal — guard against running in a non-interactive context (cron, CI) where `input()` would hang or raise `EOFError`.

**Script**
```python
#!/usr/bin/env python3
"""interactive_menu.py - A simple numbered interactive menu."""
import sys

MENU = {
    "1": ("Check disk space", lambda: print("Disk usage: 42% used")),
    "2": ("Check memory", lambda: print("Memory usage: 61% used")),
    "3": ("List running services", lambda: print("nginx, postgresql, redis")),
}


def show_menu() -> None:
    print("\n=== Ops Console ===")
    for key, (label, _) in MENU.items():
        print(f"  {key}. {label}")
    print("  q. Quit")


def main() -> None:
    if not sys.stdin.isatty():
        print("Error: this menu requires an interactive terminal.", file=sys.stderr)
        sys.exit(1)

    while True:
        show_menu()
        choice = input("\nSelect an option: ").strip().lower()

        if choice == "q":
            print("Goodbye.")
            break
        elif choice in MENU:
            label, action = MENU[choice]
            print(f"\n> Running: {label}")
            action()
        else:
            print("Invalid choice, try again.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x interactive_menu.py

# Run interactively
./interactive_menu.py

# At the prompt, type: 1, 2, 3, or q
```

**Sample output**
```text
$ ./interactive_menu.py

=== Ops Console ===
  1. Check disk space
  2. Check memory
  3. List running services
  q. Quit

Select an option: 1

> Running: Check disk space
Disk usage: 42% used

=== Ops Console ===
...
Select an option: q
Goodbye.
```

**Variations / flags**
- Swap the plain `input()` loop for `questionary.select(...)` (`pip install questionary`) for arrow-key navigation instead of typed numbers.
- Add confirmation prompts (`input("Are you sure? [y/N] ")`) before destructive menu actions.
- Log each selected action with a timestamp to an audit file for accountability on shared admin consoles.

**Common pitfalls**
- Running the script under cron or in a CI pipeline where there's no TTY — `input()` will raise `EOFError` immediately; always check `sys.stdin.isatty()` first.
- Not handling `KeyboardInterrupt` (Ctrl+C) gracefully, leaving a raw traceback instead of a clean exit message.
- Case-sensitive matching on menu input (`Q` vs `q`) confusing users — normalize with `.strip().lower()`.

### 1.14 Display Progress Bars

**Use case:** A sysadmin writes a script that copies or processes thousands of files and wants visible feedback so the operator knows it's still working (and roughly how long is left) instead of staring at a frozen-looking terminal.

**Prerequisites**
```bash
python3 -m pip install tqdm
python3 -c "import tqdm; print(tqdm.__version__)"
# Works on Linux/macOS/Windows terminals; also renders correctly in Jupyter notebooks.
```

**Cautions:** Progress bars write control characters (carriage returns) to the terminal — redirecting output to a file or a non-terminal consumer produces messy output unless the library detects it (tqdm does this automatically and falls back to plain periodic updates).

**Script**
```python
#!/usr/bin/env python3
"""progress_bar.py - Show a progress bar for a long-running loop."""
import time
from tqdm import tqdm


def process_files(file_list: list[str]) -> None:
    for _ in tqdm(file_list, desc="Processing files", unit="file"):
        time.sleep(0.05)  # simulate work


def main() -> None:
    files = [f"file_{i:04d}.log" for i in range(100)]
    process_files(files)
    print("All files processed.")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x progress_bar.py

# Run normally in a terminal - shows a live-updating bar
./progress_bar.py

# Redirected to a file - tqdm detects non-tty and reduces update frequency
./progress_bar.py > run.log 2>&1
```

**Sample output**
```text
$ ./progress_bar.py
Processing files: 100%|████████████████████| 100/100 [00:05<00:00, 19.87file/s]
All files processed.
```

**Variations / flags**
- Use `tqdm(total=known_total)` with manual `.update(n)` calls when iterating something that isn't a simple sequence (e.g. bytes downloaded).
- Nest progress bars (`tqdm` supports nested bars with `position=`) for outer/inner loop reporting (e.g. servers -> files per server).
- Use `rich.progress` instead of `tqdm` when you also want columns for time remaining, transfer speed, and spinner styles alongside the bar.

**Common pitfalls**
- Printing regular `print()` statements inside the loop alongside `tqdm`, which breaks the bar's redraw — use `tqdm.write(...)` instead of `print()` for interleaved messages.
- Forgetting the progress bar adds visible overhead for very fast loops — throttle updates (`mininterval=`) for tight, high-iteration loops.
- Assuming the bar renders identically when output is piped or logged — always test the redirected-output path before relying on it in automation.

### 1.15 Colored Terminal Output

**Use case:** A sysadmin's health-check script scans multiple servers and wants failures to jump out visually in red while successes appear in green, so a human scanning the output can spot problems at a glance.

**Prerequisites**
```bash
python3 -m pip install rich
python3 -c "import rich; print(rich.__version__)"
# rich works on Linux/macOS/Windows (handles Windows console color support automatically).
# Lighter alternative: pip install colorama (manual color codes, no layout features).
```

**Cautions:** Colored output should degrade gracefully when piped to a file or another program — most libraries (including `rich`) auto-detect a non-terminal target and strip color codes, but verify this rather than assuming it for every library.

**Script**
```python
#!/usr/bin/env python3
"""colored_output.py - Colored status reporting using rich."""
from rich.console import Console

console = Console()

SERVERS = {
    "web01": True,
    "web02": True,
    "db01": False,
    "cache01": True,
}


def main() -> None:
    console.print("[bold]Server Health Check[/bold]\n")

    for server, is_healthy in SERVERS.items():
        if is_healthy:
            console.print(f"[green]OK[/green]      {server}")
        else:
            console.print(f"[bold red]FAILED[/bold red]  {server}")

    failed = [s for s, ok in SERVERS.items() if not ok]
    if failed:
        console.print(f"\n[bold red]{len(failed)} server(s) unhealthy:[/bold red] "
                       f"{', '.join(failed)}")
    else:
        console.print("\n[bold green]All servers healthy.[/bold green]")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x colored_output.py

# Run in a terminal - colors render
./colored_output.py

# Redirected to a file - rich strips color codes automatically
./colored_output.py > report.txt
cat report.txt
```

**Sample output**
```text
$ ./colored_output.py
Server Health Check

OK      web01
OK      web02
FAILED  db01
OK      cache01

1 server(s) unhealthy: db01
```
*(In an actual terminal, "OK" renders green and "FAILED" renders bold red.)*

**Variations / flags**
- Use `rich.table.Table` for aligned multi-column colored output instead of manual string formatting.
- Add a `--no-color` flag that forces `Console(no_color=True)` for environments where color is undesired (e.g. some log aggregators).
- Use `colorama.init()` + raw ANSI codes (`\033[92m...\033[0m`) as a dependency-light alternative when `rich`'s extra features aren't needed.

**Common pitfalls**
- Hardcoding raw ANSI escape codes without checking terminal support, producing garbled `\033[92m` text in terminals or logs that don't interpret them.
- Forgetting Windows `cmd.exe` historically needed extra setup for ANSI color — `rich` and `colorama` both handle this, but raw ANSI strings without one of these libraries may not.
- Relying on color alone to convey meaning — always pair color with text labels ("OK"/"FAILED") for accessibility and for when color is stripped.

### 1.16 Pretty-Print Structured Data

**Use case:** A sysadmin's script fetches a large, deeply nested API response or config structure and needs to inspect it on the terminal without it collapsing into an unreadable single line.

**Prerequisites**
```bash
# Standard library option: pprint, json (no install needed).
python3 --version   # 3.8+

# Richer option:
python3 -m pip install rich
```

**Cautions:** Pretty-printing very large structures (megabytes of JSON) directly to the terminal can flood the screen — consider truncating or paging (`| less`) for big payloads rather than dumping everything at once.

**Script**
```python
#!/usr/bin/env python3
"""pretty_print.py - Pretty-print nested structured data two ways."""
import json
from pprint import pprint

SAMPLE_DATA = {
    "server": "web01",
    "status": "healthy",
    "metrics": {
        "cpu_percent": 23.5,
        "memory_mb": 4096,
        "disks": [
            {"mount": "/", "used_pct": 42},
            {"mount": "/data", "used_pct": 87},
        ],
    },
    "tags": ["production", "us-east-1"],
}


def main() -> None:
    print("=== Using pprint ===")
    pprint(SAMPLE_DATA, width=60, sort_dicts=False)

    print("\n=== Using json.dumps (indent=2) ===")
    print(json.dumps(SAMPLE_DATA, indent=2))


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x pretty_print.py

# Basic run
./pretty_print.py

# Page long output
./pretty_print.py | less

# For colorized structured output, use rich instead:
python3 -c "from rich import print as rprint; rprint({'a': 1, 'b': [1,2,3]})"
```

**Sample output**
```text
$ ./pretty_print.py
=== Using pprint ===
{'server': 'web01',
 'status': 'healthy',
 'metrics': {'cpu_percent': 23.5,
             'memory_mb': 4096,
             'disks': [{'mount': '/', 'used_pct': 42},
                       {'mount': '/data', 'used_pct': 87}]},
 'tags': ['production', 'us-east-1']}

=== Using json.dumps (indent=2) ===
{
  "server": "web01",
  "status": "healthy",
  "metrics": {
    "cpu_percent": 23.5,
    "memory_mb": 4096,
    "disks": [
      {
        "mount": "/",
        "used_pct": 42
      },
      {
        "mount": "/data",
        "used_pct": 87
      }
    ]
  },
  "tags": [
    "production",
    "us-east-1"
  ]
}
```

**Variations / flags**
- Use `rich.pretty.pprint()` or `rich.print()` for colorized, syntax-highlighted structured output.
- Pass `sort_keys=True` to `json.dumps` for deterministic, diff-friendly output across runs.
- Combine with `--format json|pprint` flag (via argparse) so scripts can output either machine-readable JSON or human-readable pprint depending on the caller.

**Common pitfalls**
- Using `json.dumps` on data containing non-JSON-serializable objects (e.g. `datetime`, custom classes) without a `default=` handler, causing a `TypeError`.
- Assuming `pprint`'s default key-sorting (older Python versions) preserves insertion order — pass `sort_dicts=False` if order matters for readability.
- Piping colorized `rich` output into a file and getting raw ANSI codes if color-stripping isn't triggered — check with `python3 -c "import sys; print(sys.stdout.isatty())"` piped vs not.

### 1.17 Read JSON Input

**Use case:** A sysadmin's script consumes the output of `aws ec2 describe-instances --output json` or a saved API response and needs to extract specific fields (instance IDs, states) programmatically.

**Prerequisites**
```bash
# Pure standard library (json module) - no install needed.
python3 --version   # 3.8+
```

**Cautions:** Malformed or truncated JSON (e.g. from a cut-off API response) raises `json.JSONDecodeError` — always catch it and report the problem clearly rather than letting the script crash with a raw traceback.

**Script**
```python
#!/usr/bin/env python3
"""read_json.py - Read and process a JSON file."""
import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.json>", file=sys.stderr)
        sys.exit(2)

    data = load_json(Path(sys.argv[1]))

    instances = data.get("instances", [])
    print(f"Found {len(instances)} instance(s):")
    for inst in instances:
        print(f"  {inst.get('id', '?')}: {inst.get('state', 'unknown')}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_json.py

# Create a sample file
cat > instances.json << 'JSONEOF'
{
  "instances": [
    {"id": "i-0123456789abcdef0", "state": "running"},
    {"id": "i-0fedcba9876543210", "state": "stopped"}
  ]
}
JSONEOF

# Run against it
./read_json.py instances.json

# Reading JSON from stdin instead of a file (variation)
cat instances.json | python3 -c "import json,sys; print(json.load(sys.stdin))"
```

**Sample output**
```text
$ ./read_json.py instances.json
Found 2 instance(s):
  i-0123456789abcdef0: running
  i-0fedcba9876543210: stopped
```

**Variations / flags**
- Add `--jq-like` filtering with a `--field` flag to extract a single nested value by dotted path (e.g. `instances.0.state`).
- Use `json.load(sys.stdin)` to accept piped JSON instead of a filename, matching the pattern from 1.2/1.5.
- Validate against a JSON Schema (`pip install jsonschema`) when the input format needs strict structural guarantees.

**Common pitfalls**
- Not catching `json.JSONDecodeError`, which produces a confusing traceback instead of a clear "invalid JSON" message.
- Assuming every key exists — use `.get(key, default)` instead of `data[key]` to avoid `KeyError` on optional fields.
- Large JSON files (multi-GB) loaded entirely into memory with `json.load` — use a streaming parser like `ijson` for very large inputs.

### 1.18 Read CSV Input

**Use case:** A sysadmin needs to process a CSV export of user accounts or server inventory (from a spreadsheet or a database export) to generate a report or feed it into another automation step.

**Prerequisites**
```bash
# Pure standard library (csv module) - no install needed.
python3 --version   # 3.8+
```

**Cautions:** CSV files exported from Excel often use different encodings (e.g. `utf-8-sig` with a BOM) or delimiters (`;` in some locales) — verify the actual format rather than assuming plain comma-separated UTF-8.

**Script**
```python
#!/usr/bin/env python3
"""read_csv.py - Read a CSV file as dictionaries and summarize it."""
import csv
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.csv>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Columns: {reader.fieldnames}")
    print(f"Total rows: {len(rows)}")

    active = [r for r in rows if r.get("status", "").lower() == "active"]
    print(f"Active accounts: {len(active)}")
    for r in active:
        print(f"  {r.get('username', '?')} ({r.get('email', '?')})")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_csv.py

# Create a sample CSV
cat > users.csv << 'CSVEOF'
username,email,status
jdoe,jdoe@example.com,active
asmith,asmith@example.com,disabled
bwong,bwong@example.com,active
CSVEOF

# Run against it
./read_csv.py users.csv
```

**Sample output**
```text
$ ./read_csv.py users.csv
Columns: ['username', 'email', 'status']
Total rows: 3
Active accounts: 2
  jdoe (jdoe@example.com)
  bwong (bwong@example.com)
```

**Variations / flags**
- Auto-detect the delimiter with `csv.Sniffer().sniff(sample)` when the source format is inconsistent.
- Use `pandas.read_csv()` instead of the stdlib module for large files needing filtering, grouping, or joins.
- Add `--delimiter ";"` as a CLI flag for locales/exports that use semicolons instead of commas.

**Common pitfalls**
- Opening the file without `newline=""`, which can cause blank extra rows on Windows due to line-ending translation.
- Not handling a BOM (byte-order mark) from Excel exports — `encoding="utf-8-sig"` strips it automatically; plain `utf-8` leaves a stray character in the first column name.
- Assuming column names are stable — a header rename upstream silently breaks `.get("status")` lookups; validate `reader.fieldnames` against expectations.

### 1.19 Read YAML Input

**Use case:** A sysadmin's automation script reads a `config.yaml` or a Kubernetes/Ansible-style manifest to pull settings (hosts, credentials references, feature flags) rather than hardcoding them.

**Prerequisites**
```bash
python3 -m pip install pyyaml
python3 -c "import yaml; print(yaml.__version__)"
# Not in the standard library - PyYAML is the de facto standard third-party package.
```

**Cautions:** Use `yaml.safe_load()`, never the plain `yaml.load()` without a `Loader` — the unrestricted loader can execute arbitrary Python objects embedded in a malicious YAML file, which is a real security risk if the file's origin isn't fully trusted.

**Script**
```python
#!/usr/bin/env python3
"""read_yaml.py - Safely read and process a YAML config file."""
import sys
from pathlib import Path

import yaml


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.yaml>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: invalid YAML in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"App name: {config.get('app_name', 'unknown')}")
    print(f"Environment: {config.get('environment', 'unknown')}")

    servers = config.get("servers", [])
    print(f"Servers ({len(servers)}):")
    for s in servers:
        print(f"  {s.get('host', '?')}:{s.get('port', '?')}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_yaml.py

# Create a sample config
cat > config.yaml << 'YAMLEOF'
app_name: inventory-service
environment: production
servers:
  - host: web01.internal
    port: 8080
  - host: web02.internal
    port: 8080
YAMLEOF

# Run against it
./read_yaml.py config.yaml
```

**Sample output**
```text
$ ./read_yaml.py config.yaml
App name: inventory-service
Environment: production
Servers (2):
  web01.internal:8080
  web02.internal:8080
```

**Variations / flags**
- Merge multiple YAML files (base + environment overrides) using a dict-deep-merge helper for layered configuration.
- Validate the loaded structure against a schema (`pip install pydantic` or `cerberus`) so typos in config keys fail fast with a clear message.
- Use `ruamel.yaml` instead of PyYAML when you need to preserve comments and formatting while round-tripping edits back to disk.

**Common pitfalls**
- Using `yaml.load(f)` without `Loader=yaml.SafeLoader` (or the `safe_load` shortcut) — this is a well-known security footgun with untrusted YAML.
- YAML's implicit typing surprising users — e.g. `version: 1.20` may parse as a float and lose the trailing zero; quote values in the YAML source when exact string preservation matters.
- Tab characters in YAML indentation — YAML disallows tabs for indentation and will raise a parse error; use spaces consistently.

### 1.20 Read XML Input

**Use case:** A sysadmin needs to parse an XML report from a legacy monitoring tool, a Windows-side configuration export, or a JUnit-style CI test-results file, and pull out specific fields for a summary.

**Prerequisites**
```bash
# Pure standard library (xml.etree.ElementTree) - no install needed.
python3 --version   # 3.8+
```

**Cautions:** The stdlib `xml.etree.ElementTree` parser is not hardened against certain malicious XML payloads (e.g. billion-laughs entity expansion attacks) — for XML from an untrusted source, use the `defusedxml` package instead of the raw stdlib module.

**Script**
```python
#!/usr/bin/env python3
"""read_xml.py - Parse an XML file and extract element data."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.xml>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"Error: invalid XML in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()
    print(f"Root tag: {root.tag}")

    for testsuite in root.findall(".//testsuite"):
        name = testsuite.get("name", "unknown")
        tests = testsuite.get("tests", "0")
        failures = testsuite.get("failures", "0")
        print(f"  Suite: {name} - {tests} tests, {failures} failures")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_xml.py

# Create a sample JUnit-style XML report
cat > results.xml << 'XMLEOF'
<testsuites>
  <testsuite name="auth_tests" tests="12" failures="0"></testsuite>
  <testsuite name="db_tests" tests="20" failures="2"></testsuite>
</testsuites>
XMLEOF

# Run against it
./read_xml.py results.xml
```

**Sample output**
```text
$ ./read_xml.py results.xml
Root tag: testsuites
  Suite: auth_tests - 12 tests, 0 failures
  Suite: db_tests - 20 tests, 2 failures
```

**Variations / flags**
- Switch to `defusedxml.ElementTree` as a drop-in replacement when parsing XML from an untrusted or external source.
- Use `lxml` (`pip install lxml`) instead of the stdlib module for XPath 1.0 support and faster parsing of very large documents.
- Add `--xpath ".//testcase[@name='...']"` as a CLI flag for ad-hoc queries against arbitrary XML structures.

**Common pitfalls**
- Using the plain stdlib parser on XML from an untrusted or external source without considering entity-expansion attacks — prefer `defusedxml` there.
- Forgetting XML namespaces — tags like `<ns:testsuite>` require namespace-qualified searches (`{namespace}tag`) or they silently match nothing.
- Treating attribute values as already the right type — `testsuite.get("tests")` returns a string; cast with `int(...)` before doing arithmetic.

### 1.21 Read TOML Input

**Use case:** A sysadmin's Python tooling reads its own configuration from `pyproject.toml` or a dedicated `config.toml` — TOML is common for tool configs (e.g. Poetry, Ruff, Cargo-style ecosystems) because it's less ambiguous than YAML for simple key/value settings.

**Prerequisites**
```bash
# Python 3.11+: tomllib is built into the standard library (read-only).
python3 --version   # check if >= 3.11

# Python 3.8-3.10: install the backport for reading, and 'tomli-w' if you need to write TOML.
python3 -m pip install tomli
```

**Cautions:** Both `tomllib` (3.11+) and `tomli` (backport) only *read* TOML — they intentionally don't support writing. If you need to also generate/update TOML files, add `tomli-w` (or `tomlkit` if you need to preserve comments/formatting on round-trip edits).

**Script**
```python
#!/usr/bin/env python3
"""read_toml.py - Read a TOML config file (Python 3.11+ tomllib, else tomli)."""
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.8-3.10 backport


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.toml>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open("rb") as f:  # tomllib requires binary mode
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"Error: invalid TOML in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    tool_cfg = config.get("tool", {}).get("mytool", {})
    print(f"Tool name: {config.get('project', {}).get('name', 'unknown')}")
    print(f"Tool settings: {tool_cfg}")


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_toml.py

# Create a sample TOML config
cat > pyproject_sample.toml << 'TOMLEOF'
[project]
name = "inventory-service"

[tool.mytool]
timeout = 30
retries = 3
verbose = true
TOMLEOF

# Run against it
./read_toml.py pyproject_sample.toml
```

**Sample output**
```text
$ ./read_toml.py pyproject_sample.toml
Tool name: inventory-service
Tool settings: {'timeout': 30, 'retries': 3, 'verbose': True}
```

**Variations / flags**
- Add `--check-python-version` logic that picks `tomllib` vs `tomli` explicitly and warns if running on an unsupported old Python version.
- Use `tomlkit` instead when the script must edit a TOML file and preserve human-authored comments/formatting.
- Combine with `argparse` defaults so command-line flags override TOML config values (a common CLI configuration layering pattern).

**Common pitfalls**
- Opening the file in text mode (`"r"`) instead of binary (`"rb"`) — `tomllib`/`tomli` require binary mode and will raise a `TypeError` otherwise.
- Forgetting the module name difference: it's `tomllib` built-in on 3.11+, but the separate package `tomli` (imported the same way with an alias) on older versions.
- Assuming TOML supports arbitrary nesting styles like YAML's anchors/aliases — TOML's feature set is intentionally simpler; deeply dynamic configs may not translate well.

### 1.22 Read from Password-Protected Files

**Use case:** A sysadmin receives a password-protected ZIP of log exports or credential backups from a vendor or another team and needs to extract and process its contents in an automated script rather than manually entering the password in a GUI archive tool each time.

**Prerequisites**
```bash
# Standard library 'zipfile' handles ZipCrypto-encrypted archives (the common case) natively.
python3 --version   # 3.8+

# For AES-encrypted ZIPs (stronger, common from 7-Zip/WinZip AES mode), stdlib zipfile
# cannot decrypt them - use pyzipper instead:
python3 -m pip install pyzipper

# For password-protected PDFs: pip install pikepdf
# For password-protected Office docs (.docx/.xlsx): pip install msoffcrypto-tool
```

**Cautions:** Never hardcode the password in the script source — read it from an environment variable, a secrets manager, or a secure prompt (`getpass`). ZipCrypto (the legacy encryption stdlib `zipfile` supports) is cryptographically weak; treat it as access control, not real confidentiality, for sensitive data.

**Script**
```python
#!/usr/bin/env python3
"""read_protected_zip.py - Extract a password-protected ZIP archive."""
import getpass
import sys
import zipfile
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <archive.zip>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    password = getpass.getpass("Archive password: ")

    try:
        with zipfile.ZipFile(path) as zf:
            zf.setpassword(password.encode("utf-8"))
            print(f"Contents of {path}:")
            for info in zf.infolist():
                print(f"  {info.filename} ({info.file_size} bytes)")

            # Try reading one member to validate the password actually works
            first = zf.infolist()[0]
            zf.read(first.filename)
            print("\nPassword verified successfully.")
    except RuntimeError as e:
        # zipfile raises RuntimeError (not a dedicated exception) for bad passwords
        if "password" in str(e).lower():
            print("Error: incorrect password.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except zipfile.BadZipFile:
        print(f"Error: {path} is not a valid ZIP file.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**How it works and how to run**
```bash
chmod +x read_protected_zip.py

# Create a password-protected ZIP to test with (requires the 'zip' CLI tool)
zip -e -P "correct-horse" secure_logs.zip access.log error.log

# Run the script - it will prompt for the password interactively
./read_protected_zip.py secure_logs.zip
```

**Sample output**
```text
$ ./read_protected_zip.py secure_logs.zip
Archive password: 
Contents of secure_logs.zip:
  access.log (15420 bytes)
  error.log (892 bytes)

Password verified successfully.

$ ./read_protected_zip.py secure_logs.zip
Archive password: [wrong password entered]
Error: incorrect password.
```

**Variations / flags**
- Read the password from an environment variable (`ZIP_PASSWORD`) instead of an interactive prompt for use in unattended automation — see 1.12 for the pattern, and treat the variable as a secret.
- Switch to `pyzipper.AESZipFile` when the archive uses AES-256 encryption (stdlib `zipfile` will fail silently or raise `NotImplementedError` on those).
- Add `--extract-to <dir>` to write the decrypted contents to disk with `zf.extractall(path=dir, pwd=password.encode())` instead of just listing them.

**Common pitfalls**
- Assuming stdlib `zipfile` can open any encrypted ZIP — it only supports the older ZipCrypto method; AES-encrypted archives need `pyzipper`.
- Storing the password in shell history by passing it as a command-line argument instead of prompting or using an environment variable/secrets manager.
- Not verifying the password actually worked — `zipfile` can open the archive listing without validating the password until you actually try to `read()` a member, so an incorrect password may go unnoticed until later in the script.
