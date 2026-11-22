# Template from myOpenSDET: https://myopensdet.github.io/
"""Try any query from the SQL cheat sheet on a tiny practice shop, with nothing to install.

Loads practice_shop.sql into a database in memory (SQLite, part of Python), runs your
query and prints the rows as a table. Every run starts fresh, so UPDATE and DELETE are
safe to try.

Usage:
    python try_sql.py "SELECT name, country FROM customers"
"""

import sqlite3
import sys
from pathlib import Path

SHOP = Path(__file__).with_name("practice_shop.sql")


def show(cursor: sqlite3.Cursor) -> None:
    if cursor.description is None:
        print(f"OK: {cursor.rowcount} row(s) changed.")
        return
    header = [col[0] for col in cursor.description]
    rows = [["NULL" if v is None else str(v) for v in row] for row in cursor.fetchall()]
    widths = [max(len(text) for text in col) for col in zip(header, *rows, strict=True)]
    for line in [header, ["-" * w for w in widths], *rows]:
        print("  ".join(text.ljust(w) for text, w in zip(line, widths, strict=True)).rstrip())
    print(f"({len(rows)} row{'' if len(rows) == 1 else 's'})")


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print('Usage: python try_sql.py "SELECT name, country FROM customers"')
        return 2
    db = sqlite3.connect(":memory:")
    db.executescript(SHOP.read_text(encoding="utf-8"))
    try:
        show(db.execute(sys.argv[1]))
    except sqlite3.Error as err:
        print(f"SQL error: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
