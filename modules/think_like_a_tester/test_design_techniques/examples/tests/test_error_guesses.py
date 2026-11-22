# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Error guessing: tricky inputs that break code often. Only agreed behaviour becomes a test."""

import pytest
from shop.signup import check_signup

CHARACTERS_ERROR = "Username can only use letters and numbers"


@pytest.mark.parametrize(
    "username",
    [
        " arshad ",  # spaces around, often pasted from an email
        "     ",  # only spaces: looks empty, but has a length
        "ars\thad",  # a tab
        "<b>hi</b>",  # HTML: could show up as bold, or worse, on other pages
        "x' OR '1'='1",  # looks like a database attack
        "arshad😀",  # emoji
    ],
)
def test_tricky_usernames_are_refused(username):
    assert check_signup(username, 30) == [CHARACTERS_ERROR]


def test_a_username_of_exactly_20_letters_is_accepted():
    assert check_signup("a" * 20, 30) == []


# Not tests yet: the product owner has to decide these first (see the lesson).
# - "আরশাদ" (a Bengali name) is refused, but "José" is accepted.
# - "ａｄｍｉｎ" (wide letters that look like "admin") is accepted.
