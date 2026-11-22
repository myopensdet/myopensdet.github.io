# Template from myOpenSDET: https://myopensdet.github.io/
from ex09_json import failed_tests, to_json, wrong_types

RESULTS = """
{"tests": [
  {"name": "test_device_online", "outcome": "passed"},
  {"name": "test_battery_alert", "outcome": "failed"},
  {"name": "test_export", "outcome": "skipped"}
]}
"""

SCHEMA = {"id": str, "online": bool, "battery": int}


def test_failed_tests():
    assert failed_tests(RESULTS) == ["test_battery_alert"]


def test_to_json_keeps_bengali_readable():
    assert to_json({"location": "ঢাকা অফিস"}) == '{\n  "location": "ঢাকা অফিস"\n}'


def test_wrong_types_all_right():
    assert wrong_types({"id": "SNS-0042", "online": True, "battery": 87}, SCHEMA) == []


def test_wrong_types_finds_text_and_missing_keys():
    data = {"id": "SNS-0042", "battery": "87"}
    assert wrong_types(data, SCHEMA) == ["online", "battery"]


def test_wrong_types_true_is_not_a_number():
    assert wrong_types({"id": "SNS-0042", "online": True, "battery": True}, SCHEMA) == ["battery"]
