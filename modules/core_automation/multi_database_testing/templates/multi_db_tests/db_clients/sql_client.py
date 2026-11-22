# Template from myOpenSDET: https://myopensdet.github.io/
"""What PostgreSQL, MySQL and SQLite share: Python's database API (PEP 249).

The three drivers differ in how they connect and in the placeholder they use
(%s or ?). Everything else is written once, here.
"""

from db_clients.base_client import DbClient


class SqlClient(DbClient):
    placeholder = "%s"

    def __init__(self, name: str, settings: dict):
        super().__init__(name, settings)
        self.conn = None

    def to_db(self, value):
        """Change a Python value into one this driver accepts. Override when needed."""
        return value

    def _cursor_rows(self, cursor) -> list[dict]:
        names = [col[0] for col in cursor.description]
        return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]

    def execute(self, sql: str, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            # No values: don't pass any. With values (even an empty tuple), PyMySQL and
            # psycopg read every % in the SQL as a placeholder, so '%Y-%m' would break.
            cursor.execute(sql)
        return cursor

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def create_tables(self) -> None:
        # Not every driver runs several statements at once, so split on ";".
        # Keep ";" out of comments in schema.sql, or the split breaks there.
        for statement in self.query_text("schema", ".sql").split(";"):
            if statement.strip():
                self.execute(statement)

    def insert(self, table: str, rows: list[dict]) -> None:
        columns = list(rows[0])
        marks = ", ".join([self.placeholder] * len(columns))
        # Table and column names come from this project's own files, never from user input.
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({marks})"  # noqa: S608
        cursor = self.conn.cursor()
        cursor.executemany(sql, [tuple(self.to_db(row[c]) for c in columns) for row in rows])

    def count(self, table: str) -> int:
        return self.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608

    def fetch(self, table: str) -> list[dict]:
        return self._cursor_rows(self.execute(f"SELECT * FROM {table}"))  # noqa: S608

    def columns(self, table: str) -> list[str]:
        # LIMIT 0 returns no rows, but the driver still describes the columns.
        cursor = self.execute(f"SELECT * FROM {table} LIMIT 0")  # noqa: S608
        cursor.fetchall()
        return [col[0] for col in cursor.description]

    def run_query(self, name: str) -> list[dict]:
        return self._cursor_rows(self.execute(self.query_text(name, ".sql")))
