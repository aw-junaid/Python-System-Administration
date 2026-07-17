# Data Serialization & Transformation — Scripts

This folder contains **23 standalone Python automation scripts**, one per
topic, covering common data-serialization and format-conversion tasks:
JSON, CSV, YAML, XML, INI, TOML, Pickle, MessagePack, Base64, URL
encoding, character encodings, JSON flattening, config merging, JSON
Schema validation, XSLT, and streaming large files.



Each script is:
- **Independent** — no shared modules, no numbered filenames. Every
  file can be copied out and run on its own.
- **Runnable with zero arguments** — every script ships with built-in
  demo data, so you can see exactly what it does before pointing it at
  your own files.
- **CLI-driven** — pass `--input` / `--output` (and script-specific
  flags) to use your own data instead of the demo.

---

## ⚠️ Important cautions before you start

1. **This is example/learning code**, written for the
   `Python-System-Administration` repo. Review any script before
   running it against production data or files you care about.
2. **`pickle_serialize.py` — security warning.** Python's `pickle`
   module can execute arbitrary code when loading (`pickle.load()`)
   data from an untrusted source. Only unpickle files you created
   yourself or that come from a source you fully trust. The demo in
   this script only ever loads a file it just wrote.
3. **Network access:** none of these scripts make network calls. All
   demo data is generated locally.
4. **File overwrites:** if you pass `--output path/to/file`, that file
   will be overwritten without a confirmation prompt. Point `--output`
   at a new/scratch path the first time you try a script.
5. **Python version:** these scripts target **Python 3.9+**.
   `toml_to_json.py` uses the built-in `tomllib` module on **Python
   3.11+**; on older Python versions it automatically falls back to
   the third-party `toml` package (included in `requirements.txt`).
6. Some third-party packages (`lxml`, lxml's XSLT/`libxml2` backend,
   etc.) need OS-level build tools on some platforms. If `pip install`
   fails on a package, install your OS's Python dev headers (e.g. on
   Debian/Ubuntu: `sudo apt install python3-dev libxml2-dev
   libxslt1-dev`) and try again, or check the package's PyPI page for
   platform-specific notes.

---

## 1. Installation

```bash
# Clone the repo (or just download this scripts/ folder)
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Data Serialization & Transformation/scripts"

# (Recommended) create a virtual environment first
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install all dependencies used across all 23 scripts
pip install -r requirements.txt
```

You do **not** need every package for every script — most scripts only
need 0 or 1 third-party package. See the per-script dependency notes
below. If a script needs a package that isn't installed, it will print
a clear message like:

```
ERROR: xmltodict is not installed.
Install dependencies first:  pip install -r requirements.txt
```

instead of crashing with a raw traceback.

---

## 2. Running a script

Every script follows the same pattern:

```bash
# 1. See it work immediately, no arguments, no setup required
python3 <script_name>.py

# 2. See all available options
python3 <script_name>.py --help

# 3. Run it against your own data
python3 <script_name>.py --input your_file.ext --output result.ext
```

---

## 3. Script-by-script reference

