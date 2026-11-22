# Template from myOpenSDET: https://myopensdet.github.io/
"""Turn a curl command (from "Copy as cURL" in the browser, Postman or Bruno) into a
pytest test that uses requests. Login headers and cookies are never written into the
test: it reads them from environment variables instead.

    python curl_to_pytest.py request.txt > tests/test_from_curl.py
    pbpaste | python curl_to_pytest.py > tests/test_from_curl.py      (macOS)
"""

import json
import re
import shlex
import sys
from urllib.parse import urlsplit

SECRET_HEADERS = {"authorization": "API_AUTH", "cookie": "API_COOKIE", "x-api-key": "API_KEY"}
NOISE_HEADERS = {"user-agent", "accept-language", "accept-encoding", "sec-ch-ua",
                 "sec-ch-ua-mobile", "sec-ch-ua-platform", "sec-fetch-dest", "sec-fetch-mode",
                 "sec-fetch-site", "priority", "referer", "origin", "dnt", "connection",
                 "cache-control", "pragma"}  # fmt: skip
DATA_FLAGS = {"-d", "--data", "--data-raw", "--data-binary", "--json"}


def parse(command: str) -> dict:
    lines = [line for line in command.splitlines() if not line.lstrip().startswith("#")]
    words = shlex.split("\n".join(lines).replace("\\\n", " "))
    if not words or words[0] != "curl":
        raise SystemExit("Paste a command that starts with curl")
    request = {"method": None, "url": None, "headers": {}, "body": None}
    i = 1
    while i < len(words):
        word = words[i]
        if word in ("-X", "--request"):
            request["method"] = words[i + 1].upper()
            i += 1
        elif word in ("-H", "--header"):
            name, _, value = words[i + 1].partition(":")
            request["headers"][name.strip()] = value.strip()
            i += 1
        elif word in ("-b", "--cookie"):
            request["headers"]["Cookie"] = words[i + 1]
            i += 1
        elif word in DATA_FLAGS:
            request["body"] = words[i + 1]
            if word == "--json":
                request["headers"].setdefault("Content-Type", "application/json")
            i += 1
        elif word.startswith("http"):
            request["url"] = word
        i += 1
    if not request["url"]:
        raise SystemExit("No address found in the curl command")
    request["method"] = request["method"] or ("POST" if request["body"] else "GET")
    return request


def test_name(method: str, url: str) -> str:
    path = urlsplit(url).path.strip("/") or "root"
    return "test_" + method.lower() + "_" + re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")


def to_pytest(request: dict) -> str:
    url = urlsplit(request["url"])
    base, path = (
        f"{url.scheme}://{url.netloc}",
        request["url"][len(f"{url.scheme}://{url.netloc}") :],
    )
    headers, secrets = {}, []
    for name, value in request["headers"].items():
        lower = name.lower()
        if lower in SECRET_HEADERS:
            secrets.append((name, SECRET_HEADERS[lower]))
        elif lower not in NOISE_HEADERS:
            headers[name] = value
    body_line = ""
    if request["body"] is not None:
        try:
            body = json.loads(request["body"])
            body_line = f"        json={body!r},\n"
            headers = {k: v for k, v in headers.items() if k.lower() != "content-type"}
        except ValueError:
            body_line = f"        data={request['body']!r},\n"
    lines = [
        "# Made by curl_to_pytest.py from myOpenSDET. Check it, then change the checks.",
        "import os",
        "",
        "import requests",
        "",
        f'BASE_URL = os.environ.get("BASE_URL", {base!r})',
        "",
        "",
        f"def {test_name(request['method'], request['url'])}():",
        f"    headers = {headers!r}",
    ]
    for name, variable in secrets:
        lines.append(f'    if os.environ.get("{variable}"):  # never paste the real value here')
        lines.append(f'        headers[{name!r}] = os.environ["{variable}"]')
    lines += [
        "    answer = requests.request(",
        f"        {request['method']!r},",
        f'        f"{{BASE_URL}}{path}",',
        "        headers=headers,",
    ]
    lines += [body_line.rstrip("\n")] if body_line else []
    lines += [
        "        timeout=10,",
        "    )",
        '    assert answer.status_code < 400, f"{answer.status_code}: {answer.text[:200]}"',
        "    # CHANGE: add the checks that matter, for example:",
        '    # assert answer.json()["id"] == 1',
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as file:
            text = file.read()
    else:
        text = sys.stdin.read()
    request = parse(text)
    print(to_pytest(request))
    hidden = [n for n in request["headers"] if n.lower() in SECRET_HEADERS]
    if hidden:
        print(f"Moved out of the test: {', '.join(hidden)}. Set them as environment"
              " variables before running it.", file=sys.stderr)  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
