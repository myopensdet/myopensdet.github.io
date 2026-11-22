# Template from myOpenSDET: https://myopensdet.github.io/
"""OpenAPI playbook: the inventory finds gaps in a spec, and the smoke test and the pytest
template pass on a local API that follows its spec and catch each kind of break.
All offline. With ZTS_ONLINE=1, the Petstore findings shown on the page are checked too."""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "openapi_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"

ORDER = {
    "type": "object",
    "required": ["id", "status", "total"],
    "properties": {
        "id": {"type": "integer"},
        "status": {"type": "string", "enum": ["new", "paid"]},
        "total": {"type": "string"},
    },
}
ERROR = {"type": "object", "required": ["message"], "properties": {"message": {"type": "string"}}}


def json_answer(schema_ref: str) -> dict:
    return {"application/json": {"schema": {"$ref": schema_ref}}}


ORDER_JSON = json_answer("#/components/schemas/Order")
ERROR_JSON = json_answer("#/components/schemas/Error")
ORDER_ID = {"name": "orderId", "in": "path", "required": True, "schema": {"type": "integer"}}

SPEC = {
    "openapi": "3.1.0",
    "info": {"title": "Orders API", "version": "2.4.0"},
    "security": [{"bearer": []}],
    "components": {
        "schemas": {"Order": ORDER, "Error": ERROR},
        "securitySchemes": {"bearer": {"type": "http", "scheme": "bearer"}},
    },
    "paths": {
        "/health": {
            "get": {
                "security": [],
                "responses": {"200": {"description": "up"}, "503": {"description": "down"}},
            }
        },
        "/orders": {
            "get": {
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string", "enum": ["new", "paid"]},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "orders",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Order"},
                                }
                            }
                        },
                    },
                    "401": {"description": "no login", "content": ERROR_JSON},
                },
            },
            "post": {
                "requestBody": {"content": ORDER_JSON},
                "responses": {"201": {"description": "created"}},
            },
        },
        "/orders/{orderId}": {
            "get": {
                "parameters": [ORDER_ID],
                "responses": {
                    "200": {"description": "one order", "content": ORDER_JSON},
                    "401": {"description": "no login", "content": ERROR_JSON},
                    "404": {"description": "not found", "content": ERROR_JSON},
                },
            }
        },
    },
}  # fmt: skip

