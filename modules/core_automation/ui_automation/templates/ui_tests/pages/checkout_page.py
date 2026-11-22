# Template from myOpenSDET: https://myopensdet.github.io/
"""Checkout: a form, a card field inside an iframe, and a terms link that opens a new tab."""

from playwright.sync_api import Page

from pages.header import Header


class CheckoutPage:
    path = "/checkout"

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.full_name = page.get_by_label("Full name")
        self.country = page.get_by_label("Country")
        self.terms = page.get_by_label("I accept the terms of sale")
        self.terms_link = page.get_by_role("link", name="terms of sale")
        # The card field is in another document: reach it through its iframe.
        self.card_number = page.frame_locator("iframe[title=Payment]").get_by_label("Card number")
        self.place_order_button = page.get_by_role("button", name="Place order")
        self.error = page.get_by_role("alert")

    def open(self):
        self.page.goto(self.path)
        return self

    def fill_details(self, name: str, country: str, delivery: str = "Standard"):
        self.full_name.fill(name)
        self.country.select_option(country)
        self.page.get_by_role("radio", name=delivery).check()
        return self

    def pay_with(self, card: str):
        self.card_number.fill(card)
        return self

    def accept_terms(self):
        self.terms.check()
        return self

    def open_terms(self) -> Page:
        """The link opens a new tab. Wait for it, and hand it back for checks."""
        with self.page.context.expect_page() as new_tab:
            self.terms_link.click()
        return new_tab.value

    def place_order(self):
        self.place_order_button.click()
        return OrderPage(self.page)


class OrderPage:
    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.heading = page.get_by_role("heading", name="Thank you for your order")
        self.number = page.get_by_test_id("order-number")
