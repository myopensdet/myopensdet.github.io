# Template from myOpenSDET: https://myopensdet.github.io/
"""The log-in page. Methods do what a person does; they return the page that comes next."""

from playwright.sync_api import Page

from pages.books_page import BooksPage


class LoginPage:
    path = "/login"

    def __init__(self, page: Page):
        self.page = page
        self.email = page.get_by_label("Email")
        self.password = page.get_by_label("Password")
        self.log_in_button = page.get_by_role("button", name="Log in")
        self.error = page.get_by_role("alert")

    def open(self):
        self.page.goto(self.path)
        return self

    def log_in(self, email: str, password: str) -> BooksPage:
        self.email.fill(email)
        self.password.fill(password)
        self.log_in_button.click()
        return BooksPage(self.page)
