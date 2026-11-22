# Template from myOpenSDET: https://myopensdet.github.io/
from ex04_functions import battery_ok, make_user, percent


def test_make_user_default_role():
    assert make_user("tester1") == {
        "name": "tester1",
        "role": "customer",
        "email": "tester1@example.com",
    }


def test_make_user_admin():
    assert make_user("admin1", role="admin")["role"] == "admin"


def test_percent():
    assert percent(9, 12) == 75.0
    assert percent(1, 3) == 33.3


def test_percent_of_zero():
    assert percent(0, 0) == 0.0


def test_battery_ok_with_default_minimum():
    assert battery_ok({"id": "SNS-0042", "battery": 20}) is True
    assert battery_ok({"id": "SNS-0042", "battery": 19}) is False


def test_battery_ok_with_own_minimum():
    assert battery_ok({"id": "SNS-0042", "battery": 40}, minimum=50) is False


def test_battery_missing():
    assert battery_ok({"id": "SNS-0042"}) is False
