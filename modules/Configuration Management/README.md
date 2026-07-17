# Configuration Management — Python Scripts

Companion scripts for the **Configuration Management** module of
[Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Configuration%20Management/scripts).

Every script can be run directly and includes a safe built-in demo mode — it
generates its own small demo config file if you don't give it a real path, so you can see
expected output immediately.

---

## ⚠️ Read This Before Running Anything

- Several scripts **write or overwrite files** on disk: `generate_config_file.py`,
  `modify_config_file.py`, `merge_config_files.py` (with `--output`), `backup_config.py`,
  `restore_config.py`, and `manage_app_settings.py`. Always know which file you're pointing a
  script at before running it against something real.
- `modify_config_file.py` and `restore_config.py` **overwrite the target file directly, with no
  prompt**. Run `backup_config.py` on any file you care about before modifying or restoring it.
- Demo mode in every script only touches **new demo files it creates itself** (e.g.
  `demo_config.json`) — it will never overwrite a real config file you already have unless you
  explicitly pass that file's path as an argument.
- Never commit real `.env` files or configs containing secrets/passwords to version control.
  `load_env_file.py` is for loading them locally, not for generating or sharing them.
- `parse_yaml_config.py` uses `yaml.safe_load()` intentionally (never `yaml.load()`) to avoid
  executing arbitrary content from untrusted YAML files. Do not change this without understanding
  the risk.

---

## Requirements

- Python 3.8+
- `PyYAML` (for YAML parsing/generation)
- `tomli` (only needed on Python 3.10 and earlier; Python 3.11+ has built-in `tomllib`)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Configuration Management/scripts"

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## How to Run Any Script

All scripts follow the same pattern:

```bash
python3 <script_name>.py [arguments]
```

If you run a script **with no arguments**, it creates and uses a small demo config file so you
can see expected output right away. Scripts that need a real file path or key/value will tell you
exactly how to supply it.

---

## Script Reference

| # | Script | Topic | Run Example |
|---|--------|-------|-------------|
| 1 | `read_config_file.py` | Read Configuration Files | `python3 read_config_file.py myconfig.txt` |
| 2 | `parse_ini_config.py` | Parse INI Files | `python3 parse_ini_config.py config.ini` |
| 3 | `parse_json_config.py` | Parse JSON Configuration | `python3 parse_json_config.py config.json` |
| 4 | `parse_yaml_config.py` | Parse YAML Configuration | `python3 parse_yaml_config.py config.yaml` |
| 5 | `parse_toml_config.py` | Parse TOML Configuration | `python3 parse_toml_config.py config.toml` |
| 6 | `parse_xml_config.py` | Parse XML Configuration | `python3 parse_xml_config.py config.xml` |
| 7 | `validate_config_values.py` | Validate Configuration Values | `python3 validate_config_values.py config.json` |
| 8 | `merge_config_files.py` | Merge Multiple Configuration Files | `python3 merge_config_files.py base.json override.json` |
| 9 | `generate_config_file.py` | Generate Configuration Files | `python3 generate_config_file.py --format yaml --output config.yaml` |
| 10 | `modify_config_file.py` | Modify Existing Configuration Files | `python3 modify_config_file.py config.json --key server.port --value 9090` |
| 11 | `backup_config.py` | Backup Configuration Files | `python3 backup_config.py config.json` |
| 12 | `restore_config.py` | Restore Configuration Files | `python3 restore_config.py config.json.bak config.json` |
| 13 | `manage_app_settings.py` | Manage Application Settings | `python3 manage_app_settings.py set theme dark` |
| 14 | `load_env_file.py` | Load Environment Variables (.env) | `python3 load_env_file.py .env` |

---

## Detailed Usage & Expected Output

### 1. `read_config_file.py`
Reads any plain text/config file and prints its contents with line numbers.
```bash
python3 read_config_file.py myconfig.txt
```
**Expected output:** numbered lines of the file plus a total line count.
**Caution:** read-only; never modifies the file.

### 2. `parse_ini_config.py`
Parses an INI file (`[section]` + `key = value`) using `configparser` and prints each section.
```bash
python3 parse_ini_config.py config.ini
```
**Caution:** all values are returned as strings by `configparser` — convert types yourself if
needed (see `validate_config_values.py` for a type-checking pattern).

