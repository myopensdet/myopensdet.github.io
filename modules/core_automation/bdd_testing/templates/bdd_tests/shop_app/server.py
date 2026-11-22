# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Start the practice shop in the background, on a free port of this computer only.

Set SHOP_URL to test a shop that is already running somewhere else instead.
"""

import os
import socket
import threading
import time

import uvicorn


class BackgroundShop:
    def __init__(self):
        self.server = None
        self.thread = None
        self.url = os.environ.get("SHOP_URL", "").rstrip("/")

    def start(self) -> str:
        if self.url:  # someone else runs it
            return self.url
        from shop_app.app import app  # noqa: PLC0415  (only needed when we run it)

        with socket.socket() as probe:  # ask the computer for a free port
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("The practice shop did not start within 10 seconds")
            time.sleep(0.05)
        self.url = f"http://127.0.0.1:{port}"
        return self.url

    def stop(self) -> None:
        if self.server:
            self.server.should_exit = True
            self.thread.join(timeout=10)
