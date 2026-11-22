# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The header is on every page, so it is a component that pages share, not a page."""

from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page):
        self.page = page
        nav = page.get_by_role("navigation", name="Main")
        self.books_link = nav.get_by_role("link", name="Books")
        self.cart_link = nav.get_by_role("link", name="Cart")
        self.cart_count = nav.get_by_test_id("cart-count")
        self.log_out_button = nav.get_by_role("button", name="Log out")

    def go_to_cart(self):
        from pages.cart_page import CartPage  # noqa: PLC0415  (the pages import each other)

        self.cart_link.click()
        return CartPage(self.page)

    def log_out(self):
        from pages.login_page import LoginPage  # noqa: PLC0415

        self.log_out_button.click()
        return LoginPage(self.page)
