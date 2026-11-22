# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 9: JSON."""

import json


def failed_tests(text: str) -> list[str]:
    """From a results JSON text, return the names of the tests whose outcome is "failed"."""
    data = json.loads(text)
    return [test["name"] for test in data["tests"] if test["outcome"] == "failed"]


def to_json(data: dict) -> str:
    """Turn data into JSON text with 2-space indents, keeping Bengali letters readable."""
    return json.dumps(data, indent=2, ensure_ascii=False)
