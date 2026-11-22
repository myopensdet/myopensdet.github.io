# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: reading and writing files. Run: python files_demo.py"""

import csv
from pathlib import Path

here = Path(__file__).parent
users_file = here / "users.csv"

with users_file.open(encoding="utf-8", newline="") as file:
    lines = [line for line in file if not line.startswith("#")]
for row in csv.DictReader(lines):
    print(row["username"], row["role"])

report = here / "out" / "report.txt"
report.parent.mkdir(exist_ok=True)
report.write_text("3 users checked\n", encoding="utf-8")
print(report.read_text(encoding="utf-8").strip())
print(report.exists(), report.name)
