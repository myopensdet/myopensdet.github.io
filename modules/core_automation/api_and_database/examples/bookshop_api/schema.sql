-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
-- The bookshop API's tables. The app runs this when it starts, so it's safe to run again.

CREATE TABLE IF NOT EXISTS customers (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text NOT NULL UNIQUE,
    full_name   text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS books (
    id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title  text NOT NULL,
    price  numeric(8, 2) NOT NULL CHECK (price > 0),
    stock  integer NOT NULL CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  integer NOT NULL REFERENCES customers (id),
    book_id      integer NOT NULL REFERENCES books (id),
    quantity     integer NOT NULL CHECK (quantity > 0),
    unit_price   numeric(8, 2) NOT NULL,
    total        numeric(10, 2) NOT NULL,
    status       text NOT NULL DEFAULT 'new',
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_events (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    integer NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    event       text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT clock_timestamp()
);
