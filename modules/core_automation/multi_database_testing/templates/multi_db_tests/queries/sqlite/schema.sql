-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
-- The test tables, in SQLite. It has no date or money types. Times are text, money is NUMERIC.
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    id         INTEGER PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    full_name  TEXT NOT NULL,
    country    TEXT NOT NULL
);
CREATE TABLE orders (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers (id),
    status       TEXT NOT NULL,
    total        NUMERIC NOT NULL,
    created_at   TEXT NOT NULL
);
