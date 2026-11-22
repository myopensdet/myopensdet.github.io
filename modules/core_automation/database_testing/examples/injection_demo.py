# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Why values go in as parameters, never pasted into the SQL text."""

import os

import psycopg

email = "nobody@example.com' OR '1'='1"  # what an attacker types into a search box

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    # Unsafe on purpose, to show the hole. Never write SQL like this.
    unsafe_sql = f"SELECT id, email FROM customers WHERE email = '{email}'"  # noqa: S608
    print("Pasted in: ", unsafe_sql)
    print("Rows found:", len(conn.execute(unsafe_sql).fetchall()))

    safe_sql = "SELECT id, email FROM customers WHERE email = %s"
    print("As a parameter, rows found:", len(conn.execute(safe_sql, (email,)).fetchall()))
