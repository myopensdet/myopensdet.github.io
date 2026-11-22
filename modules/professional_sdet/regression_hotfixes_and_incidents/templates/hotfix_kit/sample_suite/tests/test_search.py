# Template from myOpenSDET: https://myopensdet.github.io/
import pytest

pytestmark = [pytest.mark.search, pytest.mark.regression]


@pytest.mark.smoke
def test_search_by_title():
    assert True


def test_search_with_no_results():
    assert True


def test_search_sorting():
    assert True
