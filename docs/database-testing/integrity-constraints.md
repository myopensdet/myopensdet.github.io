---
title: "Test Database Constraints: Primary Key, Foreign Key, NOT NULL, UNIQUE"
description: "Prove the database itself refuses bad rows: test primary keys, foreign keys, NOT NULL, UNIQUE and CHECK rules from pytest, by inserting bad data on purpose and expecting the exact error."
level: Intermediate
tags:
  - Database
  - pytest
  - Test design
nav_title: "Integrity: keys and rules"
order: 50
summary: "Insert bad rows on purpose and prove the database refuses each one."
updated: "2026-11-22"
---

# Test Database Constraints: Primary Key, Foreign Key, NOT NULL, UNIQUE

The app checks what users type. But data also arrives from imports, scripts, other services and people fixing things by hand. The last line of defence is the database itself: its **constraints**, the rules written into the tables. An integrity test inserts a bad row on purpose and expects the database to refuse it. If the database takes the row, the rule is missing.

!!! note "Before you start"
    Read [Schema tests](schema-tests.md). The tests here use the template's `db` fixture and `db.savepoint()`, explained in [Transactions and clean-up](transactions-and-cleanup.md).

## What you will learn

- The five rules: primary key, foreign key, `NOT NULL`, `UNIQUE` and `CHECK`
- How to test that a bad row is refused, with the exact error
- Why every refusal test needs a matching "good row is accepted" test
- What `ON DELETE CASCADE` does, and how to test it

## Why this matters at work

"Orders with no customer" and "two accounts with one email" are real production bugs. They come from a rule nobody wrote, or one a migration dropped. A failed constraint test names the missing rule before bad data piles up. Bad data is much harder to clean up later than to keep out.

## The idea in plain words

!!! info "In plain words"
    Constraints are the bouncer at the door of each table. An integrity test sends in someone without a ticket on purpose, and checks the bouncer says no.

## Step by step

1. **Know the five rules.** All of them are in the template's `sql/schema.sql`:

    | Rule | Means | Example in the bookshop |
    | --- | --- | --- |
    | Primary key | Every row has a unique id that is never empty | `orders.id` |
    | Foreign key | This value must exist in another table | `orders.customer_id` must be a real `customers.id` |
    | `NOT NULL` | The value can't be empty | `customers.email` |
    | `UNIQUE` | No two rows have the same value | `customers.email` |
    | `CHECK` | The value must pass a condition | `books.price > 0`, `stock >= 0` |

2. **Prove a good row gets in first.** Otherwise a refusal test could pass because every insert fails, for example from a typo in a column name:

    ```python
    def test_good_row_is_accepted(db):
        assert db.run(GOOD_CUSTOMER, ("new.customer@example.com", "New Customer")) == 1
    ```

3. **Expect the exact refusal.** psycopg raises a different error class for each rule, in `psycopg.errors`. Expect the precise one. A plain `Exception` would also pass on a typo or a lost connection:

    ```python
    --8<-- "modules/core_automation/database_testing/templates/shop_db_tests/tests/test_integrity.py"
    ```

    `with pytest.raises(...), db.savepoint():` does two jobs. `pytest.raises` passes the test only if that error happens. `db.savepoint()` undoes the failed insert, because after an error PostgreSQL refuses every later query in the same transaction until something rolls back.

4. **Run it.**

    ```bash
    python -m pytest tests/test_integrity.py -v
    ```

    ```text
    tests/test_integrity.py::test_good_row_is_accepted PASSED                [ 10%]
    tests/test_integrity.py::test_email_is_required PASSED                   [ 20%]
    tests/test_integrity.py::test_email_must_be_unique PASSED                [ 30%]
    tests/test_integrity.py::test_order_needs_a_real_customer PASSED         [ 40%]
    tests/test_integrity.py::test_check_rules[price must be above 0] PASSED  [ 50%]
    tests/test_integrity.py::test_check_rules[stock can't go below 0] PASSED [ 60%]
    tests/test_integrity.py::test_check_rules[status must be a known one] PASSED [ 70%]
    tests/test_integrity.py::test_order_id_is_made_by_the_database PASSED    [ 80%]
    tests/test_integrity.py::test_customer_with_orders_cant_be_deleted PASSED [ 90%]
    tests/test_integrity.py::test_deleting_an_order_deletes_its_items PASSED [100%]
    ```

