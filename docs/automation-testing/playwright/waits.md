---
title: "Waits in Playwright: Auto-Waiting, expect() and Never Sleeping"
description: "Why UI tests become flaky, and how Playwright waits for you: actions wait until an element is ready, expect() checks again until the page matches, and some calls don't wait at all. With a real race condition found by a test, and how to fix it."
level: Intermediate
tags:
  - Playwright
  - UI
nav_title: "Waits"
order: 30
summary: "Auto-waiting, expect(), and why sleep makes tests flaky."
updated: "2026-11-22"
---

# Waits in Playwright: Auto-Waiting, expect() and Never Sleeping

Web pages don't finish at once. The HTML arrives, then scripts run, then data loads from the server, then the page changes again. A test that checks too early fails, and one that waits a fixed time is slow, and still fails on a slow day. That's the main source of **flaky tests**: they pass and fail with no code change. Playwright solves most of it for you. This lesson shows what it waits for, what it doesn't, and a real race this template's own tests found.

!!! note "Before you start"
    Read [choosing locators](choosing-locators.md). Have the [template project](index.md#templates) open.

## What you will learn

- What Playwright waits for before an action
- How `expect()` checks again until the page matches
- Which calls don't wait, and what to use instead
- How to wait for "the page is ready" in a page object

## Why this matters at work

Teams stop trusting a suite with flaky tests. People rerun until it's green, real failures get ignored, and the suite stops protecting anyone. Most flaky UI tests have one of two causes: a check that runs before the page is ready, or a fixed `sleep` that's sometimes too short. Both are fixed by waiting for what a user would wait for.

## The idea in plain words

!!! info "In plain words"
    You're waiting for a bus. You don't stand for exactly 7 minutes and then leave. You watch the road and get on when the bus comes. If it hasn't come after 20 minutes, you give up and walk. `expect()` watches the road. `sleep(7)` is the stopwatch.

## Step by step

1. **Actions wait by themselves.** Before `click()`, `fill()` or `check()`, Playwright waits until the element is there, visible, stable (not moving), enabled, and not covered by something else. In the template, `add_to_cart` clicks a button that only exists after the book list loads, and there is no wait in the code. The template gives up after 10 seconds: `context.set_default_timeout(10_000)` in `tests/conftest.py`. Without that line, it's 30.

2. **`expect()` checks again until it matches.** From `tests/test_books.py`:

    ```python
    books = BooksPage(logged_in_page).open().search("test")
    expect(books.results).to_have_count(2)
    ```

    `to_have_count(2)` reads the page, and if it's not 2 yet, reads it again, and again, for up to 5 seconds (`expect.set_options(timeout=5_000)` in the conftest). When the known bug makes a check fail, the error shows how hard it tried:

    ```text
    E       AssertionError: Locator expected to have text '1'
    E       Actual value: 3
    E       Call log:
    E         - Expect "to_have_text" get_by_role("navigation", name="Main").get_by_test_id("cart-count") with timeout 5000ms
    E         - waiting for get_by_role("navigation", name="Main").get_by_test_id("cart-count")
    E           14 × locator resolved to <span data-testid="cart-count">3</span>
    E              - unexpected value "3"
    ```

    14 tries in 5 seconds, all `3`. That's a real bug, not a timing problem.

3. **Know what doesn't wait.** Calls that *read* the page answer at once, with whatever is there right now: `count()`, `inner_text()`, `all_inner_texts()`, `is_visible()`, `get_attribute()`. Right after opening the books page:

    ```python
    logged_in_page.goto("/books")
    print("COUNT NOW:", logged_in_page.get_by_role("listitem").count())
    expect(logged_in_page.get_by_role("listitem")).to_have_count(4)
    print("COUNT AFTER EXPECT:", logged_in_page.get_by_role("listitem").count())
    ```

    ```text
    COUNT NOW: 0
    COUNT AFTER EXPECT: 4
    ```

    `assert page.get_by_role("listitem").count() == 4` would fail here on a fast computer, and pass on a slow one. Use `expect()` for checks.

4. **Wait for "ready", not for "something".** The first version of `first_look.py` waited for the status text to contain "books":

    ```python
    page.get_by_role("status").filter(has_text="books").wait_for()
    print("Books:", page.get_by_role("listitem").locator("h2").all_inner_texts())
    ```

    ```text
    Books: []
    ```

    The status said `Loading books...` at that moment. That contains "books" too, so the wait ended before any book arrived. Wait for the thing you need: `page.get_by_role("listitem").first.wait_for()`, or a check of the final text.

5. **A real race, found by the tests.** The first version of the template had no "ready" wait in `BooksPage.open()`. Two search tests failed: they typed and clicked **Search** while the first list was still loading. The screenshot from the failed run shows 6 books, though the status says `2 books`:

    ![The books page after searching for "test": the status says 2 books, but six cards are shown, the four from the first load and the two from the search](../../assets/images/ui-automation/search-race-six-books.png){ loading=lazy }

    Two answers came back, and the page showed both. That's a real bug: a fast user, or a slow network, gets the same. It was fixed twice:

    - **In the app:** the page now drops an answer when a newer search has started.
    - **In the page object:** `open()` and `search()` wait until the status says how many books it shows. From `pages/books_page.py`:

        ```python
        LOADED = re.compile(r"^(\d+ books?|No books match .*)$")
        ```

        ```python
        def wait_until_loaded(self):
            """The page is ready when the status says how many books it shows."""
            expect(self.status).to_have_text(LOADED)
        ```

    A page object that waits for its page to be ready makes every test that uses it steady.

6. **Never sleep.** `time.sleep(2)` and `page.wait_for_timeout(2000)` wait 2 seconds every time, even when the page was ready after 0.1, and still fail on the day it takes 2.1. The template's topic test fails if a test file contains either one.

    !!! success "Check: you should now be able to"
        Say which calls wait and which don't, write checks with `expect()`, and make a page object wait until its page is ready.

## When it goes wrong

- **A check fails, but the screenshot shows the right value.** The check read the page too early, and the screenshot was taken later. Look for `count()`, `inner_text()` or `is_visible()` in an `assert`, and use `expect()` instead.
- **`Timeout 10000ms exceeded`, waiting for a locator.** The element never matched: a wrong locator, a page that never got there, or a field inside an iframe. The call log says what it waited for.
- **The test passes locally, fails in the pipeline.** Pipelines are slower. A fixed sleep, or a read without waiting, works on your laptop and not there. Replace both with `expect()`.

## Common mistakes

!!! warning "Common mistakes"
    - **`assert locator.is_visible()`.** Reads once. Use `expect(locator).to_be_visible()`.
    - **Raising every timeout to 60 seconds.** Real failures then take a minute each. Fix what you wait for instead.
    - **`wait_for_load_state("networkidle")` everywhere.** It waits for the network to be quiet for a moment, which some pages never are. Wait for what the user sees.
    - **Retrying flaky tests until they pass.** The flakiness may be a real race, like the one above.

!!! failure "If you see this error"
    **`AssertionError: Locator expected to have count '0'` with `Actual value: 4`**
    From the same race: a search for "cooking" matches nothing, but the four books from the first load arrived after the search started, and stayed. More results than expected usually means an older answer arrived late. Make the page object wait until the page is ready before acting, and report the race to the developers: users can hit it too.

## Try it yourself

`test_add_to_cart_updates_the_cart_count` clicks **Add to cart** twice. Why is there no wait between the two clicks and the check of the count?

??? success "Solution"
    Each click waits until the button can be clicked. The check, `expect(books.header.cart_count).to_have_text("2")`, reads the count again and again until the page's answer from the server has updated it. Nothing needs a fixed wait.

## References

- [Playwright: Auto-waiting](https://playwright.dev/python/docs/actionability)
- [Playwright: Assertions](https://playwright.dev/python/docs/test-assertions)
- [Playwright: Timeouts](https://playwright.dev/python/docs/test-timeouts)
- [Martin Fowler: Eradicating non-determinism in tests](https://martinfowler.com/articles/nonDeterminism.html)

Written for Python 3.13 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
