# Template from myOpenSDET: https://myopensdet.github.io/
"""GraphQL errors: assert on the error code, and never on the status code alone."""

import pytest
from gql import GraphQLError

POST = "query Post($id: ID!) { post(id: $id) { id } }"


def test_a_wrong_field_name(client):
    answer = client.execute("query { post(id: 1) { id titel } }")
    assert answer.codes() == ["GRAPHQL_VALIDATION_FAILED"]
    assert 'Did you mean "title"?' in answer.errors[0]["message"]


def test_a_missing_variable_still_answers_200(client):
    answer = client.execute(POST)
    assert answer.status == 200
    assert answer.codes() == ["BAD_USER_INPUT"]


def test_a_variable_of_the_wrong_type(client):
    answer = client.execute(POST, {"id": {"x": 1}})
    assert answer.codes() == ["BAD_USER_INPUT"]


def test_broken_query_text(client):
    answer = client.execute("query { post(id: 1) { id ")
    assert answer.codes() == ["GRAPHQL_PARSE_FAILED"]


def test_data_fails_loudly_on_errors(client):
    with pytest.raises(GraphQLError, match=r"\[BAD_USER_INPUT\]"):
        client.data(POST)
