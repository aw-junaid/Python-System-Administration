#!/usr/bin/env python3
"""
packaging_automation_tools.py

Demonstrates packaging an internal automation tool for distribution,
by SCAFFOLDING a minimal, correct, installable Python package: a
`pyproject.toml` (the modern standard, replacing `setup.py`), a
package folder with an `__init__.py` and a CLI entry point, and a
README — the layout your team could `pip install -e .` or publish to
an internal PyPI index (e.g. Artifactory/Nexus/devpi).

Usage:
    python packaging_automation_tools.py
    python packaging_automation_tools.py --name my-automation-tool --outdir my-automation-tool

Expected output:
    A new folder (default: my_internal_tool/) containing a working,
    installable package skeleton:

        my_internal_tool/
          pyproject.toml
          README.md
          src/
            my_internal_tool/
              __init__.py
              cli.py

    After it's generated, `cd` into the folder and run:
        pip install -e .
        my-internal-tool --help
    to install it in editable mode and confirm the CLI entry point works.
"""

import argparse
import os


PYPROJECT_TEMPLATE = """\
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{dist_name}"
version = "0.1.0"
description = "Internal automation tool: {description}"
readme = "README.md"
requires-python = ">=3.8"
authors = [
    {{ name = "Your Team", email = "automation@example.com" }}
]
dependencies = [
    # list runtime dependencies here, e.g. "requests>=2.31",
]

[project.scripts]
{cli_command} = "{package_name}.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
"""

INIT_TEMPLATE = '''"""{package_name} — internal automation tool."""

__version__ = "0.1.0"
'''

CLI_TEMPLATE = '''"""Command-line entry point for {package_name}."""

import argparse


def main():
    parser = argparse.ArgumentParser(prog="{cli_command}", description="{description}")
    parser.add_argument("--example", help="An example option — replace with real functionality.")
    args = parser.parse_args()

    print(f"{{parser.prog}} ran successfully. example={{args.example}}")


if __name__ == "__main__":
    main()
'''

README_TEMPLATE = """\
# {dist_name}

Internal automation tool: {description}

## Install (editable, for development)

```bash
pip install -e .
```

## Install (for internal distribution)

Publish this package to your internal package index (e.g. Artifactory,
Nexus, devpi, or a private GitHub/GitLab package registry), then:

```bash
pip install {dist_name} --index-url https://your-internal-index/simple/
```

## Usage

```bash
{cli_command} --example hello
```
"""


def to_package_name(dist_name: str) -> str:
    """Convert a dash-separated distribution name to a valid Python package name."""
    return dist_name.replace("-", "_")


def scaffold_package(dist_name: str, description: str, outdir: str) -> None:
    package_name = to_package_name(dist_name)
    cli_command = dist_name

    src_dir = os.path.join(outdir, "src", package_name)
    os.makedirs(src_dir, exist_ok=True)

    with open(os.path.join(outdir, "pyproject.toml"), "w", encoding="utf-8") as f:
        f.write(PYPROJECT_TEMPLATE.format(
            dist_name=dist_name, description=description,
            cli_command=cli_command, package_name=package_name,
        ))

    with open(os.path.join(outdir, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_TEMPLATE.format(dist_name=dist_name, description=description, cli_command=cli_command))

    with open(os.path.join(src_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(INIT_TEMPLATE.format(package_name=package_name))

    with open(os.path.join(src_dir, "cli.py"), "w", encoding="utf-8") as f:
        f.write(CLI_TEMPLATE.format(package_name=package_name, cli_command=cli_command, description=description))


def main():
    parser = argparse.ArgumentParser(description="Scaffold an installable package for an internal automation tool.")
    parser.add_argument("--name", default="my-internal-tool", help="Distribution name, dash-separated (default: my-internal-tool)")
    parser.add_argument("--description", default="A reusable internal automation CLI.", help="Short package description")
    parser.add_argument("--outdir", default=None, help="Output folder (default: same as --name, underscored)")
    args = parser.parse_args()

    outdir = args.outdir or to_package_name(args.name)

    if os.path.exists(outdir):
        print(f"ERROR: output folder '{outdir}' already exists. Choose a different --outdir or remove it first.")
        return

    scaffold_package(args.name, args.description, outdir)

    print("Packaging Automation Tools Demo")
    print("=" * 40)
    print(f"Scaffolded installable package at: {os.path.abspath(outdir)}")
    print()
    print("Structure created:")
    for root, _dirs, files in os.walk(outdir):
        for fname in files:
            print(" ", os.path.relpath(os.path.join(root, fname), outdir))
    print()
    print("Next steps:")
    print(f"  cd {outdir}")
    print("  pip install -e .")
    print(f"  {args.name} --example hello")


if __name__ == "__main__":
    main()
