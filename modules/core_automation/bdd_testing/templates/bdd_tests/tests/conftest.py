# Template from myOpenSDET: https://myopensdet.github.io/
"""pytest-bdd fixtures and hooks: start the shop once, give every scenario a fresh driver.

Choose the target with --target=api (the default) or --target=ui.
"""

from pathlib import Path

import pytest
from drivers import TARGETS, ApiDriver, UiDriver
from shop_app.server import BackgroundShop

SCREENSHOTS = Path("reports") / "screenshots"


def pytest_addoption(parser):
    parser.addoption("--target", choices=TARGETS, default="api", help="api or ui")


def pytest_bdd_apply_tag(tag, function):
    """@known_bug in a feature file becomes a strict xfail that only an assert can satisfy."""
    if tag == "known_bug":
        reason = "Known bug: see the scenario's description"
        pytest.mark.xfail(reason=reason, raises=AssertionError, strict=True)(function)
        return True
    return None  # every other tag becomes a normal marker


@pytest.fixture(scope="session")
def base_url():
    shop = BackgroundShop()
    yield shop.start()
    shop.stop()


@pytest.fixture(scope="session")
def browser(request):
    if request.config.getoption("--target") != "ui":
        yield None
        return
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        yield chromium
        chromium.close()


@pytest.fixture
def shop(request, base_url, browser):
    if browser is None:
        driver = ApiDriver(base_url)
        yield driver
        driver.close()
        return
    context = browser.new_context()
    yield UiDriver(base_url, context.new_page())
    context.close()


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """A step failed: on the UI, keep a picture of the page for the bug report."""
    try:
        driver = request.getfixturevalue("shop")
    except Exception:  # noqa: BLE001  (the driver never started: nothing to take a picture of)
        return
    if isinstance(driver, UiDriver):
        SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        name = "".join(c if c.isalnum() else "_" for c in scenario.name)
        driver.page.screenshot(path=SCREENSHOTS / f"{name}.png")
