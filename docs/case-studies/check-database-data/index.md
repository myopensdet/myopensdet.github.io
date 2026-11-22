---
title: "How to Test Data in a Database With SQL and pytest, Step by Step"
description: "A step-by-step guide to database testing at work: get safe read-only access, read the tables, decide which checks you need, plan, and copy ready pytest checks and SQL queries for saved data, duplicates, orphans, wrong totals, unknown values and table structure. Then run them, read the results and fix the common errors."
level: Beginner
tags:
  - Database
  - pytest
  - Templates
nav_title: "Check database data, step by step"
order: 30
summary: "Safe access, read the tables, plan, copy the SQL checks, run, read the results."
updated: "2026-11-22"
code: "work_playbooks/check_database_data"
---

# How to Test Data in a Database With SQL and pytest, Step by Step

An API says "201 Created". A page says "Order placed". But was the data really saved, and saved right? And after last night's release, is the data in the database still healthy? This guide takes you from nothing to automated database checks: what to ask for, what to look at, which checks to write, and ready templates to copy. Follow the steps in order.

!!! example "The situation"
    **Your lead:** "After the last release, some order totals looked wrong in the admin page. Can you set up checks on the shop database, so we catch bad data before customers do?"

You'll practise on a small **shop database** in PostgreSQL, started on your computer with one command. Like real databases, it has some bad rows hidden in it. When you finish, you point the same checks at your own database.

## Step 1: Install what you need

You need **Python 3.13**, **VS Code** and **Docker** (for the practice database). If you don't have them, follow [environment setup](../../getting-started/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/check_database_data/templates). Then open the `db_checks` folder in VS Code (**File → Open Folder**).

2. **Open a terminal** in VS Code (**Terminal → New Terminal**), make a virtual environment and install the packages. pytest runs the checks; psycopg talks to PostgreSQL.

    === "macOS / Linux"

        ```bash
        python3.13 -m venv .venv
        source .venv/bin/activate
        python -m pip install -r requirements.txt
        ```

    === "Windows"

        ```powershell
        py -3.13 -m venv .venv
        .venv\Scripts\Activate.ps1
        python -m pip install -r requirements.txt
        ```

    The last line should be:

    ```text
    Successfully installed iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 psycopg-3.3.9 psycopg-binary-3.3.9 pygments-2.21.0 pytest-9.2.0
    ```

3. **Start the practice database.** First copy the settings file, then start it:

    ```bash
    cp .env.example .env
    docker compose up -d --wait
    ```

    (Windows: `copy .env.example .env`.) `--wait` returns when the database is ready:

    ```text
     Container zts-db-checks-db-1 Started
     Container zts-db-checks-db-1 Waiting
     Container zts-db-checks-db-1 Healthy
    ```

    It's on your computer only, at `127.0.0.1`, port `58232`. The tables and rows come from `sql/practice_shop.sql`.

