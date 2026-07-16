#!/usr/bin/env python3
"""
Topic: Interactive Command-Line Menus

Displays a simple numbered menu in a loop, lets the user pick an option,
and performs a corresponding action, until the user chooses to exit.

Usage:
    python interactive_menu.py

Expected Output:
    An interactive menu. Enter a number to choose an option.
    Choosing "4" (Exit) ends the program.
"""

def show_menu() -> None:
    print("\n===== Main Menu =====")
    print("1. Say hello")
    print("2. Show current time")
    print("3. Add two numbers")
    print("4. Exit")


def say_hello() -> None:
    name = input("Enter your name: ")
    print(f"Hello, {name}!")


def show_time() -> None:
    from datetime import datetime
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def add_numbers() -> None:
    try:
        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))
        print(f"Result: {a + b}")
    except ValueError:
        print("Invalid number entered.")


def main() -> None:
    actions = {
        "1": say_hello,
        "2": show_time,
        "3": add_numbers,
    }

    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()

        if choice == "4":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
