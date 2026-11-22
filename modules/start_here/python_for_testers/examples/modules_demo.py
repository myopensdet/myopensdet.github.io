# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: modules and imports. Run: python modules_demo.py"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

delivered = date(2026, 10, 16)
print(delivered + timedelta(days=30))
print((date(2026, 11, 16) - delivered).days)

print(Path("reports/nightly.json").suffix, Path("reports/nightly.json").name)
print(json.dumps({"ok": True}))

# random is fine for test data. For passwords or tokens, use the secrets module.
random.seed(1)  # the same "random" numbers every run, so tests can repeat
print(random.randint(1, 100), random.randint(1, 100))  # noqa: S311
