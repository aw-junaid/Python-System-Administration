# Package Management Scripts

Python automation scripts for common `pip` / `venv` / dependency-resolver
tasks. Each script is standalone, uses only the Python standard library,
and can be run directly with `python3 <script>.py --help`.

---

## ⚠️ Caution before you run anything

These scripts execute real `pip`, `venv`, `poetry`, and `pipenv` commands
as subprocesses. That means they can genuinely **install, upgrade, or
remove packages** on whatever interpreter you point them at.

- **Always know which interpreter you're targeting.** Every script accepts
  `--python /path/to/python` (default: whatever `python3` you invoke the
  script with). If you don't pass `--python`, you are almost certainly
  targeting your *global* system or user Python — not a project venv.
- **Test in a virtual environment first**, not your system Python. Use
  `create_venv.py` to make a throwaway one before trying the others.
- `remove_packages.py` will prompt for confirmation before uninstalling
  anything, unless you pass `--yes`. Don't script `--yes` into a cron job
  without being sure of what it targets.
- Network access is required for anything that talks to PyPI (`install_packages.py`,
  `upgrade_packages.py`, `install_from_requirements.py`, `check_outdated.py`).
  If you're on a machine with restricted/no internet access, those will
  fail with a connection error — that's expected, not a bug in the script.
- If you're pulling this code from the repo
  (`https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Package%20Management/scripts`),
  read each script before running it, the same as you should with any
  code you didn't write yourself.

---

## Setup

```bash
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Package Management/scripts"

# No third-party dependencies are required — see requirements.txt.
# (Only needed if you plan to use manage_with_poetry.py)
pip install poetry pipenv
```

All scripts support `-h` / `--help` for the full flag list.

---

## Scripts

### 1. `install_packages.py`
Install one or more packages via `pip install`, run as a subprocess.

```bash
python3 install_packages.py requests "flask>=2.0"
python3 install_packages.py --user requests
python3 install_packages.py --python ./myenv/bin/python requests
```

**Expected output:** a line per package (`[install] OK: requests` or
`[install] FAILED: ...`), then a summary of succeeded/failed packages.
Exit code `0` if everything installed, `1` if anything failed.

---

### 2. `upgrade_packages.py`
Detect and batch-upgrade outdated packages.

```bash
python3 upgrade_packages.py                 # upgrade everything outdated
python3 upgrade_packages.py requests numpy  # only these, if outdated
python3 upgrade_packages.py --dry-run       # show plan, change nothing
```

**Expected output:** list of outdated packages found, then an
`[upgrade] OK/FAILED` line per package, then a summary. With `--dry-run`,
nothing is installed — you only see `[dry-run] Would run: ...` lines.

---

### 3. `remove_packages.py`
Safely uninstall packages, with a confirmation prompt and protection
for `pip`, `setuptools`, and `wheel`.

```bash
python3 remove_packages.py requests flask
python3 remove_packages.py requests --yes         # skip confirmation
python3 remove_packages.py pip --force --yes      # override protection
```

**Expected output:** a `y/N` prompt (unless `--yes`), then
`[remove] OK: <package>` per package removed, plus a summary showing
removed / failed / skipped (protected) packages.

---

### 4. `check_outdated.py`
Programmatic inventory of outdated packages.

```bash
python3 check_outdated.py
python3 check_outdated.py --json
python3 check_outdated.py --save outdated.json
```

**Expected output:** a table of `PACKAGE / CURRENT / LATEST`, or raw JSON
with `--json`. Prints "Everything is up to date." if nothing is stale.

---

### 5. `create_venv.py`
Build an isolated virtual environment using the standard-library `venv`
module.

```bash
python3 create_venv.py myenv
python3 create_venv.py myenv --with-pip-upgrade
python3 create_venv.py myenv --clear    # wipe & recreate if it exists
```

**Expected output:** confirmation the venv was created, plus the path to
its interpreter, e.g. `myenv/bin/python` (or `myenv\Scripts\python.exe`
on Windows).

---

### 6. `activate_venv.py`
A subprocess can't change your parent shell's active environment (shell
activation is a shell-only concept), so this script instead **locates**
the venv's interpreter/activation script and prints the exact command to
run yourself — and optionally runs a one-off command using that venv.

```bash
python3 activate_venv.py myenv
python3 activate_venv.py myenv --run "-m pip -V"
```

**Expected output:** the interpreter path, the shell command to activate
it (e.g. `source myenv/bin/activate`), and (with `--run`) the output of
the command executed using that venv's python.

---

### 7. `export_requirements.py`
`pip freeze`, scoped to a specific interpreter/project.

```bash
python3 export_requirements.py
python3 export_requirements.py --python ./myenv/bin/python --output requirements.txt
```

**Expected output:** `[export] Wrote N package pin(s) to requirements.txt`,
and a `requirements.txt` file containing pinned `package==version` lines
(or an empty file if the venv has nothing installed).

---

### 8. `install_from_requirements.py`
Reproduce an environment reliably from a lock file.

```bash
python3 install_from_requirements.py requirements.txt
python3 install_from_requirements.py requirements.txt --python ./myenv/bin/python
```

**Expected output:** pip's normal install log, then
`[install-req] Environment reproduced successfully.` on success, or the
last part of pip's error output on failure. Exit code `2` if the file
path doesn't exist.

---

### 9. `manage_with_poetry.py`
Thin wrapper that drives an already-installed `poetry` or `pipenv` for
common actions: `init`, `install`, `add`, `remove`, `lock`, `show`.

```bash
python3 manage_with_poetry.py --tool poetry --action init
python3 manage_with_poetry.py --tool poetry --action add --package requests
python3 manage_with_poetry.py --tool pipenv --action install --package flask
```

**Expected output:** the underlying `poetry`/`pipenv` command's own output.
If the tool isn't installed/on PATH, the script tells you and exits with
code `1` rather than attempting to install it for you.

---

## Exit code convention (all scripts)

| Code | Meaning                                  |
|------|-------------------------------------------|
| 0    | Success                                   |
| 1    | Operation failed (pip/venv/tool error)    |
| 2    | Bad arguments / missing required input    |

This makes every script safe to chain in a shell pipeline, e.g.:

```bash
python3 create_venv.py myenv && \
python3 install_from_requirements.py requirements.txt --python myenv/bin/python && \
python3 check_outdated.py --python myenv/bin/python
```
