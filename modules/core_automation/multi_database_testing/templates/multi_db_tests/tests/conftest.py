# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Fixtures: one client per database, loaded with fresh test data once per run.

Which databases run:  TEST_DATABASES=postgres,sqlite   (default: all in config/databases.yaml)
Which get test data:  LOAD_TEST_DATA=postgres          (default: the same ones; "none" for none)
A database whose password isn't set is skipped, with the reason. One that is set but
can't be reached fails: a missing database in the pipeline must never pass quietly.
"""

import os

import pytest
from db_clients import load_config, make_client, read_env_file
from db_clients.test_data import load_all

read_env_file()
CONFIG = load_config()


def names_from_env(variable: str, default: list[str]) -> list[str]:
    value = os.environ.get(variable)
    if value is None:
        return default
    if value.strip().lower() == "none":
        return []
    names = [n.strip() for n in value.split(",") if n.strip()]
    unknown = set(names) - set(CONFIG["databases"])
    if unknown:
        raise pytest.UsageError(f"{variable}: unknown database {sorted(unknown)}")
    return names


DATABASES = names_from_env("TEST_DATABASES", list(CONFIG["databases"]))
LOADED = names_from_env("LOAD_TEST_DATA", DATABASES)
SOURCE = CONFIG["compare"]["source"]
TABLES = CONFIG["compare"]["tables"]


@pytest.fixture(scope="session")
def clients():
    """Open each database once, the first time a test asks for it."""
    opened = {}

    def get(name):
        if name not in opened:
            try:
                client = make_client(name, CONFIG["databases"][name])
            except LookupError as error:
                pytest.skip(str(error))
            client.connect()
            if name in LOADED:
                load_all(client)
            opened[name] = client
        return opened[name]

    yield get
    for client in opened.values():
        client.close()


@pytest.fixture(params=DATABASES)
def db(request, clients):
    """Each test that asks for db runs once on every database."""
    return clients(request.param)


@pytest.fixture
def source(clients):
    return clients(SOURCE)


# Comparisons need the source. If this run leaves it out, they are skipped.
TARGETS = [n for n in DATABASES if n != SOURCE] if SOURCE in DATABASES else []


@pytest.fixture(params=TARGETS)
def target(request, clients):
    """Every database except the source, one at a time."""
    return clients(request.param)
