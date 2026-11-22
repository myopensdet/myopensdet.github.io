---
title: "One Base Client, Many Database Drivers in Python"
description: "Hide the differences between PostgreSQL, MySQL, SQLite and MongoDB behind one Python base class, so every test talks to every database the same way, and each driver's quirks stay in one small class."
level: Intermediate
tags:
  - Database
  - Python
  - Clean code
nav_title: "One client, many drivers"
order: 40
summary: "One base class for every database; each driver's quirks in its own class."
updated: "2026-11-22"
---

# One Base Client, Many Database Drivers in Python

psycopg, PyMySQL, sqlite3 and PyMongo all do the same job, and every one does it a little differently. Different placeholders, different types, different ways to connect. If tests call the drivers directly, every test has four versions. The fix is a **base client**: one class that says what every database can do, and one small class per database that fills in the details.

!!! note "Before you start"
    Read [Classes and objects](../../programming-for-testers/object-oriented-programming.md) and [Connecting from Python](../connecting-from-python.md).

## What you will learn

- What the base client promises, and why tests use only that
- How three SQL databases share one class
- Where each driver's quirks go
- What MongoDB needs that SQL databases don't

## Why this matters at work

When a fifth database arrives, you add one small class, and every existing test runs on it. When a driver changes, you fix one file. That's the difference between a suite the team keeps using and one it gives up on.

## The idea in plain words

!!! info "In plain words"
    A base client is a universal power adapter. Your laptop has one plug. The adapter has one side that fits your plug, and a different tip for each country. Tests are the laptop. Each database is a country.

## Step by step

1. **Write down what every database must do.** That's the base class. Tests use only these methods:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/base_client.py"
    ```

    The methods marked `@abstractmethod` have no body: each database must write its own. `rows()` and `checksum()` are written once, here, for all of them. `__repr__` shows only the name, so a client printed in a failure never shows its password.

2. **Share what SQL databases have in common.** PostgreSQL, MySQL and SQLite all follow Python's database API ([PEP 249](https://peps.python.org/pep-0249/)): `cursor()`, `execute()`, `fetchall()`, `description`. So one class does most of the work for all three:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/sql_client.py"
    ```

    `columns()` uses a trick that works on every SQL database: `SELECT * ... LIMIT 0` returns no rows, but the driver still describes the columns.

3. **Put each driver's quirks in its own class.** What's left per database is small:

    === "PostgreSQL"

        ```python
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/postgres_client.py"
        ```

    === "MySQL"

        ```python
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/mysql_client.py"
        ```

    === "SQLite"

        ```python
        --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/sqlite_client.py"
        ```

    Each quirk has a comment saying why:

    - **MySQL** needs `charset="utf8mb4"` for full Unicode, and its `DATETIME` has no time zone, so times are saved in UTC.
    - **SQLite** uses `?` as the placeholder, ignores foreign keys until `PRAGMA foreign_keys = ON`, and can't store a `Decimal`.

4. **Give MongoDB its own client.** It has no tables, no SQL and no schema. Its client keeps the same promises in its own way:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/mongo_client.py"
    ```

    - A "table" is a collection of documents.
    - Money is stored as `Decimal128`, because BSON (MongoDB's format) has no Python `Decimal`, and read back as `Decimal`.
    - `MongoClient(...)` doesn't connect until the first real request, so `connect()` sends a `ping` to fail early with a clear error.
    - The only rules are the ones you add, like unique indexes.

5. **See the same order through every client.** `examples/types_tour.py` reads order 2 from each database:

    ```text
    postgres  raw:  total=Decimal('49.50')  created_at=datetime.datetime(2026, 10, 3, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC'))
              same: total='49.5'  created_at='2026-10-03 12:00:00'
    mysql     raw:  total=Decimal('49.50')  created_at=datetime.datetime(2026, 10, 3, 12, 0)
              same: total='49.5'  created_at='2026-10-03 12:00:00'
    sqlite    raw:  total=49.5  created_at='2026-10-03 12:00:00'
              same: total='49.5'  created_at='2026-10-03 12:00:00'
    mongo     raw:  total=Decimal('49.50')  created_at=datetime.datetime(2026, 10, 3, 12, 0)
              same: total='49.5'  created_at='2026-10-03 12:00:00'
    ```

    Raw, the four look different: one time has a zone, two don't, and SQLite gives a float and plain text. After `normalize()`, they're the same. The [comparison lesson](cross-database-comparison.md) depends on that.

    !!! success "Check: you should now be able to"
        Explain what the base client promises, how three SQL databases share one class, and where each driver's quirks belong.

## When it goes wrong

- **`sqlite3.ProgrammingError: Error binding parameter 1: type 'decimal.Decimal' is not supported`.** sqlite3 can't store `Decimal`. Change it to text in the SQLite client's `to_db`, never in the tests.
- **SQLite accepts an order for a customer that doesn't exist.** Foreign keys are off by default in SQLite. Turn them on for every connection: `PRAGMA foreign_keys = ON`.
- **Times shift by a few hours on one computer only.** Somewhere, `value.astimezone(UTC)` ran on a time with no zone, and Python assumed the computer's own time zone. The template's `as_utc()` treats a time with no zone as UTC instead. It was written after exactly this bug showed up while building the template.
- **`MongoClient` seems to connect even with the wrong password.** It connects lazily. The first real query fails instead. Send a `ping` in `connect()`.

## Common mistakes

!!! warning "Common mistakes"
    - **`if driver == "mysql":` inside tests.** Move the difference into that driver's class.
    - **One huge client class for every database.** Use a base class and small subclasses.
    - **Importing every driver at the top.** Then you can't test SQLite without installing the MongoDB driver. Import a driver only when its database is used, as `make_client` does.

!!! failure "If you see this error"
    **`TypeError: Can't instantiate abstract class MongoDbClient without an implementation for abstract method 'columns'`**
    The class is missing one of the methods the base class requires. Python refuses to create it at all, which is the point: a missing method fails at once, not halfway through a run.

## Try it yourself

A new database uses the placeholder `:1`, `:2`, ... (like Oracle's driver). Where would you put that difference?

??? success "Solution"
    In that database's own client class, by overriding `insert()` (or `placeholder` plus a small method that numbers them). Never in the tests, and not in `SqlClient`, which the other three share.

## References

- [PEP 249: Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python: abc (abstract base classes)](https://docs.python.org/3/library/abc.html)
- [PyMySQL documentation](https://pymysql.readthedocs.io/en/latest/)
- [Python: sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [PyMongo documentation](https://pymongo.readthedocs.io/en/stable/)
- [SQLite: Foreign key support](https://www.sqlite.org/foreignkeys.html)

Written for Python 3.13, psycopg 3.3, PyMySQL 1.2 and PyMongo 4.20. Outputs captured November 2026. Links checked: November 2026.
