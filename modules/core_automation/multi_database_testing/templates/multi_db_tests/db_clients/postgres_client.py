# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""PostgreSQL, through psycopg."""

import psycopg

from db_clients.sql_client import SqlClient


class PostgresClient(SqlClient):
    driver = "postgres"

    def connect(self) -> None:
        s = self.settings
        self.conn = psycopg.connect(
            host=s["host"],
            port=s["port"],
            dbname=s["database"],
            user=s["user"],
            password=s["password"],
            connect_timeout=5,
            autocommit=True,
        )
