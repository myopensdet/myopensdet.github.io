---
title: "Seed the Database, Then Call the API"
description: "Put test data straight into the database, then check the API reads, shows and changes it correctly. Faster than building everything through the API, and it reaches states the API can't make."
level: Intermediate
tags:
  - API
  - Database
  - pytest
nav_title: "Seed then call"
order: 30
summary: "Put the data in the database, then check what the API does with it."
updated: "2026-11-22"
---

# Seed the Database, Then Call the API

The last lesson went API first, database second. This one goes the other way: **put the data in the database, then call the API.** It's how you test reading, showing and deleting, and how you set up states the API has no button for.

!!! note "Before you start"
    Read [verify an API write](verify-an-api-write.md). The fixtures from there are used here.

## What you will learn

- When to seed through the database, and when through the API
- How to seed a state the API can't make on its own
- How to check a `GET` and a `DELETE` against the rows

## Why this matters at work

Tests that build everything through the API are slow, and they break when an unrelated endpoint breaks. Some states can't be reached at all: a shipped order, a customer from five years ago, a book with no stock. Seeding puts the world in place in one line.

## The idea in plain words

!!! info "In plain words"
    To test a library's "return a book" desk, you don't borrow a book first through the front desk. You put a borrowed book on someone's record, then walk to the return desk.

## Step by step

1. **Choose how to seed each thing.**

    | Seed through | When | Example in the template |
    | --- | --- | --- |
    | The API | the thing a user would make, and its rules matter | `customer` fixture |
    | The database | setup data, admin-only data, or a state the API can't reach | `book` fixture, `order_in_db` |

2. **Seed a state the API can't make.** The practice API makes every order with status `new`. To test that `GET` shows any status, seed a `shipped` order. `tests/test_seed_then_call.py`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_seed_then_call.py"
    ```

    - `test_api_shows_what_the_database_holds`: `shipped` can only come from the row, so the API must be reading it, not making it up.
    - `test_delete_through_the_api_removes_the_row`: the row is gone, and the book's stock went back up by one.
    - `test_unknown_order_is_404`: no seeding needed. An id that can't exist.

3. **Run it.**

    ```bash
    python -m pytest tests/test_seed_then_call.py -v
    ```

    ```text
    tests/test_seed_then_call.py::test_api_shows_what_the_database_holds PASSED [ 33%]
    tests/test_seed_then_call.py::test_delete_through_the_api_removes_the_row PASSED [ 66%]
    tests/test_seed_then_call.py::test_unknown_order_is_404 PASSED           [100%]
    ============================== 3 passed in 0.07s ===============================
    ```

4. **Keep seeded data real.** Seeding skips the API's checks, so nothing stops you inserting an order with a negative total, or a total that doesn't match price times quantity. The app was never built to show that, and a failure would tell you nothing. Seed only what the app could really have made.

    !!! success "Check: you should now be able to"
        Seed a row straight into the database, call the API, and check it reads or changes that row correctly.

## When it goes wrong

- **The insert fails with a foreign key error.** Seed in order: customer and book first, then the order that points at them.
- **`GET` shows a different value from your seed.** Good: that's a finding. Check whether the API rounds, formats or caches it before you report it.
- **The insert fails on a column you didn't know about.** The database has changed. Read the table with `\d orders` in `psql`, and update the fixture.

## Common mistakes

!!! warning "Common mistakes"
    - **Seeding through the database what a user would make.** You skip the very rules you need to test.
    - **Fixed ids like `id = 1`.** Another test, or another person, uses the same id. Let the database pick the id, and use `RETURNING id`.
    - **Seeding data that can't exist.** A failure on impossible data isn't a bug in the app.

!!! failure "If you see this error"
    **`psycopg.errors.ForeignKeyViolation: insert or update on table "orders" violates foreign key constraint "orders_customer_id_fkey"`**
    `DETAIL:  Key (customer_id)=(999999999) is not present in table "customers".` The customer or book id in your insert doesn't exist. Make it with its fixture first, and pass the real id.

## Try it yourself

Seed a customer straight into the database, then check `GET /customers/{id}` returns the same email and name.

??? success "Solution"
    ```python
    def test_api_shows_a_seeded_customer(api, db, cleanup, unique):
        row = db.one(
            "INSERT INTO customers (email, full_name) VALUES (%s, %s) RETURNING id",
            (f"seed.{unique}@example.com", "Seeded Customer"),
        )
        cleanup.add("customers", row["id"])

        body = api.get(f"/customers/{row['id']}").json()
        assert body == {
            "id": row["id"],
            "email": f"seed.{unique}@example.com",
            "full_name": "Seeded Customer",
        }
    ```

## References

- [PostgreSQL: Returning data from modified rows](https://www.postgresql.org/docs/17/dml-returning.html)
- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
