# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A test that needs a running server. pytest.ini skips it unless you run -m api."""

import json
from urllib.error import URLError
from urllib.request import urlopen

import pytest


@pytest.mark.api
def test_health_says_ok(base_url, env):
    try:
        with urlopen(f"{base_url}/api/health", timeout=env["timeout"]) as response:  # noqa: S310
            status, body = response.status, json.load(response)
    except URLError as error:
        pytest.skip(f"no server at {base_url} ({error.reason})")
    assert status == 200
    assert body["status"] == "ok"