### 3. `parse_json_config.py`
Parses a JSON file and pretty-prints its structure and top-level keys.
```bash
python3 parse_json_config.py config.json
```
**Caution:** JSON doesn't support comments or trailing commas — malformed files produce a clear
parse-error message instead of a crash.

### 4. `parse_yaml_config.py`
Parses a YAML file using PyYAML's `safe_load()` and prints the resulting structure.
```bash
python3 parse_yaml_config.py config.yaml
```
**Requires:** `PyYAML`.
**Caution:** YAML is indentation-sensitive; a misplaced space can change meaning or cause errors.

### 5. `parse_toml_config.py`
Parses a TOML file using the built-in `tomllib` (Python 3.11+) or `tomli` (3.10 and earlier).
```bash
python3 parse_toml_config.py config.toml
```
**Caution:** TOML files must be opened in binary mode — this script handles that for you
automatically.

### 6. `parse_xml_config.py`
Parses an XML file using the standard library's `xml.etree.ElementTree` and prints its tree.
```bash
python3 parse_xml_config.py config.xml
```
**Caution:** uses the standard library's default (safe) parser settings — avoid switching to
third-party XML parsers with entity resolution enabled on untrusted files.

### 7. `validate_config_values.py`
Validates a JSON config against a rules dictionary (required keys, types, min/max ranges) defined
inside the script, and reports every problem found.
```bash
python3 validate_config_values.py config.json
```
**Caution:** edit the `RULES` dictionary in the script to match your own schema before relying on
it for a real project.

### 8. `merge_config_files.py`
Deep-merges two or more JSON config files; later files override matching keys from earlier ones.
```bash
python3 merge_config_files.py base.json override.json --output merged.json
```
**Caution:** nested dictionaries are deep-merged, but lists are fully replaced (not concatenated).
`--output` overwrites an existing file without prompting.

### 9. `generate_config_file.py`
Generates a new config file in JSON, YAML, or INI format from a dictionary defined in the script.
```bash
python3 generate_config_file.py --format yaml --output config.yaml
```
**Caution:** overwrites the output file if it already exists. YAML output requires `PyYAML`. Edit
`DEFAULT_CONFIG` inside the script to generate your own structure.

### 10. `modify_config_file.py`
Changes a single value in a JSON config file using dot notation for nested keys, then saves it.
```bash
python3 modify_config_file.py config.json --key server.port --value 9090
```
**Caution:** overwrites the original file. Values are auto-converted (`"true"`/`"false"` → bool,
numeric strings → int/float). Back up important files first.

### 11. `backup_config.py`
Creates a timestamped copy of a config file (e.g. `config.json.20260717_101530.bak`).
```bash
python3 backup_config.py config.json --backup-dir backups
```
**Caution:** does not delete old backups automatically — clean up periodically if needed.

### 12. `restore_config.py`
Restores a config file from a previously created backup, overwriting the destination.
```bash
python3 restore_config.py config.json.20260717_101530.bak config.json
```
**⚠️ Overwrites the destination without prompting.** Does not validate the backup's contents
before restoring — verify with `read_config_file.py` first if unsure.

### 13. `manage_app_settings.py`
A minimal settings manager: get/set/list values in `app_settings.json`, creating sane defaults
on first run.
```bash
python3 manage_app_settings.py list
python3 manage_app_settings.py set theme dark
python3 manage_app_settings.py get theme
```
**Caution:** overwrites `app_settings.json` on every `set` call.

### 14. `load_env_file.py`
Loads `KEY=VALUE` pairs from a `.env` file into the current process's environment variables.
```bash
python3 load_env_file.py .env
python3 load_env_file.py .env --override
```
**Caution:** variables only persist for this Python process (and any children it launches) — not
your shell. Does not overwrite existing environment variables unless `--override` is passed.
Never commit real `.env` files with secrets to version control.

---

## General Notes

- Every script can be run standalone — none depend on each other at import time.
- Scripts that accept no arguments always fall back to a **safe demo mode**, creating their own
  small demo file rather than touching anything real.
- Where a script can modify or overwrite files, its docstring at the top contains an explicit
  **Caution** section — read it before pointing the script at a real config.
- Tested on Linux (Ubuntu) with Python 3.12. All scripts use cross-platform standard library
  calls (plus PyYAML/tomli) and should work unmodified on macOS and Windows.
