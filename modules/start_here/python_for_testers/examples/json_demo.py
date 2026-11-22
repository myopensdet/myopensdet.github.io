# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: JSON. Run: python json_demo.py"""

import json
from pathlib import Path

# 1. An API answer arrives as JSON text. json.loads turns it into Python data.
body = """
{
  "device": {"id": "SNS-0042", "online": true, "firmware": null},
  "battery": "87",
  "readings": [
    {"time": "09:00", "temperature": 21.5},
    {"time": "09:10", "temperature": 22.0}
  ]
}
"""
data = json.loads(body)
print(type(data), data["device"]["online"], data["device"]["firmware"])
print(data["readings"][-1]["temperature"], len(data["readings"]))

# 2. Check the types, not only the values. The docs say battery is a number.
print(repr(data["battery"]), isinstance(data["battery"], int))

# 3. Python data to JSON text, for a request body or a log.
request_body = {"device_id": "SNS-0042", "location": "ঢাকা অফিস", "alerts": True, "note": None}
print(json.dumps(request_body))
print(json.dumps(request_body, ensure_ascii=False))
print(json.dumps(request_body, indent=2, ensure_ascii=False))

# 4. Save the answer to a file, and read it back unchanged.
saved = Path(__file__).parent / "out" / "device.json"
saved.parent.mkdir(exist_ok=True)
saved.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(json.loads(saved.read_text(encoding="utf-8")) == data)
