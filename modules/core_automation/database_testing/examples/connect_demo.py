# Template from myOpenSDET: https://myopensdet.github.io/
"""Connect to PostgreSQL from Python, run a query with a value, and read the rows."""

import os

import psycopg
from psycopg.rows import dict_row

url = os.environ["DATABASE_URL"]  # never write the password in the file

with psycopg.connect(url, row_factory=dict_row, connect_timeout=5) as conn:
    server = conn.execute("SHOW server_version").fetchone()
    print("Connected to PostgreSQL", server["server_version"])

    rows = conn.execute(
        "SELECT id, title, stock FROM books WHERE stock < %s ORDER BY id",
        (5,),
    ).fetchall()
    print(len(rows), "books with less than 5 in stock:")
    for row in rows:
        print(" ", row)
