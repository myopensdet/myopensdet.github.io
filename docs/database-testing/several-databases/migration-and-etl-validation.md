---
title: "How to Test a Database Migration or ETL Job"
description: "Test a data migration or copy job the way a tester would: load known data into the source, run the job, and compare source and target by counts, values and business reports. With a real buggy job and what the tests found."
level: Intermediate
tags:
  - Database
  - pytest
  - Test design
nav_title: "Migration and ETL validation"
order: 70
summary: "Run the copy job, then compare source and target until nothing differs."
updated: "2026-11-22"
---

# How to Test a Database Migration or ETL Job

A **migration** moves data from one database to another, often once. An **ETL** job (Extract, Transform, Load) copies it again and again, changing it on the way, for example every night into a reporting database. Either way, the job is code, and it has bugs. You test it like any code: known input, run it, check the output.

!!! note "Before you start"
    Read [Cross-database comparison](cross-database-comparison.md). The checks here are the same tests, pointed at the job's output.

## What you will learn

- The test loop for a migration: known data in, job, compare
- What test data finds the most migration bugs
- How to run the template's comparison against a real job
- Three real bugs from a copy job, and which check caught each

## Why this matters at work

Migrations happen once, under time pressure, and nobody wants to do them twice. The data that goes wrong is usually the unusual data: accents, long names, cancelled orders, times near midnight. A tester who plans for that data saves the company from finding out in production.

## The idea in plain words

!!! info "In plain words"
    Moving house. Before the move, you list every box. After the move, you check every box arrived, nothing inside broke, and the fragile ones got special care. Then you test the house works: does the kitchen still cook?

## Step by step

1. **Ask what the job should do.** For each table: copy everything, or filter? Change any values (currencies, time zones, formats)? Which side is the source of truth? Write the answers down. A "bug" you find may be a rule nobody told you.

2. **Build test data that breaks migrations.** The template's `test_data/` has, on purpose:

    - a name with accents (`Zoë Exämple`) and a long one (`María José Fernández-Castillo Example`)
    - every status, including `cancelled`
    - an order at 23:30 on the last day of a month, where a time zone shift moves it into the next month
    - money with and without cents (`15.00`, `0.99`, `120.00`)

    Add your own edge cases: empty values, the biggest numbers, emoji, the oldest and newest dates.

3. **Load the source, run the job, compare.** `examples/etl_copy.py` is a copy job from PostgreSQL to MySQL. It has three bugs, the kind real jobs have. Load test data into PostgreSQL only, run the job, then compare:

    ```bash
    TEST_DATABASES=postgres LOAD_TEST_DATA=postgres python -m pytest -q tests/test_schema.py
    python ../../examples/etl_copy.py
    ```

    ```text
    Copied 6 customers and 7 orders to MySQL
    ```

    ```bash
    TEST_DATABASES=postgres,mysql LOAD_TEST_DATA=postgres python -m pytest -q tests/test_cross_db_compare.py
    ```

    ```text
    E       AssertionError: assert 7 == 8
    E       Failed: mysql.customers differs from postgres in 1 places:
    E       id=5 full_name: 'María José Fernández-Castillo Example' -> 'María José Fernández-Castillo '
    E       Failed: mysql.orders differs from postgres in 8 places:
    E       id=4: missing
    E       id=1 created_at: '2026-10-02 10:00:00' -> '2026-10-02 16:00:00'
    ...
    FAILED tests/test_cross_db_compare.py::test_row_counts_match[mysql-orders] - ...
    FAILED tests/test_cross_db_compare.py::test_same_data_as_the_source[mysql-customers]
    FAILED tests/test_cross_db_compare.py::test_same_data_as_the_source[mysql-orders]
    3 failed, 1 passed in 0.09s
    ```

    `LOAD_TEST_DATA=postgres` matters: MySQL must keep what the job wrote, not fresh test data.

