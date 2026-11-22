# Template from myOpenSDET: https://myopensdet.github.io/
"""Make practice log files in logs/: the same lines every time, like a small web shop's logs.

python make_practice_logs.py
"""

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

PATHS = ["/api/products", "/api/search", "/api/cart", "/api/orders", "/api/login"]


def make(folder: Path = Path("logs")) -> None:
    rng = random.Random(42)  # noqa: S311  (same practice lines everywhere, not security)
    start = datetime(2026, 11, 18, 2, 0, 0, tzinfo=UTC)
    app, worker = [], []
    for n in range(400):
        time = (start + timedelta(seconds=n * 9)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request = f"req-{n + 1000:05d}"
        path = rng.choice(PATHS)
        took = rng.randint(8, 120)
        level, status, extra = "INFO", 200, ""
        if path == "/api/search" and rng.random() < 0.3:
            took = rng.randint(1500, 4200)
            level = "WARN"
            extra = " slow=true"
        if path == "/api/orders" and rng.random() < 0.2:
            level, status = "ERROR", 500
            extra = " error=PaymentTimeout"
            worker.append(f"{time} ERROR {request} payment provider did not answer in 3000 ms")
        if path == "/api/login" and rng.random() < 0.25:
            level, status = "WARN", 401
            extra = " error=WrongPassword"
        if n == 333:
            level, status, extra = "ERROR", 500, " error=KeyError:'discount_code'"
        line = f"{time} {level:<5} {request} GET {path} status={status} took_ms={took}{extra}"
        app.append(line)
    folder.mkdir(exist_ok=True)
    (folder / "app.log").write_text("\n".join(app) + "\n", encoding="utf-8")
    (folder / "worker.log").write_text("\n".join(worker) + "\n", encoding="utf-8")
    print(
        f"Wrote {folder}/app.log ({len(app)} lines) and {folder}/worker.log ({len(worker)} lines)"
    )


if __name__ == "__main__":
    make()
