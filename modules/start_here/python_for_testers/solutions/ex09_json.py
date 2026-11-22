# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 9: JSON. Replace each raise line with your code."""

import json


def failed_tests(text: str) -> list[str]:
    """From a results JSON text, return the names of the tests whose outcome is "failed"."""
    results = json.loads(text)
    return [test["name"] for test in results["tests"] if test["outcome"] == "failed"]


def to_json(data: dict) -> str:
    """Turn data into JSON text with 2-space indents, keeping Bengali letters readable."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def wrong_types(data: dict, expected: dict) -> list[str]:
    """The keys whose value does not have the expected type, in the order of expected.

    expected looks like {"id": str, "battery": int}. A missing key counts as wrong.
    Use type(value) is expected_type, so True does not count as an int.
    """
    wrong = []
    for key, expected_type in expected.items():
        if key not in data or type(data[key]) is not expected_type:
            wrong.append(key)
    return wrong
