# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 2: lists, tuples, sets and dictionaries. Replace each raise line."""


def clean_message(text: str) -> str:
    """Remove spaces at both ends, and make it lower case: "  Saved! " -> "saved!"."""
    raise NotImplementedError("Write your code here")


def missing_devices(expected: list, reported: list) -> list:
    """Device IDs that are expected but were not reported, sorted A to Z."""
    raise NotImplementedError("Write your code here")


def missing_fields(response: dict, required: list) -> list:
    """Required keys that the API response does not have, sorted A to Z."""
    raise NotImplementedError("Write your code here")


def status_of(response: dict) -> str:
    """The response's "status", or "unknown" when the API did not send one."""
    raise NotImplementedError("Write your code here")
