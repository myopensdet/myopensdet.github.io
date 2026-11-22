# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Print every combination of yes/no conditions, as a decision table ready to fill in.

    python decision_table.py 'Member' 'Order $50 or more' 'Express'

Use single quotes: inside double quotes, the shell treats $50 as a variable and drops it.

Paste the output into your notes or the ticket, then fill the Result column
from the rules. An empty cell you can't fill is a question for the product owner.
"""

import itertools
import sys

TOO_MANY = 6  # 2 ** 6 = 64 rows: past this, split the rule or use pairwise testing


def rows(conditions: list[str]) -> list[tuple[str, ...]]:
    return list(itertools.product(("Yes", "No"), repeat=len(conditions)))


def table(conditions: list[str]) -> str:
    lines = [
        "| # | " + " | ".join(conditions) + " | Result |",
        "| --- | " + " | ".join("---" for _ in conditions) + " | --- |",
    ]
    for number, row in enumerate(rows(conditions), start=1):
        lines.append(f"| {number} | " + " | ".join(row) + " |  |")
    return "\n".join(lines)


def main(conditions: list[str]) -> int:
    if not conditions:
        print('Usage: python decision_table.py "Condition one" "Condition two" ...')
        return 2
    print(table(conditions))
    if len(conditions) > TOO_MANY:
        print(f"\nWarning: {2 ** len(conditions)} rows. Split the rule into smaller parts,")
        print("or use pairwise testing to pick fewer combinations.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