4. **Match each failure to its bug.** Look at the job's code:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/examples/etl_copy.py"
    ```

    | What the test said | The bug | Found by |
    | --- | --- | --- |
    | 7 orders, not 8; order 4 missing | Cancelled orders skipped | Row count |
    | Name cut at 30 letters | `[:30]` "names are never that long" | Values (and the long name in the test data) |
    | Every time 6 hours late | Dhaka time written as UTC | Values |

5. **Check the business answer too.** Value checks prove the copy. A report proves it's *useful*. The same "orders per month" query on the MySQL copy:

    ```bash
    TEST_DATABASES=mysql LOAD_TEST_DATA=none python -m pytest -q tests/test_data_integrity.py -k month
    ```

    ```text
    E       AssertionError: assert [('2026-10', ...'2026-11', 5)] == [('2026-10', ...'2026-11', 5)]
    E
    E         At index 0 diff: ('2026-10', 2) != ('2026-10', 3)
    ```

    October lost an order. The order at 23:30 on 31 October moved to 1 November, because of the 6-hour shift. That's the bug the finance team would have noticed at the end of the month. The test found it before the job ran for real.

6. **Run it again after the fix, and keep it.** When the developer fixes the job, the same commands must pass with nothing changed in the tests. For an ETL job that runs every night, run the comparison every night too, on real data (read-only), and alert when it fails.

    !!! success "Check: you should now be able to"
        Plan test data for a migration, run a job between a loaded source and a compare, and trace each failure to its bug.

## When it goes wrong

- **The target is reloaded before the compare.** Then you're testing your test data, not the job. Load only the source: `LOAD_TEST_DATA=postgres`.
- **MySQL refuses a long name: `ERROR 1406 (22001): Data too long for column 'full_name'`.** Good: MySQL's strict mode stopped a silent cut. A job that cuts text itself, as this one does, gets past it. Test with long values on purpose.
- **Accents turn into `?` or `Ã«`.** The target or the connection isn't using full Unicode. In MySQL, use `utf8mb4` for the tables and the connection.
- **Ids are new in the target.** The job let the target make its own ids. Compare on a natural key (email, order number) instead of `id`.
- **The real job takes hours.** Test it on a small, hand-picked copy of the data first. Run the full comparison once, at the end, with per-day counts and sums.

## Common mistakes

!!! warning "Common mistakes"
    - **Testing with only "normal" data.** Migrations break on accents, long text, odd statuses and midnight times.
    - **Checking only that the job finished without errors.** Most migration bugs don't raise errors.
    - **Testing the migration only once.** Run it again after every fix, and on a copy of production data before the real day.

!!! failure "If you see this error"
    **`AssertionError: assert 7 == 8`** in `test_row_counts_match`.
    Rows went missing (or, with the numbers the other way round, were doubled). Run the value comparison to see which ids, then look for a filter or an error in the job that skips rows.

## Try it yourself

Fix all three bugs in a copy of `etl_copy.py`, run it, and run the comparison again. What should it say?

??? success "Solution"
    Remove the `[:30]`, the `status != "cancelled"` filter and the `+ timedelta(hours=6)`. Keep `created_at` as it comes from PostgreSQL: the MySQL client saves it in UTC. Then the comparison passes:

    ```text
    4 passed
    ```

    Two row-count tests and two value tests, for `customers` and `orders`.

## References

- [MySQL: Strict SQL mode](https://dev.mysql.com/doc/refman/8.4/en/sql-mode.html#sql-mode-strict)
- [MySQL: The utf8mb4 character set](https://dev.mysql.com/doc/refman/8.4/en/charset-unicode-utf8mb4.html)
- [PostgreSQL: Date/time types and time zones](https://www.postgresql.org/docs/17/datatype-datetime.html)
- [Python: datetime and time zones](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects)

Written for Python 3.13, pytest 9.2, PostgreSQL 17 and MySQL 8.4. Outputs captured November 2026. Links checked: November 2026.
