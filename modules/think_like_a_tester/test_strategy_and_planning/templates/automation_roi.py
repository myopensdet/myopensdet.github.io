# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Work out how long an automated test takes to pay back the time spent on it.

Usage:
    python automation_roi.py --manual-minutes 30 --runs-per-month 20 \
        --build-hours 16 --upkeep-hours 2

--manual-minutes  how long one manual run takes
--runs-per-month  how often the check is run (every release, every pull request...)
--build-hours     how long it takes to write the automated test
--upkeep-hours    hours per month to keep it working (fixing locators, data...)

Time is only one reason to automate. Use the automation checklist as well.
"""

import argparse
import sys


def payback(manual_minutes: float, runs: float, build: float, upkeep: float) -> dict:
    saved = manual_minutes * runs / 60
    net = saved - upkeep
    months = build / net if net > 0 else None
    return {"saved": saved, "upkeep": upkeep, "net": net, "build": build, "months": months}


def verdict(months: float | None) -> str:
    if months is None:
        return "Never pays back on time alone: keeping it working costs more than it saves."
    if months <= 3:
        return "Pays back fast. Worth automating, if the checklist agrees."
    if months <= 12:
        return "Pays back within a year. Check the checklist before you decide."
    return "Takes over a year to pay back. Probably keep it manual, or test it at a lower level."


def main(args: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Automation payback calculator.")
    parser.add_argument("--manual-minutes", type=float, required=True)
    parser.add_argument("--runs-per-month", type=float, required=True)
    parser.add_argument("--build-hours", type=float, required=True)
    parser.add_argument("--upkeep-hours", type=float, required=True)
    a = parser.parse_args(args)
    r = payback(a.manual_minutes, a.runs_per_month, a.build_hours, a.upkeep_hours)
    print(f"Manual time saved per month: {r['saved']:5.1f} hours")
    print(f"Upkeep per month:            {r['upkeep']:5.1f} hours")
    print(f"Net saving per month:        {r['net']:5.1f} hours")
    print(f"Building it takes:           {r['build']:5.1f} hours")
    if r["months"] is not None:
        print(f"Pays back after:             {r['months']:5.1f} months")
    print(verdict(r["months"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
