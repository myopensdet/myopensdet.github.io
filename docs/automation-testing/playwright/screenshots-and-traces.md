---
title: "Screenshots and Traces on Failure in Playwright and pytest"
description: "Make every failed UI test leave evidence: a full-page screenshot of each open tab and a Playwright trace with every action, page snapshot and network call, saved only for failures by a pytest hook and fixture. Open traces with the trace viewer."
level: Intermediate
tags:
  - Playwright
  - pytest
  - Debugging
nav_title: "Screenshots and traces"
order: 60
summary: "A screenshot and a trace for every failed test, and how to read them."
updated: "2026-11-22"
---

# Screenshots and Traces on Failure in Playwright and pytest

A UI test that fails in the night run leaves you an error message and nothing else, unless you planned for it. The template saves two things for every failed test: a **screenshot** of each open tab, and a **trace**: a recording of every action, with a snapshot of the page before and after each one, the network calls and the console. With both, you can usually say what went wrong without running the test again.

!!! note "Before you start"
    Read [Page Object Model](page-object-model.md), and [fixtures and conftest](../pytest/fixtures-and-conftest.md) for `yield` fixtures. Have the [template project](index.md#templates) open.

## What you will learn

- How the template saves a screenshot and a trace only when a test fails
- How to open a trace and read it
- How to watch a test run, slowed down

## Why this matters at work

"It failed last night, I ran it this morning and it passed" is the start of many lost days. A screenshot shows the page at the moment of failure. A trace shows every step before it. Teams that keep both fix failures in minutes, and can tell a real bug from a flaky test.

## The idea in plain words

!!! info "In plain words"
    A screenshot is a photo of the crash. A trace is the dashcam recording: the minutes before it, frame by frame. The car only keeps the recording when something happened.

## Step by step

1. **Read how it works.** From `tests/conftest.py`:

    ```python
    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_makereport(item, call):
        """Keep each phase's result on the test, so fixtures can see if the test failed."""
        report = yield
        setattr(item, f"report_{report.when}", report)
        return report
    ```

    ```python
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
    ```

    - **The hook** runs after each phase of a test (set-up, call, tear-down) and keeps the result on the test as `report_setup`, `report_call` and `report_teardown`.
    - **The fixture** starts a trace for every test. After the test, it looks at `report_call`. Failed: a screenshot of every open tab, and the trace saved as a ZIP. Passed: the trace is thrown away, so passing runs leave nothing behind.
    - **The order matters:** screenshots before `context.close()`. A closed page can't be photographed.

2. **Make a test fail, and look at what it leaves.** `--runxfail` runs the known-bug test as a normal test, so it fails:

    ```bash
    python -m pytest --runxfail tests/test_cart.py::test_remove_a_book_updates_the_cart_count
    ```

    ```text
    FAILED tests/test_cart.py::test_remove_a_book_updates_the_cart_count - Assert...
    1 failed in 5.82s
    ```

    ```text
    reports/screenshots/test_remove_a_book_updates_the_cart_count_0.png
    reports/traces/test_remove_a_book_updates_the_cart_count.zip
    ```

    The screenshot (23 KB):

    ![The cart page after removing SQL in a Week: one row is left, Python for Testers, total 24.99, but the cart count in the header still says 3](../../assets/images/ui-automation/cart-count-not-updated.png){ loading=lazy }

    One book left, total 24.99, but the header still says 3. That picture is the bug report.

3. **Open the trace.**

    ```bash
    python -m playwright show-trace reports/traces/test_remove_a_book_updates_the_cart_count.zip
    ```

    It opens the trace viewer, a page in your browser. On the left, every action the test did: `goto`, `click`, each `expect`. Click one to see the page before and after it, the locator it used, and the time it took. The tabs below show network calls, console messages and errors. Here you'd see the `DELETE` call for the removed book succeed, and in the snapshot after it, the header count still at 3: the API did its job, the page didn't update.

    You can also drop the ZIP on [trace.playwright.dev](https://trace.playwright.dev/). It opens in your browser and doesn't upload the file.

4. **Watch it run.** To see what the test does, slowed down:

    ```bash
    python -m pytest --headed --slowmo=500 tests/test_cart.py
    ```

    `--headed` shows the browser window. `--slowmo=500` waits half a second before each action. Both are options from the template's `conftest.py`.

5. **Keep `reports/` out of Git, and keep it in the pipeline.** The template's `.gitignore` lists `reports/`. In a pipeline, save the folder as the job's artifact when the job fails: [CI/CD](../../devops-for-qa/ci-cd/index.md) shows how.

    !!! success "Check: you should now be able to"
        Explain how the hook and fixture save evidence only for failures, find a failed test's screenshot, and open its trace.

## When it goes wrong

- **Screenshots after closing.** Taking a screenshot after `context.close()`:

    ```text
    TargetClosedError: Page.screenshot: Target page, context or browser has been closed
    ```

    And it hides the real failure. Take screenshots first, then close, as the template does.
- **No screenshot for a failed test.** The failure was in set-up, before the test ran, so `report_call` doesn't exist. The error is in the set-up output: often the shop didn't start, or the log-in fixture failed.
- **Traces from passing tests fill the disk.** Call `tracing.stop()` without a path for passes, as the template does.
- **The trace viewer won't open in the pipeline.** It needs a screen. Download the ZIP from the pipeline's artifacts and open it on your computer.

## Common mistakes

!!! warning "Common mistakes"
    - **Screenshots only of the first tab.** The bug may be in the tab that opened. The template saves every tab.
    - **Recording video of every test.** Videos are big and slow to watch. A trace has more, in less space.
    - **Committing `reports/`.** Screenshots can show test data. Keep them out of Git.
    - **Debugging by adding `print` and rerunning ten times.** Open the trace first.

!!! failure "If you see this error"
    **`AttributeError: 'Function' object has no attribute 'report_call'`**, in the tear-down of a test whose set-up failed
    The fixture read `request.node.report_call` directly. When set-up fails, the test never runs, so there is no `report_call`, and this error is shown on top of the real one. Read it with `getattr(request.node, "report_call", None)`, as the template does.

## Try it yourself

Change the template so it also saves a screenshot when a test fails during set-up (for example, the log-in fixture fails).

??? success "Solution"
    Check `report_setup` too:

    ```python
    failed = any(
        getattr(request.node, f"report_{when}", None) is not None
        and getattr(request.node, f"report_{when}").failed
        for when in ("setup", "call")
    )
    if failed:
        ...
    ```

    A failure in a fixture that needs `context`, like `logged_in_page`, happens during set-up. The `context` fixture's clean-up still runs, so it can take the screenshot.

## Quick check

1. Why does a passing test leave no files?

    ??? question "Answer"
        The fixture calls `tracing.stop()` without a path, and takes no screenshot, unless the test failed.

2. What does a trace have that a screenshot doesn't?

    ??? question "Answer"
        Every action before the failure, with the page before and after each one, plus network calls and console messages.

3. Why take the screenshot before `context.close()`?

    ??? question "Answer"
        After closing, the page is gone, and the screenshot fails with `TargetClosedError`.

## References

- [Playwright: Trace viewer](https://playwright.dev/python/docs/trace-viewer)
- [Playwright: Screenshots](https://playwright.dev/python/docs/screenshots)
- [Playwright: Videos](https://playwright.dev/python/docs/videos)
- [pytest: Making test result information available in fixtures](https://docs.pytest.org/en/stable/example/simple.html#making-test-result-information-available-in-fixtures)

Written for Python 3.13, pytest 9 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