5. **See it catch a missing rule.** Take `UNIQUE` off `email` in the schema, as a careless migration might. The database now takes a second `arshad@example.com`, and the test says so:

    ```text
        def test_email_must_be_unique(db):
    >       with pytest.raises(errors.UniqueViolation), db.savepoint():
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    E       Failed: DID NOT RAISE UniqueViolation
    ```

    "DID NOT RAISE" means the bad row got in. That's a bug in the schema, not in the test.

6. **Test what happens on delete.** A foreign key also decides what happens when the row it points at is deleted. Two common choices, both in the template:

    - Deleting a customer who has orders is refused (`ForeignKeyViolation`). Order history must not lose its customer.
    - Deleting an order deletes its items too (`ON DELETE CASCADE`). Items make no sense without their order.

    Ask the team which one each link should have, and test it.

    !!! success "Check: you should now be able to"
        Name the five rules, test that each one refuses a bad row with the exact error, and test what a delete does to linked rows.

## When it goes wrong

- **Every refusal test passes, even with the rule removed.** You're catching a broad error like `Exception` or `psycopg.Error`. Expect the exact class, and keep the "good row is accepted" test.
- **`InFailedSqlTransaction` in the next query.** The bad insert failed outside a savepoint, so the transaction is in an error state. Put `db.savepoint()` in the same `with` as `pytest.raises`.
- **The `CHECK` test fails with `NotNullViolation`.** Your bad row is missing a required column, so a different rule fires first. Give the bad row every required value, and break only the one rule you're testing.
- **Capital letters get past `UNIQUE`.** `ARSHAD@example.com` and `arshad@example.com` are different text. See the [JOIN and GROUP BY lesson](joins-and-group-by.md). Test it, and report it if the team agrees it's a bug.

## Common mistakes

!!! warning "Common mistakes"
    - **Testing only the app's form checks.** Data also comes in through imports and scripts. Test the database's own rules too.
    - **One test for every rule at once.** When it fails, you don't know which rule. One rule per test, or per `parametrize` case.
    - **Forgetting the delete rules.** Ask what should happen to orders when a customer is deleted, and test that answer.

!!! failure "If you see this error"
    **`psycopg.errors.GeneratedAlways: cannot insert a non-DEFAULT value into column "id"`**
    The id is made by the database (`GENERATED ALWAYS AS IDENTITY`), and your insert gave one. Leave `id` out of the insert, and read it back with `RETURNING id`. The template has a test that expects exactly this refusal.

## Try it yourself

`order_items.quantity` has `CHECK (quantity > 0)`. Add a case to `test_check_rules` that proves an item with quantity 0 is refused.

??? success "Solution"
    Add this tuple to the list, with the id `"quantity must be above 0"`:

    ```python
    ("INSERT INTO order_items (order_id, book_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
     (3, 1, 0, 24.99)),
    ```

    Order 3 and book 1 both exist, and order 3 doesn't contain book 1 yet. So only the quantity rule can fail, and the test proves that rule alone.

## References

- [PostgreSQL: Constraints](https://www.postgresql.org/docs/17/ddl-constraints.html)
- [PostgreSQL: Identity columns](https://www.postgresql.org/docs/17/ddl-identity-columns.html)
- [psycopg 3: Error classes (psycopg.errors)](https://www.psycopg.org/psycopg3/docs/api/errors.html)
- [pytest: Assertions about expected exceptions](https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
