# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Collect evidence for a bug a developer can't reproduce: send the same request a few
times and record the time (UTC), status, duration, request id and app version. Prints a
block to paste into the ticket, with a curl command anyone can run. Login headers are
hidden; it reads them from the API_AUTH environment variable.

    python evidence.py http://127.0.0.1:8795/api/orders/7 --times 6
"""

import argparse
import os
import shlex
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime

ID_HEADERS = ("X-Request-Id", "X-Correlation-Id", "Traceparent")  # CHANGE: your app's names
VERSION_HEADERS = ("X-App-Version", "X-Version", "Server")


def send(url: str, method: str, data: str | None, auth: str | None) -> dict:
    request = urllib.request.Request(url, method=method, data=data.encode() if data else None)  # noqa: S310
    if data:
        request.add_header("Content-Type", "application/json")
    if auth:
        request.add_header("Authorization", auth)
    start = time.perf_counter()
    when = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        with urllib.request.urlopen(request, timeout=15) as answer:  # noqa: S310
            status, headers, body = answer.status, answer.headers, answer.read()
    except urllib.error.HTTPError as error:
        status, headers, body = error.code, error.headers, error.read()
    except (urllib.error.URLError, TimeoutError) as error:
        reason = getattr(error, "reason", error)
        return {"when": when, "status": f"no answer ({reason})", "ms": 0, "id": "-", "version": "-",
                "body": ""}  # fmt: skip
    return {
        "when": when,
        "status": status,
        "ms": round((time.perf_counter() - start) * 1000),
        "id": next((headers[h] for h in ID_HEADERS if headers.get(h)), "-"),
        "version": next((headers[h] for h in VERSION_HEADERS if headers.get(h)), "-"),
        "body": body.decode(errors="replace")[:120],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--data", help="JSON body to send")
    parser.add_argument("--times", type=int, default=5, help="how many times to send it")
    parser.add_argument("--wait", type=float, default=1.0, help="seconds between sends")
    args = parser.parse_args()
    if not args.url.startswith(("http://", "https://")):
        print(f"Not a full address: {args.url!r}. Start with http:// or https://")
        return 2
    auth = os.environ.get("API_AUTH")
    runs = []
    for number in range(args.times):
        if number:
            time.sleep(args.wait)
        runs.append(send(args.url, args.method.upper(), args.data, auth))
    bad = [r for r in runs if not (isinstance(r["status"], int) and r["status"] < 400)]

    print(f"### Evidence: {args.method.upper()} {args.url}\n")
    sent = f"{len(runs)} time{'s' * (len(runs) != 1)}"
    print(f"Sent {sent}: {len(runs) - len(bad)} OK, {len(bad)} failed.")
    if bad and len(bad) < len(runs):
        print("It fails some of the time, not always: that's why it 'works on my machine'.")
    print("\n| Time (UTC) | Status | ms | Request id | App version |")
    print("| --- | --- | --- | --- | --- |")
    for r in runs:
        print(f"| {r['when']} | {r['status']} | {r['ms']} | {r['id']} | {r['version']} |")
    if bad and bad[0]["body"]:
        print(f"\nFirst failed answer: `{bad[0]['body']}`")
    command = ["curl", "-i", "-X", args.method.upper(), args.url]
    if auth:
        command += ["-H", "Authorization: $API_AUTH"]
    if args.data:
        command += ["-H", "Content-Type: application/json", "--data", args.data]
    print("\nTo reproduce (run it several times):\n")
    print("```bash\n" + " ".join(shlex.quote(c) if "$" not in c else f'"{c}"' for c in command))
    print("```")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
