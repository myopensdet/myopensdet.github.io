# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Login: the right user gets a token; everyone else gets the same plain "no"."""

import pytest
import requests

from tests.conftest import BASE_URL, LOGIN_PATH, log_in, user_from_env

WRONG_PASSWORD = "wrong_password"  # noqa: S105  (a deliberately wrong password)


def test_right_login_gives_a_token():
    email, password = user_from_env("USER_A")
    answer = log_in(email, password)
    assert answer.status_code == 200
    assert answer.json().get("token")
    assert password not in answer.text, "the answer contains the password"


def test_wrong_password_is_refused():
    email, _ = user_from_env("USER_A")
    answer = log_in(email, WRONG_PASSWORD)
    assert answer.status_code == 401
    assert "token" not in answer.json()


def test_unknown_user_gets_the_same_answer_as_a_wrong_password():
    """Different answers tell an attacker which emails have an account."""
    email, _ = user_from_env("USER_A")
    wrong_password = log_in(email, WRONG_PASSWORD)
    unknown_user = log_in("nobody@example.com", WRONG_PASSWORD)
    unknown, wrong = unknown_user.json(), wrong_password.json()
    assert unknown == wrong, f"unknown user: {unknown}, wrong password: {wrong}"
    assert unknown_user.status_code == wrong_password.status_code


@pytest.mark.parametrize(
    "body",
    [{}, {"email": "arshad.test@example.com"}, "not json"],
    ids=["empty", "no password", "not json"],
)
def test_bad_login_requests_get_400_not_a_crash(body):
    if isinstance(body, str):
        answer = requests.post(f"{BASE_URL}{LOGIN_PATH}", data=body, timeout=10)
    else:
        answer = requests.post(f"{BASE_URL}{LOGIN_PATH}", json=body, timeout=10)
    assert answer.status_code in (400, 401, 422), f"got {answer.status_code}"
