# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: conditions and loops. Run: python loops_demo.py"""

# 1. if, elif, else: decide what one response means.
status = 503
if 200 <= status < 300:
    verdict = "PASS"
elif status in (429, 503):
    verdict = "RETRY"  # busy or starting up: try again later
else:
    verdict = "FAIL"
print(f"status {status}: {verdict}")

# 2. for: check every reading against the rule (-20 to 60 degrees).
readings = [
    {"device": "SNS-0041", "temperature": 21.5},
    {"device": "SNS-0042", "temperature": 85.0},
    {"device": "SNS-0043", "temperature": None},
    {"device": "SNS-0044", "temperature": -3.0},
]
failures = []
for reading in readings:
    temperature = reading["temperature"]
    if temperature is None:
        failures.append(f"{reading['device']}: no reading")
    elif not -20 <= temperature <= 60:
        failures.append(f"{reading['device']}: {temperature} is out of range")
print(f"{len(readings)} readings checked, {len(failures)} failed")
for failure in failures:
    print(f"  - {failure}")

# 3. A list comprehension: a loop and a filter in one line.
response_times = [0.42, 1.8, 0.35, 2.4]
slow = [seconds for seconds in response_times if seconds > 1.0]
print("slow responses:", slow)

# 4. Retry with a limit: stop when it works, never loop forever.
# A pretend device: what it says on each try. A real test would ask the API.
device_answers = ["booting", "booting", "online", "online", "online"]
max_tries = 5
for attempt in range(1, max_tries + 1):
    state = device_answers[attempt - 1]
    print(f"try {attempt}: {state}")
    if state == "online":
        print(f"PASS: online after {attempt} tries")
        break
else:
    print(f"FAIL: still not online after {max_tries} tries")
