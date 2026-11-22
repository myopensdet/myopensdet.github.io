# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""MySQL, through PyMySQL."""

from datetime import datetime

import pymysql

from db_clients.base_client import as_utc
from db_clients.sql_client import SqlClient


class MysqlClient(SqlClient):
    driver = "mysql"

    def connect(self) -> None:
        s = self.settings
        self.conn = pymysql.connect(
            host=s["host"],
            port=s["port"],
            database=s["database"],
            user=s["user"],
            password=s["password"],
            charset="utf8mb4",  # full Unicode: names like Zoë and emoji
            connect_timeout=5,
            autocommit=True,
        )

    def to_db(self, value):
        # DATETIME has no time zone. Save every time in UTC, and read it back as UTC.
        if isinstance(value, datetime):
            return as_utc(value).replace(tzinfo=None)
        return value
