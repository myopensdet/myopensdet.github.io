# Template from myOpenSDET: https://myopensdet.github.io/
"""A small practice API with a file upload and a CSV import. Only for practice.

    python practice_api.py            # http://127.0.0.1:8780, with planted bugs
    python practice_api.py --fixed    # the same API with the bugs fixed

The rules it should follow:
  POST /api/files              field "file": PNG, JPEG or PDF only, 1 byte to 5 MB
  POST /api/import/customers   field "file": CSV with columns email,name.
                               All rows or none: one bad row rejects the whole file.
  GET  /api/customers          everyone imported so far

Three planted bugs, the kind real apps ship. Python only, no packages.
It listens on your computer only (127.0.0.1) and keeps files in memory, never on disk."""

import argparse
import csv
import io
import json
import re
import threading
from email import message_from_bytes
from email.policy import HTTP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import PurePosixPath, PureWindowsPath

MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {".png": b"\x89PNG\r\n\x1a\n", ".jpg": b"\xff\xd8\xff", ".jpeg": b"\xff\xd8\xff",
           ".pdf": b"%PDF-"}  # fmt: skip
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def read_file_field(content_type: str, body: bytes) -> tuple[str, bytes] | None:
    """The name and bytes of the form field called "file", or None."""
    message = message_from_bytes(
        f"Content-Type: {content_type}\r\n\r\n".encode() + body, policy=HTTP
    )
    for part in message.iter_parts():
        if part.get_param("name", header="content-disposition") == "file":
            return part.get_filename() or "", part.get_payload(decode=True) or b""
    return None


def make_handler(fixed: bool):
    files: list[dict] = []
    customers: list[dict] = []
    lock = threading.Lock()

    class API(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):  # keep the terminal quiet
            pass

        def answer(self, status, data):
            raw = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):  # noqa: N802  (name required by http.server)
            if self.path == "/api/customers":
                return self.answer(200, customers)
            return self.answer(404, {"error": "No such page"})

        def do_POST(self):  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length)
            field = read_file_field(self.headers.get("Content-Type", ""), body)
            if field is None:
                return self.answer(400, {"error": 'Send the file in a form field called "file"'})
            if self.path == "/api/files":
                return self.upload(*field)
            if self.path == "/api/import/customers":
                return self.import_customers(field[1])
            return self.answer(404, {"error": "No such page"})

        def upload(self, name, data):
            name = PureWindowsPath(PurePosixPath(name).name).name  # drop any folder part
            suffix = PurePosixPath(name).suffix.lower()
            if not data:
                return self.answer(400, {"error": "The file is empty"})
            limit = MAX_BYTES if fixed else 50 * 1024 * 1024  # BUG 1: 50 MB, not 5 MB
            if len(data) > limit:
                return self.answer(413, {"error": "The file is bigger than 5 MB"})
            if suffix not in ALLOWED:
                return self.answer(415, {"error": "Only PNG, JPEG or PDF files"})
            if fixed and not data.startswith(ALLOWED[suffix]):  # BUG 2: name checked, not content
                return self.answer(415, {"error": "The file is not really a " + suffix})
            with lock:
                record = {"id": len(files) + 1, "name": name, "size": len(data)}
                files.append(record)
            return self.answer(201, record)

        def import_customers(self, data):
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                return self.answer(400, {"error": "Save the file as UTF-8 CSV"})
            reader = csv.DictReader(io.StringIO(text))
            if reader.fieldnames is None or not {"email", "name"} <= set(reader.fieldnames):
                return self.answer(400, {"error": "The columns must be: email,name"})
            good, errors = [], []
            for number, row in enumerate(reader, start=2):  # row 1 is the header
                email, name = (row["email"] or "").strip(), (row["name"] or "").strip()
                if not EMAIL.match(email):
                    errors.append({"row": number, "error": f"Not an email: {email!r}"})
                elif not name:
                    errors.append({"row": number, "error": "Name is empty"})
                else:
                    good.append({"email": email, "name": name})
                    if not fixed and not errors:  # BUG 3: rows before a bad one are saved
                        with lock:
                            customers.append(good[-1])
            if errors:
                return self.answer(400, {"imported": 0, "errors": errors})
            if fixed:
                with lock:
                    customers.extend(good)
            return self.answer(201, {"imported": len(good)})

    return API


class Server(ThreadingHTTPServer):
    daemon_threads = True


def serve(port: int = 8780, fixed: bool = False) -> ThreadingHTTPServer:
    return Server(("127.0.0.1", port), make_handler(fixed))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8780)
    parser.add_argument("--fixed", action="store_true", help="run with the bugs fixed")
    args = parser.parse_args()
    server = serve(args.port, args.fixed)
    kind = "bugs fixed" if args.fixed else "with planted bugs"
    print(f"Practice API ({kind}) on http://127.0.0.1:{args.port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped")