!!! success "Check"
    `(.venv)` at the start of your prompt, and `Healthy` from Docker. If not, see [when it goes wrong](#step-9-when-it-goes-wrong).

## Step 2: Get access, and read the tables

**At work, ask for four things** before you touch a database:

| Ask for | Why |
| --- | --- |
| **Which database**: host, port, name, and which environment (test, staging) | Never test on production unless your team says so in writing |
| **A read-only user** | You look at data; you never change it by accident |
| **The table diagram**, or the developer who knows the tables | To know what's linked to what |
| **"Is there real customer data in it?"** | If yes: never copy rows into tickets, chats or reports |

**Then read the tables.** Open the database in a tool (DBeaver, pgAdmin, or the one in your team), or read the file that creates them. For the practice shop, that's `sql/practice_shop.sql`:

```sql
CREATE TABLE orders (
    id           SERIAL PRIMARY KEY,
    order_number TEXT NOT NULL UNIQUE,
    customer_id  INTEGER NOT NULL,
    status       TEXT NOT NULL,
    total        NUMERIC(10, 2) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

For **each table**, write down:

| Find | Practice shop example: `orders` |
| --- | --- |
| **What it holds** | One row per checkout |
| **Linked to** | `customers` (by `customer_id`); `order_items` point to it |
| **Rules the database enforces** | `order_number` is unique; nothing is empty (`NOT NULL`) |
| **Rules only the app knows** | `status` is one of five words; `total` = the sum of its items |

The last row is where bugs hide. **The database only enforces the rules written in the table.** Every other rule depends on the app getting it right every time. Those are the rules you check.

## Step 3: Decide which checks you need

Almost every database needs the same kinds of checks. Use this list for every table:

| Kind | The question | Example check |
| --- | --- | --- |
| **Saved correctly** | After the app saves something, are the rows right? | Order `BK-1001` has status `paid`, total `64.48`, and its two items |
| **Duplicates** | Is something saved twice? | The same email twice, once with capital letters |
| **Orphans** | Does a row point to something that doesn't exist? | An order item for order 99, which isn't there |
| **Totals** | Do the parts add up? | Order total = sum of quantity × price of its items |
| **Allowed values** | Is every value one the app knows? | Status is `new`, `paid`, `shipped`, `delivered` or `cancelled` |
| **Ranges** | Are numbers where they should be? | Stock is never below 0; prices are above 0 |
| **Structure** | Are the tables, columns, types and links what the app expects? | `orders` has its 6 columns; `orders` is linked to `customers` |

One idea makes all data checks simple: **write a query that finds the bad rows.** No rows means the check passes. Rows mean the check fails, and the rows show exactly what's wrong.

## Step 4: Write a one-page plan

Copy `test_plan.md` from the project and fill it in:

1. **Access:** which database, which user, who owns the data, is there real customer data.
2. **Tables:** one row each, with links and the rules the app expects (from step 2).
3. **Checks:** the kinds from step 3 you'll automate.
4. **Questions for the team:** anything that looks odd.
5. **Not in this plan.**

Part of the plan for the practice shop:

```markdown
| Table | What it holds | Linked to | Rules the app expects |
| --- | --- | --- | --- |
| `orders` | One per checkout | `customers` | status is one of: new, paid, shipped, delivered, cancelled; total = sum of its items |
| `order_items` | Lines of an order | `orders`, `products` | every line belongs to an existing order |

## 4. Questions for the team

1. `orders.customer_id` has no foreign key. Is that on purpose?
2. Can one person have two accounts with the same email in different case?
```

Post it in the ticket. The data owner often knows rules that aren't written anywhere.

## Step 5: Set up the project

```text
db_checks/
├── requirements.txt          pytest and psycopg
├── pytest.ini                pytest settings
├── test_plan.md              your plan (step 4)
├── docker-compose.yml        the practice database (not needed for your own database)
├── .env.example              the practice database's settings
├── sql/
│   ├── practice_shop.sql     the practice tables and rows
│   └── data_checks.sql       12 ready queries to paste into any SQL tool
└── tests/
    ├── conftest.py           the connection, read-only
    ├── test_saved_data.py    was it saved correctly?
    ├── test_data_quality.py  is the data healthy?
    └── test_schema.py        is the structure right?
```

`tests/conftest.py` connects to the database in `DATABASE_URL`, and makes the connection **read-only**:

```python
--8<-- "modules/work_playbooks/check_database_data/templates/db_checks/tests/conftest.py"
```

| Part | What it is |
| --- | --- |
| `db` | One connection for all tests. `conn.read_only = True` means any `INSERT`, `UPDATE` or `DELETE` fails |
| `rows()` | Runs a query, returns the rows |
| `problems()` | Turns bad rows into a clear failure message: how many, and the first 10 |

Read-only is your seat belt. Even if a check has a mistake, it can't change anything:

```text
psycopg.errors.ReadOnlySqlTransaction: cannot execute DELETE in a read-only transaction
```

## Step 6: Copy the check templates

Each file covers one kind of question from step 3.

=== "Saved correctly"

    ```python
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/tests/test_saved_data.py"
    ```

    Use these right after your [API tests](../automate-api-tests/index.md) or UI tests: the test creates an order, then these checks look at what reached the database. Money comes back from the database as `Decimal("64.48")`, never as a float: compare with `Decimal`.

=== "Data quality"

    ```python
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/tests/test_data_quality.py"
    ```

    Every check is the same shape: a query that finds bad rows, then `assert not found`. To add a rule, copy one check and change the query.

=== "Structure"

    ```python
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/tests/test_schema.py"
    ```

    `information_schema` is a set of built-in tables that describe your tables. It exists in PostgreSQL, MySQL and SQL Server.

=== "SQL queries for any tool"

    ```sql
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/sql/data_checks.sql"
    ```

    These are the same checks as plain SQL, for when you're looking at a database in DBeaver or pgAdmin, or someone asks "can you check the data quickly?". Each one returns the bad rows.

## Step 7: Run the checks

1. **Set the database address** in the terminal (never in a file). For the practice database, the password is the one in your `.env`:

    === "macOS / Linux"

        ```bash
        export DATABASE_URL=postgresql://shop_tester:change_me_local_only@127.0.0.1:58232/shop
        ```

    === "Windows"

        ```powershell
        $env:DATABASE_URL="postgresql://shop_tester:change_me_local_only@127.0.0.1:58232/shop"
        ```

    The address has five parts: `postgresql://` **user** `:` **password** `@` **host** `:` **port** `/` **database**.

2. **Run:**

    ```bash
    python -m pytest
    ```

    ```text
    tests/test_data_quality.py::test_no_duplicate_emails FAILED              [  7%]
    tests/test_data_quality.py::test_every_order_item_belongs_to_an_order FAILED [ 14%]
    tests/test_data_quality.py::test_every_order_belongs_to_a_customer PASSED [ 21%]
    tests/test_data_quality.py::test_every_order_has_items PASSED            [ 28%]
    tests/test_data_quality.py::test_order_totals_match_their_items FAILED   [ 35%]
    tests/test_data_quality.py::test_order_statuses_are_known FAILED         [ 42%]
    tests/test_data_quality.py::test_stock_is_never_negative FAILED          [ 50%]
    tests/test_data_quality.py::test_prices_are_above_zero PASSED            [ 57%]
    tests/test_saved_data.py::test_order_is_saved_with_the_right_values PASSED [ 64%]
    tests/test_saved_data.py::test_order_items_are_saved PASSED              [ 71%]
    tests/test_saved_data.py::test_order_total_is_the_sum_of_its_items PASSED [ 78%]
    tests/test_schema.py::test_all_tables_exist PASSED                       [ 85%]
    tests/test_schema.py::test_orders_columns_and_types PASSED               [ 92%]
    tests/test_schema.py::test_orders_are_linked_to_customers_by_a_foreign_key FAILED [100%]
    ...
    ========================= 6 failed, 8 passed in 0.08s ==========================
    ```

    To try a query by hand, run the whole SQL file against the practice database:

    ```bash
    docker compose exec -T db psql -U shop_tester -d shop < sql/data_checks.sql
    ```

    ```text
            email         | how_many
    ----------------------+----------
     mia.khan@example.com |        2
    (1 row)

     id | order_id | product_id | quantity | unit_price
    ----+----------+------------+----------+------------
      6 |       99 |          1 |        1 |      24.50
    (1 row)
    ```

## Step 8: Read the results

**8 passed:** order `BK-1001` was saved right, every order has a customer and items, prices are fine, and the tables have the right columns.

**6 failed**, and each failure shows the bad rows:

```text
E       AssertionError: 1 emails used more than once: [('mia.khan@example.com', 2)]
E       AssertionError: 1 order items with no order (id, order_id): [(6, 99)]
E       AssertionError: 1 orders whose total is wrong (order, total, items): [('BK-1003', Decimal('50.00'), Decimal('45.00'))]
E       AssertionError: 1 orders with an unknown status: [('BK-1004', 'shiped')]
E       AssertionError: 1 products with negative stock: [('BOOK-PY', -3)]
E       AssertionError: orders.customer_id has no foreign key: nothing stops orders with no customer
```

Sort each into **bug** or **ask**:

| Failure | Group | What to do |
| --- | --- | --- |
| `BK-1003` total 50.00, items add up to 45.00 | **Bug** | The customer paid the wrong amount. Report it first |
| `BK-1004` status `shiped` | **Bug** | A typo in the code that sets the status. That order won't show up as shipped anywhere |
| Order item for order 99 | **Bug** | Something deleted an order and left its items, or saved items to the wrong order |
| `BOOK-PY` stock −3 | **Bug** | The shop sold 3 books it didn't have |
| `mia.khan@example.com` twice | **Ask** | Two accounts, or one person? Question 2 in the plan |
| No foreign key on `orders.customer_id` | **Ask** | On purpose, or forgotten? A foreign key would have blocked the orphan rows |

Two things to notice:

- **The bad rows are in the message.** You can paste them straight into the bug report. On a database with real customers, paste only ids and order numbers, never names or emails.
- **The database password isn't.** pytest shows the connection as `db = <psycopg.Connection [INTRANS] (host=127.0.0.1 port=58232 user=shop_tester database=shop) at 0x...>`: psycopg leaves the password out.

When the team answers the asks, either the data gets fixed, or you change the check to the agreed rule. Run these checks after every release, and before and after every data migration.

### Use it on your own database

1. Set `DATABASE_URL` to your test database, with a **read-only** user.
2. In `test_saved_data.py`: change `ORDER_NUMBER`, the table and column names, and the expected values.
3. In `test_data_quality.py`: one check per rule from your plan. Change the queries to your tables.
4. In `test_schema.py`: list your tables and the columns the app needs.
5. You don't need `docker-compose.yml` or `sql/practice_shop.sql`: they're only for practice.

Not PostgreSQL? The checks are plain SQL and work almost the same everywhere. Only the connection changes: [multi-database testing](../../database-testing/several-databases/index.md) shows MySQL, SQLite and MongoDB.

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `SKIPPED ... Set DATABASE_URL to the database you want to check` | The address isn't set in **this** terminal | Step 7.1. A new terminal forgets it |
| `required variable POSTGRES_PASSWORD is missing a value: Copy .env.example to .env first` | No `.env` file next to `docker-compose.yml` | `cp .env.example .env` |
| `connection to server at "127.0.0.1", port ... failed: Connection refused` | Nothing is listening there: the database isn't running, or the port is wrong | `docker compose ps`; check the port in `DATABASE_URL` |
| `FATAL:  password authentication failed for user "shop_tester"` | Wrong password. **Or:** you changed the password in `.env` after the database was first created. PostgreSQL keeps the first one | Use the password from `.env`. If you changed it: `docker compose down -v`, then `docker compose up -d --wait` (this deletes the practice data, which is then created again) |
| `FATAL:  database "shopp" does not exist` | A typo in the database name, the part after the last `/` | Check the name with the team |
| `psycopg.errors.UndefinedTable: relation "orderz" does not exist` | A typo in a table name, or the table is in another schema | Check the name in your SQL tool |
| `psycopg.errors.SyntaxError: syntax error at or near "order"` | `order`, `user` and `group` are SQL words. A table with that name needs quotes | Write `"order"`, with double quotes |
| `cannot execute DELETE in a read-only transaction` | A check tried to change data | That's the seat belt working. Checks only read |
| `No module named pytest` (or `psycopg`) | The virtual environment isn't active | `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`) |

When you're done practising: `docker compose down -v` stops the database and deletes its data.

Still stuck? Go deeper:

- [SQL for testers](../../database-testing/sql-for-testers.md) and [joins and GROUP BY](../../database-testing/joins-and-group-by.md): how the queries work
- [Connecting from Python](../../database-testing/connecting-from-python.md) and [data validation](../../database-testing/data-validation.md)
- [Integrity constraints](../../database-testing/integrity-constraints.md): foreign keys, `UNIQUE`, `CHECK`
- [The full database testing topic](../../database-testing/index.md)

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/check_database_data/templates).

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/test_plan.md"
    ```

=== "docker-compose.yml"

    ```yaml
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/docker-compose.yml"
    ```

=== "sql/practice_shop.sql"

    ```sql
    --8<-- "modules/work_playbooks/check_database_data/templates/db_checks/sql/practice_shop.sql"
    ```

## References

- [PostgreSQL: SELECT](https://www.postgresql.org/docs/current/sql-select.html)
- [PostgreSQL: The information schema](https://www.postgresql.org/docs/current/information-schema.html)
- [psycopg 3: Basic module usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)

Written for Python 3.13, pytest 9, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
