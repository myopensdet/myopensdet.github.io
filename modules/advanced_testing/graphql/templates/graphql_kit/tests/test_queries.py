# Template from myOpenSDET: https://myopensdet.github.io/
import pytest

POST = """
query Post($id: ID!) {
  post(id: $id) { id title user { id name } }
}
"""

POSTS_PAGE = """
query Posts($page: Int!, $limit: Int!) {
  posts(options: { paginate: { page: $page, limit: $limit } }) {
    data { id }
    meta { totalCount }
  }
}
"""


def test_post_by_id(client):
    post = client.data(POST, {"id": "1"})["post"]
    assert post["id"] == "1"
    assert post["title"]
    assert post["user"]["id"] == "1"


def test_only_the_fields_asked_for_come_back(client):
    post = client.data("query { post(id: 1) { id } }")["post"]
    assert post == {"id": "1"}


@pytest.mark.parametrize("page, limit, ids", [(1, 2, ["1", "2"]), (2, 2, ["3", "4"])])
def test_pages(client, page, limit, ids):
    posts = client.data(POSTS_PAGE, {"page": page, "limit": limit})["posts"]
    assert [p["id"] for p in posts["data"]] == ids
    assert posts["meta"]["totalCount"] == 100


@pytest.mark.xfail(strict=True, reason="Known bug: a missing post comes back as an empty object")
def test_a_missing_post_is_null(client):
    assert client.data(POST, {"id": "9999"})["post"] is None
