# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: modules and imports. Run: python modules_demo.py"""

import random
from datetime import UTC, datetime
from pathlib import Path

import device_checks
from device_checks import is_stale, is_valid_reading

# 1. Your own module: checks written once, in device_checks.py.
print(is_valid_reading(21.5), is_valid_reading(85.0), device_checks.__name__)

# 2. datetime: has the device gone quiet? "now" is fixed, so the output never changes.
now = datetime(2026, 11, 22, 9, 30, tzinfo=UTC)
last_seen = datetime.fromisoformat("2026-11-22T09:12:00+00:00")  # as an API sends it
print(now - last_seen, is_stale(last_seen, now))

# 3. pathlib: build file paths that work on every computer.
report = Path("reports") / "devices" / "2026-11-22.json"
print(report.as_posix(), report.name, report.suffix)

# 4. random: varied test data. A seed makes the same numbers every run.
random.seed(7)
print([random.randint(0, 100) for _ in range(3)])  # noqa: S311 (test data, not security)

print(__name__)
