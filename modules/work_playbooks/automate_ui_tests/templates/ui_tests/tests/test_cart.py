# Template from myOpenSDET: https://myopensdet.github.io/
"""Cart: the count, the items and the prices stay right."""

from playwright.sync_api import Page, expect

from tests.conftest import add_to_cart

PRODUCT = "Sauce Labs Backpack"  # CHANGE: a product that always exists in your test data
PRICE = "$29.99"


def test_adding_a_product_updates_the_cart_count(logged_in: Page):
    add_to_cart(logged_in, PRODUCT)
    expect(logged_in.get_by_test_id("shopping-cart-badge")).to_have_text("1")


def test_cart_shows_the_product_and_its_price(logged_in: Page):
    add_to_cart(logged_in, PRODUCT)
    logged_in.get_by_test_id("shopping-cart-link").click()
    row = logged_in.get_by_test_id("inventory-item")
    expect(row).to_have_count(1)
    expect(row.get_by_test_id("inventory-item-name")).to_have_text(PRODUCT)
    expect(row.get_by_test_id("inventory-item-price")).to_have_text(PRICE)


def test_removing_the_product_empties_the_cart(logged_in: Page):
    add_to_cart(logged_in, PRODUCT)
    logged_in.get_by_test_id("shopping-cart-link").click()
    logged_in.get_by_role("button", name="Remove").click()
    expect(logged_in.get_by_test_id("inventory-item")).to_have_count(0)
    expect(logged_in.get_by_test_id("shopping-cart-badge")).to_have_count(0)


def test_cart_is_kept_after_a_reload(logged_in: Page):
    add_to_cart(logged_in, PRODUCT)
    logged_in.reload()
    expect(logged_in.get_by_test_id("shopping-cart-badge")).to_have_text("1")
