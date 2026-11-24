# Template from myOpenSDET: https://myopensdet.github.io/
import pytest

CREATE = """
mutation Create($input: CreatePostInput!) {
  createPost(input: $input) { id title body }
}
"""

UPDATE = """
mutation Update($id: ID!, $input: UpdatePostInput!) {
  updatePost(id: $id, input: $input) { id title }
}
"""

DELETE = "mutation Delete($id: ID!) { deletePost(id: $id) }"

NEW_POST = {"title": "SNS-0042 battery low", "body": "Battery at 7% on GW-0001"}


def test_create_returns_what_was_sent(client):
    post = client.data(CREATE, {"input": NEW_POST})["createPost"]
    assert post["id"]
    assert {"title": post["title"], "body": post["body"]} == NEW_POST


def test_create_without_a_required_field(client):
    answer = client.execute(CREATE, {"input": {"title": "No body"}})
    assert answer.codes() == ["BAD_USER_INPUT"]
    assert 'Field "body" of required type "String!" was not provided' in answer.errors[0]["message"]
    assert answer.data is None


def test_update_changes_only_the_title(client):
    post = client.data(UPDATE, {"id": "1", "input": {"title": "Changed by a test"}})["updatePost"]
    assert post == {"id": "1", "title": "Changed by a test"}


def test_delete(client):
    assert client.data(DELETE, {"id": "1"})["deletePost"] is True


@pytest.mark.xfail(strict=True, reason="Known bug: deleting a post that doesn't exist says true")
def test_delete_a_missing_post(client):
    answer = client.execute(DELETE, {"id": "9999"})
    assert answer.errors or answer.data["deletePost"] is False
