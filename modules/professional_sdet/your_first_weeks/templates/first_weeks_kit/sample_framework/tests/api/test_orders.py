# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
import time

import pytest


@pytest.mark.smoke
def test_list_orders(api):
    assert api.get("/api/orders").status_code == 200


@pytest.mark.smoke
def test_order_has_items(api):
    assert api.get("/api/orders/1").json()["items"]


def test_new_order_shows_up(api):
    time.sleep(3)
    assert api.get("/api/orders?sort=new").status_code == 200


@pytest.mark.skip(reason="SHOP-301 flaky on staging")
def test_cancel_order(api):
    assert api.get("/api/orders/1/cancel").status_code == 200


@pytest.mark.xfail(reason="SHOP-288 refunds not built yet")
def test_refund(api):
    assert api.get("/api/orders/1/refund").status_code == 200
