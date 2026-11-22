# Template from myOpenSDET: https://myopensdet.github.io/
"""Pick the tests to run for a change: read the changed files, match them to areas in
test_map.ini, and print the pytest command. Smoke tests always run. Unknown code means
"run everything", because guessing is how hotfixes break things.

    git diff --name-only origin/main...HEAD | python pick_tests.py
    python pick_tests.py src/payments/refund.py src/search/index.py
"""

import configparser
import fnmatch
import sys
from pathlib import Path

MAP_FILE = Path(__file__).with_name("test_map.ini")


def split(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main() -> int:
    changed = sys.argv[1:] or [line.strip() for line in sys.stdin if line.strip()]
    if not changed:
        print("No changed files given. Example: git diff --name-only origin/main...HEAD | "
              "python pick_tests.py")  # fmt: skip
        return 2
    config = configparser.ConfigParser()
    if not config.read(MAP_FILE, encoding="utf-8"):
        print(f"No {MAP_FILE.name} next to this script.")
        return 2
    settings = config["settings"]
    ignore = split(settings.get("ignore", ""))
    markers = {settings.get("always", "smoke")}
    areas = [s for s in config.sections() if s != "settings"]

    print(f"Changed files: {len(changed)}")
    unknown = []
    for path in changed:
        if any(fnmatch.fnmatch(path, pattern) for pattern in ignore):
            print(f"  {path:<34} -> no tests needed")
            continue
        hits = [a for a in areas if any(fnmatch.fnmatch(path, p) for p in split(config[a]["code"]))]
        if hits:
            markers.update(config[a]["marker"] for a in hits)
            print(f"  {path:<34} -> {', '.join(hits)}")
        else:
            unknown.append(path)
            print(f"  {path:<34} -> NOT IN THE MAP")

    if unknown or "regression" in markers:
        reason = "code that isn't in the map" if unknown else "shared code changed"
        print(f"\nRun the full regression ({reason}):")
        print("  python -m pytest -m regression")
        if unknown:
            print("Then add the unknown files to test_map.ini, so next time is faster.")
        return 1
    print("\nRun:")
    print(f'  python -m pytest -m "{" or ".join(sorted(markers))}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
