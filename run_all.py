from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    *sorted((ROOT / "lessons").glob("[0-9][0-9]_*.py")),
    ROOT / "projects" / "balanced_network.py",
]


def main():
    failures = []
    for script in SCRIPTS:
        print(f"\n=== Running {script.relative_to(ROOT)} ===")
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        if result.returncode:
            failures.append(script)

    if failures:
        print("\nFailed examples:")
        for script in failures:
            print(f"- {script.relative_to(ROOT)}")
        raise SystemExit(1)

    print("\nAll Brian2 examples completed successfully.")


if __name__ == "__main__":
    main()

