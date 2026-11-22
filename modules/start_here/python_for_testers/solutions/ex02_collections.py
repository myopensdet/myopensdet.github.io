# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 2: lists, tuples, sets and dictionaries. Replace each raise line."""


def clean_message(text: str) -> str:
    """Remove spaces at both ends, and make it lower case: "  Saved! " -> "saved!"."""
    return text.strip().lower()


def missing_devices(expected: list, reported: list) -> list:
    """Device IDs that are expected but were not reported, sorted A to Z."""
    return sorted(set(expected) - set(reported))


def missing_fields(response: dict, required: list) -> list:
    """Required keys that the API response does not have, sorted A to Z."""
    return sorted(set(required) - response.keys())


def status_of(response: dict) -> str:
    """The response's "status", or "unknown" when the API did not send one."""
    return response.get("status", "unknown")
