---
title: "Database Schema Tests: Check Tables and Columns With pytest"
description: "Test that a database has the tables, columns, types and keys the app expects, by reading information_schema from pytest. Catch a migration that dropped NOT NULL before it reaches production."
level: Intermediate
tags:
  - Database
  - pytest
nav_title: "Schema tests"
order: 40
summary: "Check the tables, columns, types and keys match what the app expects."
updated: "2026-11-22"
---

# Database Schema Tests: Check Tables and Columns With pytest

The **schema** is the shape of the database: which tables exist, which columns they have, of which type, and which may be empty. The app's code is written for one shape. When a migration changes it by mistake, say a column becomes nullable or a type changes, the app breaks later, in a place far from the cause. A schema test catches it on the day of the change.

!!! note "Before you start"
    Read [Connecting from Python](connecting-from-python.md). The tests here use the template's `db` fixture.

## What you will learn

- Where a database describes itself: `information_schema`
- How to write the expected shape as a Python dict
- How to test columns, types, `NOT NULL`, `UNIQUE` and foreign keys
- What a failing schema test tells you

## Why this matters at work

Migrations are code, and code has bugs. Common ones: a new column left nullable when it shouldn't be, a `numeric` money column changed to `real`, a foreign key forgotten. None of them break anything on the day. They break the reports a month later. Schema tests run in seconds and point straight at the problem.

## The idea in plain words

!!! info "In plain words"
    A schema test is a checklist for the building, not the furniture. Before anyone moves in, you check every room is there, every door is where the plan says, and the fire exits aren't locked.

## Step by step

1. **Ask the database about itself.** Every SQL database has `information_schema`, a set of read-only tables that describe the other tables. The columns of `customers`:

    ```sql
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = current_schema() AND table_name = 'customers'
    ORDER BY ordinal_position;
    ```

    The template's `DbClient.columns(table)` runs exactly that and returns a dict: column name to type and "may be empty".

2. **Write down what the app expects.** Copy it from the migration or the data model, not from the database. Copying from the database would only prove the database matches itself. In the template's `tests/test_schema.py`:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_schema.py"
    ```

    One test per table, through `parametrize`, so a failure names the table. The other two tests read the keys: `email` must be `UNIQUE`, and `orders.customer_id` must point at `customers.id`.

3. **Run it.**

    ```bash
    python -m pytest tests/test_schema.py -v
    ```

    ```text
    tests/test_schema.py::test_table_has_the_expected_columns[customers] PASSED [ 16%]
    tests/test_schema.py::test_table_has_the_expected_columns[books] PASSED  [ 33%]
    tests/test_schema.py::test_table_has_the_expected_columns[orders] PASSED [ 50%]
    tests/test_schema.py::test_table_has_the_expected_columns[order_items] PASSED [ 66%]
    tests/test_schema.py::test_email_is_unique PASSED                        [ 83%]
    tests/test_schema.py::test_orders_point_at_customers PASSED              [100%]
    ```

4. **See it catch a real mistake.** Suppose a migration changed `full_name text NOT NULL` to `full_name text`. The app still works, until a customer is saved with no name and the invoice breaks. The schema test fails at once:

    ```text
    >       assert actual == EXPECTED[table]
    E       AssertionError: assert {'id': ('inte...zone', False)} == {'id': ('inte...zone', False)}
    E
    E         Omitting 3 identical items, use -vv to show
    E         Differing items:
    E         {'full_name': ('text', True)} != {'full_name': ('text', False)}
    E         Use -v to get more diff

    tests/test_schema.py:41: AssertionError
    ...
    FAILED tests/test_schema.py::test_table_has_the_expected_columns[customers]
    ```

    Read the "Differing items" line: the left side is the database, the right side is what you expected. `full_name` may now be empty (`True`), and it shouldn't (`False`).

5. **Decide what else is worth checking.** Columns and types catch most mistakes. Add checks for keys and rules the app depends on: unique emails, foreign keys, and indexes on columns the app searches by, if your team cares about speed. Don't check everything that exists. Check what would hurt if it changed.

    !!! success "Check: you should now be able to"
        Read a table's columns from `information_schema`, write the expected shape, and read a failing schema test.

## When it goes wrong

- **The test finds no columns at all.** The table is in a different schema (a namespace inside the database). `current_schema()` is usually `public`. Check with `SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'customers';`.
- **The type reads `character varying`, not `varchar`.** `information_schema` uses the long, standard names: `character varying`, `timestamp with time zone`, `numeric`. Write those in `EXPECTED`.
- **The test fails after every migration.** Good, that's its job. Check the change was meant, and update `EXPECTED` in the same pull request as the migration, so the reviewer sees both.

## Common mistakes

!!! warning "Common mistakes"
    - **Generating `EXPECTED` from the database.** Then the test can never fail. Write it from the migration or the data model.
    - **Checking only that a table exists.** A table with the wrong columns still exists.
    - **One big test for all tables.** The first difference hides the rest. One test per table.

!!! failure "If you see this error"
    ```text
    E       AssertionError: assert {} == {'id': ('inte...zone', False)}
    E
    E         Right contains 4 more items:
    ```

    The left side is empty: the query found no columns. The table name is spelled differently, or it's in another schema. See the first item in "When it goes wrong".

## Try it yourself

Add `order_status_history` to `EXPECTED`. Look at the `CREATE TABLE` in `sql/schema.sql` and write what the app needs, then run the test.

??? success "Solution"
    ```python
    "order_status_history": {
        "id": ("integer", False),
        "order_id": ("integer", False),
        "old_status": ("text", True),
        "new_status": ("text", False),
        "changed_at": ("timestamp with time zone", False),
    },
    ```

    `old_status` may be empty (`True`): the column has no `NOT NULL` in `sql/schema.sql`.

## References

- [PostgreSQL: The information schema](https://www.postgresql.org/docs/17/information-schema.html)
- [PostgreSQL: information_schema.columns](https://www.postgresql.org/docs/17/infoschema-columns.html)
- [pytest: Parametrizing tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
