# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: lists, tuples, sets and dictionaries. Run: python collections_demo.py"""

# 1. Text from a web page often has extra spaces and mixed case.
banner = "  Device SNS-0042 is ONLINE \n"
clean = banner.strip().lower()
print(repr(clean), "online" in clean, clean.split(" "))

# 2. A list: status codes from one test run, in order. Lists can change.
statuses = [200, 200, 503, 200]
statuses.append(201)
print(len(statuses), statuses[0], statuses[-1], statuses[1:3], statuses.count(200))

# 3. A tuple: values that must not change during the run.
allowed_statuses = (200, 201, 204)
print(503 in allowed_statuses, 201 in allowed_statuses)

# 4. A set: no order, no duplicates. Good for "what is missing?"
expected_devices = {"SNS-0041", "SNS-0042", "SNS-0043"}
reports = ["SNS-0042", "SNS-0043", "SNS-0043", "SNS-0099"]  # SNS-0043 sent twice
reported_devices = set(reports)
print(len(reports), len(reported_devices), sorted(expected_devices - reported_devices))
print(sorted(reported_devices - expected_devices))

# 5. A dictionary: an API response, values looked up by name (key).
response = {"id": "SNS-0042", "status": "online", "battery": 87, "firmware": None}
print(response["status"], response.get("location"), response.get("location", "unknown"))
required_fields = {"id", "status", "battery", "last_seen"}
print(sorted(required_fields - response.keys()))
response["battery"] = 86
print(response)
