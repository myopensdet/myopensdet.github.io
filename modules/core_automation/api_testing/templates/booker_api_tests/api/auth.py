# Template from myOpenSDET: https://myopensdet.github.io/
"""Login helpers for the four usual kinds: API key, Basic, Bearer token, OAuth2."""

import os

import requests
from requests.auth import AuthBase, HTTPBasicAuth


def secret(name: str) -> str:
    """Read a secret from an environment variable, with a clear message if it isn't set."""
    value = os.environ.get(name)
    if not value:
        raise LookupError(f"Set the environment variable {name} first")
    return value


def api_key_header(key: str, header: str = "X-API-Key") -> dict:
    """An API key is usually sent in a header. Check your API's docs for the name."""
    return {header: key}


def basic_auth(username: str, password: str) -> HTTPBasicAuth:
    """Basic auth: username and password in the Authorization header, on every request."""
    return HTTPBasicAuth(username, password)


class BearerAuth(AuthBase):
    """Adds "Authorization: Bearer <token>" to every request, and never prints the token."""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

    def __repr__(self):
        return "BearerAuth(token=***)"


def oauth2_client_credentials(
    token_url: str,
    client_id: str,
    client_secret: str,
    scope: str | None = None,
    timeout: float = 10,
) -> str:
    """Get an access token with the OAuth2 client credentials flow (RFC 6749, section 4.4)."""
    data = {"grant_type": "client_credentials"}
    if scope:
        data["scope"] = scope
    response = requests.post(token_url, data=data, auth=(client_id, client_secret), timeout=timeout)
    response.raise_for_status()
    return response.json()["access_token"]


def booker_token(client, username: str, password: str) -> str:
    """Restful-booker's own login: POST /auth, then send the token as a cookie."""
    body = client.post("/auth", json={"username": username, "password": password}).json()
    if "token" not in body:
        # Restful-booker answers 200 even for a wrong password, with {"reason": ...}.
        raise PermissionError(f"Login refused: {body.get('reason', body)}")
    return body["token"]
