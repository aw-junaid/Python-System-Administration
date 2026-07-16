# Input & Output Handling — Python Automation Scripts

This module contains standalone Python scripts that demonstrate common
**Input & Output (I/O) handling** techniques used in Python system
administration and automation: reading input from files, pipes, and stdin;
writing to stdout/stderr; parsing CLI arguments and options; working with
structured data formats (JSON, CSV, YAML, XML, TOML); and building simple
interactive CLI experiences (menus, progress bars, colored output,
confirmation prompts).

Each topic has its own **separate script file** — no numbering, just a
plain descriptive name — so you can copy, run, or study any single one
independently of the others.

---

## ⚠️ Caution Before You Run Anything

These scripts live in this repository:

> https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Input%20&%20Output%20Handling/scripts/

Before installing dependencies or running any script:

- **Read the script first.** Never blindly execute automation scripts,
  even educational ones, without understanding what they do.
- Some scripts **create sample files** (`.txt`, `.json`, `.csv`, `.yaml`,
  `.xml`, `.toml`, `.zip`) in your **current working directory** if you
  don't provide your own input file. Run them from a folder you don't mind
  writing test files into.
- Prefer running inside a **virtual environment** so dependencies don't
  pollute your system Python installation (see below).
- `read_password_protected_file.py` uses a hardcoded demo password
  (`secret123`) purely for teaching purposes — **never** reuse a hardcoded
  password like this for real secrets.

---

## 📦 Installation

1. Clone the repository and move into the scripts folder:

   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/Input & Output Handling/scripts"
   ```

2. (Recommended) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate       # Linux / macOS
   venv\Scripts\activate          # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Requires **Python 3.8+** (Python 3.11+ recommended, since
   `read_toml_input.py` uses the built-in `tomllib` on 3.11+ and only
   falls back to the third-party `toml` package on older versions).

---

## ▶️ How to Run a Script

Every script can be run directly with Python:

```bash
python <script_name>.py
```

Some scripts accept an optional file path argument; if you don't provide
one, they generate a small sample file automatically so you can see the
expected behavior immediately. Check the docstring at the top of each
script for exact usage and expected output.

---

## 📜 Script Reference

| Topic | Script File | Notes |
|---|---|---|
| Accept Input from a File | `input_from_file.py` | Reads a file path from argv or generates a sample |
| Accept Input from a Pipe | `input_from_pipe.py` | Try: `echo "hi" \| python input_from_pipe.py` |
| Capture and Process Command Output | `capture_command_output.py` | Runs a shell command via `subprocess` |
| Redirect Input/Output Streams | `redirect_streams.py` | Redirects `sys.stdout` to a file and restores it |
| Read from Standard Input (stdin) | `read_stdin.py` | Reads one line via `input()` / `sys.stdin` |
| Write to Standard Output (stdout) | `write_stdout.py` | `print()` vs `sys.stdout.write()` vs flushing |
| Write to Standard Error (stderr) | `write_stderr.py` | Correct way to print warnings/errors |
| Read Multiline Input | `read_multiline_input.py` | Reads lines until blank line / EOF |
| Handle Command-Line Arguments | `handle_cli_arguments.py` | Raw `sys.argv` access, no library |
| Parse Command-Line Options using argparse | `argparse_options.py` | Built-in `argparse` module |
| Parse Command-Line Options using click | `click_options.py` | **Requires `click`** |
| Parse Environment Variables | `parse_env_variables.py` | Reads `os.environ` with defaults |
| Interactive Command-Line Menus | `interactive_menu.py` | Numbered menu loop |
| Display Progress Bars | `progress_bar.py` | Manual bar + optional **`tqdm`** bar |
| Colored Terminal Output | `colored_output.py` | Uses **`colorama`**, falls back to raw ANSI |
| Pretty-Print Structured Data | `pretty_print_data.py` | `print()` vs `pprint` vs `json.dumps(indent=2)` |
| Read JSON Input | `read_json_input.py` | Built-in `json` module |
| Read CSV Input | `read_csv_input.py` | Built-in `csv` module |
| Read YAML Input | `read_yaml_input.py` | **Requires `PyYAML`** |
| Read XML Input | `read_xml_input.py` | Built-in `xml.etree.ElementTree` |
| Read TOML Input | `read_toml_input.py` | Built-in `tomllib` (3.11+) or **`toml`** (older) |
| Read from Password-Protected Files | `read_password_protected_file.py` | Built-in `zipfile`, demo password |
| Read from stdin with Timeout | `read_stdin_timeout.py` | Uses `select` (Linux/Mac only) |
| Interactive Confirmation Prompts | `interactive_confirmation.py` | Loops until valid y/n answer |

---

## 🧪 Examples

```bash
# File input
python input_from_file.py my_notes.txt

# Piped input
cat access.log | python input_from_pipe.py

# argparse-based CLI
python argparse_options.py --name Junaid --age 25 --verbose

# click-based CLI
python click_options.py --name Junaid --count 3 --shout

# Environment variables
APP_NAME=MyApp DEBUG=true python parse_env_variables.py

# JSON / CSV / YAML / XML / TOML readers (no args = auto-generates sample data)
python read_json_input.py
python read_csv_input.py
python read_yaml_input.py
python read_xml_input.py
python read_toml_input.py
```

---

## ✅ What to Expect

- Every script is **self-contained** and runnable on its own — no shared
  imports between scripts.
- Scripts that need a file to read (JSON/CSV/YAML/XML/TOML/file input) will
  **auto-generate a small sample file** in the current directory the first
  time you run them without arguments, so you always get a working demo.
- Scripts needing third-party packages (`click`, `PyYAML`, `tqdm`,
  `colorama`, `toml`) will print a clear error telling you which package to
  `pip install` if it's missing.
- Platform-specific scripts (`read_stdin_timeout.py`) note their
  limitations (e.g. Windows vs Linux/Mac) directly in their docstring and
  at runtime.

---

