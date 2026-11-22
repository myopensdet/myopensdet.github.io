---
title: "Clean Up Database Tests With Transactions and Rollback"
description: "Make database tests leave nothing behind: run every test inside a transaction that is always rolled back, use savepoints for queries that should fail, and see what goes wrong without it."
level: Intermediate
tags:
  - Database
  - pytest
  - Test data
nav_title: "Transactions and clean-up"
order: 90
summary: "Roll back every test, so the database is the same after the run as before."
updated: "2026-11-22"
---

# Clean Up Database Tests With Transactions and Rollback

A database test changes data. If it doesn't undo the change, the next run finds it there, and fails, or worse, passes for the wrong reason. Deleting rows by hand at the end of a test breaks the moment the test fails halfway. The reliable way is a **transaction** that is always rolled back: the test does whatever it likes, and at the end the database forgets all of it.

!!! note "Before you start"
    Read [Fixtures and conftest.py](../automation-testing/pytest/fixtures-and-conftest.md) and [CRUD tests](crud-tests.md).

## What you will learn

- What a transaction, a commit and a rollback are
- What goes wrong when tests leave data behind
- How the template rolls back every test with two fixtures
- What a savepoint is, and why tests that expect an error need one

## Why this matters at work

Leftover test data is behind many "flaky" database tests: the test passes on a fresh database and fails on the second run, or passes alone and fails in the full suite. Rollback clean-up also makes tests fast: no deleting, no re-seeding between tests.

## The idea in plain words

!!! info "In plain words"
    A transaction is writing in pencil. Commit goes over it in pen. Rollback rubs out everything since you picked up the pencil. Each test writes in pencil, and the fixture always rubs it out at the end.

## Step by step

1. **See a rollback by hand.** Delete every order item, look, then roll back:

    ```sql
    BEGIN;
    DELETE FROM order_items;
    SELECT COUNT(*) FROM order_items;
    ROLLBACK;
    SELECT COUNT(*) FROM order_items;
    ```

    ```text
    BEGIN
    DELETE 6
     count
    -------
         0
    (1 row)

    ROLLBACK
     count
    -------
         6
    (1 row)
    ```

    Inside the transaction, the rows were gone. After `ROLLBACK`, all 6 are back. Other connections never saw them disappear.

2. **See what goes wrong without it.** A test that saves a customer for real, with `autocommit=True`:

    ```python
    def test_new_customer_is_saved():
        with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
            conn.execute(
                "INSERT INTO customers (email, full_name) VALUES (%s, %s)",
                ("signup.test@example.com", "Signup Test"),
            )
            count = conn.execute(
                "SELECT COUNT(*) FROM customers WHERE email = %s", ("signup.test@example.com",)
            ).fetchone()[0]
        assert count == 1
    ```

    The first run passes. The second run:

    ```text
    E           psycopg.errors.UniqueViolation: duplicate key value violates unique constraint "customers_email_key"
    E           DETAIL:  Key (email)=(signup.test@example.com) already exists.
    1 failed in 0.11s
    ```

    The customer from the first run is still there. Nothing in the test is wrong. Its data is.

3. **Roll back every test with two fixtures.** The template's `tests/conftest.py`:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/conftest.py"
    ```

    - `connection` (one per run) opens a transaction with `force_rollback=True`: it rolls back at the end even if everything passed. Inside it, the demo tables and seed data are made in their own schema, `shop_test`. When the run ends, they're gone.
    - `db` (one per test) opens a **savepoint** inside that transaction, also with `force_rollback=True`. A savepoint is a transaction inside a transaction. Each test's changes are rubbed out when it ends, and the next test sees the seed data exactly as it was.

    So every test sees the same starting data, in any order, and the database is the same after the run as before. Even a crash leaves nothing: PostgreSQL rolls back an unfinished transaction when the connection drops.

4. **Use a savepoint for a query you expect to fail.** After an error, PostgreSQL refuses every later query in the transaction until a rollback, with `current transaction is aborted, commands ignored until end of transaction block`. `db.savepoint()` wraps just the failing query, so only that part is undone:

    ```python
    def test_email_is_required(db):
        with pytest.raises(errors.NotNullViolation), db.savepoint():
            db.run(GOOD_CUSTOMER, (None, "No Email"))
    ```

5. **Know where rollback doesn't reach.** Rollback only undoes what this connection did in this transaction. It can't undo:

    - what the app did through its own connection. When an API call saves an order, the app commits it. Clean that up through the API, or a fixture that deletes it ([API + database](api-and-database/index.md)).
    - emails sent, files written, or messages put on a queue.
    - sequences: a rolled-back insert still uses up an id. Never expect "the next id is 6".

    !!! success "Check: you should now be able to"
        Explain commit and rollback, roll back every test with fixtures, and wrap an expected error in a savepoint.

## When it goes wrong

- **Tests pass alone and fail together.** One test commits, or uses a connection that isn't inside the rolled-back transaction. Every query must go through the `db` fixture.
- **`current transaction is aborted`.** A query failed outside a savepoint. Find the first error above it, and wrap the query that's expected to fail in `db.savepoint()`.
- **The test hangs.** Another connection is waiting for a row your test has locked, or the other way round. Often it's the app, waiting for the test's uncommitted row. When the app has to see test data, use committed data and clean it up with a fixture.
- **A test checks an id and fails on the second run.** Rolled-back inserts still use up ids. Read ids back with `RETURNING`.

## Common mistakes

!!! warning "Common mistakes"
    - **Deleting test data in the last line of the test.** A failure skips it. Use rollback, or delete after `yield` in a fixture.
    - **Calling `conn.commit()` inside a test.** It writes for real, and rollback can't undo it.
    - **Running tests against a shared database with real data.** Rollback protects you, but one test that commits doesn't. Use a database only for tests.

!!! failure "If you see this error"
    **`psycopg.errors.UniqueViolation: duplicate key value violates unique constraint "customers_email_key"`** on the second run only.
    The first run left its row behind. Delete the row once by hand, then move the test onto the rolled-back `db` fixture so it can't happen again.

## Try it yourself

Without running it: if a test using `db` creates a customer and then fails on an assert, is the customer still in the database after the run?

??? success "Solution"
    No. The `db` fixture's savepoint is rolled back when the test ends, passed or failed. At the end of the run, the `connection` fixture's transaction is rolled back too.

## References

- [PostgreSQL tutorial: Transactions](https://www.postgresql.org/docs/17/tutorial-transactions.html)
- [PostgreSQL: SAVEPOINT](https://www.postgresql.org/docs/17/sql-savepoint.html)
- [psycopg 3: Transactions management](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)
- [pytest: Teardown with yield fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#yield-fixtures-recommended)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
