# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""MongoDB, through PyMongo. No tables: each table is a collection of documents."""

import json
from decimal import Decimal

from bson.decimal128 import Decimal128
from pymongo import ASCENDING, MongoClient

from db_clients.base_client import DbClient


class MongoDbClient(DbClient):
    driver = "mongo"

    def __init__(self, name: str, settings: dict):
        super().__init__(name, settings)
        self.client = None
        self.db = None

    def connect(self) -> None:
        s = self.settings
        self.client = MongoClient(
            host=s["host"],
            port=s["port"],
            username=s["user"],
            password=s["password"],
            authSource="admin",
            serverSelectionTimeoutMS=5000,
        )
        self.client.admin.command("ping")  # MongoClient connects lazily: fail here, not later
        self.db = self.client[s["database"]]

    def close(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None

    def create_tables(self) -> None:
        for name in ("orders", "customers"):
            self.db.drop_collection(name)
        # MongoDB has no schema, so the only rules are the ones you add, like unique indexes.
        self.db.customers.create_index([("id", ASCENDING)], unique=True)
        self.db.customers.create_index([("email", ASCENDING)], unique=True)
        self.db.orders.create_index([("id", ASCENDING)], unique=True)

    def insert(self, table: str, rows: list[dict]) -> None:
        # BSON has no Python Decimal: money is stored as Decimal128.
        docs = [
            {k: Decimal128(v) if isinstance(v, Decimal) else v for k, v in row.items()}
            for row in rows
        ]
        self.db[table].insert_many(docs)

    def count(self, table: str) -> int:
        return self.db[table].count_documents({})

    def fetch(self, table: str) -> list[dict]:
        rows = []
        for doc in self.db[table].find({}, {"_id": False}):
            rows.append(
                {k: v.to_decimal() if isinstance(v, Decimal128) else v for k, v in doc.items()}
            )
        return rows

    def columns(self, table: str) -> list[str]:
        doc = self.db[table].find_one({}, {"_id": False})
        return list(doc) if doc else []

    def run_query(self, name: str) -> list[dict]:
        pipeline = json.loads(self.query_text(name, ".json"))["pipeline"]
        return list(self.db.orders.aggregate(pipeline))
