---
title: "Logging in Tests: Python Logging Levels and pytest Log Settings"
description: "Use Python's logging module in a test suite instead of print: loggers and levels, one INFO line per API call with details at DEBUG, pytest's log_level, log_cli and log_file settings, quieting noisy libraries, and testing your logs with caplog."
level: Intermediate
tags:
  - Reporting
  - Python
  - pytest
nav_title: "Logging in tests"
order: 10
summary: "Logging levels, named loggers, and pytest's log settings."
updated: "2026-11-22"
---

# Logging in Tests: Python Logging Levels and pytest Log Settings

When a test fails, the first question is "what happened before?". **Logging** answers it: each step writes a short line, with a time, a level and where it came from. Unlike `print()`, log lines can be turned up or down, sent to a file, shown only for failed tests, and put in the HTML report. Python has logging built in, and pytest knows how to collect it.

!!! note "Before you start"
    Read [fixtures and conftest](../pytest/fixtures-and-conftest.md). Have the [template project](index.md#templates) open.

## What you will learn

- The five logging levels, and what each is for in a test suite
- Named loggers, and how to log one API call in one line
- pytest's log settings: captured, live, and to a file
- How to quiet other libraries, and how to test your own logs

## Why this matters at work

A failed test that says only `assert 400 == 201` sends someone to rerun it with prints added. One that logged `POST /api/orders -> 400` and the answer `{"detail": "Please accept the terms of sale"}` explains itself. Good logs save the hours between "it failed" and "I know why".

## The idea in plain words

!!! info "In plain words"
    A ship's log has short entries: the time, what happened, how serious it was. On a calm day, the captain reads only the important ones. After a storm, every entry. Logging levels are that choice: write everything, read what you need.

## Step by step

1. **Know the levels.**

    | Level | Use it in tests for | Example from the template |
    | --- | --- | --- |
    | `DEBUG` | Details you need only when digging: bodies, values | `POST /api/login body: {"email": "...", "password": "***"}` |
    | `INFO` | Normal steps: each call, each set-up step | `POST /api/orders -> 201 in 2 ms` |
    | `WARNING` | Something unusual that may be fine: a 4xx answer | `POST /api/login -> 401 in 1 ms` |
    | `ERROR` | Something broke that the test didn't expect | A clean-up step that failed |
    | `CRITICAL` | The run can't go on | The app under test never started |

    A setting like "INFO" means "INFO and everything more serious".

2. **Log from a named logger.** From `helpers/api_client.py`:

    ```python
    log = logging.getLogger("shop.api")
    ```

    ```python
    refused = response.status_code >= 400
    log.log(
        logging.WARNING if refused else logging.INFO,
        "%s %s -> %s in %.0f ms",
        method,
        path,
        response.status_code,
        ms,
    )
    # A refused call's answer says why: show it with the failure, not only in the log file.
    answer = short(redact_text(response.text))
    log.log(
        logging.WARNING if refused else logging.DEBUG, "%s %s answer: %s", method, path, answer
    )
    ```

    - The name, `shop.api`, appears in every line, so you know where it came from. Names with dots form a family: `tests.pages` belongs to `tests`.
    - One INFO line per call: method, path, status, time. The bodies go at DEBUG.
    - A call the app refused (4xx or 5xx) is a WARNING, and so is its answer: the answer says why, and WARNING lines show up with a failed test.
    - Pass values as arguments (`"%s", path`), not as an f-string. Logging only builds the text if the line is really written.

3. **Tell pytest what to collect.** From `pytest.ini`:

    ```ini
    --8<-- "modules/core_automation/reporting_and_logging/templates/report_tests/pytest.ini"
    ```

    | Setting | What it does |
    | --- | --- |
    | `log_level = INFO` | Lines collected for each test, shown when it fails and in the HTML report |
    | `log_format`, `log_date_format` | Time, level, logger name, message |
    | `log_file = reports/tests.log` | Every line of the whole run in one file |
    | `log_file_level = DEBUG` | The file gets the details too |

4. **See what a failed test shows.** pytest prints the lines collected for that test, split by phase:

    ```text
    ------------------------------ Captured log setup ------------------------------
    20:46:27 INFO    tests: ---- tests/test_pages.py::test_remove_updates_the_cart_count
    20:46:27 INFO    tests.pages: Cart filled through the API: 3 books
    ------------------------------ Captured log call -------------------------------
    20:46:27 INFO    tests.pages: Removed SQL in a Week
    ```

    Passing tests show nothing, so the output stays short.

5. **Watch it live.** To see log lines while tests run, add `--log-cli-level`:

    ```bash
    python -m pytest tests/test_api.py::test_express_order_adds_delivery --log-cli-level=INFO
    ```

    ```text
    -------------------------------- live log setup --------------------------------
    20:47:17 INFO    tests: ---- tests/test_api.py::test_express_order_adds_delivery
    20:47:17 INFO    tests: Testing the shop at http://127.0.0.1:52324
    20:47:17 INFO    shop.api: POST /api/login -> 200 in 6 ms
    -------------------------------- live log call ---------------------------------
    20:47:17 INFO    shop.api: POST /api/cart -> 200 in 1 ms
    20:47:17 INFO    shop.api: POST /api/cart -> 200 in 1 ms
    20:47:17 INFO    shop.api: POST /api/orders -> 201 in 1 ms
    PASSED                                                                   [100%]
    ```

6. **Read the log file.** `reports/tests.log` has every line at DEBUG. Each test starts with its name, from a hook in `tests/conftest.py`:

    ```python
    def pytest_runtest_setup(item):
        """Start each test's part of reports/tests.log with its name."""
        log.info("---- %s", item.nodeid)
    ```

    ```text
    20:46:10 DEBUG   shop.api: POST /api/orders body: {"name": "Arshad Test", "country": "Germany", "delivery": "express", "terms": true, "card": "***"}
    20:46:10 INFO    shop.api: POST /api/orders -> 201 in 2 ms
    20:46:10 DEBUG   shop.api: POST /api/orders answer: {"number": "BK-1001", "total": "49.48"}
    ```

    The card number is `***`. [Screenshots and request logs](screenshots-and-request-logs.md) shows how.

7. **Quiet other libraries.** Libraries log too. Before this template quieted them, its log file started with dozens of lines like these:

    ```text
    20:44:54 DEBUG   faker.factory: Looking for locale `en_US` in provider `faker.providers.address`.
    20:46:00 DEBUG   asyncio: Using selector: KqueueSelector
    20:46:00 DEBUG   urllib3.connectionpool: Starting new HTTP connection (1): 127.0.0.1:52264
    ```

    Keep their warnings, drop their chatter. From `tests/conftest.py`:

    ```python
    # Other libraries log a lot at DEBUG. Keep their warnings, drop their chatter.
    for noisy in ("asyncio", "urllib3", "faker"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    ```

    Add the names you see in your own log.

8. **Test your logs.** pytest's `caplog` fixture collects log lines inside a test. `tests/test_logging.py`:

    ```python
    --8<-- "modules/core_automation/reporting_and_logging/templates/report_tests/tests/test_logging.py"
    ```

    The first test fails the day someone logs a password.

    !!! success "Check: you should now be able to"
        Pick the right level for a line, log from a named logger, set up pytest's captured, live and file logs, quiet a noisy library, and check logs with `caplog`.

## When it goes wrong

- **The log file stays empty.** The first version of this template wrote nothing to `reports/tests.log` from the tests: 0 lines. The practice shop's web server, uvicorn, sets up logging when it starts, and that closes every log handler already there, including the one pytest writes the file with. The fix, in `shop_app/server.py`, tells uvicorn to leave logging alone:

    ```python
    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="warning", log_config=None
    )
    ```

    If your log file stops part way, look for a library that calls `logging.config.dictConfig` or `logging.basicConfig` during the run.
- **No log lines for a failed test.** The logger's lines are below `log_level`. A DEBUG line isn't collected with `log_level = INFO`. Lower it, or log at INFO.
- **Every line appears twice.** Your code added its own handler to the root logger, and pytest has one too. In tests, don't add handlers: let pytest's settings do it.

## Common mistakes

!!! warning "Common mistakes"
    - **`print()` instead of logging.** Prints can't be filtered by level, and have no time or source.
    - **Everything at INFO.** Bodies and values at INFO make the important lines hard to find. Details go at DEBUG.
    - **f-strings in log calls.** `log.debug(f"{big_object}")` builds the text even when DEBUG is off.
    - **Logging secrets "just for now".** Logs are copied into reports, tickets and chats. Hide them in the client, once.

!!! failure "If you see this error"
    **`--- Logging error ---`** then **`TypeError: not all arguments converted during string formatting`**
    A log call has an argument but no `%s` for it, like `log.info("Removed", book)`. Logging prints this to the screen and carries on, so the line is lost. Write `log.info("Removed %s", book)`.

## Try it yourself

Add a WARNING line to `ShopApi.call()` when a call takes longer than 500 ms. Which template test makes it appear?

??? success "Solution"
    After `ms` is computed:

    ```python
    if ms > 500:
        log.warning("%s %s was slow: %.0f ms", method, path, ms)
    ```

    The practice shop's search takes about 800 ms on purpose, so every search logs it. With `--log-cli-level=WARNING`:

    ```text
    20:49:59 WARNING shop.api: GET /api/books?q=test was slow: 802 ms
    ```

    And one test now fails:

    ```text
    E         At index 0 diff: 'GET /api/books?q=sql was slow: 805 ms' != 'GET /api/books?q=sql -> 200'
    E         Left contains one more item: 'GET /api/books?q=sql -> 200'
    FAILED tests/test_logging.py::test_each_call_is_one_info_line - AssertionErro...
    ```

    That test promised one line per call, and now a slow call writes two. The test did its job: it made the change visible. Decide which you want, then change the code or the test.

## Quick check

1. Which level for "POST /api/cart -> 200 in 3 ms"? And for the request body?

    ??? question "Answer"
        INFO for the one-line summary, DEBUG for the body.

2. Why do passing tests show no log lines in the terminal?

    ??? question "Answer"
        pytest shows captured logs only for failed tests. Use `--log-cli-level` to see them live, or read the log file.

3. What does `caplog` give you?

    ??? question "Answer"
        The log lines written during a test, so the test can check them.

## References

- [Python: Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Python: Logging levels](https://docs.python.org/3/library/logging.html#logging-levels)
- [pytest: How to manage logging](https://docs.pytest.org/en/stable/how-to/logging.html)
- [Uvicorn: Settings (log_config)](https://www.uvicorn.org/settings/#logging)

Written for Python 3.13 and pytest 9. Outputs captured November 2026. Links checked: November 2026.
