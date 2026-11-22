# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Summarise a test run saved as JSON: counts, failures, and the slowest tests.

Usage:
    python run_summary.py results.json
    python run_summary.py results.json --slowest 5

The JSON looks like this (one entry per test):
    {"run": "nightly", "tests": [
        {"name": "test_login", "outcome": "passed", "seconds": 0.4},
        {"name": "test_pay", "outcome": "failed", "seconds": 1.2, "message": "..."}
    ]}

Exit code 0 when nothing failed, 1 when a test failed, 2 when the file is wrong.
"""

import argparse
import json
import sys
from pathlib import Path


def load_tests(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("tests"), list):
        raise ValueError(f'{path} has no "tests" list')
    return data


def summary(data: dict, slowest: int = 3) -> str:
    tests = data["tests"]
    counts = {}
    for test in tests:
        counts[test["outcome"]] = counts.get(test["outcome"], 0) + 1
    passed = counts.get("passed", 0)
    rate = round(passed / len(tests) * 100, 1) if tests else 0.0
    parts = ", ".join(f"{number} {outcome}" for outcome, number in sorted(counts.items()))
    seconds = sum(test.get("seconds", 0) for test in tests)

    lines = [f"Run: {data.get('run', 'unnamed')}"]
    lines.append(f"{len(tests)} tests: {parts} ({rate}% passed)")
    lines.append(f"Total time: {seconds:.1f} seconds")

    failed = [test for test in tests if test["outcome"] == "failed"]
    if failed:
        lines.append("")
        lines.append("Failed:")
        for test in failed:
            lines.append(f"- {test['name']}: {test.get('message', 'no message')}")

    lines.append("")
    lines.append(f"Slowest {slowest}:")
    by_time = sorted(tests, key=lambda test: test.get("seconds", 0), reverse=True)
    for test in by_time[:slowest]:
        lines.append(f"- {test.get('seconds', 0):5.2f} s  {test['name']}")
    return "\n".join(lines)


def main(args: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Summarise a test run saved as JSON.")
    parser.add_argument("results", type=Path, help="the results JSON file")
    parser.add_argument("--slowest", type=int, default=3, help="how many slow tests to list")
    options = parser.parse_args(args)
    try:
        data = load_tests(options.results)
    except (OSError, ValueError) as problem:
        print(f"Can't read the results: {problem}")
        return 2
    print(summary(data, options.slowest))
    return 1 if any(test["outcome"] == "failed" for test in data["tests"]) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
