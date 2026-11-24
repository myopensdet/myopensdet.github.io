# Template from myOpenSDET: https://myopensdet.github.io/
"""Follow one request through every service, using the request id in the logs.

    python trace_request.py 4f1c2a9e0b7d                       # reads logs/*.jsonl
    docker compose logs --no-log-prefix | python trace_request.py 4f1c2a9e0b7d -

This is what tracing tools (Jaeger, Grafana Tempo, Datadog) do for you, made small:
collect every service's lines for one request, and put them in time order.
"""

import json
import sys
from pathlib import Path


def read_lines(source: str) -> list[str]:
    if source == "-":
        return sys.stdin.read().splitlines()
    lines = []
    for path in sorted(Path(source).glob("*.jsonl")):
        lines += path.read_text(encoding="utf-8").splitlines()
    return lines


def trace(request_id: str, lines: list[str]) -> list[dict]:
    events = []
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue  # not one of our JSON lines
        if isinstance(event, dict) and event.get("request_id") == request_id:
            events.append(event)
    return sorted(events, key=lambda e: e["time"])


def describe(event: dict) -> str:
    rest = {k: v for k, v in event.items() if k not in {"time", "service", "request_id", "event"}}
    details = " ".join(f"{k}={v}" for k, v in rest.items())
    return f"{event['service']:9} {event['event']:12} {details}"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python trace_request.py <request id> [logs folder, or - for stdin]")
        return 2
    events = trace(sys.argv[1], read_lines(sys.argv[2] if len(sys.argv) > 2 else "logs"))
    if not events:
        print(f"No log lines with request id {sys.argv[1]}")
        return 1
    start = events[0]["time"]
    for event in events:
        print(f"+{(event['time'] - start) * 1000:6.1f} ms  {describe(event)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
