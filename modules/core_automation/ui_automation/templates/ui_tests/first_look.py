# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A first look at Playwright, without pytest: browser, context, page, locator.

python first_look.py
"""

from playwright.sync_api import sync_playwright
from shop_app.server import BackgroundShop

shop = BackgroundShop()
url = shop.start()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()  # the browser program (no window)
    context = browser.new_context(base_url=url)  # a fresh profile: own cookies
    page = context.new_page()  # one tab

    page.goto("/login")
    print("Title:", page.title())

    button = page.get_by_role("button", name="Log in")  # a locator: a way to find it
    print("Found yet?", button)  # nothing is searched until you use it

    page.get_by_label("Email").fill("tester@example.com")
    page.get_by_label("Password").fill("local_only_password")
    button.click()  # now Playwright finds the button, waits until it can be clicked, clicks

    print("Now on:", page.url.removeprefix(url))
    page.get_by_role("listitem").first.wait_for()  # the list loads after the page: wait for it
    print("Books:", page.get_by_role("heading", level=2).all_inner_texts())

    browser.close()
shop.stop()
