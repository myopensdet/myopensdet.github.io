# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 6: classes and objects. Replace each raise line with your code."""


class TestRun:
    """The results of one test run: each test's name and outcome."""

    __test__ = False  # tells pytest this is not a test class, despite its name

    def __init__(self, name: str):
        """Keep the run's name, and start with an empty list of results."""
        self.name = name
        self.results = []

    def add(self, test_name: str, outcome: str):
        """Add one result. outcome is "passed", "failed" or "skipped"."""
        self.results.append({"test": test_name, "outcome": outcome})

    def count(self, outcome: str) -> int:
        """How many results have this outcome."""
        return len([r for r in self.results if r["outcome"] == outcome])

    def failed_tests(self) -> list[str]:
        """The names of the failed tests, in the order they were added."""
        return [r["test"] for r in self.results if r["outcome"] == "failed"]

    def summary(self) -> str:
        """Like "nightly: 3 tests, 1 failed"."""
        return f"{self.name}: {len(self.results)} tests, {self.count('failed')} failed"
