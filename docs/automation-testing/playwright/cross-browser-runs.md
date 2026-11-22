---
title: "Cross-Browser Testing With Playwright: Chromium, Firefox and WebKit"
description: "Run one Playwright and pytest suite on Chromium, Firefox and WebKit (Safari's engine) with a --browser option, decide which browsers run when, emulate a phone, and handle a browser that won't start on one machine."
level: Intermediate
tags:
  - Playwright
  - UI
nav_title: "Cross-browser runs"
order: 70
summary: "One suite on Chromium, Firefox and WebKit, and phones too."
updated: "2026-11-22"
---

# Cross-Browser Testing With Playwright: Chromium, Firefox and WebKit

Your users don't all use Chrome. Safari is on every iPhone and Mac, and Firefox has its own engine too. A page can work in one and break in another: a date field, a CSS layout, a script that uses something new. Playwright drives all three engines, **Chromium** (Chrome and Edge), **Firefox** and **WebKit** (Safari), from the same code. The template switches with one option.

!!! note "Before you start"
    Read [screenshots and traces](screenshots-and-traces.md). Download the other browsers once, in the virtual environment: `python -m playwright install firefox webkit` (about 300 MB each).

## What you will learn

- How to run the same suite on another browser
- Which browsers to run when
- How to emulate a phone
- What to do when a browser won't start on one computer

## Why this matters at work

"Works in Chrome" is how many bugs reach production. But three browsers make every run three times longer. Teams need a plan: what runs on every change, and what runs before a release. The plan is cheap to make, and it decides how often a Safari user finds a bug before you do.

## The idea in plain words

!!! info "In plain words"
    A play is rehearsed on one stage most days. Before opening night, the cast tries it in each theatre it will tour. Same play, different stages: a door that sticks in one of them is found before the audience sees it.

## Step by step

1. **Switch browser with one option.** The template's `conftest.py` adds `--browser`, and the `browser` fixture launches that engine:

    ```python
    BROWSERS = ("chromium", "firefox", "webkit")
    ```

    ```python
    def pytest_addoption(parser):
        parser.addoption("--browser", choices=BROWSERS, default="chromium", help="browser engine")
    ```

    ```python
    engine = getattr(playwright, options("--browser"))
    browser = engine.launch(headless=not options("--headed"), slow_mo=options("--slowmo"))
    ```

    No test or page object changes.

2. **Run it on WebKit.**

    ```bash
    python -m pytest --browser=webkit
    ```

    ```text
    XFAIL tests/test_cart.py::test_remove_a_book_updates_the_cart_count - Known bug: the cart count stays the same after Remove
    ======================== 15 passed, 1 xfailed in 18.34s ========================
    ```

    The same 16 results as Chromium (16.39 seconds there). The planted bug shows on both: it's in the page's script, not in one browser.

3. **Decide what runs when.** A common plan:

    | When | Browsers | Tests |
    | --- | --- | --- |
    | Every change | Chromium | All |
    | Every night | Chromium, Firefox, WebKit | All |
    | Before a release | All three, plus a phone | All |

    Look at your users first: the analytics show which browsers they really use. Run those more.

4. **Emulate a phone.** Playwright knows 207 devices. Each one sets the screen size, the browser's user agent, touch and the right engine:

    ```python
    device = playwright.devices["iPhone 15"]   # viewport 393 x 659, webkit, is_mobile
    context = browser.new_context(**device, base_url=base_url)
    ```

    Launch the device's own engine (`device["default_browser_type"]` is `webkit` for iPhones). It's an emulation, not a real phone: good for layout and touch, not for phone-only bugs. For those, teams use real-device clouds.

5. **Chrome and Edge themselves.** Playwright's Chromium is the open-source base of Chrome and Edge. To test the branded browsers installed on the computer, launch with a channel: `playwright.chromium.launch(channel="chrome")` or `channel="msedge"`.

    !!! success "Check: you should now be able to"
        Run the suite on another browser, propose which browsers run when, and emulate a phone.

## When it goes wrong

- **A browser won't start on one computer.** On the Mac these pages were made on (macOS 27.2), Firefox failed to start:

    ```text
    playwright._impl._errors.Error: BrowserType.launch: Failed to launch the browser process.
    Browser logs:
    ...
    [pid=30102][err] *** You are running in headless mode.
    [pid=30102][err] Could not find profile folder.
    ```

    Chromium and WebKit worked. Nothing in the tests was wrong: that Firefox build and that system version didn't work together. What to do: update Playwright when a newer version is out (it brings newer browsers), search Playwright's issue tracker for the error, and meanwhile run that browser where it works, usually Linux in the pipeline. The template's topic test skips a browser that won't start, and says why.
- **A wrong browser name.**

    ```text
    python -m pytest: error: argument --browser: invalid choice: 'edge' (choose from 'chromium', 'firefox', 'webkit')
    ```

    Engines, not brands: Edge is `chromium` (with `channel="msedge"` for the real Edge).
- **`Executable doesn't exist` for one browser.** It was never downloaded: `python -m playwright install firefox` (or `webkit`).
- **A test fails on one browser only.** Open its screenshot and trace from that run. If the page really differs, it's a bug for the developers. If the test relies on one browser's timing, fix the wait.

## Common mistakes

!!! warning "Common mistakes"
    - **Every browser on every change.** Three times slower feedback. Chromium on every change, all three at night.
    - **Browser checks in tests.** `if browser == "webkit": skip` hides bugs. Skip only with a reason and a ticket.
    - **Treating emulation as a real phone.** It catches layout and touch problems, not everything.
    - **Forgetting to update browsers.** The browsers come with the Playwright version. Update Playwright to test what users have now.

!!! failure "If you see this error"
    **`BrowserType.launch: Failed to launch the browser process.`**
    The browser program exists but won't start. Read the browser logs under the error. On Linux, run `python -m playwright install-deps` once to add the system libraries browsers need. On other systems, try the next Playwright version, or that browser on another system.

## Try it yourself

Run only the `@smoke` tests on WebKit.

??? success "Solution"
    ```bash
    python -m pytest -m smoke --browser=webkit
    ```

    ```text
    ======================= 3 passed, 13 deselected in 3.10s =======================
    ```

    `-m smoke` picks the tests marked `smoke`, `--browser` the engine. Options combine freely.

## References

- [Playwright: Browsers](https://playwright.dev/python/docs/browsers)
- [Playwright: Emulation (devices)](https://playwright.dev/python/docs/emulation)
- [Playwright: Docker](https://playwright.dev/python/docs/docker)
- [Playwright issues on GitHub](https://github.com/microsoft/playwright/issues)

Written for Python 3.13 and Playwright 1.64 (Chromium, Firefox 157, WebKit 27.2). Outputs captured November 2026. Links checked: November 2026.
