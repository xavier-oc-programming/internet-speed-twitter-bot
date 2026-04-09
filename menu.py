import os
import sys
import subprocess
from pathlib import Path

from art import LOGO


def main():
    base = Path(__file__).parent
    options = {
        "1": ("Original build", base / "original" / "main.py"),
        "2": ("Advanced build", base / "advanced" / "main.py"),
    }

    clear = True
    while True:
        if clear:
            os.system("cls" if os.name == "nt" else "clear")
        print(LOGO)
        print("  1. Original build  — course solution (remote debug approach)")
        print("  2. Advanced build  — undetected-chromedriver + clean architecture")
        print("  q. Quit")
        print()

        choice = input("  Select an option: ").strip().lower()

        if choice in options:
            label, path = options[choice]
            print(f"\nLaunching {label}...\n")
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
            input("\nPress Enter to return to menu...")
            clear = True
        elif choice == "q":
            break
        else:
            print("Invalid choice. Try again.")
            clear = False


if __name__ == "__main__":
    main()
