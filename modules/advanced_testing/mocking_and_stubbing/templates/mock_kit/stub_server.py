# Template from myOpenSDET: https://myopensdet.github.io/
"""A tiny stub server that answers like a real service, from files you write.

It reads WireMock's mapping format (a small part of it), so the same files work in
WireMock when you need more. Standard library only.

    python stub_server.py                       # stubs/mappings, port 8798
    python stub_server.py --port 9000 --mappings other/folder

Each mapping: when a request matches "request", send "response".
  request:  method, urlPath, bodyPatterns [{"contains": "text"}]
  response: status, headers, jsonBody (or body), fixedDelayMilliseconds
  priority: 1 wins over 10 when both match

Like WireMock, it remembers every request, so a test can check what was sent:
  GET    /__admin/requests   the requests so far, newest first
  DELETE /__admin/requests   forget them (call it at the start of each test)
"""

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MAPPINGS: list[dict] = []
JOURNAL: list[dict] = []


def load(folder: Path) -> list[dict]:
    mappings = []
    for path in sorted(folder.glob("*.json")):
        try:
            mappings.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as err:
            raise SystemExit(f"{path.name} is not valid JSON: {err}") from err
    if not mappings:
        raise SystemExit(f"No .json mapping files in {folder}")
    return sorted(mappings, key=lambda m: m.get("priority", 5))


def matches(rule: dict, method: str, path: str, body: str) -> bool:
    if rule.get("method", "ANY") not in ("ANY", method):
        return False
    if "urlPath" in rule and rule["urlPath"] != path:
        return False
    return all(p["contains"] in body for p in rule.get("bodyPatterns", []))


class Stub(BaseHTTPRequestHandler):
    def answer(self, status: int, body: str, headers: dict | None = None) -> None:
        data = body.encode()
        self.send_response(status)
        for name, value in (headers or {"Content-Type": "application/json"}).items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_any(self) -> None:
        path = urlsplit(self.path).path
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        if path == "/__admin/requests":
            if self.command == "DELETE":
                JOURNAL.clear()
            self.answer(200, json.dumps({"requests": JOURNAL, "meta": {"total": len(JOURNAL)}}))
            return
        JOURNAL.insert(0, {"request": {"method": self.command, "url": self.path, "body": body,
                                       "headers": dict(self.headers)}})  # fmt: skip
        for mapping in MAPPINGS:
            if matches(mapping["request"], self.command, path, body):
                response = mapping["response"]
                time.sleep(response.get("fixedDelayMilliseconds", 0) / 1000)
                text = json.dumps(response["jsonBody"]) if "jsonBody" in response else ""
                self.answer(response["status"], text or response.get("body", ""),
                            response.get("headers"))  # fmt: skip
                return
        self.answer(404, json.dumps({"error": f"No stub matches {self.command} {path}"}))

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = handle_any  # noqa: N815

    def log_message(self, fmt, *args):
        if not self.path.startswith("/__admin"):
            print(f"stub got: {self.command} {self.path} -> {args[1]}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="A tiny stub server.")
    parser.add_argument("--port", type=int, default=8798)
    parser.add_argument("--mappings", default=str(Path(__file__).with_name("stubs") / "mappings"))
    args = parser.parse_args()
    MAPPINGS.extend(load(Path(args.mappings)))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Stub)
    print(f"Stub with {len(MAPPINGS)} mappings on http://127.0.0.1:{args.port}"
          "  (Ctrl+C to stop)", flush=True)  # fmt: skip
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
