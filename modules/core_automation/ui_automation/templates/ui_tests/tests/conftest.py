# Template from myOpenSDET: https://myopensdet.github.io/
"""Browser fixtures for the UI tests: one browser per run, a fresh context for every test.

    python -m pytest                       # Chromium, no window
    python -m pytest --browser=firefox     # or webkit (Safari's engine)
    python -m pytest --headed --slowmo=500 # watch it, half a second per action

A failed test leaves a screenshot and a trace in reports/. Open the trace with:
    python -m playwright show-trace reports/traces/<test name>.zip
"""

from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright
from shop_app.server import BackgroundShop

BROWSERS = ("chromium", "firefox", "webkit")
REPORTS = Path("reports")
TEST_USER = {"email": "tester@example.com", "password": "local_only_password"}

expect.set_options(timeout=5_000)  # how long expect() waits for the page to match


def pytest_addoption(parser):
    parser.addoption("--browser", choices=BROWSERS, default="chromium", help="browser engine")
    parser.addoption("--headed", action="store_true", help="show the browser window")
    parser.addoption("--slowmo", type=float, default=0, help="milliseconds between actions")


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Keep each phase's result on the test, so fixtures can see if the test failed."""
    report = yield
    setattr(item, f"report_{report.when}", report)
    return report


@pytest.fixture(scope="session")
def base_url():
    shop = BackgroundShop()  # set SHOP_URL to test a shop that is already running
    yield shop.start()
    shop.stop()


@pytest.fixture(scope="session")
def browser(request):
    options = request.config.getoption
    with sync_playwright() as playwright:
        engine = getattr(playwright, options("--browser"))
        browser = engine.launch(headless=not options("--headed"), slow_mo=options("--slowmo"))
        yield browser
        browser.close()


@pytest.fixture
def context(request, browser, base_url):
    """A new context is a new, empty browser profile: no cookies, no cart from other tests."""
    context = browser.new_context(base_url=base_url, viewport={"width": 1280, "height": 800})
    context.set_default_timeout(10_000)  # clicks and fills give up after 10 seconds
    context.tracing.start(screenshots=True, snapshots=True)
    yield context
    report = getattr(request.node, "report_call", None)
    if report is not None and report.failed:
        name = "".join(c if c.isalnum() else "_" for c in request.node.name)
        for number, page in enumerate(context.pages):
            page.screenshot(path=REPORTS / "screenshots" / f"{name}_{number}.png", full_page=True)
        context.tracing.stop(path=REPORTS / "traces" / f"{name}.zip")
    else:
        context.tracing.stop()
    context.close()


@pytest.fixture
def page(context):
    return context.new_page()


@pytest.fixture
def logged_in_page(page):
    """Log in through the API: fast, and only the login tests need the login form.
    The page shares cookies with page.request, so the page is logged in too."""
    response = page.request.post("/api/login", data=TEST_USER)
    assert response.ok, response.text()
    return page


@pytest.fixture
def cart_with_books(logged_in_page):
    """Fill the cart through the API, then test the cart page itself."""
    for book in ["Python for Testers", "SQL in a Week", "SQL in a Week"]:
        assert logged_in_page.request.post("/api/cart", data={"book": book}).ok
    return logged_in_page
