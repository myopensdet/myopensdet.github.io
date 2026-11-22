-- Template from myOpenSDET: https://myopensdet.github.io/
-- A small shop database for practice. Like many real databases, it has some rules in the
-- tables (NOT NULL, UNIQUE) and some only in the app. Some rows break the app's rules:
-- the guide's checks find them. All names and emails are made up.

CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    email      TEXT NOT NULL,
    full_name  TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id    SERIAL PRIMARY KEY,
    sku   TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL
);

-- No foreign keys: an older part of the system, where the app is meant to keep things linked.
CREATE TABLE orders (
    id           SERIAL PRIMARY KEY,
    order_number TEXT NOT NULL UNIQUE,
    customer_id  INTEGER NOT NULL,
    status       TEXT NOT NULL,
    total        NUMERIC(10, 2) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

INSERT INTO customers (email, full_name) VALUES
    ('arshad.test@example.com', 'Arshad Test'),
    ('mia.khan@example.com', 'Mia Khan'),
    ('Mia.Khan@example.com', 'Mia Khan'),          -- the same person twice: case differs
    ('leo.park@example.com', 'Leo Park');

INSERT INTO products (sku, name, price, stock) VALUES
    ('BOOK-SQL', 'SQL in a Week', 24.50, 12),
    ('BOOK-API', 'APIs for Testers', 19.99, 5),
    ('BOOK-PY', 'Python Basics', 15.00, -3);       -- negative stock

INSERT INTO orders (order_number, customer_id, status, total) VALUES
    ('BK-1001', 1, 'paid', 64.48),
    ('BK-1002', 2, 'shipped', 19.99),
    ('BK-1003', 4, 'paid', 50.00),                 -- items add up to 45.00
    ('BK-1004', 1, 'shiped', 15.00);               -- a status the app doesn't know

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 24.50),
    (1, 2, 2, 19.99),
    (2, 2, 1, 19.99),
    (3, 3, 3, 15.00),
    (4, 3, 1, 15.00),
    (99, 1, 1, 24.50);                             -- order 99 doesn't exist
