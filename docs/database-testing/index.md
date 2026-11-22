---
title: "Database Testing for Beginners: A Practical Guide With SQL and pytest"
description: "How to test a database with SQL, Python and pytest: queries for testers, connecting with psycopg, schema, integrity and CRUD tests, business-rule checks, stored procedures, triggers and clean-up with rollback."
level: Intermediate
tags:
  - Database
  - Python
  - pytest
nav_title: "Database and SQL Testing"
order: 50
summary: "Write SQL to prove the right data was saved, and test schemas and rules."
updated: "2026-11-22"
code: "core_automation/database_testing"
kind: "category"
icon: "lucide/database"
card: "SQL for testers, data checks, and comparing what the API says with the database."
---

# Database Testing for Beginners: A Practical Guide With SQL and pytest

The screen says "Order placed". The API answers 201. But was the order saved, with the right total, linked to the right customer, with the stock taken? Only the database knows. **Database testing** checks the data itself, and the rules and code that live in the database. This topic goes from your first `SELECT` to a pytest project that tests a schema, its rules, its data and its stored code, and leaves nothing behind.

!!! info "In plain words"
    The app is the shop counter. The database is the stockroom and the ledger behind it. The counter can smile and say "done", but you go into the back room and check the ledger was written, and the shelf is one book lighter.

!!! example "Your task"
    Your team's bookshop app saves everything in PostgreSQL. After a bad release, a report showed the wrong totals, and nobody could tell when the data went wrong. Your lead says: "I want database tests in the pipeline. The schema matches what the app expects, the database refuses bad data, order totals add up, and the order function and the status trigger do what they should. They must run against a test database without leaving anything behind."
    This page walks through it, on a small bookshop database you can start in one command.

