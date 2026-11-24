# Template from myOpenSDET: https://myopensdet.github.io/
"""Provider side (the stock team). Replay every request in the consumers' pact files
against the real stock service, and check each answer matches what they need."""

from pathlib import Path

import pytest
import stock_service
from pact import Verifier

PACTS = Path(__file__).resolve().parents[1] / "pacts"


def in_stock(action: str, parameters: dict | None = None) -> None:
    if action == "setup":
        stock_service.ITEMS["SNS-0042"] = {"available": 40, "price_cents": 2499}


def no_such_item(action: str, parameters: dict | None = None) -> None:
    stock_service.ITEMS.pop("ZZ-9999", None)


def test_stock_keeps_every_consumer_contract():
    if not list(PACTS.glob("*-stock.json")):
        pytest.fail(
            "No pact files in pacts/. Run the consumer tests first: pytest tests/test_consumer.py"
        )
    server = stock_service.start()
    try:
        verifier = (
            Verifier("stock", host="127.0.0.1")
            .set_coloured_output(enabled=False)
            .add_transport(url=f"http://127.0.0.1:{server.server_port}")
            .add_source(PACTS)
            .state_handler(
                {"SNS-0042 is in stock": in_stock, "there is no item ZZ-9999": no_such_item},
                teardown=True,
            )
        )
        try:
            verifier.verify()
        except RuntimeError:
            # Pact's own error says only "Failed to execute verifier". Show its report instead.
            report = verifier.output(strip_ansi=True)
            raise AssertionError(report[report.find("Failures:") :].strip()) from None
    finally:
        server.shutdown()
