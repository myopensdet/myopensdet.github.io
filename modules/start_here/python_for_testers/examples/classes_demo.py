# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Lesson: classes and objects. Run: python classes_demo.py"""


class TestUser:
    """A user for tests: a name, a role, and what they are allowed to do."""

    def __init__(self, name: str, role: str = "customer"):
        self.name = name
        self.role = role

    def can_ship_orders(self) -> bool:
        return self.role == "admin"

    def __repr__(self):
        return f"TestUser({self.name!r}, {self.role!r})"


arshad = TestUser("arshad")
admin = TestUser("admin1", role="admin")
print(arshad.name, arshad.role, arshad.can_ship_orders())
print(admin.name, admin.role, admin.can_ship_orders())
print([arshad, admin])
