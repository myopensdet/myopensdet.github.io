# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Product list: what's shown, and that sorting really sorts."""

from playwright.sync_api import Page, expect

from tests.conftest import money


def test_every_product_has_a_name_a_price_and_its_own_picture(logged_in: Page):
    items = logged_in.get_by_test_id("inventory-item")
    expect(items.first).to_be_visible()
    names = items.get_by_test_id("inventory-item-name").all_inner_texts()
    prices = items.get_by_test_id("inventory-item-price").all_inner_texts()
    pictures = [img.get_attribute("src") for img in items.locator("img").all()]
    assert all(names) and len(prices) == len(names)
    assert len(set(pictures)) == len(names), f"products share pictures: {pictures}"


def test_sort_by_price_low_to_high(logged_in: Page):
    logged_in.get_by_test_id("product-sort-container").select_option("Price (low to high)")
    prices = [money(p) for p in logged_in.get_by_test_id("inventory-item-price").all_inner_texts()]
    assert prices == sorted(prices), f"not sorted: {prices}"


def test_sort_by_name_z_to_a(logged_in: Page):
    logged_in.get_by_test_id("product-sort-container").select_option("Name (Z to A)")
    names = logged_in.get_by_test_id("inventory-item-name").all_inner_texts()
    assert names == sorted(names, reverse=True), f"not sorted: {names}"
