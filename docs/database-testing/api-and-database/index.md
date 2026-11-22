---
title: "API + Database Testing With pytest: Check What the API Really Saved"
description: "Call the API, then prove the change landed in the database: verify writes, seed data then call, clean up rows the app saved, and wait for late writes without sleep. With a practice API that has two planted bugs."
level: Intermediate
tags:
  - API
  - Database
  - pytest
nav_title: "API + database"
order: 900
summary: "Call the API, then prove the change landed in the database."
updated: "2026-11-22"
code: "core_automation/api_and_database"
---

# API + Database Testing With pytest: Check What the API Really Saved

An API test checks the answer. A database test checks the rows. This topic joins them: **call the API, then prove the change landed in the database, exactly.** It finds the bugs neither one finds alone: a wrong price saved with a 201, stock that didn't go down, a duplicate account, a write that never came.

!!! info "In plain words"
    The waiter says "your order is in". API + database testing walks into the kitchen and reads the ticket on the rail: right dish, right table, right price.

!!! example "Your task"
    Your team's bookshop API takes orders. A customer complained they were charged the wrong price, and the API tests are all green. Your lead says: "I want tests that place real orders through the API, then check what's in the database: price, total, stock, history. And they must clean up after themselves: we share the test database."
    This page walks through it, with a practice API on your own computer.

