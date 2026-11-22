---
title: "How Browsers and Locators Work in Playwright"
description: "What happens when Playwright drives a browser: browser, context and page, the page's elements and the accessibility tree, and what a locator is: a lazy, strict way to find an element that waits until it can act."
level: Intermediate
tags:
  - Playwright
  - UI
nav_title: "How browsers and locators work"
order: 10
summary: "Browser, context, page and locator: what Playwright really does."
updated: "2026-11-22"
---

# How Browsers and Locators Work in Playwright

Before you write UI tests, it helps to know what Playwright actually does. It starts a real browser, opens a clean profile in it, opens a tab, and then finds things on the page the way you describe them. That description is a **locator**. Locators behave differently from what most people expect: they search nothing until you use them, they refuse to guess when two things match, and they wait for the page. Those three rules explain most UI test errors you'll ever see.

!!! note "Before you start"
    Read [fixtures and conftest](../pytest/fixtures-and-conftest.md). Have the [template project](index.md#templates) installed, with `python -m playwright install chromium` done once.

## What you will learn

- Browser, context and page, and why each test gets a new context
- What the page is made of: elements, and the accessibility tree
- What a locator is, and its three rules: lazy, strict, waiting

## Why this matters at work

When a UI test fails, the first question is always "did it find the right thing, at the right time?" If you know how locators find and wait, you can read the error and know the answer. Without it, people add `sleep` and longer XPath until the test passes, and it fails again next week.

## The idea in plain words

!!! info "In plain words"
    The browser is a building. A context is a hotel room in it: your own key, your own things, nothing left from the last guest. A page is a window in that room. A locator is a note that says "the red button by the door". You can write the note before you walk in. You only look for the button when you need to press it, and if there are two red buttons by the door, you stop and ask.

## Step by step

1. **Run a first script, without pytest.** `first_look.py` in the template starts the practice shop, logs in and reads the book list:

    ```python
    --8<-- "modules/core_automation/ui_automation/templates/ui_tests/first_look.py"
    ```

    ```bash
    python first_look.py
    ```

    ```text
    Title: Log in - Practice shop
    Found yet? <Locator frame=<Frame name= url='http://127.0.0.1:51257/login'> selector='internal:role=button[name="Log in"i]'>
    Now on: /books
    Books: ['Python for Testers', 'SQL in a Week', 'Clean Tests', 'Playwright Pocket Guide']
    ```

2. **Know the three layers.**

    | Layer | What it is | In the template |
    | --- | --- | --- |
    | Browser | The browser program, started once. Without a window ("headless") unless you ask for one | `browser` fixture, once per run |
    | Context | A fresh, private browser profile: its own cookies, storage and tabs | `context` fixture, new for every test |
    | Page | One tab in a context | `page` fixture |

    On the computer these pages were made on, starting Chromium took 0.16 seconds and a new context 0.008 seconds: twenty times less. That's why the template starts one browser for the whole run and gives every test its own context. No cookies or cart leak from one test to the next, and it stays fast.

3. **Know what the page is made of.** The browser turns the HTML into **elements**: headings, buttons, fields, links. It also builds an **accessibility tree**: what a screen reader announces. Each thing has a **role** (button, link, heading, textbox) and a **name** (its text or label). Playwright shows this tree when an `expect()` check fails:

    ```text
    - main:
      - heading "Your cart" [level=1]
      - table:
        - rowgroup:
          - row "Book Copies Price":
            - columnheader "Book"
            - columnheader "Copies"
            - columnheader "Price"
            - columnheader
        - rowgroup:
          - row "Python for Testers 1 24.99 Remove":
            - cell "Python for Testers"
            - cell "1"
            - cell "24.99"
            - cell "Remove":
              - button "Remove"
          - row "SQL in a Week 2 39.00 Remove":
            ...
    ```

    `get_by_role("button", name="Remove")` searches this tree. If a screen reader can find it, your test can too.

4. **Rule 1: a locator is lazy.** `page.get_by_role("button", name="Log in")` doesn't search the page. It's a description. The script printed it before it was used: `Found yet? <Locator ... selector='internal:role=button[name="Log in"i]'>`. The search happens each time you act on it: `click()`, `fill()`, or an `expect()` check. So a locator made once stays correct even when the page changes. Page objects depend on this.

5. **Rule 2: a locator is strict.** If an action's locator matches more than one element, Playwright refuses to guess. On the cart page, with two books:

    ```python
    page.get_by_role("button", name="Remove").click()
    ```

    ```text
    playwright._impl._errors.Error: Locator.click: Error: strict mode violation: get_by_role("button", name="Remove") resolved to 2 elements:
        1) <button data-book="Python for Testers">Remove</button> aka get_by_role("row", name="Python for Testers 1 24.99").get_by_role("button")
        2) <button data-book="SQL in a Week">Remove</button> aka get_by_role("row", name="SQL in a Week 2 39.00 Remove").get_by_role("button")
    ```

    Good: clicking the first one would remove the wrong book, and the test would fail somewhere else, confusingly. The fix is to say which one: find the row first, then the button in it. [Choosing locators](choosing-locators.md) shows how.

6. **Rule 3: a locator waits.** Before a click, Playwright waits until the element is there, visible, stable, enabled and not covered by something else. Then it clicks. Your test doesn't need to wait first. [Waits](waits.md) covers the details, and the one case where you still must wait.

    !!! success "Check: you should now be able to"
        Explain browser, context and page; say why each test gets a new context; and explain what "lazy", "strict" and "waits" mean for a locator.

## When it goes wrong

- **`strict mode violation: ... resolved to 4 elements`.** Your locator is too general. The error lists each match, with a locator that would find just that one: a good hint for a better locator.
- **`BrowserType.launch: Executable doesn't exist at ...`.** The browser was never downloaded on this computer. Run `python -m playwright install chromium` in the virtual environment.
- **A test passes alone and fails in the full run.** Something is shared between tests: a context or page with a longer scope than one test, or data on the server. Each test needs its own context, as in the template.

## Common mistakes

!!! warning "Common mistakes"
    - **One page for the whole run.** Cookies, cart and log-in leak between tests. New context per test.
    - **Reading values into variables early.** `text = locator.inner_text()` is read once, at that moment. Use `expect(locator).to_have_text(...)`, which reads again until it matches.
    - **Running with a window all the time.** Headless is faster, and is what the pipeline does. Use `--headed` only to watch.

!!! failure "If you see this error"
    **`It looks like you are using Playwright Sync API inside the asyncio loop. Please use the Async API instead.`**
    Something in the same process already runs an asyncio loop, such as a Jupyter notebook. Run your tests from the terminal with `python -m pytest`, or use Playwright's async API in that place.

## Try it yourself

Change `first_look.py` so it also prints the text of the cart count in the header, after logging in.

??? success "Solution"
    Add this line after `print("Now on:", ...)`:

    ```python
    print("Cart count:", page.get_by_test_id("cart-count").inner_text())
    ```

    It prints `Cart count: 0`: a new context means a new session and an empty cart.

## Quick check

1. Why does each test get a new context, but not a new browser?

    ??? question "Answer"
        A new context is a clean profile (no cookies, no cart) and takes milliseconds. Starting a browser takes many times longer.

2. When does a locator search the page?

    ??? question "Answer"
        Each time you use it: an action like `click()`, or an `expect()` check. Not when you create it.

3. What does strict mode protect you from?

    ??? question "Answer"
        Clicking or typing into the wrong one of several matching elements.

## References

- [Playwright: Browsers](https://playwright.dev/python/docs/browsers)
- [Playwright: Isolation (browser contexts)](https://playwright.dev/python/docs/browser-contexts)
- [Playwright: Locators](https://playwright.dev/python/docs/locators)
- [MDN: Accessibility tree](https://developer.mozilla.org/en-US/docs/Glossary/Accessibility_tree)

Written for Python 3.13 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
