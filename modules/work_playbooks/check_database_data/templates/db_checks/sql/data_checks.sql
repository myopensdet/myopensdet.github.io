-- Template from myOpenSDET: https://myopensdet.github.io/
-- Ready data checks. Each query returns the rows that BREAK a rule: no rows = all good.
-- Paste them into DBeaver, pgAdmin, psql or any SQL tool. Change the table and column
-- names to yours. Written for PostgreSQL; notes show what to change for MySQL.

-- 1. Duplicates, ignoring letter case (the same email written twice)
SELECT lower(email) AS email, count(*) AS how_many
FROM customers
GROUP BY lower(email)
HAVING count(*) > 1;

-- 2. Orphans: child rows whose parent doesn't exist
SELECT oi.*
FROM order_items oi
LEFT JOIN orders o ON o.id = oi.order_id
WHERE o.id IS NULL;

-- 3. Totals that don't match their parts
SELECT o.order_number, o.total, sum(oi.quantity * oi.unit_price) AS items_add_up_to
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, o.order_number, o.total
HAVING o.total <> sum(oi.quantity * oi.unit_price);

-- 4. Values the app doesn't know (a typo, an old value)
SELECT order_number, status
FROM orders
WHERE status NOT IN ('new', 'paid', 'shipped', 'delivered', 'cancelled');

-- 5. Numbers outside their range
SELECT sku, stock FROM products WHERE stock < 0;
SELECT sku, price FROM products WHERE price <= 0;

-- 6. Parents with no children (an order with no items)
SELECT o.order_number
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
WHERE oi.id IS NULL;

-- 7. Rows pointing to a parent that doesn't exist, one level up
SELECT o.order_number, o.customer_id
FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id
WHERE c.id IS NULL;

-- 8. Empty text where a value is required (NOT NULL lets '' and '   ' through)
SELECT id, email FROM customers WHERE trim(email) = '' OR trim(full_name) = '';

-- 9. Dates in the future
SELECT order_number, created_at FROM orders WHERE created_at > now();

-- 10. How many rows each table has (run before and after a release, and compare)
SELECT 'customers' AS table_name, count(*) FROM customers
UNION ALL SELECT 'products', count(*) FROM products
UNION ALL SELECT 'orders', count(*) FROM orders
UNION ALL SELECT 'order_items', count(*) FROM order_items;

-- 11. Columns and types of a table (MySQL: same query, add AND table_schema = 'your_db')
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'orders'
ORDER BY ordinal_position;

-- 12. Foreign keys a table has (PostgreSQL)
SELECT conname AS name, pg_get_constraintdef(oid) AS rule
FROM pg_constraint
WHERE conrelid = 'orders'::regclass AND contype = 'f';
