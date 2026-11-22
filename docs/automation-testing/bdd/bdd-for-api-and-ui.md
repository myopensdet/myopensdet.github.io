---
title: "BDD for API and UI: One Feature File, Two Ways In"
description: "Run the same Gherkin scenarios through an API with requests and through a web page with Playwright, in behave and pytest-bdd. A driver layer keeps the steps the same; screenshots catch UI failures."
level: Intermediate
tags:
  - BDD
  - API
  - Playwright
nav_title: "BDD for API and UI"
order: 60
summary: "The same scenarios, through the API and through the web page."
updated: "2026-11-22"
---

# BDD for API and UI: One Feature File, Two Ways In

A scenario describes behaviour: "When I apply the coupon SAVE10, then the cart total is 44.98". It doesn't say whether that happens through the API or the web page, and it shouldn't. With a **driver** between the steps and the app, the same feature files and the same steps run through the API (fast, for every change) and through the web page with Playwright (slower, for what users really see).

!!! note "Before you start"
    Read [tags and hooks](tags-and-hooks.md). For the web page runs, once per computer: `python -m playwright install chromium`.

## What you will learn

- The driver pattern: one interface, an API driver and a UI driver
- How to switch target in behave and in pytest-bdd
- What the UI run adds, and what to look at when it fails

## Why this matters at work

Teams often have two sets of BDD tests, one for the API and one for the UI, that slowly drift apart. One set of scenarios with two drivers means one place to change a rule, and the API run gives fast feedback while the UI run proves the page works too.

## The idea in plain words

!!! info "In plain words"
    You can order at a café by phone or at the counter. The order is the same: one coffee, no sugar. The phone and the counter are two drivers. The scenario is the order.

## Step by step

1. **Read the API driver.** `drivers/api_driver.py`:

    ```python
    --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/drivers/api_driver.py"
    ```

    When the shop refuses something, the API answers 400 with a reason. The driver keeps that reason as the message, the same message the web page shows. That's what lets one `Then I see the message …` step check both.

2. **Read the UI driver.** `drivers/ui_driver.py`:

    ```python
    --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/drivers/ui_driver.py"
    ```

    Same methods, but each one uses the page the way a person would: find the field by its label, the button by its name. [UI automation](../playwright/index.md) teaches these locators in depth.

3. **Switch target.**

    === "behave"

        ```bash
        behave --format=progress -D target=ui
        ```

        ```text
        USING RUNNER: behave.runner:Runner
        features/cart.feature  ......
        features/coupons.feature  ..

        2 features passed, 0 failed, 0 skipped
        8 scenarios passed, 0 failed, 1 skipped
        30 steps passed, 0 failed, 6 skipped
        Took 0min 1.386s
        ```

        `-D target=ui` puts `target` in `context.config.userdata`, and `before_all` starts the browser.

    === "pytest-bdd"

        ```bash
        python -m pytest --target=ui -v
        ```

        ```text
        tests/test_shop.py::test_save10_takes_10_off PASSED                      [ 11%]
        tests/test_shop.py::test_an_unknown_coupon_changes_nothing PASSED        [ 22%]
        tests/test_shop.py::test_a_coupon_works_only_once XFAIL (Known bug: ...) [ 33%]
        tests/test_shop.py::test_one_book PASSED                                 [ 44%]
        tests/test_shop.py::test_two_different_books PASSED                      [ 55%]
        tests/test_shop.py::test_several_copies_of_one_book[2-Python for Testers-49.98] PASSED [ 66%]
        tests/test_shop.py::test_several_copies_of_one_book[3-SQL in a Week-58.50] PASSED [ 77%]
        tests/test_shop.py::test_several_copies_of_one_book[10-SQL in a Week-195.00] PASSED [ 88%]
        tests/test_shop.py::test_more_than_10_copies_is_refused PASSED           [100%]
        XFAIL tests/test_shop.py::test_a_coupon_works_only_once - Known bug: see the scenario's description
        ========================= 8 passed, 1 xfailed in 2.54s =========================
        ```

        `--target=ui` comes from `pytest_addoption` in `tests/conftest.py`.

    The same scenarios, through Chromium. 2.5 seconds instead of half a second: that's why the API run is the one for every change.

4. **Look at the screenshot.** When a UI step fails, the hook saves the page to `reports/screenshots/`. The known-bug scenario, run on the UI:

    ![The practice shop's cart page after SAVE10 was applied twice: the message says "Coupon SAVE10 applied" and the total is 40.48](../../assets/images/bdd-testing/coupon-applied-twice.png){ loading=lazy }

    40.48 is 49.98 with 10% off twice. The picture goes straight into the bug report.

5. **Point it at a real shop.** The template starts its own practice shop on a free local port. Set `SHOP_URL=https://your-test-environment` and it tests that instead, with no code change.

    !!! success "Check: you should now be able to"
        Run the same scenarios through the API and the web page in both tools, and find the screenshot of a failed UI step.

## When it goes wrong

- **A UI step waits, then fails.** A button was renamed. With a 3-second timeout:

    ```text
    playwright._impl._errors.TimeoutError
    Locator.click: Timeout 3000ms exceeded.
    Call log:
      - waiting for get_by_role("button", name="Use coupon")
    ```

    The default timeout is 30 seconds. Fix the name in the UI driver, in one place. No feature file changes.
- **The API run passes, the UI run fails.** The rule works, the page doesn't: a real UI bug, or a changed page. The screenshot shows which.
- **`BrowserType.launch: Executable doesn't exist at ...`** when the browser starts, with a box that says to run `playwright install`. The browser was never downloaded on this computer. Run `python -m playwright install chromium` once.

## Common mistakes

!!! warning "Common mistakes"
    - **UI words in the steps.** "When I click Apply" can't run on the API. Keep the clicking in the UI driver.
    - **Every scenario on the UI.** Run all of them on the API, and the important ones on the UI too.
    - **Sharing one browser page between scenarios.** Each scenario gets a new browser context: its own cookies and cart.

!!! failure "If you see this error"
    **behave: `HOOK-ERROR in before_all: ValueError: -D target must be one of ('api', 'ui'), not 'web'`**
    **pytest-bdd: `error: argument --target: invalid choice: 'web' (choose from 'api', 'ui')`**
    The target name is wrong. Use `api` or `ui`, or add your own driver to `drivers/` and to `TARGETS`.

## Try it yourself

Run only the `@smoke` scenarios on the UI, in both tools.

??? success "Solution"
    behave: `behave --tags=@smoke -D target=ui`. pytest-bdd: `python -m pytest -m smoke --target=ui`. Two scenarios each.

## Quick check

1. What does the driver hide from the steps?

    ??? question "Answer"
        How the app is reached: URLs and JSON for the API, labels and buttons for the page.

2. Which run goes on every change, and why?

    ??? question "Answer"
        The API run. It's several times faster.

## References

- [Playwright for Python: Getting started](https://playwright.dev/python/docs/library)
- [Playwright: Locators](https://playwright.dev/python/docs/locators)
- [behave: User-defined data](https://behave.readthedocs.io/en/latest/new_and_noteworthy_v1.2.5/#userdata)
- [Martin Fowler: Page Object](https://martinfowler.com/bliki/PageObject.html)

Written for Python 3.13, behave 1.3, pytest-bdd 9.0 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
