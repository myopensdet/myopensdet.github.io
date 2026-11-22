# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Where the API is, and how to call it. Point it at your own app with environment variables:

BASE_URL=https://staging.your-app.example.com API_TOKEN=... python -m pytest
"""

import os

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "https://dummyjson.com").rstrip("/")
TOKEN = os.environ.get("API_TOKEN")  # never written in a file


@pytest.fixture(scope="session")
def api():
    session = requests.Session()
    session.headers["Accept"] = "application/json"
    if TOKEN:
        session.headers["Authorization"] = f"Bearer {TOKEN}"
    yield session
    session.close()
