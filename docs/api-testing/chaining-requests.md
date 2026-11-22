---
title: "Chaining Requests: Log In, Create, Use the Id, Clean Up"
description: "Pass values from one API response to the next request: a login token, a new id. Build the chain with pytest fixtures so every test makes its own data and deletes it afterwards, even when it fails."
level: Intermediate
tags:
  - API
  - pytest
  - Test data
nav_title: "Chaining requests"
order: 80
summary: "Pass a token and an id from one call to the next, with fixtures that clean up."
updated: "2026-11-22"
---

# Chaining Requests: Log In, Create, Use the Id, Clean Up

Real API tests are chains. Log in, keep the token. Create a booking, keep its id. Use both in the next request. Then delete what you made. Done badly, chains turn into one long test where step 3 fails because step 1 did. Done with **pytest fixtures**, each test gets fresh data, and the clean-up runs even when the test fails.

!!! note "Before you start"
    Read [Fixtures and conftest.py](../automation-testing/pytest/fixtures-and-conftest.md) and [Authentication](authentication.md) first.

## What you will learn

- How to pass a value from one response to the next request
- How to build the chain from fixtures, with the right scope
- How to clean up with `yield`, even after a failure
- Why tests mustn't depend on each other's data

## Why this matters at work

Shared test environments fill up with junk data, and tests fail because "booking 1" was changed by someone else's run. Tests that make their own data and delete it are faster to debug, can run in any order, and can run at the same time.

## The idea in plain words

!!! info "In plain words"
    Like borrowing a meeting room: book it, use it, give the key back. Each test books its own room, and the clean-up gives the key back, even if the meeting went badly.

## Step by step

1. **Pass values by hand first.** The [methods tour](http-methods.md) does it: `token = ...json()["token"]`, then `booking_id = ...json()["bookingid"]`, then both go in the next request. Fine for a script. In a test suite, every test would repeat it.

2. **Turn each link into a fixture.** The template's `tests/conftest.py`:

    ```python
    --8<-- "modules/core_automation/api_testing/templates/booker_api_tests/tests/conftest.py"
    ```

    The chain is `client` → `token` → `auth` → `new_booking`. Each fixture asks for the one before it by naming it as an argument. pytest works out the order.

3. **Pick the scope for each link.**

    - `client`, `token` and `auth` are `scope="session"`: one login for the whole run. Logging in for every test is slow, and some APIs block you for it.
    - `new_booking` has the default scope, one per test, so every test gets a fresh booking nobody else touched.

4. **Clean up after `yield`.** Everything after `yield booking_id, data` runs when the test ends, passed or failed. So the booking is deleted either way. The fixture also gives the test the data it sent, so the test can compare.

5. **Use the chain in a test.** The test just names what it needs:

    ```python
    --8<-- "modules/core_automation/api_testing/templates/booker_api_tests/tests/test_patch_booking.py"
    ```

    Three lines of real test. The login, the create and the clean-up are all in fixtures.

6. **Run the suite.**

    ```bash
    export BOOKER_USERNAME=admin BOOKER_PASSWORD=password123
    python -m pytest -v
    ```

    ```text
    tests/test_auth.py::test_login_gives_a_token PASSED                      [  8%]
    tests/test_auth.py::test_wrong_password_is_refused PASSED                [ 16%]
    tests/test_delete_booking.py::test_delete_removes_the_booking PASSED     [ 25%]
    tests/test_delete_booking.py::test_delete_without_login_is_refused PASSED [ 33%]
    tests/test_get_booking.py::test_get_returns_the_saved_booking PASSED     [ 41%]
    tests/test_get_booking.py::test_get_unknown_booking_is_404 PASSED        [ 50%]
    tests/test_get_booking.py::test_response_is_json PASSED                  [ 58%]
    tests/test_patch_booking.py::test_patch_changes_only_what_was_sent PASSED [ 66%]
    tests/test_post_booking.py::test_create_booking PASSED                   [ 75%]
    tests/test_post_booking.py::test_missing_field_is_a_client_error XFAIL   [ 83%]
    tests/test_put_booking.py::test_put_replaces_the_booking PASSED          [ 91%]
    tests/test_put_booking.py::test_put_without_login_is_refused PASSED      [100%]

    =========================== short test summary info ============================
    XFAIL tests/test_post_booking.py::test_missing_field_is_a_client_error - Restful-booker answers 500 for a missing field; it should be 400
    ======================== 11 passed, 1 xfailed in 6.03s =========================
    ```

    Without the login variables, the `token` fixture skips every test that needs it, with the reason:

    ```text
    SKIPPED [1] tests/test_auth.py:8: Set the environment variable BOOKER_USERNAME first
    ```

7. **Don't chain tests to each other.** "Test 1 creates, test 2 updates, test 3 deletes" breaks when test 1 fails, when you run test 2 alone, and when tests run in parallel. Chain requests *inside* a test, through fixtures. Never between tests.

    !!! success "Check: you should now be able to"
        Pass a token and an id from response to request, build the chain as fixtures with the right scopes, and clean up with `yield`.

## When it goes wrong

- **Junk data piles up.** A test deletes in its last line, so a failure skips the delete. Move the delete after `yield` in a fixture.
- **Tests pass alone and fail together.** They share data. Give each test its own, from a function-scoped fixture.
- **Every test fails with 401 halfway through a long run.** The session token expired. Ask how long tokens last. Log in again in the fixture when you get a 401, or ask for a longer-lived test token.
- **The clean-up itself fails.** The fixture's error shows as an `ERROR at teardown`, after the test result. Read it. Often the token was missing, so the delete got a 403.

## Common mistakes

!!! warning "Common mistakes"
    - **Logging in for every test.** Use `scope="session"` for the token.
    - **Sharing one booking between tests.** Use a function-scoped fixture.
    - **Tests that need to run in order.** Each test must work alone.

!!! failure "If you see this error"
    **`ScopeMismatch: You tried to access the function scoped fixture new_booking with a session scoped request object`**
    A session-scoped fixture asked for a function-scoped one. The longer-lived fixture can't depend on the shorter-lived one. Give the asking fixture the shorter scope, or move the shared part up.

## Try it yourself

Write a fixture `booking_without_breakfast` that builds on `new_booking`: it PATCHes the booking to `additionalneeds = ""`, then yields the id. Does it need its own clean-up?

??? success "Solution"
    ```python
    @pytest.fixture
    def booking_without_breakfast(client, auth, new_booking):
        booking_id, data = new_booking
        check_status(client.patch(f"/booking/{booking_id}", json={"additionalneeds": ""}, headers=auth), 200)
        yield booking_id
    ```

    No own clean-up: it uses `new_booking`, and `new_booking` deletes the booking after the test. Each fixture cleans up only what it made.

## References

- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest: Teardown with yield fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#yield-fixtures-recommended)
- [pytest: Fixture scopes](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session)

Written for Python 3.13, pytest 9.2 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
