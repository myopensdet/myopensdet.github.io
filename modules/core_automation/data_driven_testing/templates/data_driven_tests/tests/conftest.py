# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
from helpers.factories import SEED


def pytest_report_header():
    """Print the fake-data seed, so a failing run can be repeated with TEST_SEED=<seed>."""
    return f"fake data seed: {SEED} (repeat with TEST_SEED={SEED})"
