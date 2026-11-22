# Template from myOpenSDET: https://myopensdet.github.io/
"""Read pytest's JUnit XML report and write a short summary: the totals, then every
failed test with the first line of its error. In GitHub Actions it also goes on the
run's summary page.

    python -m pytest --junitxml=reports/junit.xml
    python ci_summary.py reports/junit.xml
"""

import os
import sys
import xml.etree.ElementTree as ET  # noqa: S405 (our own pytest report, not outside data)


def summarise(report_path: str) -> str:
    root = ET.parse(report_path).getroot()  # noqa: S314
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(suite.get("tests", 0))
    failed = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    skipped = int(suite.get("skipped", 0))
    passed = total - failed - skipped
    lines = [
        "## Test results",
        "",
        f"**{passed} passed, {failed} failed, {skipped} skipped** "
        f"in {float(suite.get('time', 0)):.1f} s",
    ]
    problems = []
    for case in suite.iter("testcase"):
        for tag in ("failure", "error"):
            found = case.find(tag)
            if found is not None:
                message = (found.get("message") or "").splitlines()[0][:150]
                problems.append(f"| `{case.get('name')}` | {tag} | {message} |")
    if problems:
        lines += ["", "| Test | Kind | First line of the error |", "| --- | --- | --- |"]
        lines += problems
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python ci_summary.py reports/junit.xml", file=sys.stderr)
        return 2
    if not os.path.exists(sys.argv[1]):
        print(f"No report at {sys.argv[1]}: did the tests run at all?", file=sys.stderr)
        return 1
    text = summarise(sys.argv[1])
    print(text)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as file:
            file.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
