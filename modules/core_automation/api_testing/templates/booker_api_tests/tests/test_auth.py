# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Logging in, and what happens with a wrong password."""

import pytest
from api.auth import booker_token


def test_login_gives_a_token(token):
    assert len(token) > 10


def test_wrong_password_is_refused(client):
    # Restful-booker answers 200 with {"reason": "Bad credentials"}.
    # The helper turns that into an error, so the test reads clearly.
    with pytest.raises(PermissionError, match="Login refused: Bad credentials"):
        booker_token(client, "admin", "wrong-password")
