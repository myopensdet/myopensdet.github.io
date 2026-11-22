---
title: "Data Validation Tests: Business Rules as SQL Queries"
description: "Turn business rules into SQL queries that find the rows breaking them, and run them in pytest: totals that don't add up, orders with no items, duplicate emails ignoring case."
level: Intermediate
tags:
  - Database
  - pytest
  - Test data
nav_title: "Data validation"
order: 70
summary: "Write each business rule as a query that must return zero rows."
updated: "2026-11-22"
---

# Data Validation Tests: Business Rules as SQL Queries

Constraints can't hold every rule. "An order's total equals the sum of its items" spans two tables. "No two customers share an email, ignoring capitals" needs `LOWER()`. Rules like these are checked with **data validation** queries: each one finds the rows that break a rule. A healthy database returns zero rows for every rule.

!!! note "Before you start"
    Read [JOIN, GROUP BY and subqueries](joins-and-group-by.md). The rules use all three.

## What you will learn

- How to turn a business rule into a "find the rows that break it" query
- How to run a list of rules as one parametrized test
- How to prove a rule works by breaking it on purpose
- Where else these rules are useful: after imports, migrations and in production checks

## Why this matters at work

Data goes bad slowly: a bug in one release, a manual fix, a half-finished import. Nobody notices until a report is wrong. A list of rule queries, run in the pipeline and against staging after each deploy, finds it in days instead of months. And each production data bug becomes one more rule, so it can't come back unnoticed.

## The idea in plain words

!!! info "In plain words"
    Each rule is a question with only one healthy answer: "show me every order whose total doesn't add up". An empty list means all is well. Any row in the list is a problem, with its id, ready for the bug report.

## Step by step

1. **Write the rule in plain words first.** Ask the business, not the database: "the total is the sum of the items", "every order has at least one item", "an email belongs to one customer".

2. **Turn it into a query that finds the breakers.** For "the total is the sum of the items": group items by order, add them up, and keep the orders where the sum differs. Return the ids and the numbers, so a failure explains itself.

3. **Keep the rules in a list, and test each one.** The template's `tests/test_data_rules.py`:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_data_rules.py"
    ```

    The dict key is the rule in plain words. `parametrize` makes it the test name, so the report reads like the business rules.

4. **Run it.**

    ```bash
    python -m pytest tests/test_data_rules.py -v
    ```

    ```text
    tests/test_data_rules.py::test_rule_holds[order total equals the sum of its items] PASSED [ 16%]
    tests/test_data_rules.py::test_rule_holds[every order has at least one item] PASSED [ 33%]
    tests/test_data_rules.py::test_rule_holds[no two customers share an email, ignoring case] PASSED [ 50%]
    tests/test_data_rules.py::test_rule_holds[emails look like emails] PASSED [ 66%]
    tests/test_data_rules.py::test_rule_holds[updated_at is never before created_at] PASSED [ 83%]
    tests/test_data_rules.py::test_rules_catch_bad_data PASSED               [100%]
    ```

5. **See a rule catch bad data.** Change order 2's total in the seed from 49.50 to 49.00, as a rounding bug might. The rule names the order, the saved total and what the items add up to:

    ```text
    E       AssertionError: 1 rows break the rule: [{'id': 2, 'total': Decimal('49.00'), 'items_total': Decimal('49.50')}]
    E       assert [{'id': 2, 't...mal('49.50')}] == []
    ...
    FAILED tests/test_data_rules.py::test_rule_holds[order total equals the sum of its items]
    ```

    That message is most of a bug report already.

6. **Prove each rule can fail.** A rule query with a mistake in it returns zero rows forever, and passes forever. `test_rules_catch_bad_data` breaks the data on purpose and checks the rule finds it. Do this once for every new rule.

7. **Use the same rules outside the tests.** The queries are plain SQL. Run them after a data import, after a migration, or every night against staging (read-only). Ask before running anything against production, even a `SELECT`: a slow query can slow the live site.

    !!! success "Check: you should now be able to"
        Turn a business rule into a query that finds the rows breaking it, run a list of rules in pytest, and prove a rule works.

## When it goes wrong

- **A rule passes on data you know is bad.** The query is wrong. Break the data on purpose, as in step 6, and fix the query until it finds the row.
- **A rule fails on thousands of rows at once.** Either the rule is wrong or the data has been bad for a long time. Check five rows by hand. Then ask the team. Don't just delete the rule.
- **The failure message is huge.** The template shows the first five rows only (`broken[:5]`) and the count. Keep it that way.
- **A rule is slow on a big table.** Rule queries scan whole tables. Run them on a copy or at quiet times, and ask whether an index would help.

## Common mistakes

!!! warning "Common mistakes"
    - **Rules that only return a count.** Return the ids and values, so a failure tells you which rows.
    - **Never proving a rule can fail.** A broken query passes forever.
    - **Inventing rules.** Ask the business what the rule is. "Total includes tax?" is their call, not yours.

!!! failure "If you see this error"
    **`ERROR:  aggregate functions are not allowed in WHERE`**
    A rule like `WHERE SUM(...) <> o.total` puts a total in `WHERE`. Rules about totals go in `HAVING`, after `GROUP BY`. See the first rule in the template.

## Try it yourself

Write a rule: "a cancelled order was never shipped". Use the `order_status_history` table the trigger fills (see [Stored procedures and triggers](procedures-and-triggers.md)).

??? success "Solution"
    ```python
    "a cancelled order was never shipped": """
        SELECT o.id FROM orders o
        JOIN order_status_history h ON h.order_id = o.id
        WHERE o.status = 'cancelled' AND h.new_status = 'shipped'
    """,
    ```

    Prove it can fail: in a test, change an order to `shipped`, then to `cancelled`, and check the rule finds it.

## Quick check

1. What's the healthy answer for every rule query?

    ??? question "Answer"
        Zero rows.

2. Why test that a rule finds bad data?

    ??? question "Answer"
        A rule query with a mistake in it returns zero rows forever, and passes forever.

3. Where else can you run the rules?

    ??? question "Answer"
        After imports and migrations, and on a schedule against staging. Production only after asking.

## References

- [PostgreSQL tutorial: Aggregate functions](https://www.postgresql.org/docs/17/tutorial-agg.html)
- [PostgreSQL: Pattern matching with LIKE](https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-LIKE)
- [pytest: Parametrizing tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
