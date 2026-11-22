# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Plan and smoke-test an API from its OpenAPI (Swagger) file.

    python openapi_check.py inventory openapi.json --plan endpoint_plan.md
        Every endpoint in one table, gaps in the spec itself, and a plan to fill in.

    python openapi_check.py smoke openapi.json --base-url https://staging.example.com/api \\
        --param petId=10 --param username=user1
        Calls every GET it can, and checks the status, the format and the schema
        against the spec, and that endpoints that need a login refuse a call without one.
        Exit code 1 if anything is wrong, so a pipeline can use it.

The spec can be a file or a URL, in JSON (or YAML, with PyYAML installed). Only GET
requests are sent. Header values for Authorization, Cookie and API keys are never printed.
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from jsonschema import Draft202012Validator

SECRET_HEADERS = {"authorization", "cookie", "x-api-key", "api-key", "api_key"}
SENSITIVE_FIELDS = {"password", "passwd", "secret", "token", "pin", "cvv", "card_number"}


@dataclass
class Operation:
    method: str
    path: str
    spec: dict
    parameters: list

    @property
    def name(self) -> str:
        return f"{self.method} {self.path}"


# ---------- reading the spec ----------


def load_spec(source: str) -> dict:
    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        text = response.text
    else:
        text = Path(source).read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        return json.loads(text)
    try:
        import yaml  # noqa: PLC0415  (only needed for YAML specs)
    except ImportError:
        sys.exit("This spec is YAML: python -m pip install pyyaml, or use the JSON version")
    return yaml.safe_load(text)


def operations(spec: dict) -> list[Operation]:
    found = []
    for path, item in spec.get("paths", {}).items():
        shared = item.get("parameters", [])
        for method in ("get", "post", "put", "patch", "delete"):
            if method in item:
                op = item[method]
                params = shared + op.get("parameters", [])
                found.append(Operation(method.upper(), path, op, params))
    return found


def resolve(spec: dict, node: dict) -> dict:
    """Follow a {"$ref": "#/components/..."} to what it points to."""
    for _ in range(20):  # a $ref can point to another $ref
        if not (isinstance(node, dict) and "$ref" in node):
            return node
        target = spec
        for part in node["$ref"].lstrip("#/").split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        node = target
    return node


def needs_login(spec: dict, op: Operation) -> bool:
    rules = op.spec.get("security", spec.get("security", []))
    return any(rule for rule in rules)


def field_names(spec: dict, schema: dict, depth: int = 0) -> set[str]:
    """Every property name in a schema, following $refs, arrays and nested objects."""
    schema = resolve(spec, schema or {})
    if depth > 6 or not isinstance(schema, dict):
        return set()
    names = set()
    for name, sub in schema.get("properties", {}).items():
        names.add(name.lower())
        names |= field_names(spec, sub, depth + 1)
    if "items" in schema:
        names |= field_names(spec, schema["items"], depth + 1)
    for key in ("allOf", "oneOf", "anyOf"):
        for sub in schema.get(key, []):
            names |= field_names(spec, sub, depth + 1)
    return names


# ---------- inventory ----------


def spec_gaps(spec: dict, op: Operation) -> list[str]:
    responses = op.spec.get("responses", {})
    codes = set(responses)
    gaps = []
    if needs_login(spec, op) and not codes & {"401", "403"}:
        gaps.append("needs login, but no 401/403 listed")
    if not any(code.startswith("4") for code in codes):
        gaps.append("no error answer listed")
    elif all("content" not in resolve(spec, r) for c, r in responses.items() if c[0] == "4"):
        gaps.append("error answers have no body format")
    for code, answer in responses.items():
        if code.startswith("2"):
            for media in resolve(spec, answer).get("content", {}).values():
                exposed = field_names(spec, media.get("schema", {})) & SENSITIVE_FIELDS
                if exposed:
                    gaps.append(f"answer includes {', '.join(sorted(exposed))}")
                    break
    return sorted(set(gaps))


