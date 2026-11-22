# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Turn the test idea banks into one checklist for the feature you're testing.

Each file in ideas/ is one kind of feature (login.md, payments.md ...). Pick the ones
your feature touches, and get a single Markdown checklist to paste into the ticket, or
a CSV to import into a test management tool. Add your own banks: copy a file in ideas/,
and keep the "## Area" headings and "- idea" lines.

Usage:
    python idea_checklist.py --list
    python idea_checklist.py login sign_up
    python idea_checklist.py cart payments --only security
    python idea_checklist.py cart payments --csv > ideas.csv
"""

import argparse
import csv
import sys
from pathlib import Path

IDEAS = Path(__file__).with_name("ideas")


def read_bank(path: Path) -> tuple[str, dict[str, list[str]]]:
    title, areas, area = path.stem, {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = line[2:].split(":")[0].strip()
        elif line.startswith("## "):
            area = line[3:].strip()
            areas[area] = []
        elif line.startswith("- ") and area:
            areas[area].append(line[2:].strip())
    return title, areas


def find(name: str, banks: list[Path]) -> Path:
    matches = [p for p in banks if p.stem == name] or [p for p in banks if p.stem.startswith(name)]
    if len(matches) != 1:
        names = ", ".join(p.stem for p in banks)
        raise SystemExit(f"No single idea bank called '{name}'. Choose from: {names}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Make a test idea checklist.")
    parser.add_argument("features", nargs="*", help="idea banks to use, like: login payments")
    parser.add_argument("--list", action="store_true", help="show the idea banks")
    parser.add_argument("--only", help="only areas whose name has this word, like: security")
    parser.add_argument("--csv", action="store_true", help="write CSV instead of Markdown")
    args = parser.parse_args()

    banks = sorted(IDEAS.glob("*.md"))
    if args.list or not args.features:
        for path in banks:
            title, areas = read_bank(path)
            print(f"{path.stem:<22} {sum(map(len, areas.values())):>3} ideas  {title}")
        if args.list:
            return 0
        print("\nChoose one or more, like: python idea_checklist.py login payments")
        return 2

    chosen = [read_bank(find(name, banks)) for name in args.features]
    rows = [
        (title, area, idea)
        for title, areas in chosen
        for area, ideas in areas.items()
        if not args.only or args.only.lower() in area.lower()
        for idea in ideas
    ]
    if not rows and not args.only:
        print("No ideas found. Each idea is a line starting with '- ', under a '## ' area heading.")
        return 1
    if not rows:
        areas = "works, refuses, edges, security, people"
        print(f"No area has '{args.only}' in its name. Try: {areas}")
        return 1

    if args.csv:
        out = csv.writer(sys.stdout, lineterminator="\n")
        out.writerow(["Feature", "Area", "Idea"])
        out.writerows(rows)
        return 0

    print(f"# Test ideas: {', '.join(title for title, _ in chosen)}\n")
    print(f"{len(rows)} ideas. Tick what you tested. Strike out what doesn't apply, and say why.")
    last = None
    for title, area, idea in rows:
        if (title, area) != last:
            if last is None or title != last[0]:
                print(f"\n## {title}")
            print(f"\n### {area}\n")
            last = (title, area)
        print(f"- [ ] {idea}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
