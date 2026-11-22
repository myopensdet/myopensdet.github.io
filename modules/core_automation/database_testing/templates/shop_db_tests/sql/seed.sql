-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
-- Fake test data for the bookshop. Every name and email is made up.

INSERT INTO customers (email, full_name, created_at) VALUES
    ('arshad@example.com', 'Arshad Test',   '2026-10-01 09:00+00'),
    ('nadia@example.com',  'Nadia Sample',  '2026-10-03 14:30+00'),
    ('ola@example.com',    'Ola Example',   '2026-10-05 11:15+00'),
    ('ben@example.com',    'Ben Demo',      '2026-10-08 16:45+00'),
    ('lena@example.com',   'Lena Fake',     '2026-10-12 10:00+00');

INSERT INTO books (title, price, stock) VALUES
    ('Python for Testers',      24.99, 10),
    ('SQL in a Week',           19.50,  3),
    ('The Bug Hunter''s Guide', 30.00,  0),
    ('Clean Tests',             15.00, 25);

INSERT INTO orders (customer_id, status, total, created_at, updated_at) VALUES
    (1, 'paid',      49.98, '2026-11-02 10:00+00', '2026-11-02 10:05+00'),
    (2, 'shipped',   49.50, '2026-11-03 12:00+00', '2026-11-04 08:00+00'),
    (1, 'new',       15.00, '2026-11-05 09:30+00', '2026-11-05 09:30+00'),
    (3, 'cancelled', 24.99, '2026-11-06 15:00+00', '2026-11-06 15:20+00'),
    (4, 'paid',      39.00, '2026-11-07 18:00+00', '2026-11-07 18:02+00');

INSERT INTO order_items (order_id, book_id, quantity, unit_price) VALUES
    (1, 1, 2, 24.99),
    (2, 2, 1, 19.50),
    (2, 4, 2, 15.00),
    (3, 4, 1, 15.00),
    (4, 1, 1, 24.99),
    (5, 2, 2, 19.50);
