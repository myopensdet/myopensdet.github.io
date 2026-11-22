# Template from myOpenSDET: https://myopensdet.github.io/
"""Check test results against the exit criteria in the test plan.

Usage:
    python exit_check.py exit_criteria.toml results.toml

Every criterion is a limit: "at most this many". For example
open_critical_bugs = 0 means no critical bug may be open.
Exit code 0 means every criterion is met, 1 means at least one is not.
"""

import sys
import tomllib


def load(path: str) -> dict:
    with open(path, "rb") as file:
        return tomllib.load(file)


def check(criteria: dict, results: dict) -> list[tuple[str, str]]:
    """Return (status, line) for each criterion. Status is "met" or "not met"."""
    lines = []
    for name, limit in criteria.items():
        if name not in results:
            lines.append(("not met", f"MISSING  {name}: no result (at most {limit})"))
        elif results[name] <= limit:
            lines.append(("met", f"met      {name}: {results[name]} (at most {limit})"))
        else:
            lines.append(("not met", f"NOT MET  {name}: {results[name]} (at most {limit})"))
    return lines


def main(args: list[str]) -> int:
    if len(args) != 2:
        print(__doc__)
        return 2
    criteria = load(args[0]).get("exit", {})
    if not criteria:
        print(f"No [exit] section in {args[0]}.")
        return 2
    lines = check(criteria, load(args[1]))
    for _, line in lines:
        print(line)
    failed = sum(status == "not met" for status, _ in lines)
    print()
    if failed:
        word = "criterion" if failed == 1 else "criteria"
        print(
            f"{failed} exit {word} not met. Don't sign off yet, or agree an exception in writing."
        )
        return 1
    print("All exit criteria met. Write the test summary and share it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