!!! note "Before you start"
    Read [pytest framework](../automation-testing/pytest/index.md) first. You need Docker for the practice database ([Environment setup](../getting-started/environment-setup/index.md#5-install-docker) shows how), and these in a virtual environment: `python -m pip install "pytest==9.2.0" "psycopg[binary]==3.3.9"`.

## Jump to what you need

1. [SQL for testers](sql-for-testers.md): `SELECT`, `WHERE`, `ORDER BY`, `COUNT` and `NULL`
2. [JOIN, GROUP BY and subqueries](joins-and-group-by.md): read two tables together, find missing links and duplicates
3. [Connecting from Python](connecting-from-python.md): psycopg, parameters, SQL injection, a client class
4. [Schema tests](schema-tests.md): tables and columns match what the app expects
5. [Integrity: keys and rules](integrity-constraints.md): the database refuses bad rows
6. [CRUD tests](crud-tests.md): create, read, update, delete, and check what was saved
7. [Data validation](data-validation.md): business rules as "must return zero rows" queries
8. [Stored procedures and triggers](procedures-and-triggers.md): code inside the database, tested from outside
9. [Transactions and clean-up](transactions-and-cleanup.md): roll back every test

## 1. Understand the ask

| You ask | Your lead answers |
| --- | --- |
| Which database, and which version? | PostgreSQL 17 |
| Which database do the tests use? | A test database only. Never production |
| Where are the tables defined? | In the app's migrations. Ask for the data model too |
| Which rules matter most? | Order totals, unique emails, stock never below zero |
| Is there logic in the database? | Yes: `place_order()` and a trigger that logs status changes |
| What must the tests not do? | Leave data behind, or print the password |

## 2. Picture the system

```mermaid
erDiagram
    customers ||--o{ orders : places
    orders ||--|{ order_items : contains
    books ||--o{ order_items : "is in"
    orders ||--o{ order_status_history : "status changes"
```

Read it as: one customer places many orders, each order contains one or more items, each item is one book, and each status change of an order writes one history row. Draw this for your own database before writing a test. Most bugs are in the links.

## 3. Learn just enough

Read [SQL for testers](sql-for-testers.md) and [JOIN, GROUP BY and subqueries](joins-and-group-by.md) first (an hour together). They're most of the SQL a tester needs. Then [Connecting from Python](connecting-from-python.md), and you can start on tests.

## 4. Get something running

Start a throwaway PostgreSQL that only your computer can reach, then load the bookshop tables and fake data from the [template project](#templates):

```bash
docker run --rm -d --name shop-db -e POSTGRES_USER=shop_tester \
  -e POSTGRES_PASSWORD=local_only_password -e POSTGRES_DB=shop \
  -p 127.0.0.1:5432:5432 postgres:17
docker exec -i shop-db psql -U shop_tester -d shop < sql/schema.sql
docker exec -i shop-db psql -U shop_tester -d shop < sql/seed.sql
```

```text
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE FUNCTION
CREATE TRIGGER
CREATE FUNCTION
INSERT 0 5
INSERT 0 4
INSERT 0 5
INSERT 0 6
```

Now `docker exec -it shop-db psql -U shop_tester -d shop` opens a SQL prompt for the lessons. The password is a fake one for a database that lives only on your computer. `docker stop shop-db` deletes the whole thing.

## 5. Decide what to put in

Five kinds of test, each answering one question:

| Kind | The question |
| --- | --- |
| Schema | Are the tables and columns what the app expects? |
| Integrity | Does the database refuse bad rows? |
| CRUD | Is what we save exactly what we read back? |
| Data rules | Does the data follow the business rules? |
| Stored code | Do the functions and triggers change the right tables, and only those? |

Every test runs inside a transaction that's rolled back, so they can run in any order, as often as you like.

## 6. Write a one-page plan

The plan is the table above with your tables filled in: which columns, which rules, which functions, and the business rules from the product owner, word for word. The [template project](#templates) is that plan turned into tests, one file per kind.

## 7. Build in small steps

Start with the schema test, because everything else depends on the tables being right. Then one integrity test per rule. Then CRUD for the most important table. Add data rules as the business names them, and one more every time a data bug reaches production. The finished project:

```bash
export DATABASE_URL=postgresql://shop_tester:local_only_password@127.0.0.1:5432/shop
python -m pytest
```

```text
.................................                                        [100%]
33 passed in 0.32s
```

33 tests in a third of a second, and the database is exactly as it was before.

## 8. Check it with your team

Show the schema test's `EXPECTED` dict and the list of data rules to the developers and the product owner. Ask: "is anything here wrong, and what's missing?" They'll correct rules you guessed, and name ones you didn't know. Agree who updates `EXPECTED` when a migration changes a table: the same pull request, every time.

## 9. Keep learning on your own

Next, [multi-database testing](several-databases/index.md) runs the same tests on MySQL, SQLite and MongoDB, and [API + database](api-and-database/index.md) checks that an API call saved the right rows.

!!! tip "How an experienced SDET thinks about this"
    - Check the data, not the message. "Saved" on screen proves nothing until the row is there.
    - Every rule gets two tests: bad data is refused, and good data gets in.
    - Prove each test can fail. A check that never fails isn't checking anything.
    - Every production data bug becomes a new rule, so it can't come back unnoticed.

!!! warning "Red flags"
    - Tests that run against production, or against a database shared with people.
    - SQL built with f-strings.
    - The database password in a file in git.
    - Tests that delete their data in the last line, or don't clean up at all.
    - `SELECT *` and no `ORDER BY` in a test that compares rows.

!!! question "Stuck? Try this"
    - **Can't connect.** Check `docker ps`, the port, and that `DATABASE_URL` is set in this terminal. See [Connecting from Python](connecting-from-python.md#when-it-goes-wrong).
    - **A test passes alone and fails in the full run.** Leftover or shared data. See [Transactions and clean-up](transactions-and-cleanup.md).
    - **You don't know what the right data is.** Ask the product owner for the rule in words, then write the query. Don't guess business rules.
    - **The query is right but slow.** Ask a developer for `EXPLAIN` help, and run heavy checks on a copy.

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/core_automation/database_testing/templates).

Copy the whole `shop_db_tests` folder, or the parts you need. Each file starts with a line that says where it came from.

=== "db/client.py"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/db/client.py"
    ```

=== "tests/conftest.py"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/conftest.py"
    ```

=== "Schema"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_schema.py"
    ```

=== "Integrity"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_integrity.py"
    ```

=== "CRUD"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_crud.py"
    ```

=== "Data rules"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_data_rules.py"
    ```

=== "Procedures and triggers"

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_procedures_and_triggers.py"
    ```

=== "sql/schema.sql"

    ```sql
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/sql/schema.sql"
    ```

=== "sql/seed.sql"

    ```sql
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/sql/seed.sql"
    ```

=== "How to use them"

    1. Copy `shop_db_tests`, make a virtual environment, and `python -m pip install -r requirements.txt`.
    2. Start a test database, set `DATABASE_URL`, then `python -m pytest`. Without it, every test is skipped with a reason.
    3. For your own database: in `tests/conftest.py`, delete the lines that make the `shop_test` schema and run the `.sql` files. Change `EXPECTED` and the rules to match your tables.
    4. Keep the patterns: everything through the `db` fixture, exact error classes, one rule per test, and a test that proves each rule can fail.

## Official resources

- [PostgreSQL 17 documentation](https://www.postgresql.org/docs/17/index.html), and its [tutorial](https://www.postgresql.org/docs/17/tutorial.html)
- [psycopg 3 documentation](https://www.psycopg.org/psycopg3/docs/)
- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [OWASP: SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Docker: the official postgres image](https://hub.docker.com/_/postgres)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.

## All lessons in this category

<!-- BEGIN topics (generated by scripts/build_nav.py, do not edit by hand) -->

<div class="zts-topics zts-order" markdown>

1.  [**SQL for testers**](sql-for-testers.md)

    Read, filter, sort and count rows: the queries you'll type every day.

    <span class="zts-chip">Intermediate</span>

2.  [**JOIN, GROUP BY and subqueries**](joins-and-group-by.md)

    Join tables, find missing links and duplicates, and compare with a subquery.

    <span class="zts-chip">Intermediate</span>

3.  [**Connecting from Python**](connecting-from-python.md)

    Connect with psycopg, pass values as parameters, and read rows as dicts.

    <span class="zts-chip">Intermediate</span>

4.  [**Schema tests**](schema-tests.md)

    Check the tables, columns, types and keys match what the app expects.

    <span class="zts-chip">Intermediate</span>

5.  [**Integrity: keys and rules**](integrity-constraints.md)

    Insert bad rows on purpose and prove the database refuses each one.

    <span class="zts-chip">Intermediate</span>

6.  [**CRUD tests**](crud-tests.md)

    Create, read, update and delete a row, and check exactly what was saved.

    <span class="zts-chip">Intermediate</span>

7.  [**Data validation**](data-validation.md)

    Write each business rule as a query that must return zero rows.

    <span class="zts-chip">Intermediate</span>

8.  [**Stored procedures and triggers**](procedures-and-triggers.md)

    Call database functions, check every table they touch, and test triggers.

    <span class="zts-chip">Intermediate</span>

9.  [**Transactions and clean-up**](transactions-and-cleanup.md)

    Roll back every test, so the database is the same after the run as before.

    <span class="zts-chip">Intermediate</span>

10.  [**API + database**](api-and-database/index.md)

    Call the API, then prove the change landed in the database.

    <span class="zts-chip">Intermediate</span>

11.  [**Multi-database testing**](several-databases/index.md)

    Run one test on MySQL, PostgreSQL, SQLite and MongoDB.

    <span class="zts-chip">Intermediate</span>

</div>

<!-- END topics -->
