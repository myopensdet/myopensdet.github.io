# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Example tests. Replace them with your own, and keep the patterns."""

import pytest


@pytest.mark.smoke
def test_environment_has_a_base_url(base_url):
    assert base_url.startswith(("http://", "https://"))


@pytest.mark.parametrize(("text", "expected"), [("  Admin ", "admin"), ("maria", "maria")])
def test_usernames_are_cleaned(text, expected):
    assert text.strip().lower() == expected


@pytest.mark.api
def test_needs_a_token(api_token, base_url):
    # Call your API here with the token, for example with requests or httpx.
    assert api_token
