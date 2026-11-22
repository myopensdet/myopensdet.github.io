---
title: "Attach Screenshots and Request Logs to pytest Reports"
description: "Make every failure explain itself: log each API call in one line with its status and time, show a refused call's answer with the failure, hide passwords and card numbers before they're written, and put a screenshot of the page into the pytest-html report when a browser test fails."
level: Intermediate
tags:
  - Reporting
  - API
  - Playwright
nav_title: "Screenshots and request logs"
order: 40
summary: "Request logs and screenshots on every failure, with secrets hidden."
updated: "2026-11-22"
---

# Attach Screenshots and Request Logs to pytest Reports

An assertion error says what was wrong: `assert 400 == 201`. It doesn't say why. The why is in what the app answered, and for page tests, in what the page looked like. This lesson puts both into the report for every failure: **a log line for every API call**, the **answer of any refused call**, and a **screenshot of the page** when a browser test fails. And it keeps passwords, tokens and card numbers out, because reports get shared.

!!! note "Before you start"
    Read [logging in tests](logging-in-tests.md) and [HTML reports with pytest-html](html-reports-with-pytest-html.md). Have the [template project](index.md#templates) open.

## What you will learn

- What to log for each API call, and at which level
- How to hide secrets before they're written anywhere
- How to put a screenshot into the pytest-html report on failure
- How to test that a secret never reaches the log

## Why this matters at work

A developer gets a failed-test link. With only `assert 400 == 201`, they rerun it, add prints, and ask you. With the request log they see `POST /api/orders -> 400` and `{"detail": "Please accept the terms of sale"}`, and know. Teams also get burnt the other way: a token in a log, copied into a ticket, read by people who shouldn't have it.

## The idea in plain words

!!! info "In plain words"
    A delivery driver photographs every parcel at the door. If a customer says it never came, the photo answers. But the photo shows the parcel, not the customer's door code. Logs and screenshots are your photos: enough to prove what happened, never the secrets.

## Step by step

1. **Read the API client.** `helpers/api_client.py`:

    ```python
    --8<-- "modules/core_automation/reporting_and_logging/templates/report_tests/helpers/api_client.py"
    ```

    For each call:

    | Line | Level | Why |
    | --- | --- | --- |
    | `POST /api/orders body: {..., "card": "***"}` | DEBUG | What was sent, secrets hidden |
    | `POST /api/orders -> 201 in 2 ms` | INFO | One line per call: method, path, status, time |
    | `POST /api/orders -> 400 in 1 ms` | WARNING | The app refused it |
    | `POST /api/orders answer: {"detail": "..."}` | DEBUG, or WARNING if refused | What came back, shortened to 500 characters |

    Every API call in every test goes through `call()`, so every test gets this for free.

2. **Hide secrets before they're written.** `redact()` replaces the value of every key in `SECRETS`, at any depth of the JSON, with `***`. It runs on the body before it's logged, and on the answer. So the log file says:

    ```text
    20:46:10 DEBUG   shop.api: POST /api/orders body: {"name": "Arshad Test", "country": "Germany", "delivery": "express", "terms": true, "card": "***"}
    ```

    Hide secrets at the source, in the client. Not later, in the report: by then they're in the log file, the JUnit XML and the console output too.

3. **See a failed API test in the report.** Here a test expected `201` where the app said `400`. The report shows the error, then the captured logs (click **expand [+]** to see all of them):

    ![A failed test in the pytest-html report: assert 400 == 201, then the captured log, ending with two WARNING lines: POST /api/orders -> 400 in 1 ms, and the answer: Please accept the terms of sale](../../assets/images/reporting-and-logging/failed-api-test-with-log.png){ loading=lazy }

    The last line answers "why?". The first version of this template logged answers only at DEBUG, so a failure showed the `400` but not the reason: it was only in `reports/tests.log`. Logging a refused call's answer at WARNING fixed that.

4. **Put a screenshot into the report.** From `tests/conftest.py`:

    ```python
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
    ```

    - The hook runs after each phase of each test. `report.when == "call"` and `report.failed` pick the failed test body.
    - `item.funcargs` holds the fixtures the test used, also indirectly: `test_remove_updates_the_cart_count` uses `cart_page`, which uses `page`.
    - The page is still open here: fixtures close after the test's report is made. So the screenshot shows the page at the moment of failure.
    - `pytest_html.extras.png()` adds it to the report. With `--self-contained-html`, it's inside the HTML file.

    The [HTML reports lesson](html-reports-with-pytest-html.md#step-by-step) shows the result: the screenshot next to the error of the failed cart test.

5. **Other extras.** `pytest_html.extras` also has `text()`, `json()`, `url()`, `html()`, `jpg()`, `svg()` and `video()`. A failed API test could attach the last answer as `extras.json(...)`. Keep it to what helps someone understand the failure.

6. **Test the secrets rule.** `tests/test_logging.py` logs in and checks the log:

    ```python
    def test_passwords_never_reach_the_log(base_url, caplog):
        caplog.set_level(logging.DEBUG, logger="shop.api")
        ShopApi(base_url).log_in(**TEST_USER)
        assert TEST_USER["password"] not in caplog.text
        assert '"password": "***"' in caplog.text
    ```

    With `"password"` removed from `SECRETS`, it fails, and shows where:

    ```text
    E       assert 'local_only_password' not in '20:08:07 DE...ogged in"}\n'
    E
    E         'local_only_password' is contained here:
    E           ssword": "local_only_password"}
    ```

    !!! success "Check: you should now be able to"
        Log each API call at the right level, show a refused call's answer with the failure, hide secrets in the client, attach a screenshot to the report on failure, and test that a secret never reaches the log.

## When it goes wrong

- **A secret in the log.** A new field (`otp`, `pin`, `secret`) isn't in `SECRETS`. Add it, and add a check like `test_passwords_never_reach_the_log` for it. Check headers too, if you ever log them: `Authorization` and `Cookie` are in the list for that.
- **No screenshot in the report.** The test didn't use the `page` fixture (directly or through another fixture), or it passed, or the report was made without pytest-html. API tests have no page to photograph: their evidence is the request log.
- **The failure shows the status but not the reason.** The answer was logged below the captured level. Log a refused call's answer at WARNING, as the template does.
- **The log is flooded with huge bodies.** Shorten them, as `short()` does, and keep bodies at DEBUG for successful calls.

## Common mistakes

!!! warning "Common mistakes"
    - **Hiding secrets in the report instead of the client.** The console, the log file and the XML already have them.
    - **A screenshot for every step of every test.** Reports get huge and nobody looks. Failures only.
    - **Logging full response headers.** They carry cookies and tokens. Log the status and the body you need.
    - **Writing request logs by hand in each test.** Put logging in the one client every test uses.

!!! failure "If you see this error"
    **`playwright._impl._errors.TargetClosedError: Page.screenshot: Target page, context or browser has been closed`** in the report hook
    The page was closed before the hook ran: a fixture closed it during the test, or the screenshot is taken in the `teardown` phase. Take it when `report.when == "call"`, while the page is still open.

## Try it yourself

Add `"otp"` (one-time code) to the secrets, and extend `test_passwords_never_reach_the_log` with a check that `redact()` hides it, without calling the API.

??? success "Solution"
    In `helpers/api_client.py`:

    ```python
    SECRETS = {"password", "card", "token", "authorization", "cookie", "api_key", "otp"}
    ```

    In `tests/test_logging.py`:

    ```python
    from helpers.api_client import redact

    def test_one_time_codes_are_hidden():
        assert redact({"user": "a@example.com", "otp": "123456"}) == {
            "user": "a@example.com",
            "otp": "***",
        }
    ```

    `redact()` is a plain function, so it can be tested on its own, with no app running.

## References

- [pytest-html: Extras](https://pytest-html.readthedocs.io/en/latest/user_guide.html#extra-content)
- [pytest: Making test result information available in fixtures](https://docs.pytest.org/en/stable/example/simple.html#making-test-result-information-available-in-fixtures)
- [Playwright: Screenshots](https://playwright.dev/python/docs/screenshots)
- [OWASP: Logging Cheat Sheet (data to exclude)](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#data-to-exclude)

Written for Python 3.13, pytest 9, pytest-html 4.2 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
