# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Shared setup for login, token and permission tests.

Change the parts marked CHANGE for your own app. Users come from the terminal,
never from a file:  export USER_A="email:password"  (and USER_B, ADMIN)."""

import os

import pytest
import requests

# CHANGE 1: the address of the API you test.
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8765")

# CHANGE 2: the paths in your API.
LOGIN_PATH = "/api/login"
LOGOUT_PATH = "/api/logout"
ME_PATH = "/api/me"  # any page that needs a login
ADMIN_PATH = "/api/admin/users"  # a page only admins may open

# CHANGE 3: one record that belongs to user A, and one that belongs to user B.
A_RECORD_PATH = "/api/orders/101"
B_RECORD_PATH = "/api/orders/102"


class HiddenHeaders(dict):
    """Headers that print as *** so the token never shows in a failure message."""

    def __repr__(self):
        return repr(dict.fromkeys(self, "***"))


def user_from_env(name: str) -> tuple[str, str]:
    email, _, password = os.environ.get(name, "").partition(":")
    if not (email and password):
        pytest.skip(f'Set {name}="email:password" to run this test')
    return email, password


def log_in(email: str, password: str) -> requests.Response:
    """CHANGE 4: how your app logs in (here: JSON body, token in the answer)."""
    return requests.post(
        f"{BASE_URL}{LOGIN_PATH}", json={"email": email, "password": password}, timeout=10
    )


def headers_for(token: str) -> HiddenHeaders:
    """CHANGE 5: how your app wants the token (here: Authorization: Bearer ...)."""
    return HiddenHeaders(Authorization=f"Bearer {token}")


def login_headers(name: str) -> HiddenHeaders:
    email, password = user_from_env(name)
    answer = log_in(email, password)
    assert answer.status_code == 200, f"{name} could not log in: {answer.status_code}"
    return headers_for(answer.json()["token"])


@pytest.fixture
def user_a() -> HiddenHeaders:
    return login_headers("USER_A")


@pytest.fixture
def user_b() -> HiddenHeaders:
    return login_headers("USER_B")


@pytest.fixture
def admin() -> HiddenHeaders:
    return login_headers("ADMIN")


def get(path: str, headers: dict | None = None) -> requests.Response:
    return requests.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
