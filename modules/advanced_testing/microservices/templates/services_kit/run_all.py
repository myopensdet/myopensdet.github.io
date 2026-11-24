# Template from myOpenSDET: https://myopensdet.github.io/
"""Start the three practice services on this computer, without Docker.

    python run_all.py                         # orders 8811, stock 8812, payments 8813
    ORDERS_BUG=no_release python run_all.py   # with the planted bug

Each service writes its log lines to logs/<service>.jsonl. Ctrl+C stops all three.
"""

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
PORTS = {"orders": 8811, "stock": 8812, "payments": 8813}


def start(logs: Path = HERE / "logs", ports: dict = PORTS) -> list[subprocess.Popen]:
    logs.mkdir(exist_ok=True)
    env = os.environ | {
        "STOCK_URL": f"http://127.0.0.1:{ports['stock']}",
        "PAYMENTS_URL": f"http://127.0.0.1:{ports['payments']}",
    }
    for name, port in ports.items():
        check_port_free(port, name)
    processes = []
    for name, port in ports.items():
        out = (logs / f"{name}.jsonl").open("w", encoding="utf-8")
        processes.append(
            subprocess.Popen(  # noqa: S603 (our own service files)
                [sys.executable, str(HERE / "services" / f"{name}.py")],
                env=env | {"PORT": str(port)},
                stdout=out,
                stderr=subprocess.DEVNULL,
            )  # fmt: skip
        )
    for name, port in ports.items():
        wait_until_up(f"http://127.0.0.1:{port}/health", name)
    return processes


def check_port_free(port: int, name: str) -> None:
    """Fail early if something already listens there: an old run, or another app.
    Otherwise the tests would quietly talk to that old process instead."""
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(
                f"Port {port} for {name} is already in use. Stop the old run first "
                f"(Ctrl+C in its terminal), or find it with: lsof -i :{port}"
            )


def wait_until_up(url: str, name: str, seconds: float = 10) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):  # noqa: S310 (http only)
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"{name} did not start: nothing answered at {url}")


def stop(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait(timeout=5)


if __name__ == "__main__":
    # Stop the services on Ctrl+C, on "kill", and when the terminal closes (SIGHUP,
    # not on Windows), so none is left running on its port.
    for name in ("SIGTERM", "SIGHUP"):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), lambda *_: sys.exit(0))
    running = start()
    for name, port in PORTS.items():
        print(f"{name:9} http://127.0.0.1:{port}", flush=True)
    print("Logs in logs/. Ctrl+C to stop.", flush=True)
    try:
        while all(p.poll() is None for p in running):
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        stop(running)
