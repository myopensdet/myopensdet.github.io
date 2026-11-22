---
title: "Verify an API Write in the Database With pytest"
description: "Call the API with requests, then read the saved row with psycopg and check every value that matters. Includes the API and database helpers, the fixtures, and how to mark a known bug with a strict xfail."
level: Intermediate
tags:
  - API
  - Database
  - pytest
nav_title: "Verify an API write"
order: 20
summary: "Call the API, then read the row and check each value."
updated: "2026-11-22"
---

# Verify an API Write in the Database With pytest

This is the core pattern of the topic: **call the API, read the row, check the values.** It needs two helpers, one for the API and one for the database, and a few fixtures that hand them to each test.

!!! note "Before you start"
    Read [why check the database](why-check-the-database.md). Have the practice API running and the [template project](index.md#templates) open.

## What you will learn

- A small API helper and a small database helper
- How the test reads the database the app writes to
- How to check one write completely: values, side effects, and a refused request
- How to mark a known bug so the run stays green, and turns red when it's fixed

## Why this matters at work

The pattern is the same for every write your API does: create, update, delete, cancel. Get one test right, and the rest are copies with different values.

## The idea in plain words

!!! info "In plain words"
    Two windows open side by side: the app on the left, the database on the right. Click "Order" on the left, then look on the right. The test does exactly that, in code.

## Step by step

1. **Read the helpers.** `helpers/clients.py`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/helpers/clients.py"
    ```

    - `Api` wraps `requests` with a base URL, a timeout and one log line per call. pytest shows those lines when a test fails.
    - `Db` uses **autocommit**. The app and the test use different connections, and each can only see what the other has committed. The test's own inserts must be committed for the app to see them.
    - `setting()` reads `API_URL` and `DATABASE_URL` from the environment. No address or password is written in a file.

2. **Read the fixtures.** `tests/conftest.py` gives each test `api`, `db`, a `customer` made through the API, a `book` put straight into the database, and `place_order`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/conftest.py"
    ```

    `cleanup` and `place_order` are explained in [cleanup after API tests](cleanup-after-api-tests.md).

3. **Check one write completely.** `tests/test_create_order.py`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_create_order.py"
    ```

    - `test_order_is_saved_as_the_api_said`: every column, and the total as a `Decimal`. Money in the database is exact. Comparing it with a float hides rounding bugs.
    - `test_order_takes_the_stock`: the side effect.
    - `test_refused_order_changes_nothing`: a refused request (quantity 11, the API allows 10) must leave no order and no stock change behind.
    - `test_price_comes_from_the_database_not_the_client`: the planted bug, compared with the book's real price.

4. **Run it.**

    ```bash
    python -m pytest tests/test_create_order.py -v
    ```

    ```text
    tests/test_create_order.py::test_order_is_saved_as_the_api_said PASSED   [ 25%]
    tests/test_create_order.py::test_order_takes_the_stock PASSED            [ 50%]
    tests/test_create_order.py::test_refused_order_changes_nothing PASSED    [ 75%]
    tests/test_create_order.py::test_price_comes_from_the_database_not_the_client XFAIL [100%]
    XFAIL tests/test_create_order.py::test_price_comes_from_the_database_not_the_client - Practice API bug: a price sent by the client is saved
    ========================= 3 passed, 1 xfailed in 1.99s =========================
    ```

5. **See the bug the xfail is holding.** `--runxfail` runs it as a normal test:

    ```bash
    python -m pytest tests/test_create_order.py -k price --runxfail
    ```

    ```text
    >       assert saved == book["price"]
    E       AssertionError: assert Decimal('0.01') == Decimal('24.99')

    tests/test_create_order.py:53: AssertionError
    ------------------------------ Captured log setup ------------------------------
    INFO     api_db:clients.py:34 POST /customers -> 201
    ------------------------------ Captured log call -------------------------------
    INFO     api_db:clients.py:34 POST /orders -> 201
    ```

    The failure says what was saved and what should have been. That line goes straight into the bug report.

    !!! success "Check: you should now be able to"
        Write a test that calls the API, reads the saved row, and checks its values, its side effects, and what a refused request leaves behind.

## When it goes wrong

- **The row is there in `psql`, but the test gets `None`.** The test is reading another database. Print `DATABASE_URL` and compare it with the app's.
- **Your test inserts a row, and the app answers 404 for it.** The insert wasn't committed. `Db` uses autocommit for this reason.
- **An xfail test shows XFAIL, but for the wrong reason.** While writing this page, a test called a helper with names that no longer existed. It raised `NameError: name 'api' is not defined`, and pytest still showed XFAIL, because a plain xfail accepts any error. `raises=AssertionError` fixes that: only a failed check counts as the expected failure.

## Common mistakes

!!! warning "Common mistakes"
    - **`assert saved["total"] == 49.98`.** That compares a `Decimal` with a float. Use `Decimal("49.98")`.
    - **An xfail without `strict=True`.** When the developers fix the bug, the test passes quietly and nobody removes the mark. Strict turns that into a failure you see.
    - **An xfail without `raises=`.** A typo in the test hides behind the known bug.

!!! failure "If you see this error"
    **`[XPASS(strict)] Practice API bug: a price sent by the client is saved`**
    The bug is fixed. Remove the `xfail` mark: the test is now a normal test that keeps the bug from coming back.

## Try it yourself

Add a test: an order for a book that doesn't exist (`book_id` 999999999) must answer 404 and leave the number of orders unchanged.

??? success "Solution"
    ```python
    def test_unknown_book_changes_nothing(api, db, customer):
        before = db.value("SELECT COUNT(*) FROM orders")
        response = api.post(
            "/orders", json={"customer_id": customer["id"], "book_id": 999999999, "quantity": 1}
        )
        assert response.status_code == 404
        assert db.value("SELECT COUNT(*) FROM orders") == before
    ```

## References

- [requests: Advanced usage (sessions, timeouts)](https://requests.readthedocs.io/en/latest/user/advanced/)
- [psycopg 3: Transactions management](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)
- [pytest: Skip and xfail](https://docs.pytest.org/en/stable/how-to/skipping.html)

Written for Python 3.13, pytest 9.2, requests 2.34, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
