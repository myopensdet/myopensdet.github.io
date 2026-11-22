---
title: "CRUD Tests for a Database: Create, Read, Update, Delete"
description: "Write pytest tests that create, read, update and delete rows, and check exactly what the database saved: every field, the defaults, the row count, and that nothing else changed."
level: Intermediate
tags:
  - Database
  - pytest
nav_title: "CRUD tests"
order: 60
summary: "Create, read, update and delete a row, and check exactly what was saved."
updated: "2026-11-22"
---

# CRUD Tests for a Database: Create, Read, Update, Delete

**CRUD** stands for the four things every app does with data: Create, Read, Update, Delete. In SQL they are `INSERT`, `SELECT`, `UPDATE` and `DELETE`. A CRUD test does one of them and then checks the result in the database, field by field. It sounds simple, and it's where many real bugs hide: a field not saved, an update that touched every row, a delete that did nothing.

!!! note "Before you start"
    Read [Connecting from Python](connecting-from-python.md). The tests use the template's `db` fixture, which undoes each test's changes ([Transactions and clean-up](transactions-and-cleanup.md)).

## What you will learn

- How to test each of the four operations
- How to get a new row's id back with `RETURNING`
- How to check an update changed only the row it should
- How to use the row count that `UPDATE` and `DELETE` return

## Why this matters at work

The most expensive data bugs are quiet. An `UPDATE` with a broken `WHERE` changes every customer's name, and nothing fails until someone looks. A CRUD test that checks "nothing else changed" catches that on the first run.

## The idea in plain words

!!! info "In plain words"
    Testing a save is like checking a parcel arrived: not only that the courier said "delivered", but that the box is there, with everything inside, at the right house, and that the neighbour didn't get it too.

## Step by step

1. **Create with a fixture, and get the id back.** `RETURNING id` makes the `INSERT` hand back the id the database made, so you don't have to search for the row:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_crud.py"
    ```

    The `customer_id` fixture creates a customer for each test that asks for it. The `db` fixture undoes it after the test.

2. **Create: check every field, and the defaults.** `test_create_saves_every_field` reads the row back and checks each field. It also checks `created_at`, which the test never sent: the database's default should fill it in.

3. **Read: check you get exactly one.** `test_read_finds_exactly_one` compares the whole list to `[{"id": customer_id}]`. That fails on zero rows and on two rows, where `rows[0]["id"] == customer_id` would miss the second.

4. **Update: check the row count, the new value, and that nothing else changed.** `test_update_changes_only_that_row` saves every other row before the update, and compares after. If someone breaks the `WHERE`, the last assert fails. `db.run` returns the row count from the database: an update of one customer must say 1.

5. **Delete: check it's gone.** And check the count is 1. A delete that matches nothing doesn't fail in SQL. It just says 0.

6. **The unknown id.** `test_update_of_unknown_id_changes_nothing` checks an update of an id that doesn't exist changes 0 rows. The app should then answer "not found", not "saved". Test that in the [API + database](api-and-database/index.md) topic.

7. **Run it.**

    ```bash
    python -m pytest tests/test_crud.py -v
    ```

    ```text
    tests/test_crud.py::test_create_saves_every_field PASSED                 [ 20%]
    tests/test_crud.py::test_read_finds_exactly_one PASSED                   [ 40%]
    tests/test_crud.py::test_update_changes_only_that_row PASSED             [ 60%]
    tests/test_crud.py::test_delete_removes_the_row PASSED                   [ 80%]
    tests/test_crud.py::test_update_of_unknown_id_changes_nothing PASSED     [100%]
    ```

    !!! success "Check: you should now be able to"
        Test all four operations, get a new id with `RETURNING`, and prove an update changed only its own row.

## When it goes wrong

- **The read-back finds nothing, but the insert said 1.** You read on a different connection, and the insert isn't committed yet. Each transaction only sees its own changes and committed ones. Read on the same connection, which the `db` fixture does.
- **`assert 0 == 1` on an update.** The `WHERE` matched no rows: wrong id, or the row was deleted by a fixture. Print the id and run the same `WHERE` as a `SELECT`.
- **Comparing a price fails: `Decimal('24.99') == 24.99` is `False`.** Money comes back as `Decimal`. Compare with `Decimal("24.99")`, or with `str(value) == "24.99"`. Never turn money into a `float`.
- **The `created_at` check fails by a few hours.** Time zones. The column is `timestamptz`, so Python gets a time with a zone. Compare times with times that also have a zone.

## Common mistakes

!!! warning "Common mistakes"
    - **Checking only the row count.** "1 row inserted" doesn't mean every field was saved right. Read the row back.
    - **Not checking the rest of the table on update.** The bug that changes every row is the worst one.
    - **Depending on a seed row that another test changes.** Each test makes its own row in a fixture.

!!! failure "If you see this error"
    **`TypeError: 'NoneType' object is not subscriptable`**
    `db.one(...)` returned `None` because no row matched, and the next line did `row["email"]`. Assert the row exists first: `assert row is not None`.

## Try it yourself

Write a test that creating a book with no `stock` saves it with stock 0, the column's default.

??? success "Solution"
    ```python
    def test_new_book_has_no_stock(db):
        book_id = db.value(
            "INSERT INTO books (title, price) VALUES (%s, %s) RETURNING id", ("New Book", 10)
        )
        assert db.value("SELECT stock FROM books WHERE id = %s", (book_id,)) == 0
    ```

## Quick check

1. What does `RETURNING id` give you?

    ??? question "Answer"
        The id the database made for the new row, straight from the `INSERT`.

2. An `UPDATE` with a wrong `WHERE` matches nothing. Does SQL raise an error?

    ??? question "Answer"
        No. It changes 0 rows and says so. Check the row count.

3. Why save the other rows before an update?

    ??? question "Answer"
        To prove the update changed only its own row.

## References

- [PostgreSQL: Returning data from modified rows](https://www.postgresql.org/docs/17/dml-returning.html)
- [PostgreSQL: Inserting, updating and deleting data](https://www.postgresql.org/docs/17/dml.html)
- [psycopg 3: Adapting numbers (Decimal)](https://www.psycopg.org/psycopg3/docs/basic/adapt.html#numbers-adaptation)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
