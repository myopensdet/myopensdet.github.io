# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
import os

import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    url = os.environ.get("BASE_URL", "").rstrip("/")
    if not url:
        pytest.fail(
            "BASE_URL is not set. Locally: export BASE_URL=...; in CI: add it as a variable"
        )
    return url


@pytest.fixture(scope="session")
def auth_headers() -> dict:
    token = os.environ.get("API_AUTH")
    return {"Authorization": token} if token else {}
