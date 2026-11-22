# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 3: if and loops."""


def status_group(code: int) -> str:
    """Name the group of an HTTP status code: "ok", "client error" or "server error"."""
    if 200 <= code < 300:
        return "ok"
    elif 400 <= code < 500:
        return "client error"
    elif 500 <= code < 600:
        return "server error"
    return "other"


def count_outcomes(outcomes: list[str]) -> dict[str, int]:
    """Count each outcome: ["passed", "failed", "passed"] -> {"passed": 2, "failed": 1}."""
    counts = {}
    for outcome in outcomes:
        counts[outcome] = counts.get(outcome, 0) + 1
    return counts
