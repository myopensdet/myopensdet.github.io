---
title: "Compare Data Across Databases: Row Counts, Checksums and Values"
description: "Prove two databases hold the same data: compare row counts, then a checksum of each whole table, then the exact rows and fields that differ, after normalizing each database's types."
level: Intermediate
tags:
  - Database
  - pytest
  - Test data
nav_title: "Cross-database comparison"
order: 60
summary: "Counts, then checksums, then the exact values that differ."
updated: "2026-11-22"
---

# Compare Data Across Databases: Row Counts, Checksums and Values

"Do these two databases hold the same data?" sounds like one question. It's three, from cheap to detailed: **the same number of rows? the same fingerprint? and if not, which values differ?** Asked in that order, a comparison is fast when the data matches, and precise when it doesn't.

!!! note "Before you start"
    Read [One client, many drivers](one-client-many-drivers.md), especially the types each database returns.

## What you will learn

- Why values must be normalized before comparing
- How to compare row counts, checksums and values
- How to read a comparison failure
- How to pick the key that matches rows up

## Why this matters at work

After a migration, a copy job or a sync, somebody asks "is it all there?". Counting rows by hand in two tools isn't an answer. A comparison test that names every missing row and changed value is, and it can run every night.

## The idea in plain words

!!! info "In plain words"
    Checking two copies of a long book. First, count the pages. Then weigh them: same weight, almost certainly the same book. Only if the weight differs do you read page by page to find what changed.

## Step by step

1. **Normalize first.** The same price comes back as `Decimal('49.50')` from PostgreSQL, `49.5` from SQLite and `Decimal128('49.50')` from MongoDB. One time has a time zone, another doesn't. Compared raw, they all "differ". `normalize()` in `db_clients/base_client.py` writes each value one way:

    - numbers and money: `"49.5"`, the same from every database
    - times: `"2026-10-03 12:00:00"`, in UTC
    - everything else: as text

    Normalize only what really differs between databases. Never round or trim values in the normalizer: that would hide real bugs.

2. **Pick the key.** Rows are matched by a column that identifies them. Here it's `id`, set in `config/databases.yaml` under `compare.tables`. If ids are made again in the target (a new auto-increment), use a natural key instead, like the email or an order number.

