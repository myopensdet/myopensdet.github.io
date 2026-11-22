---
title: "SQL for Testers: SELECT, WHERE, ORDER BY and COUNT"
description: "The SQL a tester uses every day: read rows with SELECT, filter with WHERE, sort, count, and handle NULL, on a small bookshop database in PostgreSQL."
level: Intermediate
tags:
  - Database
nav_title: "SQL for testers"
order: 10
summary: "Read, filter, sort and count rows: the queries you'll type every day."
updated: "2026-11-22"
---

# SQL for Testers: SELECT, WHERE, ORDER BY and COUNT

The app says "Order placed". Was it saved, with the right total, for the right customer? The only way to know is to look in the database, and you look with **SQL** (Structured Query Language). A tester needs a small part of SQL, and uses it every day: read rows, filter them, sort them, count them.

!!! note "Before you start"
    You need a PostgreSQL database with the bookshop tables. The [topic page](index.md#4-get-something-running) shows how to start one in Docker and load the tables in two commands.

## What you will learn

- How tables, rows and columns fit together
- `SELECT`, `WHERE`, `ORDER BY` and `LIMIT`
- `COUNT`, `SUM` and other totals
- Why `NULL` needs `IS NULL`, not `= NULL`

## Why this matters at work

Bug reports get better when you can say "order 3 is saved with status `new` and total 15.00" instead of "the order looks wrong". Checking the database also finds bugs the screen hides: a rounding error, a missing row, a wrong status.

## The idea in plain words

!!! info "In plain words"
    A database is a set of spreadsheets that know about each other. Each table is one sheet, each row is one line, and each column has one kind of value. SQL is how you ask: "show me these columns, from this sheet, only the lines where this is true".

## Step by step

1. **Open a SQL prompt.** With the Docker database from the topic page:

    ```bash
    docker exec -it shop-db psql -U shop_tester -d shop
    ```

    `psql` is PostgreSQL's own command line. Type a query, end it with `;`, press Enter. `\q` quits. `\dt` lists the tables:

    ```text
                      List of relations
     Schema |         Name         | Type  |    Owner
    --------+----------------------+-------+-------------
     public | books                | table | shop_tester
     public | customers            | table | shop_tester
     public | order_items          | table | shop_tester
     public | order_status_history | table | shop_tester
     public | orders               | table | shop_tester
    (5 rows)
    ```

2. **Read rows with `SELECT`.** Name the columns you want, and the table:

    ```sql
    SELECT id, title, price, stock FROM books;
    ```

    ```text
     id |         title          | price | stock
    ----+------------------------+-------+-------
      1 | Python for Testers     | 24.99 |    10
      2 | SQL in a Week          | 19.50 |     3
      3 | The Bug Hunter's Guide | 30.00 |     0
      4 | Clean Tests            | 15.00 |    25
    (4 rows)
    ```

    `SELECT *` gives every column. Fine for a quick look, but name the columns in tests, so a new column doesn't change the result.

3. **Filter with `WHERE`.** Only the books that are almost sold out:

    ```sql
    SELECT title, stock FROM books WHERE stock < 5;
    ```

    ```text
             title          | stock
    ------------------------+-------
     SQL in a Week          |     3
     The Bug Hunter's Guide |     0
    (2 rows)
    ```

    Text goes in single quotes: `WHERE status = 'paid'`. Combine conditions with `AND` and `OR`, and lists with `IN`: `WHERE status IN ('paid', 'shipped')`.

4. **Sort with `ORDER BY`, and take the first few with `LIMIT`.** The three newest orders:

    ```sql
    SELECT id, customer_id, status, total, created_at
    FROM orders ORDER BY created_at DESC LIMIT 3;
    ```

    ```text
     id | customer_id |  status   | total |       created_at
    ----+-------------+-----------+-------+------------------------
      5 |           4 | paid      | 39.00 | 2026-11-07 18:00:00+00
      4 |           3 | cancelled | 24.99 | 2026-11-06 15:00:00+00
      3 |           1 | new       | 15.00 | 2026-11-05 09:30:00+00
    (3 rows)
    ```

    Without `ORDER BY`, the database may return rows in any order, and the order can change between runs. A test that compares a list of rows must sort them.

5. **Count and add up.** How many paid orders are there, and how much money do they bring in? `COUNT` and `SUM` work over many rows:

    ```sql
    SELECT COUNT(*) AS orders, SUM(total) AS money FROM orders WHERE status = 'paid';
    ```

    ```text
     orders | money
    --------+-------
          2 | 88.98
    (1 row)
    ```

    `MIN`, `MAX` and `AVG` work the same way. `AS` gives the column a readable name.

6. **Find empty values with `IS NULL`.** `NULL` means "no value", and it's not equal to anything, not even another `NULL`. So `= NULL` never finds a row:

    ```sql
    SELECT COUNT(*) FROM order_status_history WHERE old_status = NULL;
    SELECT COUNT(*) FROM order_status_history WHERE old_status IS NULL;
    ```

    Both answer 0 right now, because nothing has changed status yet. The [triggers lesson](procedures-and-triggers.md) adds rows here. Once a row with no `old_status` exists, the first query still says 0, and only the second finds it.

    !!! success "Check: you should now be able to"
        Read the columns you need from a table, filter, sort, take the first few rows, and count them.

## When it goes wrong

- **`ERROR:  column "Paid" does not exist`** from `WHERE status = "Paid"`. You used double quotes. In SQL, `'paid'` is text and `"paid"` is a column name. Use single quotes for values.
- **The query never ends.** `psql` waits for the `;`. The prompt changes from `shop=#` to `shop-#` while it waits. Type `;` and press Enter.
- **The row is there, but `WHERE email = 'Arshad@example.com'` finds nothing.** Text comparison is case-sensitive. Use `WHERE LOWER(email) = LOWER('Arshad@example.com')`, and ask whether the app should save emails in lower case.
- **The numbers look rounded.** Money should be a `numeric` column, never `real` or `double precision`. Check with `\d orders`. A float column is a bug to report.

## Common mistakes

!!! warning "Common mistakes"
    - **Comparing with `= NULL`.** Use `IS NULL` and `IS NOT NULL`.
    - **No `ORDER BY` in a test.** The order of rows isn't promised.
    - **Running `UPDATE` or `DELETE` by hand on a shared database without a `WHERE`.** It changes every row. Run the same `WHERE` as a `SELECT` first.

!!! failure "If you see this error"
    ```text
    ERROR:  syntax error at or near "FROM"
    LINE 1: SELECT id, title, FROM books;
                              ^
    ```

    Usually a comma before `FROM`. The `^` points at the word right after the mistake. Remove the last comma in the column list.

## Try it yourself

Write one query that lists the title and price of every book under 20.00, cheapest first.

??? success "Solution"
    ```sql
    SELECT title, price FROM books WHERE price < 20 ORDER BY price;
    ```

    Two rows: `Clean Tests` at 15.00, then `SQL in a Week` at 19.50.

## References

- [PostgreSQL tutorial: Querying a table](https://www.postgresql.org/docs/17/tutorial-select.html)
- [PostgreSQL: Comparison operators and IS NULL](https://www.postgresql.org/docs/17/functions-comparison.html)
- [PostgreSQL: Aggregate functions](https://www.postgresql.org/docs/17/functions-aggregate.html)
- [psql reference](https://www.postgresql.org/docs/17/app-psql.html)

Written for PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