def inputs_of(spec: dict, op: Operation) -> str:
    needed = [
        p["name"] for p in map(lambda p: resolve(spec, p), op.parameters) if p.get("required")
    ]
    if "requestBody" in op.spec:
        needed.append("body")
    return ", ".join(needed) or "-"


def cmd_inventory(args) -> int:
    spec = load_spec(args.spec)
    ops = operations(spec)
    info = spec.get("info", {})
    print(f"{info.get('title', 'API')} {info.get('version', '')}: {len(ops)} endpoints\n")
    print(f"{'endpoint':<36} {'login':<5}  {'needs':<20} {'answers':<24} spec gaps")
    print("-" * 120)
    gap_count = 0
    for op in ops:
        codes = ",".join(op.spec.get("responses", {}))
        gaps = spec_gaps(spec, op)
        gap_count += len(gaps)
        login = "yes" if needs_login(spec, op) else "no"
        print(f"{op.name:<36} {login:<5}  {inputs_of(spec, op):<20} {codes:<24} {'; '.join(gaps)}")
    print(f"\n{gap_count} spec gaps. Each one is a question for the team.")
    if args.plan:
        write_plan(spec, ops, Path(args.plan))
        print(f"Plan written to {args.plan}")
    return 0


def write_plan(spec: dict, ops: list[Operation], path: Path) -> None:
    info = spec.get("info", {})
    lines = [
        "<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->",
        f"# Test plan: {info.get('title', 'API')} {info.get('version', '')}",
        "",
        "Priority: 1 = money, security or data loss; 2 = main user flows; 3 = the rest.",
        "Tick a box when the checks exist. Write questions under the table.",
        "",
        "| Endpoint | Login | Priority | Happy path | Bad input | No / wrong login | Not found |"
        " Spec gaps |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for op in ops:
        login = "yes" if needs_login(spec, op) else "no"
        gaps = "; ".join(spec_gaps(spec, op)) or "-"
        auth_box = "[ ]" if login == "yes" else "n/a"
        not_found = "[ ]" if "{" in op.path else "n/a"
        lines.append(
            f"| `{op.name}` | {login} | ? | [ ] | [ ] | {auth_box} | {not_found} | {gaps} |"
        )
    lines += ["", "## Questions for the team", "", "1. ?", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------- smoke ----------


def value_for(param: dict, given: dict) -> str | None:
    if param["name"] in given:
        return given[param["name"]]
    schema = param.get("schema", {})
    for key in ("example", "default"):
        if key in param:
            return str(param[key])
        if key in schema:
            return str(schema[key])
    if schema.get("enum"):
        return str(schema["enum"][0])
    return None


def build_request(spec: dict, op: Operation, given: dict) -> tuple[str, dict] | str:
    """(path with values, query) or the reason it can't be called."""
    path, query = op.path, {}
    for param in map(lambda p: resolve(spec, p), op.parameters):
        where, name = param.get("in"), param["name"]
        value = value_for(param, given)
        if where == "path":
            if value is None:
                return f"needs --param {name}=..."
            path = path.replace("{" + name + "}", value)
        elif where == "query" and (param.get("required") or name in given):
            if value is None:
                return f"needs --param {name}=..."
            query[name] = value
    return path, query


def check_answer(
    spec: dict, op: Operation, response: requests.Response, logged_in: bool
) -> list[str]:
    problems = []
    status = str(response.status_code)
    responses = op.spec.get("responses", {})
    if needs_login(spec, op) and not logged_in and response.status_code < 400:
        problems.append("answered without login")
    if response.status_code >= 500:
        problems.append(f"server error {status}")
    if status not in responses:
        problems.append(f"{status} is not listed in the spec")
    documented = resolve(spec, responses.get(status, responses.get("default", {})))
    content = documented.get("content", {})
    media = response.headers.get("Content-Type", "").split(";")[0].strip()
    if not content:
        return problems
    if media not in content:
        problems.append(f"answer is {media or 'untyped'}, spec says {', '.join(content)}")
        return problems
    if "json" in media:
        try:
            body = response.json()
        except ValueError:
            return [*problems, "says JSON, but the body isn't JSON"]
        schema = content[media].get("schema")
        if schema:
            root = {**schema, "components": spec.get("components", {})}
            errors = sorted(Draft202012Validator(root).iter_errors(body), key=str)
            if errors:
                where = "/".join(str(p) for p in errors[0].absolute_path) or "body"
                problems.append(f"schema: {where}: {errors[0].message[:80]}")
    return problems


def parse_pairs(items: list[str], sep: str, what: str) -> dict:
    pairs = {}
    for item in items:
        key, found, value = item.partition(sep)
        if not found:
            sys.exit(f'A {what} needs "{sep}", like name{sep}value: {item!r}')
        pairs[key.strip()] = value.strip()
    return pairs


def base_url_of(spec: dict, source: str, given: str | None) -> str:
    if given:
        return given.rstrip("/")
    server = (spec.get("servers") or [{"url": ""}])[0]["url"]
    if server.startswith("http"):
        return server.rstrip("/")
    if source.startswith("http"):
        return urljoin(source, server).rstrip("/")
    sys.exit("The spec has no full server address: add --base-url https://...")


def cmd_smoke(args) -> int:
    spec = load_spec(args.spec)
    base = base_url_of(spec, args.spec, args.base_url)
    given = parse_pairs(args.param, "=", "--param")
    headers = parse_pairs(args.header, ":", "header")
    shown = {k: ("***" if k.lower() in SECRET_HEADERS else v) for k, v in headers.items()}
    print(f"Smoke test of {base}" + (f"  headers: {shown}" if shown else "") + "\n")
    print(f"{'endpoint':<36} {'status':>6} {'ms':>5}  result")
    print("-" * 110)
    counts = {"ok": 0, "problem": 0, "skipped": 0}
    for op in operations(spec):
        if op.method != "GET":
            continue
        built = build_request(spec, op, given)
        if isinstance(built, str):
            counts["skipped"] += 1
            print(f"{op.name:<36} {'-':>6} {'-':>5}  skipped: {built}")
            continue
        path, query = built
        start = time.perf_counter()
        try:
            response = requests.get(base + path, params=query, headers=headers, timeout=15)
        except requests.RequestException as error:
            counts["problem"] += 1
            print(f"{op.name:<36} {'ERROR':>6} {'-':>5}  {type(error).__name__}")
            continue
        ms = (time.perf_counter() - start) * 1000
        logged_in = any(name.lower() in SECRET_HEADERS for name in headers)
        problems = check_answer(spec, op, response, logged_in)
        counts["problem" if problems else "ok"] += 1
        result = "; ".join(problems) or "ok"
        print(f"{op.name:<36} {response.status_code:>6} {ms:>5.0f}  {result}")
    print(f"\n{counts['ok']} ok, {counts['problem']} with problems, {counts['skipped']} skipped")
    return 1 if counts["problem"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("inventory", help="list endpoints and spec gaps, write a plan")
    inv.add_argument("spec", help="file or URL of the OpenAPI spec")
    inv.add_argument("--plan", help="write a Markdown test plan to this file")
    inv.set_defaults(run=cmd_inventory)

    smoke = sub.add_parser("smoke", help="call every GET and check it against the spec")
    smoke.add_argument("spec", help="file or URL of the OpenAPI spec")
    smoke.add_argument("--base-url", help="where the API runs, if not in the spec")
    smoke.add_argument("--param", action="append", default=[], help="name=value")
    smoke.add_argument("-H", "--header", action="append", default=[], help='"Name: value"')
    smoke.set_defaults(run=cmd_smoke)

    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
