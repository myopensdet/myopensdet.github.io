# Template from myOpenSDET: https://myopensdet.github.io/
"""Compare two JSON files, like an expected and an actual API response.

Usage:
    python compare_json.py expected.json actual.json
    python compare_json.py expected.json actual.json --ignore id,created_at

Prints one line per difference, with the path to it, like $.items[0].price.
Exit code 0 when they match, 1 when they differ.
"""

import argparse
import json
import sys
from pathlib import Path


def differences(expected, actual, path="$", ignore=frozenset()) -> list[str]:
    """Return a list of differences between two JSON values."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        found = []
        for key in expected:
            if key in ignore:
                continue
            if key not in actual:
                found.append(f"{path}.{key}: missing in actual")
            else:
                found += differences(expected[key], actual[key], f"{path}.{key}", ignore)
        for key in actual:
            if key not in expected and key not in ignore:
                found.append(f"{path}.{key}: not expected, got {show(actual[key])}")
        return found
    if isinstance(expected, list) and isinstance(actual, list):
        found = []
        if len(expected) != len(actual):
            found.append(f"{path}: expected {len(expected)} items, got {len(actual)}")
        # Compare the items both lists have. The length line above covers the rest.
        for index, (one, other) in enumerate(zip(expected, actual, strict=False)):
            found += differences(one, other, f"{path}[{index}]", ignore)
        return found
    # type() too: in Python 1 == 1.0 and 1 == True, but in JSON they are different.
    if expected != actual or type(expected) is not type(actual):
        return [f"{path}: expected {show(expected)}, got {show(actual)}"]
    return []


def show(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def main(args: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compare two JSON files.")
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--ignore", default="", help="keys to skip, comma separated")
    options = parser.parse_args(args)
    expected = json.loads(options.expected.read_text(encoding="utf-8"))
    actual = json.loads(options.actual.read_text(encoding="utf-8"))
    ignore = frozenset(key.strip() for key in options.ignore.split(",") if key.strip())
    found = differences(expected, actual, ignore=ignore)
    for line in found:
        print(line)
    print(f"{len(found)} difference(s)." if found else "They match.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
