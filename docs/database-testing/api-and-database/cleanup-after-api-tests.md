---
title: "Clean Up After API Tests: Rows the App Saved"
description: "Rollback can't undo rows an API saved through its own connection. Track every row a test makes, delete them newest first, use unique test data, and wait for the app to finish before cleaning up."
level: Intermediate
tags:
  - API
  - Database
  - pytest
nav_title: "Cleanup after API tests"
order: 40
summary: "Rollback can't undo what the app saved. Track it and delete it."
updated: "2026-11-22"
---

# Clean Up After API Tests: Rows the App Saved

In [Database testing](../transactions-and-cleanup.md), every test ran inside a transaction that was rolled back at the end. That trick stops working the moment an API is involved: **the app saves through its own connection, and your rollback can't reach it.** This lesson shows the proof, and the cleanup that works instead.

!!! note "Before you start"
    Read [seed then call](seed-then-call.md) and [transactions and cleanup](../transactions-and-cleanup.md).

## What you will learn

- Why rollback doesn't undo an API's writes
- A cleanup tracker that deletes every row a test made, newest first
- Unique test data that never clashes
- Why cleanup must wait until the app has finished

## Why this matters at work

A shared test environment fills up with "test1@example.com" rows from every test run. Then a test fails because the email is "already taken", someone deletes data by hand, and a colleague's test data disappears with it. Tests that clean up after themselves stop all of this.

## The idea in plain words

!!! info "In plain words"
    You borrow a friend's kitchen. You can't "undo" the cooking, but you can wash every dish you used, in the right order: pans before you put the stove cover back. The tracker is your list of dishes.

## Step by step

1. **See that rollback doesn't work.** Open a transaction on the test's connection, make a customer through the API, then roll back:

    ```python
    with db.conn.transaction(force_rollback=True):
        r = api.post("/customers", json={"email": "rollback.demo@example.com", "full_name": "Rollback Demo"})
        print("API answered", r.status_code, r.json())
    print("after rollback:", db.one("SELECT id, email FROM customers WHERE email = %s", ("rollback.demo@example.com",)))
    ```

    ```text
    API answered 201 {'id': 114, 'email': 'rollback.demo@example.com', 'full_name': 'Rollback Demo'}
    after rollback: {'id': 114, 'email': 'rollback.demo@example.com'}
    ```

    The row is still there. The app committed it on its own connection. Your rollback only covers what *your* connection did.

2. **Track every row, and delete newest first.** The `Cleanup` class in `helpers/clients.py`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/helpers/clients.py:95:118"
    ```

    Every fixture that makes a row calls `cleanup.add(table, id)`. After the test, pass or fail, the rows are deleted in reverse order: the order first, then the book and customer it points at. Deleting the customer first would break the foreign key. A failed delete doesn't stop the others. It's reported at the end, with the rows left behind.

3. **Make test data unique.** The `unique` fixture gives every test a random tag: `test.2eabb6ea@example.com`, `Test Book 2eabb6ea`. Two people can run the suite at the same time on the same database, and nothing clashes.

4. **Wait for the app to finish before cleaning up.** The practice API writes an `order_created` event half a second *after* it answers. The first version of the template deleted the order before that. The tests passed, and the app's log filled with this:

    ```text
    ERROR:    Exception in ASGI application
    ...
    psycopg.errors.ForeignKeyViolation: insert or update on table "order_events" violates foreign key constraint "order_events_order_id_fkey"
    DETAIL:  Key (order_id)=(8) is not present in table "orders".
    ```

    Green tests, red app logs. In a shared environment, that's an alert for someone else. The `place_order` fixture in `tests/conftest.py` fixes it: after placing an order, it waits until the event row is there, so cleanup only starts when the app has finished.

5. **Check nothing was left behind.** After the full run:

    ```sql
    SELECT (SELECT count(*) FROM customers) customers,
           (SELECT count(*) FROM books WHERE title LIKE 'Test Book%') test_books,
           (SELECT count(*) FROM orders) orders;
    ```

    ```text
     customers | test_books | orders
    -----------+------------+--------
             0 |          0 |      0
    ```

    !!! success "Check: you should now be able to"
        Explain why rollback doesn't clean up API writes, and track and delete every row a test makes, after the app has finished with it.

## When it goes wrong

- **`AssertionError: Clean-up failed, rows left behind:`.** A row couldn't be deleted. Most often another table points at it, and the test made that row without `cleanup.add`. Add it.
- **The app's log shows errors, and every test passed.** Cleanup is racing the app's background work. Wait for it to finish first, as `place_order` does.
- **Rows left behind after a run was killed.** The pipeline stopped it, or the computer went to sleep, so teardown never ran. Use the unique tag to find and delete them: `WHERE email LIKE 'test.%@example.com'`.

## Common mistakes

!!! warning "Common mistakes"
    - **Cleaning up at the start of the next run.** Rows stay for hours, and you may delete a colleague's data.
    - **`DELETE FROM customers` with no `WHERE`.** On a shared database, that deletes everyone's data. Delete by the ids you tracked.
    - **Cleanup inside the test body.** A failed assert skips it. Fixtures run their teardown even when the test fails.

!!! failure "If you see this error"
    **`psycopg.errors.ForeignKeyViolation: update or delete on table "customers" violates foreign key constraint "orders_customer_id_fkey" on table "orders"`**
    You're deleting a row while another row still points at it. Delete newest first, and make sure every row the test made is tracked.

## Try it yourself

`DELETE /orders/{id}` removes an order. A test that deletes its own order through the API leaves an id in the tracker that no longer exists. Is that a problem for `Cleanup`?

??? success "Solution"
    No. `DELETE ... WHERE id = %s` on a missing row deletes nothing and raises no error. The template's `test_delete_through_the_api_removes_the_row` does exactly this, and passes.

## References

- [pytest: Teardown and cleanup with yield fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#teardown-cleanup-aka-fixture-finalization)
- [psycopg 3: Transactions management](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
