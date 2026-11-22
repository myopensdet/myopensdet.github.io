# Template from myOpenSDET: https://myopensdet.github.io/
"""Fixtures and report hooks: an API client that logs, a browser page, and evidence in the report.

python -m pytest                 # writes reports/report.html, junit.xml and tests.log
python -m pytest --log-cli-level=INFO   # also show the log lines live in the terminal
"""

import base64
import logging

import pytest
import pytest_html
from helpers.api_client import ShopApi
from playwright.sync_api import sync_playwright
from pytest_metadata.plugin import metadata_key
from shop_app.server import BackgroundShop

TEST_USER = {"email": "tester@example.com", "password": "local_only_password"}
log = logging.getLogger("tests")

# Other libraries log a lot at DEBUG. Keep their warnings, drop their chatter.
for noisy in ("asyncio", "urllib3", "faker"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def pytest_runtest_setup(item):
    """Start each test's part of reports/tests.log with its name."""
    log.info("---- %s", item.nodeid)


def pytest_html_report_title(report):
    report.title = "Practice shop: test report"


@pytest.fixture(scope="session")
def base_url(request):
    shop = BackgroundShop()  # set SHOP_URL to test a shop that is already running
    url = shop.start()
    request.config.stash[metadata_key]["Shop URL"] = url  # shown under Environment
    log.info("Testing the shop at %s", url)
    yield url
    shop.stop()


@pytest.fixture
def api(base_url):
    """A logged-in API client."""
    client = ShopApi(base_url)
    assert client.log_in(**TEST_USER).status_code == 200
    return client


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser, base_url):
    """A logged-in browser tab, with a fresh context."""
    context = browser.new_context(base_url=base_url, viewport={"width": 1000, "height": 600})
    page = context.new_page()
    assert page.request.post("/api/login", data=TEST_USER).ok
    yield page
    context.close()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """When a test with a browser page fails, put a screenshot of the page in the HTML report."""
    report = yield
    page = item.funcargs.get("page")
    if report.when == "call" and report.failed and page is not None:
        png = base64.b64encode(page.screenshot()).decode()
        report.extras = [*getattr(report, "extras", []), pytest_html.extras.png(png, "Screenshot")]
        log.info("Screenshot added to the report")
    return report
