---
title: "SQL JOIN, GROUP BY and Subqueries for Testers"
description: "Join tables to see an order with its customer, find rows with nothing linked using LEFT JOIN, find duplicates with GROUP BY and HAVING, and compare against a subquery."
level: Intermediate
tags:
  - Database
nav_title: "JOIN, GROUP BY and subqueries"
order: 20
summary: "Join tables, find missing links and duplicates, and compare with a subquery."
updated: "2026-11-22"
---

# SQL JOIN, GROUP BY and Subqueries for Testers

One table rarely answers a tester's question. "Which customer placed order 3?" needs `orders` and `customers`. "Did anyone sign up twice?" needs rows grouped together. This lesson covers the three tools for that: **JOIN**, **GROUP BY** and **subqueries**. Most data bugs are found with one of them.

!!! note "Before you start"
    Read [SQL for testers](sql-for-testers.md) first, and keep the bookshop database open in `psql`.

## What you will learn

- `JOIN` to read two tables together
- `LEFT JOIN ... WHERE ... IS NULL` to find rows with nothing linked
- `GROUP BY` and `HAVING` to count per group and find duplicates
- Subqueries: a query inside a query

## Why this matters at work

"The report shows 6 orders but the screen shows 5." "A customer got two welcome emails." Questions like these are answered with a join or a group. They also become the [data rules](data-validation.md) that run in your test suite.

## The idea in plain words

!!! info "In plain words"
    A join is a lookup. Each order has a `customer_id`. The join looks up that number in the customers table and puts the name next to the order, like matching a seat number to a guest list.

## Step by step

1. **Join orders to customers.** `JOIN ... ON` says which columns match. The short names `o` and `c` save typing:

    ```sql
    SELECT o.id, c.full_name, o.status, o.total
    FROM orders o
    JOIN customers c ON c.id = o.customer_id
    ORDER BY o.id;
    ```

    ```text
     id |  full_name   |  status   | total
    ----+--------------+-----------+-------
      1 | Arshad Test  | paid      | 49.98
      2 | Nadia Sample | shipped   | 49.50
      3 | Arshad Test  | new       | 15.00
      4 | Ola Example  | cancelled | 24.99
      5 | Ben Demo     | paid      | 39.00
    (5 rows)
    ```

    A plain `JOIN` keeps only rows that match on both sides.

2. **Find what has nothing linked, with `LEFT JOIN`.** A `LEFT JOIN` keeps every row from the left table, and fills the right side with `NULL` when nothing matches. So `WHERE o.id IS NULL` finds customers who never ordered:

    ```sql
    SELECT c.full_name, o.id AS order_id
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.id
    WHERE o.id IS NULL;
    ```

    ```text
     full_name | order_id
    -----------+----------
     Lena Fake |
    (1 row)
    ```

    Turn it around and it's a bug finder: orders with no items, items whose book was deleted, payments with no order. The [data rules](data-validation.md) use exactly this.

3. **Count per group with `GROUP BY`.** How many orders and how much money per customer, without cancelled orders:

    ```sql
    SELECT c.full_name, COUNT(o.id) AS orders, SUM(o.total) AS spent
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status <> 'cancelled'
    GROUP BY c.full_name
    ORDER BY spent DESC;
    ```

    ```text
      full_name   | orders | spent
    --------------+--------+-------
     Arshad Test  |      2 | 64.98
     Nadia Sample |      1 | 49.50
     Ben Demo     |      1 | 39.00
    (3 rows)
    ```

    Every column in the `SELECT` must be either in the `GROUP BY` or inside a total like `COUNT` or `SUM`.

4. **Filter groups with `HAVING`.** `WHERE` filters rows before grouping, and `HAVING` filters groups after. Customers with more than one order:

    ```sql
    SELECT customer_id, COUNT(*) AS orders
    FROM orders GROUP BY customer_id HAVING COUNT(*) > 1;
    ```

    ```text
     customer_id | orders
    -------------+--------
               1 |      2
    (1 row)
    ```

