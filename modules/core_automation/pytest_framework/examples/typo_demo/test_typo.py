# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The marker is misspelled on purpose: smok instead of smoke."""

import pytest


@pytest.mark.smok
def test_home_page_loads():
    assert True
