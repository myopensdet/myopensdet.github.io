---
title: "An API Client Class: One Place for the URL, Headers, Timeout and Logging"
description: "Build a small ApiClient for tests with requests.Session: the base URL, default headers, timeout and logging set once, plus a check_status helper whose failures show the method, URL, status and body with secrets hidden."
level: Intermediate
tags:
  - API
  - Python
  - Clean code
nav_title: "An API client class"
order: 100
summary: "One class for the base URL, headers, timeout and logging, and clear failures."
updated: "2026-11-22"
---

# An API Client Class: One Place for the URL, Headers, Timeout and Logging

After a few test files, the same lines repeat everywhere: the base URL, `Accept: application/json`, `timeout=15`, the login header. An **API client class** puts them in one place. Tests then read like `client.get("/booking/1")`, and when the base URL or a header changes, you change one file.

!!! note "Before you start"
    Read [Classes](../programming-for-testers/object-oriented-programming.md) and [Chaining requests](chaining-requests.md) first.

## What you will learn

- How to build a small client on `requests.Session`
- How to log every request, with its time
- How to make failures show everything needed to debug, with secrets hidden
- What belongs in the client, and what doesn't

## Why this matters at work

When an API test fails in CI at night, the failure message is all you have. "assert 403 == 200" tells you nothing. "PUT /booking/1 returned 403, expected 200" with the headers and the body tells you it was the login. A good client gives every test that message for free.

## The idea in plain words

!!! info "In plain words"
    The client is a phone with the office number saved, and a call log. You press "call", and it dials, waits a set time, and writes down who you called and how long it took.

## Step by step

1. **Read the client.** The template's `api/client.py`:

    ```python
    --8<-- "modules/core_automation/api_testing/templates/booker_api_tests/api/client.py"
    ```

2. **One session for everything.** `requests.Session()` keeps the connection open between requests, which is faster, and holds the default headers and login. Every request adds `Accept: application/json` without the test saying so.

3. **The timeout is set once.** `kwargs.setdefault("timeout", self.timeout)` gives every request the default, and a test can still pass its own for a slow call.

4. **Every request is logged.** The `api` logger writes the method, the full URL, the status and the time in milliseconds. pytest shows these lines for failed tests, so you see the whole conversation before the failure.

5. **`check_status` fails with everything you need.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/client_demo.py"
    ```

    ```bash
    python client_demo.py
    ```

    ```text
    api: GET https://restful-booker.herokuapp.com/ping -> 201 in 637 ms
    api: GET https://restful-booker.herokuapp.com/booking?firstname=Test -> 200 in 158 ms
    api: PUT https://restful-booker.herokuapp.com/booking/1 -> 403 in 158 ms
    PUT https://restful-booker.herokuapp.com/booking/1 returned 403, expected 200
    request headers: {'User-Agent': 'python-requests/2.34.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive', 'Cookie': '***', 'Content-Length': '2', 'Content-Type': 'application/json'}
    response body: 'Forbidden'
    ```

    Your times will be different. The failure names the method and URL, shows the headers with `Cookie` hidden as `***`, and shows the start of the body. Restful-booker's `/ping` answers 201, another of its wrong codes; most health checks answer 200.

6. **Know what the body excerpt can hold.** `check_status` hides secret *headers*, but it prints the body as it is. If an API echoes your token or personal data in its error body, that ends up in the failure message, and in CI logs. For such APIs, shorten the excerpt or hide those fields too.

7. **Keep the client small.** It holds the *how*: URL, headers, timeout, logging, login. It doesn't hold the *what*: no asserts about bookings, no test data. Those stay in tests and fixtures. When the client grows a method per endpoint, like `get_booking(id)`, keep each one thin: build the request, return the response, and let the test check it.

    !!! success "Check: you should now be able to"
        Build a client on a session with defaults set once, log each request, and fail with a clear message that hides secrets.

## When it goes wrong

- **Every request fails with `MissingSchema`.** The base URL has no `https://`. Check the setting it comes from.
- **Double slashes, like `//booking`, or a missing one.** The template strips slashes from both sides and joins with one. Keep that in your own client.
- **A header from one test shows up in another.** A test changed `client.session.headers`, and the client is session-scoped. Pass per-request headers with `headers=` instead.
- **No log lines in the pytest output.** Logs show only for failing tests, at the level in `pytest.ini` (`log_level = INFO`). Use `-o log_cli=true` to see them live.

## Common mistakes

!!! warning "Common mistakes"
    - **Asserts inside the client.** A test that expects 404 can't use a client that fails on 404.
    - **Logging the full headers or body.** Hide secrets: `safe_headers()` does it for headers.
    - **A new session for every request.** It throws away the speed and the defaults.

!!! failure "If you see this error"
    **`requests.exceptions.MissingSchema: Invalid URL 'restful-booker.herokuapp.com/ping': No scheme supplied. Perhaps you meant https://restful-booker.herokuapp.com/ping?`**
    The client was built with a base URL without `https://`. Fix the setting, for example `BOOKER_URL=https://restful-booker.herokuapp.com`.

## Try it yourself

Add a `health()` method to `ApiClient` that calls `/ping` and returns `True` when the status is what the API uses for "up". Then use it in a session fixture that skips the whole run when the API is down.

??? success "Solution"
    ```python
    def health(self, path: str = "/ping", up: int = 201) -> bool:
        try:
            return self.get(path).status_code == up
        except requests.ConnectionError:
            return False
    ```

    ```python
    @pytest.fixture(scope="session", autouse=True)
    def api_is_up(client):
        if not client.health():
            pytest.skip("The API is down: skipping instead of failing every test")
    ```

    One clear skip reason beats a hundred connection errors. Restful-booker uses 201 for "up"; most APIs use 200.

## Quick check

1. Why build the client on `requests.Session`?

    ??? question "Answer"
        It keeps the connection open, and holds default headers and the login for every request.

2. Why shouldn't the client assert status codes?

    ??? question "Answer"
        Tests that expect 404 or 403 need to see those answers. The test decides what's right.

3. What does `check_status` hide, and what doesn't it?

    ??? question "Answer"
        It hides secret headers: `Authorization`, `Cookie`, `X-API-Key`. It doesn't hide anything in the body.

## References

- [Requests: Session objects](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects)
- [Python: Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [pytest: How to manage logging](https://docs.pytest.org/en/stable/how-to/logging.html)

Written for Python 3.13, pytest 9.2 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
