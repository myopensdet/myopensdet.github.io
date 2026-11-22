# Template from myOpenSDET: https://myopensdet.github.io/
"""A small API client for tests: one place for the base URL, headers, timeout and logging."""

import logging

import requests

log = logging.getLogger("api")

# Header names whose values must never appear in logs or failure messages.
SECRET_HEADERS = {"authorization", "cookie", "x-api-key"}


class ApiClient:
    """Send requests to one API. Every test uses the same settings, set once here."""

    def __init__(self, base_url: str, timeout: float = 10, headers: dict | None = None, auth=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", **(headers or {})})
        if auth is not None:
            self.session.auth = auth

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, url, **kwargs)
        log.info(
            "%s %s -> %s in %d ms",
            method,
            response.url,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def safe_headers(headers) -> dict:
    """A copy of the headers with secret values hidden, safe to print."""
    return {
        name: "***" if name.lower() in SECRET_HEADERS else value for name, value in headers.items()
    }


def check_status(response: requests.Response, expected: int) -> None:
    """Fail with everything you need to debug: method, URL, status and the start of the body."""
    if response.status_code != expected:
        request = response.request
        raise AssertionError(
            f"{request.method} {request.url} returned {response.status_code}, expected {expected}\n"
            f"request headers: {safe_headers(request.headers)}\n"
            f"response body: {response.text[:300]!r}"
        )
