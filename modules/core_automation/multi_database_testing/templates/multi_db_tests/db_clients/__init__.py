# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Read the settings and make the right client for each database."""

import os
from pathlib import Path

import yaml

from db_clients.base_client import DbClient

PROJECT = Path(__file__).resolve().parents[1]


def read_env_file(path: Path = PROJECT / ".env") -> None:
    """Load KEY=VALUE lines from .env into the environment. Real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def load_config(path: Path = PROJECT / "config" / "databases.yaml") -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)  # safe_load: a config file must never run code


def make_client(name: str, settings: dict) -> DbClient:
    """The client for one database, with its password taken from the environment."""
    settings = dict(settings)
    if "password_env" in settings:
        env_name = settings.pop("password_env")
        if not os.environ.get(env_name):
            raise LookupError(f"Set {env_name} in .env or the environment to test {name}")
        settings["password"] = os.environ[env_name]
    port_env = settings.pop("port_env", None)
    if port_env and os.environ.get(port_env):
        settings["port"] = int(os.environ[port_env])

    # Each driver is imported only when its database is used, so you can test
    # SQLite without installing the MongoDB driver, and so on.
    driver = settings["driver"]
    if driver == "postgres":
        from db_clients.postgres_client import PostgresClient as Client
    elif driver == "mysql":
        from db_clients.mysql_client import MysqlClient as Client
    elif driver == "sqlite":
        from db_clients.sqlite_client import SqliteClient as Client
    elif driver == "mongo":
        from db_clients.mongo_client import MongoDbClient as Client
    else:
        raise ValueError(f"Unknown driver {driver!r} for {name}")
    return Client(name, settings)