| # | Script | What it does | Needs (beyond stdlib) | Try it |
|---|--------|---------------|------------------------|--------|
| 337 | `json_serialize.py` | Serialize dicts, lists, dataclasses, datetimes to a JSON string/file | — | `python3 json_serialize.py` |
| 338 | `json_deserialize.py` | Parse JSON text/file back into Python objects + structure summary | — | `python3 json_deserialize.py` |
| 339 | `json_to_csv.py` | Flatten a JSON array of (nested) objects into CSV rows | — | `python3 json_to_csv.py` |
| 340 | `csv_to_json.py` | Convert CSV rows into a nested JSON array (dot-notation columns become nested objects) | — | `python3 csv_to_json.py` |
| 341 | `json_to_yaml.py` | Convert JSON to YAML | `PyYAML` | `python3 json_to_yaml.py` |
| 342 | `yaml_to_json.py` | Convert YAML config files to JSON | `PyYAML` | `python3 yaml_to_json.py` |
| 343 | `xml_to_json.py` | Convert XML documents to JSON | `xmltodict` | `python3 xml_to_json.py` |
| 344 | `json_to_xml.py` | Build XML from JSON (single root key required) | `xmltodict` | `python3 json_to_xml.py` |
| 345 | `csv_to_xml.py` | Convert CSV rows into hierarchical XML | — | `python3 csv_to_xml.py` |
| 346 | `xml_to_csv.py` | Flatten repeated XML elements into CSV rows | — | `python3 xml_to_csv.py` |
| 347 | `jq_query.py` | Apply simplified jq-style path queries (`.a.b[*].c`) to JSON | — (pure Python) | `python3 jq_query.py --query ".employees[*].name"` |
| 348 | `ini_to_json_yaml.py` | Migrate legacy `.ini` config files to JSON or YAML | `PyYAML` (only for `--format yaml`) | `python3 ini_to_json_yaml.py` |
| 349 | `toml_to_json.py` | Convert TOML (e.g. `pyproject.toml`) to JSON | `toml` (only on Python < 3.11) | `python3 toml_to_json.py` |
| 350 | `pickle_serialize.py` | Binary-serialize complex Python objects (sets, tuples, custom classes) with `pickle` | — | `python3 pickle_serialize.py` |
| 351 | `msgpack_serialize.py` | Pack/unpack data with MessagePack; compares size vs. JSON | `msgpack` | `python3 msgpack_serialize.py` |
| 352 | `base64_codec.py` | Base64 encode/decode text or files | — | `python3 base64_codec.py` |
| 353 | `url_codec.py` | Percent-encode/decode URLs and query strings | — | `python3 url_codec.py` |
| 354 | `encoding_convert.py` | Transcode text between character encodings (UTF-8, Latin-1, ASCII, ...) | — | `python3 encoding_convert.py` |
| 355 | `flatten_json.py` | Flatten nested JSON to flat dot-notation keys, and unflatten it back | — | `python3 flatten_json.py` |
| 356 | `merge_configs.py` | Deep-merge multiple JSON/YAML config files (later files override earlier) | `PyYAML` (only for `.yaml`/`.yml` inputs) | `python3 merge_configs.py` |
| 357 | `validate_json_schema.py` | Validate JSON data against a JSON Schema | `jsonschema` | `python3 validate_json_schema.py` |
| 358 | `xslt_transform.py` | Apply an XSLT stylesheet to transform XML (e.g. to HTML) | `lxml` | `python3 xslt_transform.py` |
| 359 | `stream_large_dataset.py` | Stream large JSON/CSV files row-by-row instead of loading them fully into memory | `ijson` (only for JSON streaming) | `python3 stream_large_dataset.py` |

---

## 4. Worked examples

```bash
# Serialize a dict to JSON, write to file
python3 json_serialize.py --output out.json

# Flatten a JSON API response into a CSV for Excel/Sheets
python3 json_to_csv.py --input api_response.json --output report.csv

# Turn a legacy INI config into YAML
python3 ini_to_json_yaml.py --input app.ini --format yaml --output app.yaml

# Pull every employee name out of a JSON document (jq-style)
python3 jq_query.py --input company.json --query ".employees[*].name"

# Validate a JSON payload against a schema before accepting it
python3 validate_json_schema.py --schema schema.json --data payload.json

# Merge a base config with an environment-specific override
python3 merge_configs.py --inputs base.json production.yaml --output final.json

# Safely inspect how big a 100k-row CSV/JSON file is without loading it all
python3 stream_large_dataset.py --format csv --input huge_export.csv
```

---

## 5. Expected output, in general

- **Conversion scripts** (`*_to_*.py`) print the converted data to the
  terminal, and additionally write it to `--output PATH` if you supply
  one. Exit code `0` means success; a non-zero exit code with an
  `ERROR: ...` message means the input was invalid, malformed, or a
  dependency was missing.
- **Validation script** (`validate_json_schema.py`) prints `VALID` or
  a bulleted list of `INVALID` reasons — it does not raise an
  exception for a failed validation, only for a malformed schema/JSON
  file.
- **Binary scripts** (`pickle_serialize.py`, `msgpack_serialize.py`)
  print the byte size of the file they wrote, and (for
  `msgpack_serialize.py`) compare that size against equivalent JSON.
- **`stream_large_dataset.py`** prints a running row count plus
  min/max/average of a numeric column, and the peak memory used during
  the whole run (should stay flat/low even as the input file size
  grows, which is the point of streaming).

## 6. Folder layout expected in the repo

```
modules/Data Serialization & Transformation/
├── README.md                 <- this file
└── scripts/
    ├── requirements.txt
    ├── json_serialize.py
    ├── json_deserialize.py
    ├── json_to_csv.py
    ├── csv_to_json.py
    ├── json_to_yaml.py
    ├── yaml_to_json.py
    ├── xml_to_json.py
    ├── json_to_xml.py
    ├── csv_to_xml.py
    ├── xml_to_csv.py
    ├── jq_query.py
    ├── ini_to_json_yaml.py
    ├── toml_to_json.py
    ├── pickle_serialize.py
    ├── msgpack_serialize.py
    ├── base64_codec.py
    ├── url_codec.py
    ├── encoding_convert.py
    ├── flatten_json.py
    ├── merge_configs.py
    ├── validate_json_schema.py
    ├── xslt_transform.py
    └── stream_large_dataset.py
```

If you're placing `requirements.txt` at the module root instead of
inside `scripts/`, just adjust the `pip install -r ...` path in the
commands above to match.
