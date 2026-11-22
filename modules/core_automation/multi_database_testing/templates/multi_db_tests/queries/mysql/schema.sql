-- Template from myOpenSDET: https://myopensdet.github.io/
-- The test tables, in MySQL's types. Text needs a length, and DATETIME has no time zone.
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    id         INT PRIMARY KEY,
    email      VARCHAR(255) NOT NULL UNIQUE,
    full_name  VARCHAR(100) NOT NULL,
    country    CHAR(2) NOT NULL
) DEFAULT CHARSET = utf8mb4;
CREATE TABLE orders (
    id           INT PRIMARY KEY,
    customer_id  INT NOT NULL,
    status       VARCHAR(20) NOT NULL,
    total        DECIMAL(10, 2) NOT NULL,
    created_at   DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
) DEFAULT CHARSET = utf8mb4;
