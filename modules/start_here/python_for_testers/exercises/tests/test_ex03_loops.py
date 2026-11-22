# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
import pytest
from ex03_loops import count_outcomes, status_group


@pytest.mark.parametrize(
    ("code", "group"),
    [(200, "ok"), (201, "ok"), (404, "client error"), (500, "server error"), (302, "other")],
)
def test_status_group(code, group):
    assert status_group(code) == group


def test_count_outcomes():
    assert count_outcomes(["passed", "failed", "passed"]) == {"passed": 2, "failed": 1}


def test_count_outcomes_of_nothing():
    assert count_outcomes([]) == {}
