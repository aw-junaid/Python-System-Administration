#!/usr/bin/env python3
"""
validate_config_values.py

Purpose:
    Validate a JSON configuration file's values against a simple set of
    rules: required keys, expected types, and (optionally) allowed
    ranges — reporting every problem found rather than stopping at the
    first one.

Usage:
    python3 validate_config_values.py <path_to_file.json>

    If no path is given, this script validates a demo config (which
    intentionally includes one bad value, to show validation catching
    a real problem).

Expected Output:
    Validating: demo_config.json

    ISSUE: 'port' should be of type int, got str ('8080a')
    ISSUE: 'timeout' is missing a required key.

    Validation FAILED with 2 issue(s).

    (Or, for a fully valid config:)
    Validation PASSED. All required keys present with correct types.

Caution:
    - This is a simple, illustrative validator. Edit the RULES
      dictionary inside this script to match your own configuration
      schema (required keys, types, min/max ranges).
    - This script only reads and reports; it does not modify the
      config file, even when issues are found.
    - For complex schemas, consider a dedicated validation library
      (e.g. 'jsonschema' or 'pydantic') instead of this hand-rolled
      approach.
"""

import json
import os
import sys

DEMO_FILE = "demo_config_to_validate.json"
# Demo file intentionally has a bad "port" value and is missing "timeout"
DEMO_CONTENT = {
    "host": "127.0.0.1",
    "port": "8080a",
    "debug": True
}

# Define your validation rules here: key -> (expected_type, required, min, max)
RULES = {
    "host": {"type": str, "required": True},
    "port": {"type": int, "required": True, "min": 1, "max": 65535},
    "debug": {"type": bool, "required": True},
    "timeout": {"type": int, "required": True, "min": 1, "max": 300},
}


def validate(data: dict, rules: dict) -> list:
    issues = []
    for key, rule in rules.items():
        if key not in data:
            if rule.get("required"):
                issues.append(f"'{key}' is missing a required key.")
            continue

        value = data[key]
        expected_type = rule["type"]
        if not isinstance(value, expected_type):
            issues.append(
                f"'{key}' should be of type {expected_type.__name__}, "
                f"got {type(value).__name__} ({value!r})"
            )
            continue

        if "min" in rule and value < rule["min"]:
            issues.append(f"'{key}' value {value} is below minimum {rule['min']}.")
        if "max" in rule and value > rule["max"]:
            issues.append(f"'{key}' value {value} is above maximum {rule['max']}.")
    return issues


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, validating a demo config (with an intentional error).\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                json.dump(DEMO_CONTENT, f, indent=2)
        path = DEMO_FILE

    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return

    print(f"Validating: {path}\n")
    issues = validate(data, RULES)

    if issues:
        for issue in issues:
            print(f"ISSUE: {issue}")
        print(f"\nValidation FAILED with {len(issues)} issue(s).")
    else:
        print("Validation PASSED. All required keys present with correct types.")


if __name__ == "__main__":
    main()
