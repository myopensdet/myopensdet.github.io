# Template from myOpenSDET: https://myopensdet.github.io/
"""Logs are evidence, and evidence gets shared. Check that secrets never reach them."""

import logging

from helpers.api_client import ShopApi

from tests.conftest import TEST_USER


def test_passwords_never_reach_the_log(base_url, caplog):
    caplog.set_level(logging.DEBUG, logger="shop.api")
    ShopApi(base_url).log_in(**TEST_USER)
    assert TEST_USER["password"] not in caplog.text
    assert '"password": "***"' in caplog.text


def test_each_call_is_one_info_line(base_url, caplog):
    caplog.set_level(logging.INFO, logger="shop.api")
    ShopApi(base_url).books("sql")
    assert [r.getMessage().split(" in ")[0] for r in caplog.records] == [
        "GET /api/books?q=sql -> 200"
    ]
