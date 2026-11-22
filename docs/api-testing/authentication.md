---
title: "API Authentication: API Keys, Basic, Bearer Tokens and OAuth2"
description: "The four ways APIs usually check who you are (API key, Basic auth, Bearer token, OAuth2 client credentials), how to send each with requests, what to test, and how to keep secrets out of code and logs."
level: Intermediate
tags:
  - API
  - Security
nav_title: "Authentication"
order: 60
summary: "API keys, Basic, Bearer tokens and OAuth2, and keeping secrets out of code."
updated: "2026-11-22"
---

# API Authentication: API Keys, Basic, Bearer Tokens and OAuth2

Most APIs want to know who's calling. Almost all of them use one of four ways: an **API key** in a header, **Basic auth** with a username and password, a **Bearer token** you got from a login, or **OAuth2**, where a separate server gives out tokens. Your tests need to send the right one, and test what happens without it, because a missing login check is one of the worst bugs an API can have.

!!! note "Before you start"
    Read [Headers and JSON](headers-and-json.md) first. Every login travels in a header.

## What you will learn

- How each of the four kinds works, and how to send it with `requests`
- How to test login: with it, without it, with a wrong one, with an expired one
- How OAuth2 client credentials works in tests
- How to keep secrets out of code, logs and failure messages

## Why this matters at work

Login bugs are security bugs: an endpoint that works without a token, a token that never expires, another user's data behind your token. And login code is where secrets leak: a token pasted into a test file, or printed in a CI log that everyone can read.

## The idea in plain words

!!! info "In plain words"
    An API key is a building pass with your name on it. Basic auth is saying your name and password at the door, every time. A Bearer token is a visitor's badge you got at reception: whoever holds it gets in, until it expires. OAuth2 is the reception desk that hands out the badges.

## Step by step

1. **Run the tour.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/auth_demo.py"
    ```

    ```bash
    python auth_demo.py
    ```

    ```text
    API key    200 server got test-key-123
    Basic      200 True | wrong password: 401
    Bearer     200 True | no token: 401
    Login      200 then /auth/me: 200 emilys
    Bad token  401 {'message': 'Invalid/Expired Token!'}
    ```

    The keys and passwords are fake, or the demo accounts that [httpbin](https://httpbin.org/) and [DummyJSON](https://dummyjson.com/docs/auth) publish for practice.

2. **API key.** A fixed key in a header, often `X-API-Key`. The name depends on the API, so check its docs. Some APIs take the key in the query (`?api_key=...`). Avoid that if you can: URLs end up in logs.

3. **Basic auth.** `auth=("tester", "s3cret")` sends the username and password in the `Authorization` header on every request. It's only encoded, not encrypted, so it's safe only over HTTPS.

4. **Bearer token.** First log in, then send `Authorization: Bearer <token>` on every call. DummyJSON's login returns an `accessToken`, and `/auth/me` answers with the user it belongs to. A made-up token gets 401. Tokens expire, so a test suite logs in once per run, in a fixture, not once per file.

    Restful-booker is different: it wants the token as a cookie, `Cookie: token=...`. Always read the API's docs. "Token" doesn't always mean "Bearer".

5. **OAuth2 client credentials.** For service-to-service APIs, a separate token server gives out tokens. Your test sends a client id and client secret to the token URL, gets an `access_token`, then calls the API with it as a Bearer token. The template's helper does exactly that:

    ```python
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
    ```

    There's no public OAuth2 server for practice that's safe to depend on, so this site's tests check the helper against a small local server. At work, your team will give you a token URL, a client id and a client secret for the test environment. The token request is a form (`data=`), not JSON, as the [OAuth2 standard](https://www.rfc-editor.org/rfc/rfc6749#section-4.4) says.

6. **Test the login itself.** For every endpoint that needs a login:

    | Case | Expect |
    | --- | --- |
    | A valid login | 200, and only your data |
    | No login at all | 401 |
    | A wrong or made-up token | 401 |
    | An expired token | 401 |
    | A valid login without the right role | 403 |

    The template project's `test_put_without_login_is_refused` checks the "no login" row, and then checks the booking didn't change.

7. **Keep secrets out of code.** Read them from environment variables:

    ```python
    def secret(name: str) -> str:
        """Read a secret from an environment variable, with a clear message if it isn't set."""
        value = os.environ.get(name)
        if not value:
            raise LookupError(f"Set the environment variable {name} first")
        return value
    ```

    In CI, the values come from the CI tool's secret store. Never commit them, not even for a test environment. And never print them: the template's `BearerAuth` prints as `BearerAuth(token=***)`, and `check_status` hides `Authorization`, `Cookie` and `X-API-Key` in failure messages.

    !!! success "Check: you should now be able to"
        Send each of the four kinds, list the login cases to test, and keep the secrets in environment variables.

## When it goes wrong

- **401 with a token that worked a minute ago.** It expired. Log in again in the fixture, or ask for a longer-lived test token.
- **401 although the token is right.** Check the header: `Bearer` with a capital B and one space, or a cookie instead. Print the header names you send (not the values).
- **403 instead of 200.** You're logged in, but your test user lacks a role. Ask for a test user with the right role. Don't reuse an admin for everything, or you'll never catch role bugs.
- **The test passes on your machine and skips in CI.** The environment variable isn't set in CI. The template skips with `Set the environment variable BOOKER_USERNAME first`, so the reason is clear.

## Common mistakes

!!! warning "Common mistakes"
    - **A token pasted into a test file.** Once it's in git history, treat it as leaked: ask for it to be replaced.
    - **Only testing with a valid login.** The missing and wrong cases are the security tests.
    - **Printing the response to debug a login.** Login answers contain tokens. Print the status and the keys, not the values.

!!! failure "If you see this error"
    **`LookupError: Set the environment variable BOOKER_USERNAME first`**
    The template's `secret()` couldn't find the variable. Set it in the same terminal before running: `export BOOKER_USERNAME=admin BOOKER_PASSWORD=password123` (Restful-booker's public demo login).

## Try it yourself

Write a test that checks DummyJSON's `/auth/me` refuses a request with no `Authorization` header at all. What status do you expect?

??? success "Solution"
    ```python
    import requests

    def test_me_needs_a_login():
        response = requests.get("https://dummyjson.com/auth/me", timeout=15)
        assert response.status_code == 401
    ```

    401: there's no login at all. Run it and check. If an API answers 200 here, that's a serious bug.

## Quick check

1. Why should an API key go in a header, not the URL?

    ??? question "Answer"
        URLs end up in server logs, browser history and proxies. Headers usually don't.

2. What do you send to get an OAuth2 client credentials token?

    ??? question "Answer"
        A form with `grant_type=client_credentials`, and the client id and secret (usually as Basic auth), to the token URL.

3. Where do test secrets live?

    ??? question "Answer"
        In environment variables, filled from the CI tool's secret store. Never in code.

## References

- [MDN: HTTP authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication)
- [Requests: Authentication](https://requests.readthedocs.io/en/latest/user/authentication/)
- [Requests: Custom authentication](https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication)
- [RFC 6749: OAuth 2.0, client credentials grant](https://www.rfc-editor.org/rfc/rfc6749#section-4.4)
- [DummyJSON: Auth](https://dummyjson.com/docs/auth)
- [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
