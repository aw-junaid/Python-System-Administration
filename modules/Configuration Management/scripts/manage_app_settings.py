#!/usr/bin/env python3
"""
manage_app_settings.py

Purpose:
    A small reusable "settings manager" for an application: load
    settings from a JSON file (creating sane defaults if missing),
    get/set individual values, and save changes back to disk.

Usage:
    python3 manage_app_settings.py get theme
    python3 manage_app_settings.py set theme dark
    python3 manage_app_settings.py list

    If no arguments are given, this script runs a demo: it creates a
    default settings file, sets a value, and lists all settings.

Expected Output:
    (list)
    Current application settings:
      theme = light
      language = en
      notifications_enabled = True

    (set theme dark)
    Updated 'theme' = 'dark'

Caution:
    - Settings are stored in 'app_settings.json' in the current
      directory by default; delete that file if you want to reset to
      defaults.
    - This script OVERWRITES app_settings.json on every 'set' call.
      Use backup_config.py first if you want a safety copy of settings
      you care about.
    - Values passed via 'set' are auto-converted (true/false -> bool,
      numeric strings -> int/float); everything else is stored as a
      string.
"""

import json
import os
import sys

SETTINGS_FILE = "app_settings.json"
DEFAULT_SETTINGS = {
    "theme": "light",
    "language": "en",
    "notifications_enabled": True
}


def load_settings() -> dict:
    if not os.path.isfile(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def convert_value(raw: str):
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def cmd_get(key: str) -> None:
    settings = load_settings()
    if key in settings:
        print(f"{key} = {settings[key]}")
    else:
        print(f"Setting '{key}' not found.")


def cmd_set(key: str, raw_value: str) -> None:
    settings = load_settings()
    value = convert_value(raw_value)
    settings[key] = value
    save_settings(settings)
    print(f"Updated '{key}' = {value!r}")


def cmd_list() -> None:
    settings = load_settings()
    print("Current application settings:")
    for key, value in settings.items():
        print(f"  {key} = {value}")


def main():
    args = sys.argv[1:]

    if not args:
        print("No arguments given, running demo mode.\n")
        cmd_list()
        print()
        cmd_set("theme", "dark")
        print()
        cmd_list()
        return

    action = args[0].lower()
    if action == "get" and len(args) >= 2:
        cmd_get(args[1])
    elif action == "set" and len(args) >= 3:
        cmd_set(args[1], args[2])
    elif action == "list":
        cmd_list()
    else:
        print("Usage:")
        print("  python3 manage_app_settings.py get <key>")
        print("  python3 manage_app_settings.py set <key> <value>")
        print("  python3 manage_app_settings.py list")


if __name__ == "__main__":
    main()
