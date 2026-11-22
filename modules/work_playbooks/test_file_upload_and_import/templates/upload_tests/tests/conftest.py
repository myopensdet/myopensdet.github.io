# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Shared setup for upload and import tests. Test files are made here, in code,
so you never need a folder of sample files. Change the parts marked CHANGE."""

import os

import requests

# CHANGE 1: the address of the API you test.
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8780")

# CHANGE 2: your paths, the form field name, and the size limit from the spec.
UPLOAD_PATH = "/api/files"
IMPORT_PATH = "/api/import/customers"
LIST_PATH = "/api/customers"  # where imported rows can be read back
FIELD = "file"
MAX_BYTES = 5 * 1024 * 1024

# CHANGE 3: if your API needs a login, put the header here (from the terminal, never a file).
HEADERS = {"Authorization": os.environ["API_AUTH"]} if os.environ.get("API_AUTH") else {}

# Real file starts ("magic bytes"): servers that check content look at these.
PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 100
PDF = b"%PDF-1.7\n" + b"\0" * 100


def upload(path: str, name: str, data: bytes, mime: str = "application/octet-stream"):
    return requests.post(
        f"{BASE_URL}{path}", files={FIELD: (name, data, mime)}, headers=HEADERS, timeout=60
    )


def csv_file(*lines: str, bom: bool = False) -> bytes:
    text = "\r\n".join(lines) + "\r\n"
    return ("﻿" if bom else "").encode() + text.encode("utf-8")


def count_rows() -> int:
    return len(requests.get(f"{BASE_URL}{LIST_PATH}", headers=HEADERS, timeout=10).json())
