# Template from myOpenSDET: https://myopensdet.github.io/
import os

import pytest
from gql import GraphQLClient

# The practice API: a free, public GraphQL server. Mutations answer, but nothing is saved.
# For your own app, set GRAPHQL_URL (and GRAPHQL_TOKEN if it needs a login).
PRACTICE_API = "https://graphqlzero.almansi.me/api"


@pytest.fixture(scope="session")
def client():
    headers = {}
    if token := os.environ.get("GRAPHQL_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    gql = GraphQLClient(os.environ.get("GRAPHQL_URL", PRACTICE_API), headers=headers)
    yield gql
    gql.close()
