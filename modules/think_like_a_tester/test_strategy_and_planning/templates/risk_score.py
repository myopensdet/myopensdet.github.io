# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Score each risk by likelihood x impact, and say how deeply to test it.

Usage:
    python risk_score.py risks.csv

The CSV needs the columns Area, Risk, Likelihood and Impact.
Likelihood and Impact are 1 (low), 2 (medium) or 3 (high).
Lines that start with "#" are ignored.
"""

import csv
import sys

# Lowest score for each depth, checked from the top.
DEPTHS = [(6, "deep"), (3, "normal"), (1, "light")]


def depth(score: int) -> str:
    for lowest, name in DEPTHS:
        if score >= lowest:
            return name
    raise ValueError(f"score must be 1 to 9, got {score}")


def level(row: dict, column: str, number: int) -> int:
    value = (row.get(column) or "").strip()
    if value not in {"1", "2", "3"}:
        raise ValueError(f"Row {number}: {column} must be 1, 2 or 3, got '{value}'")
    return int(value)


def read_risks(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as file:
        lines = [line for line in file if not line.startswith("#")]
    risks = []
    for number, row in enumerate(csv.DictReader(lines), start=1):
        score = level(row, "Likelihood", number) * level(row, "Impact", number)
        risks.append({**row, "Score": score, "Depth": depth(score)})
    # Highest score first. Equal scores keep the order of the file.
    return sorted(risks, key=lambda risk: -risk["Score"])


def report(risks: list[dict]) -> str:
    lines = ["| Score | Depth | Area | Risk |", "| --- | --- | --- | --- |"]
    for risk in risks:
        lines.append(f"| {risk['Score']} | {risk['Depth']} | {risk['Area']} | {risk['Risk']} |")
    counts = [sum(r["Depth"] == name for r in risks) for _, name in DEPTHS]
    lines.append("")
    lines.append(
        f"{counts[0]} deep, {counts[1]} normal, {counts[2]} light. Test the deep ones first."
    )
    return "\n".join(lines)


def main(args: list[str]) -> int:
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        risks = read_risks(args[0])
    except ValueError as problem:
        print(problem)
        return 2
    print(report(risks))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