GAPPY_SPEC = {
    "openapi": "3.0.3",
    "info": {"title": "Users API", "version": "1.0.0"},
    "paths": {
        "/users/{name}": {
            "get": {
                "security": [{"key": []}],
                "parameters": [{"name": "name", "in": "path", "required": True}],
                "responses": {
                    "200": {
                        "description": "a user",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "password": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
SUFFIXES = {".py", ".ini", ".txt", ".md", ".json"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in SUFFIXES or p.name == ".gitignore")
    and p.name != "__init__.py"
)


def make_handler(bug: str | None):
    class Orders(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep test output quiet
            pass

        def answer(self, status, data, media="application/json"):
            raw = data.encode() if isinstance(data, str) else json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", media)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):  # noqa: N802  (name required by http.server)
            path = self.path.split("?")[0]
            if path == "/health":
                return self.answer(200, "")
            logged_in = self.headers.get("Authorization") == "Bearer test-token"
            if not logged_in and bug != "no-login-check":
                return self.answer(401, {"message": "Log in first"})
            if path == "/orders":
                order = {"id": 7, "status": "new", "total": "10.00"}
                if bug == "schema":
                    del order["total"]
                return self.answer(200, [order])
            if path.startswith("/orders/"):
                if path.endswith("/7"):
                    if bug == "content-type":
                        return self.answer(200, "<order/>", "application/xml")
                    return self.answer(200, {"id": 7, "status": "paid", "total": "10.00"})
                if bug == "crash":
                    return self.answer(500, {"message": "NullPointerException"})
                return self.answer(404, {"message": "No such order"})
            return self.answer(404, {"message": "No such page"})

    return Orders


@pytest.fixture
def server(request):
    bug = getattr(request, "param", None)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(bug))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


@pytest.fixture
def spec_file(tmp_path):
    path = tmp_path / "openapi.json"
    path.write_text(json.dumps(SPEC), encoding="utf-8")
    return path


def check(*args, cwd=KIT):
    return subprocess.run(
        [sys.executable, str(KIT / "openapi_check.py"), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )


def smoke(spec_file, base, *extra):
    return check("smoke", str(spec_file), "--base-url", base, "--param", "orderId=7", *extra)


LOGIN = ("-H", "Authorization: Bearer test-token")


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_inventory_lists_every_endpoint_and_writes_a_plan(spec_file, tmp_path):
    plan = tmp_path / "plan.md"
    result = check("inventory", str(spec_file), "--plan", str(plan))
    assert result.returncode == 0, result.stderr
    assert "Orders API 2.4.0: 4 endpoints" in result.stdout
    assert "POST /orders" in result.stdout
    text = plan.read_text(encoding="utf-8")
    assert CREDIT in text
    assert "| `GET /orders/{orderId}` | yes | ? | [ ] | [ ] | [ ] | [ ] |" in text
    assert "| `GET /health` | no | ? | [ ] | [ ] | n/a | n/a |" in text


def test_inventory_finds_the_gaps_in_a_spec(tmp_path):
    path = tmp_path / "users.yaml"
    path.write_text(yaml.safe_dump(GAPPY_SPEC), encoding="utf-8")  # YAML works too
    result = check("inventory", str(path))
    line = next(row for row in result.stdout.splitlines() if row.startswith("GET /users"))
    assert "answer includes password" in line
    assert "needs login, but no 401/403 listed" in line
    assert "no error answer listed" in line


def test_smoke_passes_on_an_api_that_follows_its_spec(spec_file, server):
    result = smoke(spec_file, server, *LOGIN)
    assert result.returncode == 0, result.stdout
    assert "3 ok, 0 with problems, 0 skipped" in result.stdout
    assert "test-token" not in result.stdout
    assert "'Authorization': '***'" in result.stdout


def test_smoke_says_what_it_could_not_call(spec_file, server):
    result = check("smoke", str(spec_file), "--base-url", server, *LOGIN)
    assert "skipped: needs --param orderId=..." in result.stdout


@pytest.mark.parametrize(
    ("server", "expected"),
    [
        ("schema", "schema: 0: 'total' is a required property"),
        ("content-type", "answer is application/xml, spec says application/json"),
        ("no-login-check", "answered without login"),
    ],
    indirect=["server"],
)
def test_smoke_catches_each_kind_of_break(spec_file, server, expected):
    extra = () if expected == "answered without login" else LOGIN
    result = smoke(spec_file, server, *extra)
    assert result.returncode == 1
    assert expected in result.stdout


@pytest.mark.parametrize("server", ["crash"], indirect=True)
def test_smoke_catches_a_server_error(spec_file, server):
    result = check("smoke", str(spec_file), "--base-url", server, "--param", "orderId=999", *LOGIN)
    assert "server error 500; 500 is not listed in the spec" in result.stdout


def test_without_login_the_api_refuses_and_smoke_is_happy(spec_file, server):
    result = smoke(spec_file, server)
    assert result.returncode == 0, result.stdout


def run_template(spec_file, server, login=True):
    env = {**os.environ, "OPENAPI_SPEC": str(spec_file), "BASE_URL": server}
    env.pop("AUTH_HEADER", None)
    env.pop("AUTH_VALUE", None)
    if login:
        env |= {"AUTH_HEADER": "Authorization", "AUTH_VALUE": "Bearer test-token"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=KIT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_the_template_passes_on_an_api_that_follows_its_spec(spec_file, server):
    result = run_template(spec_file, server)
    assert result.returncode == 0, result.stdout[-2000:]
    assert "3 passed" in result.stdout


@pytest.mark.parametrize("server", ["schema"], indirect=True)
def test_the_template_names_the_endpoint_that_broke(spec_file, server):
    result = run_template(spec_file, server)
    assert "FAILED tests/test_contract.py::test_get_matches_the_spec[GET /orders]" in result.stdout


@pytest.mark.skipif(os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1 to call Petstore")
def test_petstore_still_shows_what_the_page_shows():
    url = "https://petstore3.swagger.io/api/v3/openapi.json"
    result = check("smoke", url, "--param", "petId=1", "--param", "orderId=1",
                   "--param", "username=user1", "--param", "tags=tag1")  # fmt: skip
    rows = {line.split("  ")[0].strip(): line for line in result.stdout.splitlines()}
    assert "answered without login" in rows["GET /store/inventory"]
    assert "server error 500" in rows["GET /pet/{petId}"]
    assert "says JSON, but the body isn't JSON" in rows["GET /user/login"]
