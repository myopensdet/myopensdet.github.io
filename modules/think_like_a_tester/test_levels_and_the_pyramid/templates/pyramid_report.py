# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Show how many tests you have at each level, as a pyramid.

Use it with the level markers from conftest.py and pytest.ini. From your
project's main folder:

    python pyramid_report.py            all tests
    python pyramid_report.py tests/     one folder

It only collects the tests (it does not run them), so it takes a second or two.
"""

from __future__ import annotations

import subprocess
import sys

LEVELS = ("e2e", "ui", "api", "integration", "unit")  # top of the pyramid first
BAR_WIDTH = 20


def count(paths: list[str], marker: str | None = None) -> int:
    command = [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"]
    if marker:
        command += ["-m", marker]
    result = subprocess.run(command + paths, capture_output=True, text=True, check=False)  # noqa: S603  (fixed command)
    if result.returncode not in (0, 5):  # 5 means "no tests collected", which is fine here
        raise RuntimeError(result.stdout + result.stderr)
    return sum(1 for line in result.stdout.splitlines() if "::" in line)


def report(paths: list[str]) -> str:
    total = count(paths)
    if total == 0:
        return "No tests found."
    counts = {level: count(paths, level) for level in LEVELS}
    lines = ["Tests per level (a healthy suite is widest at the bottom)", ""]
    for level, number in counts.items():
        share = number / total
        bar = "#" * max(1 if number else 0, round(share * BAR_WIDTH))
        lines.append(f"{level:<12} {bar:<{BAR_WIDTH}} {number:4}  {share:4.0%}")
    unmarked = total - sum(counts.values())
    lines += [
        "",
        f"Total: {total} tests" + (f" ({unmarked} not in a level folder)" if unmarked else ""),
    ]
    if counts["ui"] + counts["e2e"] > counts["unit"]:
        lines += [
            "",
            "Warning: more UI and end-to-end tests than unit tests.",
            "This is the 'ice cream cone' shape: slow, and often flaky.",
            "Look for UI tests that could become API or unit tests.",
        ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(sys.argv[1:]))
