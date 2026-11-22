# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
from ex09_json import failed_tests, to_json

RESULTS = """
{"tests": [
  {"name": "test_login", "outcome": "passed"},
  {"name": "test_refund_day_31", "outcome": "failed"},
  {"name": "test_search", "outcome": "skipped"}
]}
"""


def test_failed_tests():
    assert failed_tests(RESULTS) == ["test_refund_day_31"]


def test_to_json_keeps_bengali_readable():
    assert to_json({"name": "আরশাদ"}) == '{\n  "name": "আরশাদ"\n}'
