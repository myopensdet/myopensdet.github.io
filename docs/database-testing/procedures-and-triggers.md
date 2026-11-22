---
title: "How to Test Stored Procedures and Triggers in PostgreSQL"
description: "Test code that runs inside the database: call a stored function from pytest and check every table it changes, test that a trigger fires (and doesn't), and avoid the now() trap inside transactions."
level: Intermediate
tags:
  - Database
  - pytest
nav_title: "Stored procedures and triggers"
order: 80
summary: "Call database functions, check every table they touch, and test triggers."
updated: "2026-11-22"
---

# How to Test Stored Procedures and Triggers in PostgreSQL

Some logic lives inside the database, not in the app. A **stored procedure** (in PostgreSQL usually a *function*) is code you call by name: `place_order(customer, book, quantity)`. A **trigger** is code that runs by itself when a row changes: "when an order's status changes, write it to the history table". Both are easy to forget in testing, because no screen shows them. Test them the same way: set up, act, then check every table they should change, and the ones they shouldn't.

!!! note "Before you start"
    Read [CRUD tests](crud-tests.md) and [Integrity: keys and rules](integrity-constraints.md). The function and the trigger are in the template's `sql/schema.sql`.

## What you will learn

- How to see which functions and triggers a database has
- How to call a stored function from pytest and check all its effects
- How to test that a trigger fires, and that it doesn't fire when it shouldn't
- Why `now()` doesn't move inside a transaction, and what to use instead

## Why this matters at work

Database code is often old, written by someone who left, and has no tests. When it breaks, money goes wrong: stock taken twice, an order saved without its items. Testing it from outside, through its effects on the tables, works without reading every line of it.

## The idea in plain words

!!! info "In plain words"
    A stored function is a vending machine: put in the money and a number, and check you get the snack, the change, and one fewer snack in the machine. A trigger is the machine's counter that ticks by itself every time. You test it by buying something and checking the counter moved.

## Step by step

1. **Find what's there.** In `psql`, `\df` lists functions. `\d orders` shows the table, and its triggers at the bottom:

    ```text
                                                      List of functions
     Schema |       Name        | Result data type |                     Argument data types                      | Type
    --------+-------------------+------------------+--------------------------------------------------------------+------
     public | log_status_change | trigger          |                                                              | func
     public | place_order       | integer          | p_customer_id integer, p_book_id integer, p_quantity integer | func
    (2 rows)
    ```

    Read each function's code once (`\sf place_order`) and write down what it should change. For `place_order`: take stock from the book, write an order with the right total, write one item, return the new order id. And if there isn't enough stock: change nothing and raise an error.

2. **Try it by hand, inside a transaction.** `ROLLBACK` at the end undoes everything:

    ```sql
    BEGIN;
    SELECT place_order(2, 1, 3) AS new_order_id;
    SELECT id, title, stock FROM books WHERE id = 1;
    SELECT place_order(1, 3, 1);
    ROLLBACK;
    ```

    ```text
    BEGIN
     new_order_id
    --------------
                6
    (1 row)

     id |       title        | stock
    ----+--------------------+-------
      1 | Python for Testers |     7
    (1 row)

    ERROR:  Not enough stock for book 3
    CONTEXT:  PL/pgSQL function place_order(integer,integer,integer) line 11 at RAISE
    ROLLBACK
    ```

    Stock went from 10 to 7. Book 3 has none, so the second call was refused.