5. **Find duplicates.** `GROUP BY` plus `HAVING COUNT(*) > 1` is the duplicate finder. Here it finds a real gap. The `email` column is `UNIQUE`, but is `ARSHAD@example.com` the same as `arshad@example.com`? Try it inside a transaction, so `ROLLBACK` undoes it:

    ```sql
    BEGIN;
    INSERT INTO customers (email, full_name) VALUES ('ARSHAD@example.com', 'Arshad Again');
    SELECT LOWER(email) AS email, COUNT(*) AS how_many
    FROM customers GROUP BY LOWER(email) HAVING COUNT(*) > 1;
    ROLLBACK;
    ```

    ```text
    BEGIN
    INSERT 0 1
           email        | how_many
    --------------------+----------
     arshad@example.com |        2
    (1 row)

    ROLLBACK
    ```

    The database took the second row. `UNIQUE` compares text exactly, so the same email in capitals counts as different. That's a bug to report: one person can now have two accounts, and "forgot password" may email the wrong one.

6. **Compare with a subquery.** A subquery is a query in brackets, used as a value or a list. Books nobody has ever ordered:

    ```sql
    SELECT title FROM books WHERE id NOT IN (SELECT book_id FROM order_items);
    ```

    ```text
             title
    ------------------------
     The Bug Hunter's Guide
    (1 row)
    ```

    Orders above the average total:

    ```sql
    SELECT id, total FROM orders WHERE total > (SELECT AVG(total) FROM orders) ORDER BY id;
    ```

    ```text
     id | total
    ----+-------
      1 | 49.98
      2 | 49.50
      5 | 39.00
    (3 rows)
    ```

    !!! success "Check: you should now be able to"
        Join two tables, find rows with nothing linked, count per group, find duplicates, and compare against a subquery.

## When it goes wrong

- **Far too many rows.** The `ON` condition is missing or wrong, so every row is paired with every row. `SELECT COUNT(*) FROM orders, customers;` answers 25: 5 orders times 5 customers. Check each join has an `ON` that matches a key.
- **Rows disappear after a join.** A plain `JOIN` drops rows with no match. If you need every customer, even those with no orders, use `LEFT JOIN`.
- **A total counts twice.** Joining orders to `order_items` repeats each order once per item, so `SUM(o.total)` adds an order's total once for every book in it. Order 2 has two books, so its 49.50 comes out as 99.00. Sum the items, or total the orders before joining.
- **`NOT IN` returns nothing at all.** If the subquery returns even one `NULL`, `NOT IN` finds no rows. Use `NOT EXISTS`, or add `WHERE book_id IS NOT NULL` inside the subquery.

## Common mistakes

!!! warning "Common mistakes"
    - **Filtering a group with `WHERE`.** `WHERE COUNT(*) > 1` fails with `ERROR:  aggregate functions are not allowed in WHERE`. Use `HAVING`.
    - **Trusting `UNIQUE` for emails.** It's case-sensitive. Check with `LOWER()`.
    - **No table name on shared columns.** Both tables have `id`. Write `o.id` or `c.id`.

!!! failure "If you see this error"
    ```text
    ERROR:  column reference "id" is ambiguous
    LINE 1: SELECT id, full_name FROM orders JOIN customers ON customers...
                   ^
    ```

    Two joined tables both have an `id` column, and PostgreSQL doesn't know which one you mean. Put the table name or its short name in front: `orders.id`.

## Try it yourself

Write a query that shows each book's title and how many copies have been ordered in total, including books never ordered (they should show 0).

??? success "Solution"
    ```sql
    SELECT b.title, COALESCE(SUM(i.quantity), 0) AS copies
    FROM books b
    LEFT JOIN order_items i ON i.book_id = b.id
    GROUP BY b.title
    ORDER BY copies DESC;
    ```

    ```text
             title          | copies
    ------------------------+--------
     Clean Tests            |      3
     SQL in a Week          |      3
     Python for Testers     |      3
     The Bug Hunter's Guide |      0
    (4 rows)
    ```

    `LEFT JOIN` keeps the book nobody ordered. `COALESCE` turns its `NULL` sum into 0. The three books with 3 copies may come back in a different order: sorting on `copies` alone doesn't decide ties. Add `, b.title` to the `ORDER BY` when the order matters.

## References

- [PostgreSQL tutorial: Joins between tables](https://www.postgresql.org/docs/17/tutorial-join.html)
- [PostgreSQL tutorial: Aggregate functions, GROUP BY and HAVING](https://www.postgresql.org/docs/17/tutorial-agg.html)
- [PostgreSQL: Subquery expressions](https://www.postgresql.org/docs/17/functions-subquery.html)

Written for PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
