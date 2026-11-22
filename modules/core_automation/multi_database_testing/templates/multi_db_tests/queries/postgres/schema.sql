-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
-- The test tables, in PostgreSQL's types.
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    id         integer PRIMARY KEY,
    email      text NOT NULL UNIQUE,
    full_name  text NOT NULL,
    country    char(2) NOT NULL
);
CREATE TABLE orders (
    id           integer PRIMARY KEY,
    customer_id  integer NOT NULL REFERENCES customers (id),
    status       text NOT NULL,
    total        numeric(10, 2) NOT NULL,
    created_at   timestamptz NOT NULL
);
