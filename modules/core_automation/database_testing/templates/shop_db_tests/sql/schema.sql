-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
-- A small bookshop: customers, books, orders and the books in each order.
-- In a real project these tables come from your app's migrations, not from here.

CREATE TABLE customers (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text NOT NULL UNIQUE,
    full_name   text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE books (
    id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title  text NOT NULL,
    price  numeric(8, 2) NOT NULL CHECK (price > 0),
    stock  integer NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE orders (
    id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  integer NOT NULL REFERENCES customers (id),
    status       text NOT NULL DEFAULT 'new'
                 CHECK (status IN ('new', 'paid', 'shipped', 'cancelled')),
    total        numeric(10, 2) NOT NULL DEFAULT 0 CHECK (total >= 0),
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    order_id    integer NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    book_id     integer NOT NULL REFERENCES books (id),
    quantity    integer NOT NULL CHECK (quantity > 0),
    unit_price  numeric(8, 2) NOT NULL CHECK (unit_price > 0),
    PRIMARY KEY (order_id, book_id)
);

CREATE TABLE order_status_history (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    integer NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    old_status  text,
    new_status  text NOT NULL,
    changed_at  timestamptz NOT NULL DEFAULT clock_timestamp()
);

-- Trigger: every status change is written to order_status_history,
-- and updated_at moves to the time of the change.
-- clock_timestamp() is the real time now. now() would be the time the
-- transaction started, which never moves inside one transaction.
CREATE FUNCTION log_status_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO order_status_history (order_id, old_status, new_status)
        VALUES (NEW.id, OLD.status, NEW.status);
        NEW.updated_at := clock_timestamp();
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER orders_status_change
    BEFORE UPDATE OF status ON orders
    FOR EACH ROW EXECUTE FUNCTION log_status_change();

-- Stored function: place an order for one book. Takes the stock, writes the
-- order and its item, and returns the new order id. All or nothing.
CREATE FUNCTION place_order(p_customer_id integer, p_book_id integer, p_quantity integer)
RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
    v_price     numeric(8, 2);
    v_order_id  integer;
BEGIN
    UPDATE books SET stock = stock - p_quantity
    WHERE id = p_book_id AND stock >= p_quantity
    RETURNING price INTO v_price;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Not enough stock for book %', p_book_id;
    END IF;

    INSERT INTO orders (customer_id, total)
    VALUES (p_customer_id, v_price * p_quantity)
    RETURNING id INTO v_order_id;

    INSERT INTO order_items (order_id, book_id, quantity, unit_price)
    VALUES (v_order_id, p_book_id, p_quantity, v_price);

    RETURN v_order_id;
END;
$$;
