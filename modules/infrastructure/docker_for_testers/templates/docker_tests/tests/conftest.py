# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Where the app and the database are. The same tests run inside a container and on your
computer: only these two addresses change, and they come from the environment."""

import os

import psycopg
import pytest
import requests

# In docker compose: http://api:8000. On your computer: the port in .env.
API_URL = os.environ.get("API_URL", "http://127.0.0.1:58180")
DATABASE_URL = os.environ.get("DATABASE_URL")


@pytest.fixture(scope="session")
def api():
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def db():
    if not DATABASE_URL:
        pytest.skip("Set DATABASE_URL to check the database too")
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        yield conn
