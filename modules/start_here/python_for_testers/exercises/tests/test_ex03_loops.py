# Template from myOpenSDET: https://myopensdet.github.io/
import pytest
from ex03_loops import count_outcomes, first_ok_try, status_group


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


def test_first_ok_try():
    assert first_ok_try([503, 503, 200], max_tries=5) == 3
    assert first_ok_try([200], max_tries=5) == 1


def test_first_ok_try_respects_the_limit():
    assert first_ok_try([503, 503, 503, 200], max_tries=3) == 0
    assert first_ok_try([], max_tries=3) == 0
