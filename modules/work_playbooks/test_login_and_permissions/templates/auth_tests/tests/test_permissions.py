# Template from myOpenSDET: https://myopensdet.github.io/
"""Permissions: each user sees only their own data; only admins open admin pages."""

from tests.conftest import A_RECORD_PATH, ADMIN_PATH, B_RECORD_PATH, get


def test_user_can_read_their_own_record(user_a):
    assert get(A_RECORD_PATH, user_a).status_code == 200


def test_user_cannot_read_another_users_record(user_a):
    answer = get(B_RECORD_PATH, user_a)
    assert answer.status_code in (403, 404), f"user A read user B's record: {answer.text}"


def test_other_user_cannot_read_user_as_record(user_b):
    answer = get(A_RECORD_PATH, user_b)
    assert answer.status_code in (403, 404), f"user B read user A's record: {answer.text}"


def test_normal_user_cannot_open_the_admin_page(user_a):
    assert get(ADMIN_PATH, user_a).status_code == 403


def test_admin_can_open_the_admin_page(admin):
    assert get(ADMIN_PATH, admin).status_code == 200
