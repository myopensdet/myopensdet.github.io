# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
import pytest


@pytest.mark.parametrize("user_id", [1, 2, 3])
def test_user_profile(api, user_id):
    assert api.get(f"/api/users/{user_id}").status_code == 200


def test_admin_sees_all_users(admin_api):
    assert len(admin_api.get("/api/users").json()) > 0


@pytest.mark.skip
def test_delete_user(admin_api):
    assert admin_api.get("/api/users/9/delete").status_code == 200
