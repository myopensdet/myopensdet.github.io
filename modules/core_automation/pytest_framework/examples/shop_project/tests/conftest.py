# Template from myOpenSDET: https://myopensdet.github.io/
"""Shared fixtures and the --env option. pytest finds this file by its name."""

import os
import tomllib
from pathlib import Path

import pytest
from shop.cart import Cart

CONFIG = Path(__file__).parents[1] / "config" / "environments.toml"
ENVIRONMENT = pytest.StashKey[dict]()


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        default=os.environ.get("TEST_ENV", "local"),
        help="environment to test, from config/environments.toml (default: local)",
    )


def pytest_configure(config):
    name = config.getoption("--env")
    environments = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    if name not in environments:
        choices = ", ".join(environments)
        raise pytest.UsageError(f"Unknown environment '{name}'. Choose one of: {choices}")
    config.stash[ENVIRONMENT] = {"name": name, **environments[name]}


def pytest_report_header(config):
    env = config.stash[ENVIRONMENT]
    return f"environment: {env['name']} ({env['base_url']})"


@pytest.fixture(scope="session")
def env(request):
    """The chosen environment's settings, read once per run."""
    return request.config.stash[ENVIRONMENT]


@pytest.fixture(scope="session")
def base_url(env):
    return env["base_url"]


@pytest.fixture
def api_token(env):
    """The token, from an environment variable. Skips the test if it isn't set."""
    token = os.environ.get(env["token_variable"])
    if not token:
        pytest.skip(f"set {env['token_variable']} to run tests that need a token")
    return token


@pytest.fixture
def cart():
    """A new, empty cart for each test."""
    return Cart()


@pytest.fixture
def cart_with_items(cart):
    """A cart with two notebooks and a pen: 10.00 in total."""
    cart.add("Pocket notebook", 425, quantity=2)
    cart.add("Pen", 150)
    return cart


@pytest.fixture
def order_store():
    """A pretend order database. Everything saved in a test is removed after it."""
    store = []
    yield store
    store.clear()