3. **Turn it into tests.** A function is called with `SELECT`. A procedure (made with `CREATE PROCEDURE`) is called with `CALL`. The template's tests:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_procedures_and_triggers.py"
    ```

    Look at what each test checks:

    - **The good case checks every table:** stock, the order, the total and the item. Checking only the return value would miss a function that forgot the item.
    - **The refusal checks nothing changed:** same number of orders, same stock. "All or nothing" is the promise, and this test holds it to that.
    - **A negative quantity:** `stock - (-2)` would *add* stock. The `CHECK` on `order_items` stops it, and the whole function is undone. The test proves the stock is still 10.

4. **Test the trigger fires.** Change the status, then look in the history table:

    ```sql
    BEGIN;
    UPDATE orders SET status = 'shipped' WHERE id = 1;
    SELECT order_id, old_status, new_status FROM order_status_history;
    ROLLBACK;
    ```

    ```text
    BEGIN
    UPDATE 1
     order_id | old_status | new_status
    ----------+------------+------------
            1 | paid       | shipped
    (1 row)

    ROLLBACK
    ```

    And test it doesn't fire when it shouldn't: setting the same status again must not add a history row (`test_same_status_is_not_logged`). Triggers that fire too often are as common as triggers that don't fire.

5. **Watch out for `now()` inside a transaction.** In PostgreSQL, `now()` is the time the transaction *started*. It doesn't move until the transaction ends. `clock_timestamp()` is the real time:

    ```sql
    BEGIN;
    SELECT now(), clock_timestamp();
    SELECT pg_sleep(1);
    SELECT now(), clock_timestamp();
    ROLLBACK;
    ```

    ```text
                  now              |       clock_timestamp
    -------------------------------+------------------------------
     2026-11-16 07:46:49.506637+00 | 2026-11-16 07:46:49.50681+00
    (1 row)
    ...
                  now              |        clock_timestamp
    -------------------------------+-------------------------------
     2026-11-16 07:46:49.506637+00 | 2026-11-16 07:46:50.515602+00
    (1 row)
    ```

    One second later, `now()` hasn't moved. This matters twice. In the app: a trigger that sets `updated_at := now()` sets the same time as `created_at` when both happen in one transaction. In tests: every test runs in one transaction (the [clean-up lesson](transactions-and-cleanup.md)), so `now()` never moves during a test. With `now()` in the trigger, `test_status_change_moves_updated_at` fails:

    ```text
    >       assert times["updated_at"] > times["created_at"]
    E       AssertionError: assert datetime.datetime(2026, 11, 16, 7, 44, 0, 134984, tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')) > datetime.datetime(2026, 11, 16, 7, 44, 0, 134984, tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC'))
    ```

    Same time, to the microsecond. The test makes a brand-new order on purpose, because that's the case where it shows. A test on an old seed row would have passed and hidden it.

    !!! success "Check: you should now be able to"
        List a database's functions, call one from pytest and check every table it touches, and test that a trigger fires only when it should.

## When it goes wrong

- **`ERROR:  function place_order(integer, integer) does not exist`.** Wrong number or types of arguments. PostgreSQL finds a function by its name *and* its argument types. Check with `\df place_order`.
- **The function works by hand but not in the test.** The test's search path is different, so it can't see the function. Check `SELECT current_schema();` in both, or write the schema in front: `public.place_order(...)`.
- **A trigger test passes even with the trigger dropped.** The test checks something the app also does. Check something only the trigger does, like the history row.
- **A time check fails by exactly zero.** `now()` inside one transaction. See step 5.

## Common mistakes

!!! warning "Common mistakes"
    - **Checking only the return value.** Check every table the function should change.
    - **Not testing the refusal.** "Nothing changed" is half the promise.
    - **Testing triggers only for firing.** Also test they don't fire when nothing changed.

!!! failure "If you see this error"
    **`psycopg.errors.RaiseException: Not enough stock for book 3`**
    The function itself raised this on purpose, with `RAISE EXCEPTION`. In a test that expects it, catch exactly this class and check the message: `pytest.raises(errors.RaiseException, match="Not enough stock")`.

## Try it yourself

Write a test that `place_order` with an unknown customer id (99999) raises an error and leaves the stock as it was.

??? success "Solution"
    ```python
    def test_place_order_refuses_an_unknown_customer(db):
        with pytest.raises(errors.ForeignKeyViolation), db.savepoint():
            db.value("SELECT place_order(%s, %s, %s)", (99999, 1, 1))
        assert stock(db, 1) == 10
    ```

    The stock was already taken when the order insert failed. The error undid the whole function, stock included, and the test proves it.

## Quick check

1. How do you call a function, and how a procedure?

    ??? question "Answer"
        A function with `SELECT name(...)`. A procedure with `CALL name(...)`.

2. What does `now()` return inside a transaction?

    ??? question "Answer"
        The time the transaction started. It doesn't move. `clock_timestamp()` is the real time.

3. Why does the trigger test check the history table, not just the status?

    ??? question "Answer"
        The status changes without the trigger too. Only the history row proves the trigger ran.

## References

- [PostgreSQL: PL/pgSQL](https://www.postgresql.org/docs/17/plpgsql.html)
- [PostgreSQL: Trigger functions](https://www.postgresql.org/docs/17/plpgsql-trigger.html)
- [PostgreSQL: CREATE PROCEDURE and CALL](https://www.postgresql.org/docs/17/sql-createprocedure.html)
- [PostgreSQL: Current date and time (now and clock_timestamp)](https://www.postgresql.org/docs/17/functions-datetime.html#FUNCTIONS-DATETIME-CURRENT)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
