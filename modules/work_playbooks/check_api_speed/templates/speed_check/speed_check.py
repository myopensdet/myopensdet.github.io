# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Send many requests at once to one address and report how fast the answers came.

    python speed_check.py http://127.0.0.1:8770/api/products --users 10 --seconds 10
    python speed_check.py URL --users 10 --seconds 10 --max-p95 300 --max-errors 1
    python speed_check.py URL -H "Authorization: Bearer $TOKEN"

Each "user" sends one request, waits for the answer, then sends the next.
Exit code 1 if --max-p95 or --max-errors is broken, so a pipeline can stop on it.
Only use it on systems you're allowed to load, and tell the team first."""

import argparse
import statistics
import sys
import threading
import time
from collections import Counter
from dataclasses import dataclass, field

import requests


@dataclass
class Result:
    times_ms: list[float] = field(default_factory=list)
    statuses: Counter = field(default_factory=Counter)
    seconds: float = 0.0

    def __repr__(self) -> str:  # keep failure messages short
        return f"Result({self.count} requests)"

    @property
    def count(self) -> int:
        return sum(self.statuses.values())

    @property
    def errors(self) -> int:
        return sum(n for status, n in self.statuses.items() if status == "failed" or status >= 400)

    @property
    def error_percent(self) -> float:
        return 100 * self.errors / self.count if self.count else 0.0

    def percentile(self, p: int) -> float:
        if len(self.times_ms) < 2:
            return self.times_ms[0] if self.times_ms else 0.0
        return statistics.quantiles(self.times_ms, n=100, method="inclusive")[p - 1]


def run(url: str, users: int, seconds: float, headers: dict | None = None) -> Result:
    result = Result()
    lock = threading.Lock()
    stop_at = time.perf_counter() + seconds

    def one_user():
        with requests.Session() as session:
            while time.perf_counter() < stop_at:
                start = time.perf_counter()
                try:
                    status = session.get(url, headers=headers, timeout=30).status_code
                except requests.RequestException:
                    status = "failed"
                took = (time.perf_counter() - start) * 1000
                with lock:
                    result.statuses[status] += 1
                    result.times_ms.append(took)

    started = time.perf_counter()
    threads = [threading.Thread(target=one_user) for _ in range(users)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    result.seconds = time.perf_counter() - started
    return result


def report(url: str, users: int, result: Result) -> str:
    statuses = ", ".join(f"{s}: {n}" for s, n in sorted(result.statuses.items(), key=str))
    return "\n".join([
        f"{url}  ({users} user{'s' if users != 1 else ''}, {result.seconds:.0f} s)",
        f"  requests   {result.count}  ({result.count / result.seconds:.0f} per second)",
        f"  answers    {statuses}",
        f"  errors     {result.errors}  ({result.error_percent:.1f}%)",
        f"  time (ms)  p50 {result.percentile(50):.0f}   p95 {result.percentile(95):.0f}"
        f"   p99 {result.percentile(99):.0f}   max {max(result.times_ms, default=0):.0f}",
    ])  # fmt: skip


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--max-p95", type=float, help="fail if p95 is above this, in ms")
    parser.add_argument("--max-errors", type=float, help="fail if errors are above this, in %%")
    parser.add_argument("-H", "--header", action="append", default=[], help='"Name: value"')
    args = parser.parse_args()
    headers = dict(h.split(":", 1) for h in args.header)
    headers = {name.strip(): value.strip() for name, value in headers.items()}

    result = run(args.url, args.users, args.seconds, headers)
    print(report(args.url, args.users, result))
    problems = []
    if args.max_p95 is not None and result.percentile(95) > args.max_p95:
        problems.append(f"p95 {result.percentile(95):.0f} ms is above {args.max_p95:.0f} ms")
    if args.max_errors is not None and result.error_percent > args.max_errors:
        problems.append(f"errors {result.error_percent:.1f}% are above {args.max_errors}%")
    for problem in problems:
        print(f"  TOO SLOW OR FAILING: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
