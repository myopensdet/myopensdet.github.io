# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Smoke tests: the quick checks that run first on every change. CHANGE the paths to
your app's most important pages and endpoints."""

import time

import pytest
import requests

PAGES = ["/", "/health"]  # CHANGE: your home page and health check


@pytest.mark.parametrize("path", PAGES)
def test_page_answers(base_url, auth_headers, path):
    answer = requests.get(base_url + path, headers=auth_headers, timeout=10)
    assert answer.status_code == 200, f"{path} gave {answer.status_code}"


def test_home_page_is_fast(base_url, auth_headers):
    start = time.perf_counter()
    requests.get(base_url + "/", headers=auth_headers, timeout=10)
    seconds = time.perf_counter() - start
    assert seconds < 2, f"the home page took {seconds:.1f} s"
