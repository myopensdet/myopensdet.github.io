# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Robot Framework keywords for the shop rules. Each method is a keyword:
order_total_should_be becomes "Order Total Should Be". Run from the template folder:

    robot --pythonpath . --outputdir results robot
"""

from decimal import Decimal

from app.shop_rules import check_signup, order_total


class ShopKeywords:
    ROBOT_LIBRARY_SCOPE = "TEST"  # a fresh order for every test

    def __init__(self):
        self.subtotal = Decimal("0")
        self.coupon = None
        self.member = False

    def signup_problems_should_be(self, email: str, password: str, age: int, expected: str = ""):
        problems = " ".join(check_signup(email, password, age))
        if problems != expected:
            raise AssertionError(f"Expected problems '{expected}', got '{problems}'")

    def start_an_order_of(self, subtotal: Decimal):
        self.subtotal = subtotal

    def apply_coupon(self, code: str):
        self.coupon = code

    def customer_is_a_member(self):
        self.member = True

    def total_should_be(self, expected: Decimal):
        total = order_total(self.subtotal, self.coupon, self.member)
        if total != expected:
            raise AssertionError(f"Expected total {expected}, got {total}")
