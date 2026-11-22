# Template from myOpenSDET: https://myopensdet.github.io/
"""One check per GET endpoint in the spec: the status is listed, the format and the schema
match, and endpoints that need a login refuse a call without one. New endpoints in the
spec get a check without any change here."""

import pytest
import requests
from conftest import BASE_URL, HEADERS, PARAMS, SPEC
from openapi_check import build_request, check_answer, load_spec, operations

spec = load_spec(SPEC)
GETS = [op for op in operations(spec) if op.method == "GET"]


@pytest.mark.parametrize("op", GETS, ids=[op.name for op in GETS])
def test_get_matches_the_spec(op):
    built = build_request(spec, op, PARAMS)
    if isinstance(built, str):
        pytest.skip(built)
    path, query = built
    response = requests.get(BASE_URL + path, params=query, headers=HEADERS, timeout=15)
    problems = check_answer(spec, op, response, logged_in=bool(HEADERS))
    assert not problems, f"{response.status_code}: {'; '.join(problems)}"
