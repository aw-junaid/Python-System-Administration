# Automation Best Practices

Twelve standalone Python scripts, each one demonstrating a single
automation best practice with a runnable, self-contained example —
not just theory. Read the code, run it, and see the practice in
action.

Every script:
- Runs completely on its own (no shared modules to import).
- Works out of the box — no input files or setup required to try it.
- Accepts `--help` where relevant for extra options.
- Includes an "anti-pattern" comment near the top contrasting what
  *not* to do with the pattern it demonstrates.

> ⚠️ **Before you run anything:** a few of these scripts write files
> (config files, log files, a scaffolded package, generated docs) to
> your current working directory, and `packaging_automation_tools.py`
> / `documentation_generation.py` create new folders. Review any
> script before running it, run it inside a project folder or virtual
> environment (not a system directory), and never run automation
> scripts from an untrusted repo without reading the code first. This
> applies to every script in this repo, not just this module.

---

## 1. Install

Clone the repo, then from inside this module's folder:

```bash
# (Recommended) create a virtual environment first
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install all dependencies for every script
pip install -r requirements.txt
```

Requires **Python 3.8+**. Most scripts need no extra packages at all
— see the table below for which ones do.

---

## 2. Scripts overview

| # | Script | Best practice | Extra dependency |
|---|--------|----------------|-------------------|
| 1 | `exception_handling.py` | Catch specific exceptions, not bare `except:` | none (stdlib only) |
| 2 | `logging_best_practices.py` | Use appropriate log levels & handlers | none (stdlib only) |
| 3 | `retry_strategies.py` | Exponential backoff + jitter + idempotency | none (stdlib only) |
| 4 | `secure_credential_handling.py` | Never hardcode secrets; load from env/vault | `python-dotenv` (optional) |
| 5 | `idempotent_automation.py` | Design scripts safe to rerun | none (stdlib only) |
| 6 | `modular_scripting.py` | Break monoliths into functions/classes | none (stdlib only) |
| 7 | `configuration_management.py` | Externalize magic numbers/strings | `PyYAML` (optional) |
| 8 | `testing_automation_scripts.py` | Unit test `subprocess` calls with pytest | `pytest` |
| 9 | `packaging_automation_tools.py` | `pyproject.toml` for internal distribution | none (stdlib only) |
| 10 | `cross_platform_scripting.py` | Handle path separators & null devices portably | none (stdlib only) |
| 11 | `performance_optimization.py` | Profile with `cProfile` before optimizing | none (stdlib only) |
| 12 | `documentation_generation.py` | Auto-build docs from docstrings with Sphinx | `sphinx` (optional) |

Run any script with `-h` to see its options where applicable:

```bash
python configuration_management.py -h
```

---

## 3. Usage and expected output, per script

### 1. `exception_handling.py`
Catches specific errors (`FileNotFoundError`, `ValueError`,
`PermissionError`, `OSError`) instead of a bare `except:`.

```bash
python exception_handling.py
```
**Expected output:** four simulated tasks run (missing config, divide
by zero, bad int conversion, unwritable path). Each failure is caught
by a specific handler and reported clearly, then a summary line shows
how many tasks needed a handled failure — nothing crashes with an
unhandled traceback, and nothing is silently swallowed.

---

### 2. `logging_best_practices.py`
Uses `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` appropriately, with a
console handler and a rotating file handler.

```bash
python logging_best_practices.py
python logging_best_practices.py --log-file automation.log --verbose
```
**Expected output:** console shows INFO+ messages (or DEBUG+ with
`--verbose`) from a simulated backup task. A rotating log file (default
`automation.log`) captures every level including DEBUG, each line
timestamped and tagged.

---

### 3. `retry_strategies.py`
Exponential backoff **with jitter**, a max attempt cap, and a separate
demonstration of an **idempotent** retried operation using an
idempotency key.

```bash
python retry_strategies.py
python retry_strategies.py --max-attempts 5 --base-delay 0.5
```
**Expected output:** log lines showing a simulated flaky API call
retried with increasing, randomized (jittered) delays until it
succeeds or attempts run out. Then a second demo shows calling an
idempotent "create order" function twice with the same key — the
second call returns the cached result instead of creating a duplicate.

---

### 4. `secure_credential_handling.py`
Loads secrets from environment variables (or a local `.env` file via
`python-dotenv`), never hardcodes them, and masks them in all output.

```bash
python secure_credential_handling.py
# or, with real values:
export API_TOKEN="s3cr3t-value-123"
export DB_PASSWORD="hunter2xxxx"
python secure_credential_handling.py
```
**Expected output:** without the required env vars set, the script
exits with a clear, non-zero error telling you exactly what to set —
it does **not** fall back to a hardcoded secret. With them set, it
prints masked previews only (e.g. `s3cr********-123`), never the raw
value.

