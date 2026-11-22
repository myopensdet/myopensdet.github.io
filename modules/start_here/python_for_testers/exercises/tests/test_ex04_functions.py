# Template from myOpenSDET: https://myopensdet.github.io/
from ex04_functions import make_user, percent


def test_make_user_default_role():
    assert make_user("arshad") == {
        "name": "arshad",
        "role": "customer",
        "email": "arshad@example.com",
    }


def test_make_user_admin():
    assert make_user("admin1", role="admin")["role"] == "admin"


def test_percent():
    assert percent(9, 12) == 75.0
    assert percent(1, 3) == 33.3


def test_percent_of_zero():
    assert percent(0, 0) == 0.0
