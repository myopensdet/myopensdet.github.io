# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: file handling. Run: python files_demo.py"""

import csv
from pathlib import Path

here = Path(__file__).parent  # the folder this script is in
data_file = here / "devices.csv"
out = here / "out"
out.mkdir(exist_ok=True)

# 1. Read test data from a CSV file. Every value arrives as text.
with data_file.open(encoding="utf-8", newline="") as file:
    lines = [line for line in file if not line.startswith("#")]  # skip the comment line
cases = list(csv.DictReader(lines))
print(len(cases), cases[0])

# 2. Run the checks. A dictionary stands in for the real API answers.
api_answers = {"SNS-0041": (200, 0.42), "SNS-0042": (503, 0.10), "SNS-0043": (404, 0.31)}
results = []
for case in cases:
    status, seconds = api_answers[case["device_id"]]
    passed = status == int(case["expected_status"]) and seconds <= float(case["max_seconds"])
    results.append(
        {"device_id": case["device_id"], "status": status, "result": "PASS" if passed else "FAIL"}
    )

# 3. Write the results as a new CSV file ("w" replaces the old file).
report = out / "results.csv"
with report.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["device_id", "status", "result"])
    writer.writeheader()
    writer.writerows(results)
print(report.read_text(encoding="utf-8"), end="")

# 4. Add a line to a log file ("a" keeps what is already there).
log = out / "run.log"
log.write_text("", encoding="utf-8")  # start empty, so every run prints the same
for _ in range(2):
    with log.open("a", encoding="utf-8") as file:
        file.write(f"checked {len(results)} devices at {cases[0]['location']}\n")
print(log.read_text(encoding="utf-8"), end="")
print(report.exists(), report.name, report.stat().st_size > 0)