---

### 5. `idempotent_automation.py`
Ensures a directory exists, a config line is present exactly once, and
expensive processing is skipped when nothing changed — all safe to
rerun.

```bash
python idempotent_automation.py
python idempotent_automation.py   # run again — see "no changes needed"
```
**Expected output:** first run reports every change it made (directory
created, config line added, file processed). Running it again
immediately reports **no changes needed**, proving the automation is
idempotent. Creates a small workspace at `./idempotent_demo/`.

---

### 6. `modular_scripting.py`
Composes a system report from small, single-responsibility functions
and a coordinating class, instead of one giant inline script.

```bash
python modular_scripting.py
```
**Expected output:** a system report (platform, Python version, CPU
count, disk usage, working directory) printed to the console, each
section produced by its own small function you could reuse or unit
test independently elsewhere.

---

### 7. `configuration_management.py`
Externalizes settings (retry counts, timeouts, URLs) to a YAML config
file, with environment-variable overrides and validation.

```bash
python configuration_management.py
APP_MAX_RETRIES=10 python configuration_management.py
```
**Expected output:** on first run, creates a default `config.yaml`
next to the script and prints the effective configuration, labeling
each value as coming from the config file or an environment override.
A tiny simulated task then runs using those externalized values.

---

### 8. `testing_automation_scripts.py`
Contains an automation function that wraps `subprocess` AND its
`pytest` unit tests (using `unittest.mock` so no real commands run
during testing).

```bash
# Run the automation function directly (executes a real command):
python testing_automation_scripts.py

# Run the unit tests (subprocess is mocked — no real commands run):
pip install pytest
pytest testing_automation_scripts.py -v
```
**Expected output:** running the script directly prints your real disk
usage percentage. Running `pytest` runs 4 test cases (success,
non-zero exit code, command-not-found fallback, timeout) that all pass
in well under a second with zero side effects.

---

### 9. `packaging_automation_tools.py`
Scaffolds a modern, installable package (`pyproject.toml`, not the
older `setup.py`) for distributing an internal automation tool.

```bash
python packaging_automation_tools.py
python packaging_automation_tools.py --name my-automation-tool --outdir my-automation-tool
```
**Expected output:** a new folder (default `my_internal_tool/`)
containing a working package skeleton with a `pyproject.toml`, README,
and a CLI entry point. The script prints exactly what to run next:
`pip install -e .` followed by the generated CLI command.

---

### 10. `cross_platform_scripting.py`
Uses `pathlib`, `os.devnull`, and `os.pathsep` instead of hardcoded
`/`, `\`, `/dev/null`, or `:`/`;`.

```bash
python cross_platform_scripting.py
```
**Expected output:** a report showing your detected OS, a path built
portably with pathlib, the correct null device for your OS, and a
demonstration of running a command while discarding its output
portably (works unmodified on Windows, macOS, and Linux).

---

### 11. `performance_optimization.py`
Profiles code with `cProfile` before optimizing, then shows a concrete
before/after speedup (list vs. set membership checks).

```bash
python performance_optimization.py
```
**Expected output:** two `cProfile` reports (unoptimized vs.
optimized), followed by a summary line showing the measured speedup
(typically tens-of-times faster). Two `.prof` files are also written
for deeper inspection with `snakeviz` or `pstats`.

---

### 12. `documentation_generation.py`
Scaffolds a Sphinx project pointed at a sample module with real
docstrings, and builds HTML docs automatically if Sphinx is installed.

```bash
pip install sphinx
python documentation_generation.py
python documentation_generation.py --outdir mydocs
```
**Expected output:** a folder (default `docs_demo/`) containing the
sample module, Sphinx config, and — if Sphinx is installed — a built
`build/html/index.html` you can open in a browser to see the
docstrings rendered as documentation. If Sphinx isn't installed, the
script still scaffolds everything and prints the exact commands to
finish the build yourself.

---

## 4. Troubleshooting

- **`ModuleNotFoundError`** — install the specific optional package
  listed in the table above for that script, or just
  `pip install -r requirements.txt` to get everything at once.
- **`pytest` not found** — `pip install pytest`, then run
  `pytest testing_automation_scripts.py -v` from inside this folder.
- **`sphinx-build` not found** — `documentation_generation.py` still
  scaffolds the project either way; install Sphinx to get the actual
  HTML build (`pip install sphinx`).
- **Permission errors writing output** — several scripts write to the
  current directory; run them from a folder you have write access to.
- **Windows-specific behavior** — `cross_platform_scripting.py` is
  designed to adapt automatically; if something looks off, check that
  you're running a recent Python 3.8+ and not a very old interpreter.
