# Template from myOpenSDET: https://myopensdet.github.io/
"""Start the stub server once for the test run, on a free port, and give tests its address.

To use WireMock instead (Docker): docker compose up -d, then
    STUB_URL=http://127.0.0.1:8799 python -m pytest
"""

import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import requests

KIT = Path(__file__).resolve().parents[1]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def stub_url():
    if url := os.environ.get("STUB_URL"):
        yield url
        return
    port = free_port()
    server = subprocess.Popen(
        [sys.executable, "stub_server.py", "--port", str(port)],
        cwd=KIT, stdout=subprocess.PIPE, text=True,
    )  # fmt: skip
    assert "Stub with" in server.stdout.readline()
    yield f"http://127.0.0.1:{port}"
    server.terminate()
    server.wait(timeout=10)


@pytest.fixture
def stub(stub_url):
    """The stub's address, with its request list emptied for this test."""
    requests.delete(f"{stub_url}/__admin/requests", timeout=5)
    return stub_url


def sent_to(stub_url: str) -> list[dict]:
    """What the stub received, newest first."""
    answer = requests.get(f"{stub_url}/__admin/requests", timeout=5).json()
    return [entry["request"] for entry in answer["requests"]]
