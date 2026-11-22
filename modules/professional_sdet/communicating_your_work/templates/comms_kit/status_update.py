# Template from myOpenSDET: https://myopensdet.github.io/
"""Turn test results and your notes into a clear status, written three ways: a short
chat message, an email for a manager, and a ticket comment. Same facts, different
readers. The verdict is GREEN, AMBER or RED, with the reason.

    python status_update.py reports/junit.xml status_notes.ini
"""

import configparser
import sys
import xml.etree.ElementTree as ET  # noqa: S405 (our own pytest report, not outside data)
from pathlib import Path


def results(report: str) -> tuple[int, list[str]]:
    root = ET.parse(report).getroot()  # noqa: S314
    total, failed = 0, []
    for case in root.iter("testcase"):
        total += 1
        if case.find("failure") is not None or case.find("error") is not None:
            failed.append(case.get("name"))
    return total, failed


def plural(count: int, word: str) -> str:
    return f"{count} {word}{'s' * (count != 1)}"


def verdict(failed: list[str], risks: dict, blockers: dict) -> tuple[str, str]:
    if blockers:
        return "RED", "blocked: " + "; ".join(blockers.values())
    if failed:
        return "RED", f"{plural(len(failed), 'test')} failing: {', '.join(failed)}"
    if risks:
        return "AMBER", f"tests pass, {plural(len(risks), 'known risk')} to accept"
    return "GREEN", "tests pass, no known risks"


def main() -> int:
    if len(sys.argv) != 3 or not all(Path(p).is_file() for p in sys.argv[1:]):
        print("Usage: python status_update.py <junit.xml> <status_notes.ini>")
        return 2
    total, failed = results(sys.argv[1])
    notes = configparser.ConfigParser(delimiters=("=",))
    notes.optionxform = str  # keep the case of names
    notes.read(sys.argv[2], encoding="utf-8")
    name = notes.get("release", "name", fallback="this release")
    date = notes.get("release", "date", fallback="")
    tested = dict(notes["tested"]) if notes.has_section("tested") else {}
    untested = dict(notes["not tested"]) if notes.has_section("not tested") else {}
    risks = dict(notes["risks"]) if notes.has_section("risks") else {}
    blockers = dict(notes["blockers"]) if notes.has_section("blockers") else {}
    colour, reason = verdict(failed, risks, blockers)
    passed = total - len(failed)

    print("== For the team chat (one glance)\n")
    print(f"{colour}: {name} testing: {passed}/{total} tests pass. {reason.capitalize()}.")
    print("\n== For a manager (email)\n")
    print(f"Subject: {name} testing status: {colour}\n")
    advice = {"GREEN": "Ready to release from a testing point of view.",
              "AMBER": "Can release if you accept the risks below. Your decision.",
              "RED": "Not ready yet. What's needed is below."}[colour]  # fmt: skip
    print(f"{advice}{' Planned: ' + date + '.' if date else ''}\n")
    must_fix = {f"FAILED {test}": "a test is failing" for test in failed} | blockers
    for title, items in (("Must fix first", must_fix), ("Risks", risks), ("Not tested", untested)):
        if items:
            print(f"{title}:")
            for key, value in items.items():
                print(f"- {key}: {value}")
            print()
    print("== For the ticket (details)\n")
    print(f"Automated tests: {passed} passed, {len(failed)} failed (of {total}).")
    for name_failed in failed:
        print(f"- FAILED {name_failed}")
    print("Tested:")
    for area, how in tested.items():
        print(f"- {area}: {how}")
    print("Not tested:")
    for area, why in untested.items() or {"(nothing)": ""}.items():
        print(f"- {area}{': ' + why if why else ''}")
    return {"GREEN": 0, "AMBER": 0, "RED": 1}[colour]


if __name__ == "__main__":
    sys.exit(main())
