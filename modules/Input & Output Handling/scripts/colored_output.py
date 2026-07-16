#!/usr/bin/env python3
"""
Topic: Colored Terminal Output

Demonstrates printing colored text using the third-party 'colorama' library
(cross-platform, including Windows), with plain ANSI codes as a fallback.

Requires (optional): colorama  (see requirements.txt)

Usage:
    python colored_output.py

Expected Output:
    Several lines of text printed in different colors (red, green, yellow,
    blue) and styles (bright/normal).
"""

def main() -> None:
    try:
        from colorama import init, Fore, Style
        init(autoreset=True)

        print(Fore.RED + "This text is red (error style).")
        print(Fore.GREEN + "This text is green (success style).")
        print(Fore.YELLOW + "This text is yellow (warning style).")
        print(Fore.BLUE + "This text is blue (info style).")
        print(Style.BRIGHT + Fore.MAGENTA + "This text is bright magenta.")

    except ImportError:
        print("colorama not installed, falling back to raw ANSI escape codes.")
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        RESET = "\033[0m"

        print(f"{RED}This text is red (error style).{RESET}")
        print(f"{GREEN}This text is green (success style).{RESET}")
        print(f"{YELLOW}This text is yellow (warning style).{RESET}")
        print(f"{BLUE}This text is blue (info style).{RESET}")


if __name__ == "__main__":
    main()
