#!/usr/bin/env python3
"""
configuration_management.py

Demonstrates externalizing "magic numbers" and hardcoded strings into
a configuration file, with sane defaults, environment-variable
overrides for deployment-specific values, and validation — instead of
scattering literals like `retries = 3` or `"https://api.example.com"`
throughout the code.

Usage:
    python configuration_management.py
    python configuration_management.py --config custom_config.yaml
    # Override a value without editing the file:
    APP_MAX_RETRIES=10 python configuration_management.py

Expected output:
    On first run (no config file present), the script creates a
    default `config.yaml` next to itself, prints the effective
    configuration (showing which values came from the file vs. an
    environment variable override), and runs a tiny simulated task
    using those externalized values instead of hardcoded literals.
"""

import argparse
import os
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


DEFAULT_CONFIG = {
    "app_name": "backup-automation",
    "max_retries": 3,
    "timeout_seconds": 30,
    "api_base_url": "https://api.example.com",
    "log_level": "INFO",
    "batch_size": 100,
}

# Maps environment variable names to config keys, so deployment-specific
# values (e.g. in Docker/Kubernetes/CI) can override the file without
# editing it.
ENV_OVERRIDES = {
    "APP_MAX_RETRIES": ("max_retries", int),
    "APP_TIMEOUT_SECONDS": ("timeout_seconds", int),
    "APP_API_BASE_URL": ("api_base_url", str),
    "APP_LOG_LEVEL": ("log_level", str),
    "APP_BATCH_SIZE": ("batch_size", int),
}


def write_default_config(path: str) -> None:
    if HAS_YAML:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(DEFAULT_CONFIG, f, sort_keys=False)
    else:
        # Fall back to a tiny hand-rolled YAML-ish writer if PyYAML isn't installed.
        with open(path, "w", encoding="utf-8") as f:
            for key, value in DEFAULT_CONFIG.items():
                f.write(f"{key}: {value}\n")


def load_config_file(path: str) -> dict:
    if not os.path.isfile(path):
        print(f"No config file found at '{path}'; creating one with defaults.")
        write_default_config(path)
        return dict(DEFAULT_CONFIG)

    if HAS_YAML:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        print("(Tip: install PyYAML for full YAML support: pip install pyyaml)")
        data = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, _, value = line.partition(":")
                    data[key.strip()] = value.strip()

    # Merge over defaults so a partial config file still works.
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def apply_env_overrides(config: dict) -> dict:
    """Environment variables take precedence over the config file — useful for
    per-environment (dev/staging/prod) overrides without maintaining separate files."""
    applied = []
    for env_var, (key, caster) in ENV_OVERRIDES.items():
        if env_var in os.environ:
            try:
                config[key] = caster(os.environ[env_var])
                applied.append(env_var)
            except ValueError:
                print(f"WARNING: could not parse {env_var}={os.environ[env_var]!r} as {caster.__name__}; ignoring.")
    return config, applied


def validate_config(config: dict) -> None:
    if config["max_retries"] < 0:
        raise ValueError("max_retries must be >= 0")
    if config["timeout_seconds"] <= 0:
        raise ValueError("timeout_seconds must be > 0")
    if config["batch_size"] <= 0:
        raise ValueError("batch_size must be > 0")


def run_task(config: dict) -> None:
    """A tiny simulated task that USES the externalized config instead of
    hardcoded literals like `for attempt in range(3)` or a hardcoded URL."""
    print(f"\nRunning '{config['app_name']}' against {config['api_base_url']} "
          f"(timeout={config['timeout_seconds']}s, batch_size={config['batch_size']})")
    for attempt in range(1, config["max_retries"] + 1):
        print(f"  attempt {attempt}/{config['max_retries']} ... (simulated)")
    print("Task complete.")


def main():
    parser = argparse.ArgumentParser(description="Demonstrate configuration management for automation scripts.")
    parser.add_argument("--config", default="config.yaml", help="Path to the YAML config file (default: config.yaml)")
    args = parser.parse_args()

    print("Configuration Management Demo")
    print("=" * 40)

    config = load_config_file(args.config)
    config, overridden = apply_env_overrides(config)

    try:
        validate_config(config)
    except ValueError as e:
        print(f"ERROR: invalid configuration: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nEffective configuration (from '{args.config}', env overrides: {overridden or 'none'}):")
    for key, value in config.items():
        source = "env var" if key in [ENV_OVERRIDES[e][0] for e in overridden] else "config file/default"
        print(f"  {key}: {value}   [{source}]")

    run_task(config)


if __name__ == "__main__":
    main()
