# Template from myOpenSDET: https://myopensdet.github.io/
"""Read last night's test report (JUnit XML) and sort the failures before stand-up:
known problems (already have a ticket), and new ones (need a look today). Failures
with the same error are grouped, because one cause often breaks many tests.

    python morning_triage.py reports/junit.xml
    python morning_triage.py reports/junit.xml --known known_issues.txt
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET  # noqa: S405 (our own pytest report, not outside data)
from collections import defaultdict
from pathlib import Path


def read_known(path: str | None) -> list[tuple[str, str]]:
    """Each line: a piece of the error text, then | and the ticket. # lines are comments."""
    if not path:
        return []
    known = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            pattern, _, ticket = line.partition("|")
            known.append((pattern.strip(), ticket.strip()))
    return known


def failures(report: str) -> list[tuple[str, str]]:
    root = ET.parse(report).getroot()  # noqa: S314
    found = []
    for case in root.iter("testcase"):
        for tag in ("failure", "error"):
            problem = case.find(tag)
            if problem is not None:
                message = (problem.get("message") or tag).splitlines()[0]
                found.append((case.get("name"), message))
    return found


def shape(message: str) -> str:
    """The same error with different numbers counts as one: 'took 3012 ms' ~ 'took 2987 ms'."""
    return re.sub(r"\d+", "N", message)[:120]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report")
    parser.add_argument("--known", help="file of known errors and their tickets")
    args = parser.parse_args()
    if not Path(args.report).exists():
        print(f"No report at {args.report}. Download it from last night's run first.")
        return 2
    known = read_known(args.known)
    total = sum(1 for _ in ET.parse(args.report).getroot().iter("testcase"))  # noqa: S314
    failed = failures(args.report)
    print(f"Last night: {total} test{'s' * (total != 1)}, {len(failed)} failed\n")
    groups = defaultdict(list)
    for name, message in failed:
        groups[shape(message)].append((name, message))
    new, shown_known = [], False
    for tests in sorted(groups.values(), key=len, reverse=True):
        message = tests[0][1]
        ticket = next((t for pattern, t in known if pattern in message), None)
        line = f"  {len(tests):>2} x {message[:90]}"
        if ticket:
            print(f"KNOWN ({ticket})\n{line}")
            shown_known = True
        else:
            new.append((line, tests))
    if new:
        print(("\n" if shown_known else "") + "NEW: look at these today")
        for line, tests in new:
            print(line)
            for name, _ in tests[:5]:
                print(f"       - {name}")
    else:
        print(("\n" if shown_known else "") + "No new failures.")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
