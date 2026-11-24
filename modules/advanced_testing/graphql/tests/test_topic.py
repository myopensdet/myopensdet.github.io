# Template from myOpenSDET: https://myopensdet.github.io/
"""GraphQL testing: the client and the schema check work offline against a local server,
and, with ZTS_ONLINE=1, the kit passes against the public practice API."""

import json
import os
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[1].parent
KIT = TOPIC / "templates" / "graphql_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts
    and (p.suffix in {".py", ".ini", ".txt"} or p.name == ".gitignore")
)  # fmt: skip

sys.path.insert(0, str(KIT))
from gql import GraphQLClient, GraphQLError  # noqa: E402
from schema_check import compare, schema_fields, type_name  # noqa: E402


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


def test_expected_fields_is_valid_json():
    expected = json.loads((KIT / "expected_fields.json").read_text(encoding="utf-8"))
    assert all(isinstance(fields, dict) and fields for fields in expected.values())


# A local server that answers with whatever the test puts in ANSWER, and keeps what it got.
ANSWER: dict = {}
RECEIVED: list = []


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        RECEIVED.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        body = ANSWER["body"].encode()
        self.send_response(ANSWER["status"])
        self.send_header("Content-Type", ANSWER["type"])
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


@pytest.fixture(scope="module")
def local():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield GraphQLClient(f"http://127.0.0.1:{server.server_port}/graphql")
    server.shutdown()


def answer(status=200, body=None, type_="application/json"):
    ANSWER.update(status=status, body=json.dumps(body) if body is not None else "", type=type_)


def test_client_sends_query_variables_and_operation(local):
    answer(body={"data": {"post": {"id": "1"}}})
    assert local.data("query P($id: ID!) { post(id: $id) { id } }", {"id": "1"}, "P") == {
        "post": {"id": "1"}
    }
    assert RECEIVED[-1] == {
        "query": "query P($id: ID!) { post(id: $id) { id } }",
        "variables": {"id": "1"},
        "operationName": "P",
    }


def test_data_fails_on_errors_even_with_200(local):
    error = {"message": "boom", "path": ["post", 0, "id"], "extensions": {"code": "X_CODE"}}
    answer(body={"data": {"post": None}, "errors": [error]})
    with pytest.raises(GraphQLError) as caught:
        local.data("{ post { id } }")
    message = "GraphQL answered 200 with 1 error(s):\n  [X_CODE] at post.0.id: boom"
    assert str(caught.value) == message
    assert local.execute("{ post { id } }").codes() == ["X_CODE"]


def test_a_non_json_answer_is_explained(local):
    ANSWER.update(status=403, body="<html>Forbidden</html>", type="text/html")
    with pytest.raises(AssertionError, match=r"^Not a GraphQL answer: 403 text/html '<html>"):
        local.execute("{ x }")


def test_type_names_are_written_like_the_schema():
    string = {"kind": "SCALAR", "name": "String"}
    assert type_name(string) == "String"
    assert type_name({"kind": "NON_NULL", "ofType": string}) == "String!"
    listed = {"kind": "LIST", "ofType": {"kind": "NON_NULL", "ofType": string}}
    assert type_name({"kind": "NON_NULL", "ofType": listed}) == "[String!]!"


def test_compare_lists_every_problem():
    def field(name, type_):
        return {"name": name, "type": {"kind": "SCALAR", "name": type_}}

    introspection = {
        "__schema": {
            "types": [
                {"name": "Post", "fields": [field("id", "ID")]},
                {"name": "__Type", "fields": [field("x", "X")]},
                {"name": "Int", "fields": None},
            ]
        }
    }
    actual = schema_fields(introspection)
    assert actual == {"Post": {"id": "ID"}}
    expected = {"Post": {"id": "ID!", "title": "String"}, "User": {"id": "ID"}}
    assert compare(expected, actual) == [
        "changed Post.id: expected ID!, found ID",
        "missing field Post.title",
        "missing type User",
    ]
    assert compare({"Post": {"id": "ID"}}, actual) == []


online = pytest.mark.skipif(
    os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1 to call the real public APIs"
)


@online
def test_kit_passes_against_the_practice_api():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"],
        cwd=KIT, capture_output=True, text=True, timeout=300,
    )  # fmt: skip
    assert "14 passed, 2 xfailed" in result.stdout, result.stdout[-3000:]


@online
def test_schema_check_passes_against_the_practice_api():
    result = subprocess.run(
        [sys.executable, "schema_check.py"], cwd=KIT, capture_output=True, text=True, timeout=120
    )
    assert result.stdout.strip() == "12 fields checked, 0 problem(s)", result.stdout
    assert result.returncode == 0
