<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# SQL cheat sheet for testers

Every query here runs on `practice_shop.sql`: try one with `python try_sql.py "<query>"`. On your own database, change the table and column names. Read-only queries first; change data only on a test database.

## Read rows

```sql
SELECT * FROM customers;
```

```sql
SELECT name, email FROM customers WHERE country = 'UK';
```

```sql
SELECT id, total FROM orders ORDER BY total DESC LIMIT 3;
```

| Part | Does |
| --- | --- |
| `SELECT a, b` | Which columns. `*` means all: fine to look, slow on big tables |
| `WHERE` | Which rows |
| `ORDER BY x DESC` | Sort, biggest first. `ASC` (the default) is smallest first |
| `LIMIT 3` | Only the first 3 rows |

## Filter

| You want | Write |
| --- | --- |
| Equal, not equal | `status = 'paid'`, `status <> 'paid'` |
| One of a list | `status IN ('paid', 'cancelled')` |
| A range (both ends included) | `created_at BETWEEN '2026-11-01' AND '2026-11-03'` |
| Text contains | `email LIKE '%@example.com'` (`%` = any text, `_` = one character) |
| Empty (no value) | `email IS NULL`. Never `= NULL`: it matches nothing |
| Combine | `status = 'paid' AND total > 10`, `country = 'UK' OR country = 'BD'` |

```sql
SELECT id, status, total FROM orders
WHERE status IN ('paid', 'cancelled') AND total > 10;
```

## Count and add up

```sql
SELECT COUNT(*) AS orders, SUM(total) AS money FROM orders WHERE status = 'paid';
```

```sql
SELECT status, COUNT(*) AS how_many FROM orders GROUP BY status;
```

```sql
SELECT customer_id, COUNT(*) AS orders FROM orders
GROUP BY customer_id HAVING COUNT(*) > 1;
```

`WHERE` filters rows **before** grouping; `HAVING` filters the groups **after**. `COUNT(email)` skips empty emails; `COUNT(*)` counts every row.

## Join tables

```sql
SELECT o.id, c.name, o.total
FROM orders o
JOIN customers c ON c.id = o.customer_id;
```

```sql
SELECT o.id, o.customer_id, c.name
FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id;
```

| Join | Keeps |
| --- | --- |
| `JOIN` (inner) | Only rows that match on both sides |
| `LEFT JOIN` | Every row from the left table; `NULL` where the right side has no match |

## Checks testers run every week

Each query should return **0 rows**. Any row it returns is a bug to report.

```sql
-- Duplicates: the same email used twice
SELECT email, COUNT(*) AS times FROM customers
WHERE email IS NOT NULL
GROUP BY email HAVING COUNT(*) > 1;
```

```sql
-- Orphans: orders whose customer doesn't exist
SELECT o.id, o.customer_id FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id
WHERE c.id IS NULL;
```

```sql
-- Missing values: customers with no email
SELECT id, name FROM customers WHERE email IS NULL;
```

```sql
-- Totals that don't add up: order total vs the sum of its lines
SELECT o.id, o.total, SUM(l.quantity * l.price) AS lines_total
FROM orders o
JOIN order_lines l ON l.order_id = o.id
GROUP BY o.id, o.total
HAVING ABS(o.total - SUM(l.quantity * l.price)) > 0.005;
```

```sql
-- The newest rows: did my test just create this?
SELECT * FROM orders ORDER BY created_at DESC LIMIT 5;
```

## Change data (test databases only)

```sql
INSERT INTO customers (id, name, email, country, created_at)
VALUES (6, 'Arshad Test', 'new.user@example.com', 'BD', '2026-11-19');
```

```sql
UPDATE orders SET status = 'cancelled' WHERE id = 102;
```

```sql
DELETE FROM order_lines WHERE order_id = 103;
```

**Always** write the `WHERE` first. `UPDATE` or `DELETE` without it changes **every row**. Run the same `WHERE` as a `SELECT` first, and check the row count.

Try a change, look, then undo it. Run this in a database tool (`try_sql.py` runs one statement at a time, and starts fresh every run anyway):

```sql
BEGIN;
UPDATE orders SET status = 'refunded' WHERE id = 101;
SELECT id, status FROM orders WHERE id = 101;
ROLLBACK;
```

## Differences between databases

| You want | SQLite, PostgreSQL, MySQL | SQL Server |
| --- | --- | --- |
| First 3 rows | `LIMIT 3` | `SELECT TOP 3 ...` |
| Join text | `a || b` (MySQL: `CONCAT(a, b)`) | `a + b` or `CONCAT(a, b)` |
| Today | `CURRENT_DATE` | `CAST(GETDATE() AS date)` |
| Contains, any case | PostgreSQL: `ILIKE`. MySQL and SQLite: `LIKE` ignores case for English letters | `LIKE` (depends on the collation) |
