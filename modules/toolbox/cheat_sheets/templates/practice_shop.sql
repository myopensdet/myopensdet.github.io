-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
-- A tiny shop database to try every query on the SQL cheat sheet. Fake data only.
-- It has planted problems on purpose: a duplicate email, an order with no customer,
-- a customer with no email, and an order whose total doesn't match its lines.

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    country TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    status TEXT NOT NULL,
    total NUMERIC NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE order_lines (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC NOT NULL
);

INSERT INTO customers VALUES
    (1, 'Arshad Test', 'arshad.test@example.com', 'BD', '2026-10-01'),
    (2, 'Sam Tester', 'sam@example.com', 'UK', '2026-10-03'),
    (3, 'Kim Lee', 'kim@example.com', 'KR', '2026-10-05'),
    (4, 'Sam Twin', 'sam@example.com', 'UK', '2026-10-09'),
    (5, 'No Email', NULL, 'US', '2026-10-12');

INSERT INTO products VALUES
    (1, 'Practice book', 24.50),
    (2, 'Test mug', 9.99),
    (3, 'Bug sticker', 1.50);

INSERT INTO orders VALUES
    (101, 1, 'paid', 34.49, '2026-11-01'),
    (102, 2, 'paid', 3.00, '2026-11-02'),
    (103, 3, 'cancelled', 24.50, '2026-11-03'),
    (104, 1, 'paid', 40.00, '2026-11-05'),
    (105, 99, 'paid', 9.99, '2026-11-06');

INSERT INTO order_lines VALUES
    (1, 101, 1, 1, 24.50),
    (2, 101, 2, 1, 9.99),
    (3, 102, 3, 2, 1.50),
    (4, 103, 1, 1, 24.50),
    (5, 104, 1, 1, 24.50),
    (6, 105, 2, 1, 9.99);
