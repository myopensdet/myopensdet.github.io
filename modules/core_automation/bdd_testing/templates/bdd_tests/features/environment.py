# Template from myOpenSDET: https://myopensdet.github.io/
"""behave hooks: start the shop once, give every scenario a fresh driver.

Choose the target with -D target=api (the default) or -D target=ui.
"""

from pathlib import Path

from drivers import TARGETS, ApiDriver, UiDriver
from shop_app.server import BackgroundShop

SCREENSHOTS = Path("reports") / "screenshots"


def before_all(context):
    # Set everything first, so after_all can clean up even when a step below fails.
    context.background_shop = BackgroundShop()
    context.playwright = context.browser = None
    context.target = context.config.userdata.get("target", "api")
    if context.target not in TARGETS:
        raise ValueError(f"-D target must be one of {TARGETS}, not {context.target!r}")
    context.base_url = context.background_shop.start()
    if context.target == "ui":
        from playwright.sync_api import sync_playwright  # noqa: PLC0415

        context.playwright = sync_playwright().start()
        context.browser = context.playwright.chromium.launch()


def before_scenario(context, scenario):
    if context.target == "ui":
        context.browser_context = context.browser.new_context()
        context.shop = UiDriver(context.base_url, context.browser_context.new_page())
    else:
        context.shop = ApiDriver(context.base_url)


def after_scenario(context, scenario):
    if context.target == "ui":
        if scenario.status == "failed":  # a picture of the page, for the bug report
            SCREENSHOTS.mkdir(parents=True, exist_ok=True)
            name = "".join(c if c.isalnum() else "_" for c in scenario.name)
            context.shop.page.screenshot(path=SCREENSHOTS / f"{name}.png")
        context.browser_context.close()
    else:
        context.shop.close()


def after_all(context):
    # Close only what was started: a failed before_all may have stopped halfway.
    if context.browser:
        context.browser.close()
    if context.playwright:
        context.playwright.stop()
    context.background_shop.stop()
