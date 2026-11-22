---
title: "Connect to PostgreSQL From Python With psycopg"
description: "Open a database connection from Python with psycopg, run queries with parameters instead of pasted values, read rows as dicts, and wrap it all in a small client class for tests."
level: Intermediate
tags:
  - Database
  - Python
  - Security
nav_title: "Connecting from Python"
order: 30
summary: "Connect with psycopg, pass values as parameters, and read rows as dicts."
updated: "2026-11-22"
---

# Connect to PostgreSQL From Python With psycopg

Queries typed in `psql` are for looking around. Tests need the same queries from Python, so they run in the pipeline on every change. For PostgreSQL the usual library is **psycopg** (version 3). This lesson connects, runs a query with a value, reads the rows, and then puts that in a small client class the tests share.

!!! note "Before you start"
    Read [SQL for testers](sql-for-testers.md), and have the bookshop database running. Install the library in your virtual environment: `python -m pip install "psycopg[binary]==3.3.9"`. The `[binary]` part brings a ready-built copy, so you don't need PostgreSQL's own files on your computer.

## What you will learn

- How to connect with an address kept in an environment variable
- Why values go in as parameters, never pasted into the SQL
- How to read rows as dicts
- How a small `DbClient` class keeps tests short

## Why this matters at work

Every database test starts with a connection. Get two things right on day one: the password never goes in a file, and values never get pasted into the SQL text. The first leaks secrets through git. The second is **SQL injection**, one of the most common security holes there is, and a test suite that builds SQL with f-strings teaches the whole team the wrong habit.

## The idea in plain words

!!! info "In plain words"
    A connection is a phone call to the database. You dial once (the address and password), say what you want (the query), hear the answer (the rows), and hang up. A parameter is like spelling a name out letter by letter: the database writes down exactly what you said, and never mistakes it for an instruction.

## Step by step

1. **Keep the address in an environment variable.** The address holds the user, password, host, port and database name. Set it in the terminal, never in code:

    ```bash
    export DATABASE_URL=postgresql://shop_tester:local_only_password@127.0.0.1:5432/shop
    ```

    In the pipeline, it comes from the CI secrets store. The password here is a fake one for a throwaway local database.

2. **Connect and run a query.** `connect_demo.py`:

    ```python
    --8<-- "modules/core_automation/database_testing/examples/connect_demo.py"
    ```

    ```bash
    python connect_demo.py
    ```

    ```text
    Connected to PostgreSQL 17.12 (Debian 17.12-1.pgdg13+1)
    2 books with less than 5 in stock:
      {'id': 2, 'title': 'SQL in a Week', 'stock': 3}
      {'id': 3, 'title': "The Bug Hunter's Guide", 'stock': 0}
    ```

    Three things to notice:

    - `with psycopg.connect(...)` closes the connection at the end, even after an error.
    - `row_factory=dict_row` gives each row as a dict, so tests read `row["stock"]` instead of `row[2]`.
    - The value 5 is not in the SQL text. The SQL has `%s`, and the value goes separately in a tuple: `(5,)`. The comma matters, because `(5)` is just the number 5.

3. **See why parameters matter.** `injection_demo.py` searches for a customer by email twice: once with the value pasted into the SQL, once as a parameter. The "email" is what an attacker might type into a search box:

    ```python
    --8<-- "modules/core_automation/database_testing/examples/injection_demo.py"
    ```

    ```text
    Pasted in:  SELECT id, email FROM customers WHERE email = 'nobody@example.com' OR '1'='1'
    Rows found: 5
    As a parameter, rows found: 0
    ```

    Pasted in, the quote mark in the input ends the text early, and `OR '1'='1'` becomes part of the query. It's true for every row, so every customer comes back. As a parameter, the database looks for a customer whose email is that whole odd string, and finds none. Always use parameters. When you test the app, try inputs like this one in its search boxes. If you get every row back, you've found a security bug.

4. **Wrap it in a client class.** Tests repeat the same few moves: get all rows, get one row, get one value, change rows. The template's `db/client.py` puts them in one place, and logs every query without its values, because values can be personal data:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/db/client.py"
    ```

    A test then reads like the question it asks:

    ```python
    def test_book_is_in_stock(db):
        assert db.value("SELECT stock FROM books WHERE title = %s", ("Clean Tests",)) == 25
    ```

    The `db` fixture comes from the [transactions lesson](transactions-and-cleanup.md).

    !!! success "Check: you should now be able to"
        Connect with an address from the environment, pass values as parameters, read rows as dicts, and explain SQL injection with an example.

## When it goes wrong

- **`KeyError: 'DATABASE_URL'`.** The variable isn't set in this terminal. Each new terminal starts without it. Run the `export` line again. The template's `database_url()` gives a clearer message: `Set the environment variable DATABASE_URL first`.
- **`password authentication failed for user "shop_tester"`.** Wrong user or password in the address. If the password has `@`, `:` or `/` in it, those must be written as `%40`, `%3A` and `%2F` in the address.
- **`Connection refused`.** Nothing is listening at that host and port. Is the database running (`docker ps`)? Is the port right?
- **`current transaction is aborted, commands ignored until end of transaction block`.** An earlier query in the same transaction failed, and PostgreSQL ignores everything after it until a rollback. Find the first error, not this one. In tests, wrap queries you expect to fail in a savepoint ([transactions lesson](transactions-and-cleanup.md)).

The real messages, from a wrong password and from a port with nothing on it:

```text
psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 5432 failed: FATAL:  password authentication failed for user "shop_tester"
```

```text
psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 5433 failed: could not receive data from server: Connection refused
```

## Common mistakes

!!! warning "Common mistakes"
    - **Building SQL with f-strings or `+`.** Use `%s` and a tuple of values. Only table and column names can't be parameters. Never take those from user input.
    - **The password in the code or in `pytest.ini`.** It ends up in git history forever. Use an environment variable.
    - **Printing the connection address in a log.** It holds the password.
    - **`(5)` instead of `(5,)`.** Without the comma it isn't a tuple.

!!! failure "If you see this error"
    **`psycopg.ProgrammingError: the query has 0 placeholders but 1 parameters were passed`**
    You wrote `?` as the placeholder, from SQLite or another library. psycopg uses `%s`. The same error appears if you forgot the placeholder altogether.

## Try it yourself

Write a function `customer_by_email(conn, email)` that returns the customer's row as a dict, or `None`, and finds `Arshad@Example.com` too.

??? success "Solution"
    ```python
    def customer_by_email(conn, email):
        return conn.execute(
            "SELECT id, email, full_name FROM customers WHERE LOWER(email) = LOWER(%s)",
            (email,),
        ).fetchone()
    ```

    `fetchone()` returns `None` when there's no row. `LOWER` on both sides makes the match ignore capitals. The email still goes in as a parameter.

## References

- [psycopg 3: Basic module usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
- [psycopg 3: Passing parameters to SQL queries](https://www.psycopg.org/psycopg3/docs/basic/params.html)
- [psycopg 3: Row factories](https://www.psycopg.org/psycopg3/docs/advanced/rows.html)
- [PostgreSQL: Connection URIs](https://www.postgresql.org/docs/17/libpq-connect.html#LIBPQ-CONNSTRING-URIS)
- [OWASP: SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

Written for Python 3.13, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
