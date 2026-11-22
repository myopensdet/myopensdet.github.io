# Template from myOpenSDET: https://myopensdet.github.io/
"""An API client that logs every call: what was sent, what came back, and how long it took.

INFO: one line per call. DEBUG: the bodies too, with secrets replaced by "***".
WARNING: a call the app refused (4xx or 5xx), with its answer.
The logs end up in the console (on failure), the HTML report and reports/tests.log.
"""

import json
import logging
import time

import requests

log = logging.getLogger("shop.api")
SECRETS = {"password", "card", "token", "authorization", "cookie", "api_key"}
MAX_BODY = 500  # characters of a body to log; enough to read, not enough to flood


def redact(data):
    """A copy of data with the value of every secret-looking key replaced."""
    if isinstance(data, dict):
        return {k: "***" if k.lower() in SECRETS else redact(v) for k, v in data.items()}
    if isinstance(data, list):
        return [redact(item) for item in data]
    return data


def short(text: str) -> str:
    return text if len(text) <= MAX_BODY else text[:MAX_BODY] + f"... ({len(text)} characters)"


class ShopApi:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def call(self, method: str, path: str, body: dict | None = None) -> requests.Response:
        if body is not None:
            log.debug("%s %s body: %s", method, path, json.dumps(redact(body)))
        start = time.perf_counter()
        response = self.session.request(method, self.base_url + path, json=body, timeout=10)
        ms = (time.perf_counter() - start) * 1000
        refused = response.status_code >= 400
        log.log(
            logging.WARNING if refused else logging.INFO,
            "%s %s -> %s in %.0f ms",
            method,
            path,
            response.status_code,
            ms,
        )
        # A refused call's answer says why: show it with the failure, not only in the log file.
        answer = short(redact_text(response.text))
        log.log(
            logging.WARNING if refused else logging.DEBUG, "%s %s answer: %s", method, path, answer
        )
        return response

    def log_in(self, email: str, password: str):
        return self.call("POST", "/api/login", {"email": email, "password": password})

    def books(self, search: str = ""):
        return self.call("GET", f"/api/books?q={search}")

    def add_to_cart(self, book: str):
        return self.call("POST", "/api/cart", {"book": book})

    def place_order(self, **order):
        return self.call("POST", "/api/orders", order)


def redact_text(text: str) -> str:
    """Redact a JSON answer; leave other text as it is."""
    try:
        return json.dumps(redact(json.loads(text)))
    except ValueError:
        return text
