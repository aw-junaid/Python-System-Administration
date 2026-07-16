#!/usr/bin/env python3
"""
Topic: Parse Command-Line Options using click

Demonstrates defining CLI options and arguments using the third-party
'click' library, which offers a friendlier decorator-based API than argparse.

Requires: click  (see requirements.txt)

Usage:
    python click_options.py --name Junaid --count 3
    python click_options.py --help

Expected Output:
    Prints a greeting the given number of times.
"""

import click


@click.command()
@click.option("--name", default="World", help="Name to greet.")
@click.option("--count", default=1, show_default=True, help="Number of greetings.")
@click.option("--shout/--no-shout", default=False, help="Print in uppercase.")
def greet(name: str, count: int, shout: bool) -> None:
    """Simple CLI tool that greets NAME COUNT times."""
    message = f"Hello, {name}!"
    if shout:
        message = message.upper()

    for _ in range(count):
        click.echo(message)


if __name__ == "__main__":
    greet()
