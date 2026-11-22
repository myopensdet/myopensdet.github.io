# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 3: conditions and loops. Replace each raise line with your code."""


def status_group(code: int) -> str:
    """Name the group of an HTTP status code.

    200-299: "ok", 400-499: "client error", 500-599: "server error",
    anything else: "other".
    """
    raise NotImplementedError("Write your code here")


def count_outcomes(outcomes: list[str]) -> dict[str, int]:
    """Count each outcome: ["passed", "failed", "passed"] -> {"passed": 2, "failed": 1}."""
    raise NotImplementedError("Write your code here")


def first_ok_try(statuses: list[int], max_tries: int) -> int:
    """The try number (1, 2, ...) of the first 200, looking at no more than max_tries.

    Return 0 when no try within the limit got a 200.
    """
    raise NotImplementedError("Write your code here")
