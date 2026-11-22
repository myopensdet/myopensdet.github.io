# Template from myOpenSDET: https://myopensdet.github.io/
"""The cart page: a table with a Remove button on every row, and a confirm dialog."""

from playwright.sync_api import Locator, Page

from pages.header import Header


class CartPage:
    path = "/cart"

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.rows = page.get_by_role("row").filter(has=page.get_by_role("cell"))
        self.total = page.get_by_test_id("cart-total")
        self.empty_message = page.get_by_text("Your cart is empty.")
        self.empty_button = page.get_by_role("button", name="Empty cart")
        self.checkout_link = page.get_by_role("link", name="Go to checkout")

    def open(self):
        self.page.goto(self.path)
        return self

    def row(self, title: str) -> Locator:
        return self.rows.filter(has_text=title)

    def remove(self, title: str):
        self.row(title).get_by_role("button", name="Remove").click()
        return self

    def empty_cart(self, *, confirm: bool):
        """Click "Empty cart" and answer the browser's confirm dialog with OK or Cancel."""
        self.page.once("dialog", lambda dialog: dialog.accept() if confirm else dialog.dismiss())
        self.empty_button.click()
        return self

    def go_to_checkout(self):
        from pages.checkout_page import CheckoutPage  # noqa: PLC0415  (they import each other)

        self.checkout_link.click()
        return CheckoutPage(self.page)