3. **Read the comparison tests.** `tests/test_cross_db_compare.py`:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/tests/test_cross_db_compare.py"
    ```

    - `test_row_counts_match`: the cheapest check. It finds lost and doubled rows.
    - `test_same_data_as_the_source`: a checksum of each whole table. If the fingerprints match, it stops. If not, `differences()` lists rows missing, rows extra, and every changed value, with the old and new value.

4. **Run it.** The source is PostgreSQL, and the three others are compared against it:

    ```bash
    python -m pytest -v tests/test_cross_db_compare.py
    ```

    ```text
    tests/test_cross_db_compare.py::test_row_counts_match[mysql-customers] PASSED [  2%]
    tests/test_cross_db_compare.py::test_row_counts_match[mysql-orders] PASSED [  4%]
    tests/test_cross_db_compare.py::test_row_counts_match[sqlite-customers] PASSED [  6%]
    tests/test_cross_db_compare.py::test_row_counts_match[sqlite-orders] PASSED [  9%]
    tests/test_cross_db_compare.py::test_row_counts_match[mongo-customers] PASSED [ 11%]
    tests/test_cross_db_compare.py::test_row_counts_match[mongo-orders] PASSED [ 13%]
    tests/test_cross_db_compare.py::test_same_data_as_the_source[mysql-customers] PASSED [ 15%]
    tests/test_cross_db_compare.py::test_same_data_as_the_source[mysql-orders] PASSED [ 18%]
    tests/test_cross_db_compare.py::test_same_data_as_the_source[sqlite-customers] PASSED [ 20%]
    tests/test_cross_db_compare.py::test_same_data_as_the_source[sqlite-orders] PASSED [ 22%]
    tests/test_cross_db_compare.py::test_same_data_as_the_source[mongo-customers] PASSED [ 25%]
    tests/test_cross_db_compare.py::test_same_data_as_the_source[mongo-orders] PASSED [ 27%]
    ```

    (These lines are from the full run, so the percentages stop at 27%.)

5. **Read a failure.** The [migration lesson](migration-and-etl-validation.md) copies the data with a buggy job. Here's what the comparison says about it:

    ```text
    E       AssertionError: assert 7 == 8
    E        +  where 7 = count('orders')
    ...
    E       Failed: mysql.customers differs from postgres in 1 places:
    E       id=5 full_name: 'María José Fernández-Castillo Example' -> 'María José Fernández-Castillo '
    ...
    E       Failed: mysql.orders differs from postgres in 8 places:
    E       id=4: missing
    E       id=1 created_at: '2026-10-02 10:00:00' -> '2026-10-02 16:00:00'
    E       id=2 created_at: '2026-10-03 12:00:00' -> '2026-10-03 18:00:00'
    E       id=3 created_at: '2026-10-31 23:30:00' -> '2026-11-01 05:30:00'
    ...
    ```

    Read it top down. 7 orders where there should be 8. Order 4 is the missing one. A name was cut at 30 letters. Every time is 6 hours late. That's three separate bugs, each with the row that proves it.

    !!! success "Check: you should now be able to"
        Normalize values, compare counts, checksums and values, and read a comparison failure.

## When it goes wrong

- **Thousands of differences, all in one column.** A type or format difference, not a data one: `'49.5'` against `'49.50'`, or one side in local time. Fix the normalizer, or the copy. Check five rows by hand first, to know which one it is.
- **Every row is "missing" and "extra" at once.** The keys don't match: `1` against `'1'`, or new ids in the target. Normalize the key, or match on a natural key.
- **The checksum differs, but the value list is empty.** The difference is in a column that isn't in the source rows, such as an extra column in the target. Compare `columns()` too.
- **It's slow on big tables.** Comparing every row in Python works for test data and medium tables. For millions of rows, compare per-day counts and sums inside each database first, then compare only the days that differ.

## Common mistakes

!!! warning "Common mistakes"
    - **Comparing raw values.** Normalize first, or every row "differs".
    - **Rounding in the normalizer.** It hides real money bugs.
    - **Only checking counts.** Counts can't see changed values.
    - **Showing every difference.** The template shows the first ten and the total. Nobody reads ten thousand lines.

!!! failure "If you see this error"
    **`decimal.InvalidOperation`** while sorting rows.
    The key column has a value that isn't a number, like an email or a code. `rows()` sorts keys as numbers. For text keys, change the sort in `rows()` to plain text.

## Try it yourself

Add a check that every target has exactly the same columns as the source, for every table.

??? success "Solution"
    ```python
    @pytest.mark.parametrize("table", TABLES)
    def test_same_columns_as_the_source(source, target, table):
        assert target.columns(table) == source.columns(table)
    ```

    `columns()` works the same on SQL and MongoDB, because it's part of the base client.

## Quick check

1. In what order are the three checks, and why?

    ??? question "Answer"
        Counts, then checksums, then values: cheapest first, most detail last, and only when needed.

2. Why mustn't the normalizer round values?

    ??? question "Answer"
        It would make real money differences disappear.

3. What does "every row missing and extra" usually mean?

    ??? question "Answer"
        The keys don't match between the two sides.

## References

- [Python: hashlib](https://docs.python.org/3/library/hashlib.html)
- [Python: decimal](https://docs.python.org/3/library/decimal.html)
- [PyMongo: BSON Decimal128](https://pymongo.readthedocs.io/en/stable/api/bson/decimal128.html)

Written for Python 3.13, pytest 9.2, PostgreSQL 17, MySQL 8.4, SQLite 3 and MongoDB 8.0. Outputs captured November 2026. Links checked: November 2026.
