# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Send many variations of one request and see every answer in one table.

Use it in your first hour with a new endpoint, before you write any test:

    python api_probe.py POST https://your-app.example.com/api/orders --cases cases.json
    python api_probe.py GET  https://your-app.example.com/api/orders/42

Each case in cases.json has a "name" and a "body" (any JSON, or a string to send as-is).
The file is a list of cases, or {"cases": [...]} with a "$comment" line on top.
Add headers with -H, as often as needed. Read secrets from the environment, not the command:

    export API_TOKEN=...   then   -H "Authorization: Bearer $API_TOKEN"

Show only the fields you care about, instead of the start of each answer:

    --field total --field products.0.quantity

Header values for Authorization, Cookie and API keys are never printed.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

SECRET_HEADERS = {"authorization", "cookie", "x-api-key", "api-key"}
WIDTH = 70  # characters of each answer shown in the table


def parse_headers(raw: list[str]) -> dict[str, str]:
    headers = {}
    for item in raw:
        name, sep, value = item.partition(":")
        if not sep:
            sys.exit(f'A header needs a colon, like "Accept: application/json": {item!r}')
        headers[name.strip()] = value.strip()
    return headers


def load_cases(path: str | None) -> list[dict]:
    if path is None:
        return [{"name": "no body", "body": None}]
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(cases, dict):  # {"$comment": "...", "cases": [...]}
        cases = cases["cases"]
    for case in cases:
        if "name" not in case or "body" not in case:
            sys.exit(f'Every case needs a "name" and a "body": {case}')
    return cases


def pick(answer: str, paths: list[str]) -> str:
    """Show only the chosen fields: "total=179.96 products.0.quantity=4"."""
    try:
        data = json.loads(answer)
    except ValueError:
        return answer
    shown, found = [], False
    for path in paths:
        value, text = data, None
        for key in path.split("."):
            if isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            elif isinstance(value, dict) and key in value:
                value = value[key]
            else:
                text = "-"  # not in this answer
                break
        found = found or text is None
        shown.append(f"{path}={text or json.dumps(value)}")
    # None of the fields: show the answer itself, usually an error message.
    return " ".join(shown) if found else answer


def send(method: str, url: str, headers: dict, body, timeout: float) -> dict:
    kwargs = {}
    if isinstance(body, str):
        kwargs["data"] = body.encode()
        headers = {"Content-Type": "application/json", **headers}
    elif body is not None:
        kwargs["json"] = body
    start = time.perf_counter()
    try:
        response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    except requests.RequestException as error:
        return {"status": "ERROR", "ms": 0, "answer": type(error).__name__}
    ms = (time.perf_counter() - start) * 1000
    answer = " ".join(response.text.split())
    return {"status": response.status_code, "ms": ms, "answer": answer}


def shorten(text: str) -> str:
    return text if len(text) <= WIDTH else text[: WIDTH - 3] + "..."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("method", help="GET, POST, PUT, PATCH or DELETE")
    parser.add_argument("url")
    parser.add_argument("--cases", help="a JSON file with a list of {name, body}")
    parser.add_argument("-H", "--header", action="append", default=[], help='"Name: value"')
    parser.add_argument("--timeout", type=float, default=10, help="seconds per request")
    parser.add_argument("--field", action="append", default=[], help="a field to show: a.0.b")
    parser.add_argument("--save", help="also write every full answer to this JSON file")
    args = parser.parse_args(argv)

    headers = parse_headers(args.header)
    shown = {k: ("***" if k.lower() in SECRET_HEADERS else v) for k, v in headers.items()}
    print(f"{args.method.upper()} {args.url}")
    if shown:
        print("Headers:", shown)
    print()
    print(f"{'case':<28} {'status':>6} {'ms':>6}  answer")
    print("-" * (28 + 1 + 6 + 1 + 6 + 2 + WIDTH))

    results = []
    for case in load_cases(args.cases):
        result = send(args.method.upper(), args.url, headers, case["body"], args.timeout)
        results.append({"name": case["name"], "body": case["body"], **result})
        answer = pick(result["answer"], args.field) if args.field else result["answer"]
        row = f"{case['name'][:28]:<28} {result['status']!s:>6} {result['ms']:>6.0f}"
        print(f"{row}  {shorten(answer)}")

    if args.save:
        Path(args.save).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nFull answers saved to {args.save}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
