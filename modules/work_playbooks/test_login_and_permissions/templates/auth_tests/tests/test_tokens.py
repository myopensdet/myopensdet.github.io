# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Tokens: only a real, current token opens a page that needs a login."""

import requests

from tests.conftest import (
    BASE_URL,
    LOGOUT_PATH,
    ME_PATH,
    get,
    headers_for,
    log_in,
    user_from_env,
)


def test_no_token_gets_401():
    assert get(ME_PATH).status_code == 401


def test_made_up_token_gets_401():
    assert get(ME_PATH, headers_for("made-up-token")).status_code == 401


def test_changed_token_gets_401():
    email, password = user_from_env("USER_A")
    token = log_in(email, password).json()["token"]
    changed = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert get(ME_PATH, headers_for(changed)).status_code == 401


def test_token_opens_the_right_account(user_a):
    email, _ = user_from_env("USER_A")
    answer = get(ME_PATH, user_a)
    assert answer.status_code == 200
    assert answer.json()["email"] == email


def test_token_stops_working_after_logout():
    email, password = user_from_env("USER_A")
    headers = headers_for(log_in(email, password).json()["token"])
    logout = requests.post(f"{BASE_URL}{LOGOUT_PATH}", headers=headers, timeout=10)
    assert logout.status_code in (200, 204)
    assert get(ME_PATH, headers).status_code == 401, "the token still works after logout"
