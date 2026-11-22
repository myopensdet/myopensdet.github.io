# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Page objects: one class per page, so tests talk about the shop, not about HTML."""

from pages.books_page import BooksPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage, OrderPage
from pages.header import Header
from pages.login_page import LoginPage

__all__ = ["BooksPage", "CartPage", "CheckoutPage", "Header", "LoginPage", "OrderPage"]
