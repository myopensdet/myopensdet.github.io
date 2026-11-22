<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Database tests for a bookshop

Tests for a small PostgreSQL bookshop database: schema, integrity rules, CRUD, data rules, a stored function and a trigger. Point `DATABASE_URL` at your own test database and swap the demo tables for yours to test it the same way.

## Set up once

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

You need a PostgreSQL database you are allowed to write to. A throwaway one in Docker, reachable only from your own computer:

```bash
docker run --rm -d --name shop-db -e POSTGRES_USER=shop_tester \
  -e POSTGRES_PASSWORD=local_only_password -e POSTGRES_DB=shop \
  -p 127.0.0.1:5432:5432 postgres:17
```

## Run

The address comes from an environment variable, never from a file:

```bash
export DATABASE_URL=postgresql://shop_tester:local_only_password@127.0.0.1:5432/shop
python -m pytest
```

Without it, every test is skipped, with a reason. The tests never leave anything behind: the demo tables live in a schema that is rolled back at the end, and each test's changes are rolled back when it ends.

## Where things are

| Path | What |
| --- | --- |
| `db/client.py` | `DbClient`: queries, logging and the column list in one place |
| `sql/schema.sql` | the demo tables, a trigger and a stored function |
| `sql/seed.sql` | fake test data |
| `tests/conftest.py` | fixtures: one connection, and a rolled-back savepoint per test |
| `tests/test_schema.py` | tables and columns are what the app expects |
| `tests/test_integrity.py` | the database refuses bad rows |
| `tests/test_crud.py` | create, read, update, delete |
| `tests/test_data_rules.py` | business rules as "must return zero rows" queries |
| `tests/test_procedures_and_triggers.py` | `place_order()` and the status history trigger |

## Using it on your own database

1. Use a test database, never production.
2. In `tests/conftest.py`, delete the lines that create the `shop_test` schema and run the two `.sql` files. Your app's migrations make the tables.
3. Change `EXPECTED` in `tests/test_schema.py`, and the rules in `tests/test_data_rules.py`, to match your tables.
