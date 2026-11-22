# Template from myOpenSDET: https://myopensdet.github.io/
"""Estimate test work as a range, not one number. For each task give three guesses in
hours: best case, most likely, worst case. Uses the three-point (PERT) formula:
(best + 4 x likely + worst) / 6, and shows a likely range.

    python estimate.py estimate.csv
"""

import csv
import math
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        print("Usage: python estimate.py <estimate.csv>  (columns: task,best,likely,worst)")
        return 2
    rows = []
    with open(sys.argv[1], encoding="utf-8", newline="") as file:
        for row in csv.DictReader(line for line in file if not line.startswith("#")):
            try:
                best, likely, worst = (float(row[k]) for k in ("best", "likely", "worst"))
            except (KeyError, TypeError, ValueError):
                print(f"Can't read this row: {row}. Each row needs task,best,likely,worst")
                return 2
            if not best <= likely <= worst:
                got = f"{best:g}, {likely:g}, {worst:g}"
                print(f"'{row['task']}': needs best <= likely <= worst, got {got}")
                return 2
            rows.append((row["task"], best, likely, worst))
    total, variance, worst_total = 0.0, 0.0, 0.0
    print(f"{'Task':<36} {'best':>5} {'likely':>6} {'worst':>6} {'expect':>7}")
    for task, best, likely, worst in rows:
        expected = (best + 4 * likely + worst) / 6
        total += expected
        variance += ((worst - best) / 6) ** 2
        worst_total += worst
        print(f"{task:<36} {best:>5g} {likely:>6g} {worst:>6g} {expected:>7.1f}")
    spread = math.sqrt(variance)
    low, high = total - spread, total + spread
    print(f"\nExpected: {total:.0f} hours. Likely between {low:.0f} and {high:.0f} hours.")
    print(f"If every task hits its worst case: {worst_total:.0f} hours.")
    print(f'Say: "About {total:.0f} hours, probably {low:.0f} to {high:.0f}. '
          f'I\'ll update you if the worst cases happen."')  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
