# Template from myOpenSDET: https://myopensdet.github.io/
import os
from pathlib import Path

# Pact sends anonymous usage numbers (its version, your operating system) unless
# this is set. Set before pact is imported. Remove the line only if you want to send them.
os.environ.setdefault("PACT_DO_NOT_TRACK", "true")

import pytest  # noqa: E402
from pact import Pact  # noqa: E402

PACTS = Path(__file__).resolve().parents[1] / "pacts"


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Remember each test's result, so the pact fixture knows if the test passed."""
    report = yield
    setattr(item, f"result_{report.when}", report)
    return report


@pytest.fixture(scope="session")
def fresh_pacts():
    """Start every consumer run with no old pact file, so nothing stale is kept."""
    PACTS.mkdir(exist_ok=True)
    for old in PACTS.glob("orders-*.json"):
        old.unlink()
    return PACTS


@pytest.fixture
def pact(request, fresh_pacts):
    """One Pact per test: a Pact can't take new interactions after it has served once.
    Each passing test adds its interaction to pacts/orders-stock.json."""
    pact = Pact("orders", "stock").with_specification("V4")
    yield pact
    result = getattr(request.node, "result_call", None)
    if result is not None and result.passed:
        pact.write_file(fresh_pacts, overwrite=False)
