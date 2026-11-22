# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Reach the shop through its web page, the way a person would."""

from decimal import Decimal

from playwright.sync_api import Page


class UiDriver:
    def __init__(self, base_url: str, page: Page):
        self.base_url = base_url
        self.page = page

    def start_empty_cart(self) -> None:
        self.page.goto(f"{self.base_url}/shop")

    def add_book(self, book: str, copies: int) -> None:
        self.page.get_by_label("Book").select_option(book)
        self.page.get_by_label("Copies").fill(str(copies))
        self.page.get_by_role("button", name="Add to cart").click()

    def apply_coupon(self, code: str) -> None:
        self.page.get_by_label("Coupon").fill(code)
        self.page.get_by_role("button", name="Apply coupon").click()

    def total(self) -> Decimal:
        return Decimal(self.page.get_by_test_id("total").inner_text())

    def message(self) -> str:
        return self.page.get_by_role("status").inner_text()

    def close(self) -> None:
        self.page.close()
