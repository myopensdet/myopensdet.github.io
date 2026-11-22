# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A practice framework 'someone else wrote', for map_test_suite.py to read."""

import os

import pytest
from helpers.api import ApiClient


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "https://staging.shop.example.com")


@pytest.fixture(scope="session")
def api(base_url):
    return ApiClient(base_url, token=os.environ["API_TOKEN"])


@pytest.fixture
def admin_api(base_url):
    return ApiClient(base_url, token=os.getenv("ADMIN_TOKEN"))
