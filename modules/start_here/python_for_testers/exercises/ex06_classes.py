# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 6: classes and objects. Replace each raise line with your code."""


class TestRun:
    """The results of one test run: each test's name and outcome."""

    __test__ = False  # tells pytest this is not a test class, despite its name

    def __init__(self, name: str):
        """Keep the run's name, and start with an empty list of results."""
        raise NotImplementedError("Write your code here")

    def add(self, test_name: str, outcome: str):
        """Add one result. outcome is "passed", "failed" or "skipped"."""
        raise NotImplementedError("Write your code here")

    def count(self, outcome: str) -> int:
        """How many results have this outcome."""
        raise NotImplementedError("Write your code here")

    def failed_tests(self) -> list[str]:
        """The names of the failed tests, in the order they were added."""
        raise NotImplementedError("Write your code here")

    def summary(self) -> str:
        """Like "nightly: 3 tests, 1 failed"."""
        raise NotImplementedError("Write your code here")