!!! note "Before you start"
    Read [API testing](../../api-testing/index.md) and [Database testing](../index.md) first. You need Docker, and these in a virtual environment: `python -m pip install -r requirements.txt` in both the [practice API](#4-get-something-running) folder and the [template project](#templates) (all pinned).

## Jump to what you need

1. [Why check the database](why-check-the-database.md): what an API answer can't tell you
2. [Verify an API write](verify-an-api-write.md): call, read the row, check each value
3. [Seed then call](seed-then-call.md): put the data in first, then check what the API does with it
4. [Cleanup after API tests](cleanup-after-api-tests.md): rollback can't undo what the app saved
5. [Waiting for late writes](waiting-for-async-writes.md): poll with a timeout, never sleep

## 1. Understand the ask

| You ask | Your lead answers |
| --- | --- |
| Which database, and can I read it? | PostgreSQL 17. A test database you can read and write, never production |
| Where does the price come from? | The `books` table, always. The client never sends a price |
| Is an email unique? | Yes, and `A@x.com` is the same person as `a@x.com` |
| Does the app write anything after it answers? | An `order_created` event, a moment later |
| Do others use the same database? | Yes. Leave nothing behind |

## 2. Picture the system

```mermaid
flowchart LR
    T[test_*.py] -->|"1 POST /orders"| A[Bookshop API]
    A -->|"2 saves the order"| D[(PostgreSQL)]
    A -.->|"3 a moment later:<br/>order_created event"| D
    T -->|"4 reads the rows"| D
    T -->|"5 deletes its rows"| D
```

The test talks to the API like a user, and to the database like a developer. The dotted line is the late write the test must wait for.

## 3. Learn just enough

Read [why check the database](why-check-the-database.md) (10 minutes) and [cleanup after API tests](cleanup-after-api-tests.md). The second one is the part people get wrong most.

## 4. Get something running

The practice API is in `modules/core_automation/api_and_database/examples/bookshop_api`. It has two bugs planted on purpose. From that folder:

```bash
python -m pip install -r requirements.txt
cp .env.example .env              # then change the password
docker compose up -d --wait
export DATABASE_URL=postgresql://shop_tester:local_only_password@127.0.0.1:5432/bookshop
uvicorn app:app --host 127.0.0.1 --port 8090
```

Use the password from your `.env` in `DATABASE_URL`. Then, from the template project folder, in a second terminal:

```bash
export API_URL=http://127.0.0.1:8090
export DATABASE_URL=postgresql://shop_tester:local_only_password@127.0.0.1:5432/bookshop
python -m pytest
```

```text
XFAIL tests/test_create_order.py::test_price_comes_from_the_database_not_the_client - Practice API bug: a price sent by the client is saved
XFAIL tests/test_customers.py::test_same_email_in_capitals_is_refused - Practice API bug: email case is not ignored
9 passed, 2 xfailed in 2.70s
```

9 checks pass. The 2 xfails are the planted bugs, found and marked. Without `API_URL` and `DATABASE_URL`, every test is skipped with the reason: `Set the environment variable DATABASE_URL first`. If port 5432 is taken, set `POSTGRES_PORT=5433` in `.env` and use 5433 in `DATABASE_URL`.

## 5. Decide what to put in

| Check | Example in the template | Finds |
| --- | --- | --- |
| The saved values | `test_order_is_saved_as_the_api_said` | a wrong price, total or status |
| The side effects | `test_order_takes_the_stock` | stock or history not updated |
| A refused request | `test_refused_order_changes_nothing` | half-saved data after an error |
| A rule against known data | `test_price_comes_from_the_database_not_the_client` | the client changing what it shouldn't |
| Duplicates | `test_same_email_in_capitals_is_refused` | two accounts for one person |
| Reads of seeded data | `test_api_shows_what_the_database_holds` | an API that shows the wrong row |
| Late writes | `test_order_event_is_written` | a background job that never runs |

## 6. Write a one-page plan

For each endpoint that writes: which tables change, which values must be exact, which side effects must happen, and what a refused request must leave unchanged. Add who owns the test database, and how tests clean up. The [template project](#templates) is that plan as code for one shop.

## 7. Build in small steps

Start with one `POST` and one `SELECT`. Then add the side effects, then a refused request, then cleanup. Run the whole file twice in a row: if the second run fails, something wasn't cleaned up. Add late writes last.

## 8. Check it with your team

Show the developers the two xfail tests, with `--runxfail` output. Agree on the rules they test: does the price always come from the database? Is email case ignored? Then agree how long the background job may take, and use that as the `wait_for` timeout.

## 9. Keep learning on your own

Next, [data-driven testing](../../automation-testing/data-driven/index.md) runs the same checks over many inputs from a file. For queues and events in bigger systems, see [microservices testing](../../api-testing/microservices/index.md).

!!! tip "How an experienced SDET thinks about this"
    - Check the row against something you know, not only against the answer.
    - A refused request is a write test too: nothing may change.
    - Every row a test makes, the test deletes. Newest first, after the app is done.
    - Wait for late writes with a timeout. Never sleep.

!!! warning "Red flags"
    - "The API returned 201, so it's saved."
    - Tests that only pass on an empty database.
    - `time.sleep(2)` before a database check.
    - A database URL with a password written in a test file.
    - The app's log full of errors while every test is green.

!!! question "Stuck? Try this"
    - **Everything is skipped.** `API_URL` or `DATABASE_URL` isn't set in this terminal. The skip reason names it.
    - **The API says 201, the test finds no row.** The test and the app are using different databases. Compare the two URLs.
    - **The second run fails, the first passed.** A row was left behind. Find the fixture that makes it without `cleanup.add`.
    - **A late-write test is flaky.** Raise the timeout to what the team agreed, and read the app's log.

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/core_automation/api_and_database/templates).

Copy the whole `api_db_tests` folder, or the parts you need. Each file starts with a line that says where it came from.

=== "helpers/clients.py"

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/helpers/clients.py"
    ```

=== "tests/conftest.py"

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/conftest.py"
    ```

=== "test_create_order.py"

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_create_order.py"
    ```

=== "test_seed_then_call.py"

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_seed_then_call.py"
    ```

=== "test_customers.py"

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_customers.py"
    ```

=== "test_background_writes.py"

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_background_writes.py"
    ```

=== "pytest.ini"

    ```ini
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/pytest.ini"
    ```

=== "How to use them"

    1. Copy `api_db_tests`, make a virtual environment, and `python -m pip install -r requirements.txt`.
    2. Set `API_URL` and `DATABASE_URL` in the terminal, or in your pipeline's secret settings. Never in a file.
    3. For your own API: change the paths and fields in the fixtures and tests, the table and column names in the SQL, and the expected values.
    4. Keep `cleanup.add` on every row a test makes, and wait for late writes before cleanup, as `place_order` does.
    5. Point it at a test database only. The tests insert and delete rows.

## Official resources

- [requests documentation](https://requests.readthedocs.io/en/latest/)
- [psycopg 3 documentation](https://www.psycopg.org/psycopg3/docs/)
- [FastAPI: Background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [OWASP: Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)

Written for Python 3.13, pytest 9.2, requests 2.34, psycopg 3.3, FastAPI 0.163 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
