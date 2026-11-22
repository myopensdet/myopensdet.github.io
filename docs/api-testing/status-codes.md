---
title: "Status Codes: What 200, 201, 404 and 500 Mean, and What APIs Get Wrong"
description: "The HTTP status code groups an API tester needs, the codes you'll see most, why requests doesn't raise on 4xx and 5xx, raise_for_status, and how to test and report wrong status codes."
level: Beginner
tags:
  - API
  - Bug reports
nav_title: "Status codes"
order: 30
summary: "What 200, 201, 404 and 500 mean, and how to test wrong ones."
updated: "2026-11-22"
---

# Status Codes: What 200, 201, 404 and 500 Mean, and What APIs Get Wrong

The **status code** is the first thing to check in every response. It's a three-digit number, and its first digit says the group: 2xx worked, 4xx the request was wrong, 5xx the server broke. Clients, browsers and monitoring all depend on these codes, so a wrong code is a real bug, even when the body looks fine.

!!! note "Before you start"
    Read [How HTTP works](how-http-works.md) first.

## What you will learn

- The five groups of status codes, and the codes you'll see most
- Why `requests` doesn't raise an error for 404 or 500, and how to make it
- What to test: the right code for each case, not just "not 500"
- How to report a wrong status code

## Why this matters at work

A mobile app decides what to show from the status code: "try again" for 503, "log in" for 401, "not found" for 404. If the API answers 200 with an error inside, or 500 for a missing field, the app shows the wrong thing. Testers are often the only ones who check.

## The idea in plain words

!!! info "In plain words"
    Status codes are like a delivery note. 2xx: "delivered". 4xx: "wrong address, your mistake". 5xx: "our van broke down, our mistake". If the note always says "delivered", nobody knows what really happened.

## Step by step

1. **Know the groups.**

    | Group | Means | You'll see |
    | --- | --- | --- |
    | 1xx | Still working | Rarely, in tests |
    | 2xx | It worked | 200 OK, 201 Created, 204 No Content |
    | 3xx | Look somewhere else | 301, 302, 304 (redirects and caching) |
    | 4xx | The request was wrong | 400, 401, 403, 404, 409, 422, 429 |
    | 5xx | The server failed | 500, 502, 503, 504 |

2. **See them from Python.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/status_codes.py"
    ```

    ```bash
    python status_codes.py
    ```

    ```text
    200 OK                     ok
    201 Created                ok
    204 No Content             ok
    400 Bad Request            not ok
    401 Unauthorized           not ok
    403 Forbidden              not ok
    404 Not Found              not ok
    500 Internal Server Error  not ok
    503 Service Unavailable    not ok
    HTTPError: 404 Client Error: Not Found for url: https://httpbin.org/status/404
    ```

3. **Know that `requests` doesn't raise for 4xx and 5xx.** A 404 is still a successful conversation, so `requests` gives you the response and lets you decide. That's what tests need: a test for "unknown id gives 404" must be able to see the 404. Use `raise_for_status()` in helper code where any error should stop everything, like logging in.

4. **Learn the 4xx codes that matter in tests.**

    | Code | Means | Test it with |
    | --- | --- | --- |
    | 400 Bad Request | The request is malformed or invalid | A missing field, a wrong type |
    | 401 Unauthorized | Not logged in, or the login is invalid | No token, an expired token |
    | 403 Forbidden | Logged in, but not allowed | Another user's booking |
    | 404 Not Found | It doesn't exist | An unknown id, a deleted booking |
    | 409 Conflict | It clashes with what's there | The same email twice |
    | 422 Unprocessable Content | Valid JSON, but the values break a rule | Checkout before checkin |
    | 429 Too Many Requests | Slow down | Many requests very fast |

    401 versus 403 is a common mix-up. 401 means "who are you?". 403 means "I know who you are, and no".

5. **Test for the exact code.** `assert response.status_code == 404` is a real check. `assert response.status_code != 500` isn't: it passes for 200, 403 and 418 too.

6. **Report wrong codes.** Restful-booker gets several wrong, on purpose, for practice:

    | Case | Restful-booker answers | Should be |
    | --- | --- | --- |
    | Create a booking | 200 | 201 Created |
    | Delete a booking | 201 Created | 204 No Content, or 200 |
    | Wrong password on `/auth` | 200 with `{"reason": "Bad credentials"}` | 401 |
    | A required field missing | 500 | 400, saying which field |

    In your tests, write what the API really does today, with a comment, or keep the right expectation in a test marked `xfail` with the bug's reason, like the template project does. Then file the bug. Never quietly change a test to match a wrong answer.

    !!! success "Check: you should now be able to"
        Name the status code groups, pick the right code for a case, and explain why `!= 500` isn't a test.

## When it goes wrong

- **Everything answers 200, even errors.** Some APIs put the error in the body. Check the body too, and report it. Clients can't rely on such an API.
- **You expect 404 but get 401.** Many APIs check the login before anything else. Send a valid login, then test for 404.
- **You get 301 or 302, and then a different page.** `requests` follows redirects by default. `response.history` shows them. Use `allow_redirects=False` to test the redirect itself.
- **You get 429.** You're sending too fast, often from a test loop. Slow down, or ask for a higher limit on the test environment.

## Common mistakes

!!! warning "Common mistakes"
    - **Only checking `response.ok`.** It's true for 200 and 204, which may not both be right.
    - **Mixing up 401 and 403.**
    - **Accepting 500 as "the API refused it".** A 500 is always a bug: the server failed.

!!! failure "If you see this error"
    **`requests.exceptions.HTTPError: 404 Client Error: Not Found for url: ...`**
    Something called `raise_for_status()` on a 404. In a test that expects 404, don't call it. Check `response.status_code` instead.

## Try it yourself

Write a test that checks a wrong password gets a 401 from Restful-booker's `/auth`. Run it. What happens, and what should you do next?

??? success "Solution"
    ```python
    import requests

    def test_wrong_password_is_401():
        response = requests.post(
            "https://restful-booker.herokuapp.com/auth",
            json={"username": "admin", "password": "wrong"},
            timeout=15,
        )
        assert response.status_code == 401
    ```

    It fails with `assert 200 == 401`. The test is right, and the API is wrong. Mark it `xfail` with the reason, and file a bug with the request and the response body `{"reason": "Bad credentials"}`.

## References

- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)
- [RFC 9110: Status codes](https://www.rfc-editor.org/rfc/rfc9110#name-status-codes)
- [Requests: Response status codes](https://requests.readthedocs.io/en/latest/user/quickstart/#response-status-codes)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
