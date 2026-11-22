---
title: "Run One pytest Test on Every Database With Parametrized Fixtures"
description: "Write each database test once and run it on PostgreSQL, MySQL, SQLite and MongoDB, with a parametrized pytest fixture. Ask the same question in each database's own query language."
level: Intermediate
tags:
  - Database
  - pytest
nav_title: "One test on every database"
order: 50
summary: "Write a test once, and pytest runs it on all four databases."
updated: "2026-11-22"
---

# Run One pytest Test on Every Database With Parametrized Fixtures

You've seen [`pytest.mark.parametrize`](../../automation-testing/pytest/parametrize.md) run one test with many inputs. A **parametrized fixture** does the same with a resource: every test that asks for `db` runs once per database. Write the test once. Four databases means four results, each with the database's name in it.

!!! note "Before you start"
    Read [Parametrize](../../automation-testing/pytest/parametrize.md), [Fixtures and conftest.py](../../automation-testing/pytest/fixtures-and-conftest.md) and [One client, many drivers](one-client-many-drivers.md).

## What you will learn

- How a fixture with `params` runs each test on every database
- How to open each database only once per run
- How to write checks that work on SQL and MongoDB alike
- How to ask the same question in four query languages

## Why this matters at work

When a product supports several databases, a bug often shows up on one only: the query works on PostgreSQL and breaks on MySQL. A test suite that runs everything everywhere finds it before a customer on that database does.

## The idea in plain words

!!! info "In plain words"
    One recipe, cooked in four kitchens. You write the recipe once. The fixture walks it into each kitchen in turn, and tells you which kitchen burned it.

## Step by step

1. **Read the fixtures.** `tests/conftest.py`:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/tests/conftest.py"
    ```

    - `clients` (one per run) opens each database the first time a test asks for it, loads fresh test data, and closes them all at the end. Each database is opened once, not once per test.
    - `db` has `params=DATABASES`. pytest runs every test that uses `db` once for each name, and puts the name in the test id.
    - `source` and `target` are for the [comparison lesson](cross-database-comparison.md).

2. **Write checks that work on every database.** `tests/test_data_integrity.py` reads rows through `db.rows()`, which are normalized Python dicts on every database, and checks them in Python:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/tests/test_data_integrity.py"
    ```

    "Every order has a real customer" is a `LEFT JOIN` in SQL, and there's no `JOIN` in MongoDB. In Python, it's one set and one list, and it works on all four. For small and medium test data, that's the simplest way to write one check for every database.

3. **Ask the same question in each database's language.** Some questions need the database to do the work: a report, a big table. "Orders per month" in four languages, in `queries/<driver>/`:

    === "PostgreSQL"

        ```sql
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/queries/postgres/orders_per_month.sql"
        ```

    === "MySQL"

        ```sql
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/queries/mysql/orders_per_month.sql"
        ```

    === "SQLite"

        ```sql
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/queries/sqlite/orders_per_month.sql"
        ```

    === "MongoDB"

        ```json
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/queries/mongo/orders_per_month.json"
        ```

    `test_orders_per_month` runs the right file for each database with `db.run_query("orders_per_month")`, and expects the same answer from all four. The test is written once. Only the query differs.

4. **Run it.**

    ```bash
    python -m pytest -v tests/test_data_integrity.py -k month
    ```

    ```text
    tests/test_data_integrity.py::test_orders_per_month[postgres] PASSED     [ 75%]
    tests/test_data_integrity.py::test_orders_per_month[mysql] PASSED        [ 77%]
    tests/test_data_integrity.py::test_orders_per_month[sqlite] PASSED       [ 79%]
    tests/test_data_integrity.py::test_orders_per_month[mongo] PASSED        [ 81%]
    ```

    (These lines are from the full run, so the percentages run on.) The whole suite on all four:

    ```text
    ............................................                             [100%]
    44 passed in 0.20s
    ```

    !!! success "Check: you should now be able to"
        Run one test on every database with a parametrized fixture, open each database once per run, and keep one question in several query languages.

## When it goes wrong

- **A test fails on one database only.** Read the id: `[mysql]`. Run just that one with `TEST_DATABASES=mysql`. The difference is almost always types or the query dialect.
- **`pymysql.err.ProgrammingError: not enough arguments for format string`.** A MySQL query has `%` in it (`'%Y-%m'`), and values were passed, even an empty tuple. PyMySQL then reads every `%` as a placeholder. Pass no values at all when there are none, as `SqlClient.execute` does, or write `%%`.
- **`You have an error in your SQL syntax ... near 'DATETIME has no time zone.`** while creating tables. The client splits `schema.sql` on `;`, and a comment had a `;` in it. Keep `;` out of comments in SQL files that get split.
- **The test is slow on four databases.** Each database should be opened once per run (`scope="session"`), not once per test.

## Common mistakes

!!! warning "Common mistakes"
    - **Copying a test four times, one per database.** Use the `db` fixture.
    - **One SQL string for all databases.** Date functions, string functions and `LIMIT` differ. Keep one file per database in `queries/`.
    - **Checking MongoDB with SQL in your head.** It has no joins and no schema. Check in Python, or with a pipeline.

!!! failure "If you see this error"
    **`fixture 'db' not found`**
    The test file isn't under the folder that holds `conftest.py`, or you ran pytest from another folder. Run `python -m pytest` from the project folder.

## Try it yourself

Add a query `paid_total` that returns the sum of `total` for paid orders, in all four languages, and a test that expects 273.46 from every database.

??? success "Solution"
    `queries/postgres/paid_total.sql`, and the same text for MySQL and SQLite:

    ```sql
    SELECT SUM(total) AS paid FROM orders WHERE status = 'paid'
    ```

    `queries/mongo/paid_total.json`:

    ```json
    {"pipeline": [
      {"$match": {"status": "paid"}},
      {"$group": {"_id": null, "paid": {"$sum": "$total"}}},
      {"$project": {"_id": 0, "paid": 1}}
    ]}
    ```

    The test, with `normalize` so `Decimal`, float and `Decimal128` compare alike:

    ```python
    from db_clients.base_client import normalize

    def test_paid_total(db):
        assert normalize(db.run_query("paid_total")[0]["paid"]) == "273.46"
    ```

## References

- [pytest: Parametrizing fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#parametrizing-fixtures)
- [PostgreSQL: to_char](https://www.postgresql.org/docs/17/functions-formatting.html)
- [MySQL: DATE_FORMAT](https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html#function_date-format)
- [SQLite: Core functions (substr)](https://www.sqlite.org/lang_corefunc.html)
- [MongoDB: $dateToString](https://www.mongodb.com/docs/manual/reference/operator/aggregation/dateToString/)

Written for Python 3.13, pytest 9.2, PostgreSQL 17, MySQL 8.4, SQLite 3 and MongoDB 8.0. Outputs captured November 2026. Links checked: November 2026.
