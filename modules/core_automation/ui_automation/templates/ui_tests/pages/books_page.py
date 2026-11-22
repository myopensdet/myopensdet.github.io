# Template from myOpenSDET: https://myopensdet.github.io/
"""The book list. It loads after the page does, so tests check it with expect(), which waits."""

import re

from playwright.sync_api import Locator, Page, expect

from pages.header import Header

LOADED = re.compile(r"^(\d+ books?|No books match .*)$")


class BooksPage:
    path = "/books"

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.heading = page.get_by_role("heading", name="Books", level=1)
        self.search_box = page.get_by_role("searchbox", name="Search books")
        self.search_button = page.get_by_role("button", name="Search")
        self.status = page.get_by_role("status")
        self.results = page.get_by_role("list", name="Books").get_by_role("listitem")

    def open(self):
        self.page.goto(self.path)
        self.wait_until_loaded()
        return self

    def wait_until_loaded(self):
        """The page is ready when the status says how many books it shows."""
        expect(self.status).to_have_text(LOADED)

    def search(self, text: str):
        self.search_box.fill(text)
        self.search_button.click()
        self.wait_until_loaded()
        return self

    def book(self, title: str) -> Locator:
        """The card of one book: every card has an "Add to cart" button, so find the card first."""
        return self.results.filter(has=self.page.get_by_role("heading", name=title))

    def add_to_cart(self, title: str):
        self.book(title).get_by_role("button", name="Add to cart").click()
        return self
