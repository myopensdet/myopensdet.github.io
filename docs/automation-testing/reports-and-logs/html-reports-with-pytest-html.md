---
title: "HTML Test Reports With pytest-html"
description: "Make a one-file HTML report of every pytest run with pytest-html: what it shows, a self-contained file you can attach anywhere, a custom title, your own Environment rows, what to hide before sharing it, and the captured logs of each failed test."
level: Intermediate
tags:
  - Reporting
  - pytest
nav_title: "HTML reports with pytest-html"
order: 20
summary: "One HTML file per run that anyone can open."
updated: "2026-11-22"
---

# HTML Test Reports With pytest-html

pytest's terminal output is for the person who ran the tests. Everyone else needs something they can open: a page with what passed and failed, the error of each failure, and the logs. **pytest-html** writes that page after every run, as one HTML file you can attach to a ticket, a chat or a pipeline run. It takes one line in `pytest.ini`.

!!! note "Before you start"
    Read [logging in tests](logging-in-tests.md). Have the [template project](index.md#templates) installed: `requirements.txt` includes `pytest-html==4.2.0`.

## What you will learn

- How to make an HTML report on every run, as one file
- What the report shows, and how to read a failure in it
- How to change its title and add your own Environment rows
- What to hide before you share a report

## Why this matters at work

"Can you send me the results?" is asked after every test run. A screenshot of a terminal doesn't answer it, and a 2,000-line console log doesn't either. One HTML file does: anyone can open it, filter it to failures, and read the error and the logs, without Python installed.

## The idea in plain words

!!! info "In plain words"
    The terminal output is your own rough notes during an exam. The HTML report is the clean results sheet you hand to the teacher: every question, right or wrong, and your working for the wrong ones.

## Step by step

1. **Make it on every run.** In `pytest.ini`:

    ```ini
    addopts = -ra --strict-markers
        --html=reports/report.html --self-contained-html
        --junitxml=reports/junit.xml
    ```

    `--html` names the file. `--self-contained-html` puts the styles and the screenshots inside it. Without it, pytest-html writes a second file, `reports/assets/style.css`, and the report looks broken when you send `report.html` alone. One file is easier to share.

2. **Run and open it.**

    ```bash
    python -m pytest --runxfail
    ```

    `--runxfail` runs the known-bug test as a normal test, so the report has a real failure. Open `reports/report.html` in a browser:

    ![The pytest-html report's summary and results: 1 failed and 6 passed, with check boxes to filter by result. The failed test is open, showing its code, the assertion error "Locator expected to have text '1', Actual value: 3", and a screenshot of the cart page on the right](../../assets/images/reporting-and-logging/pytest-html-report.png){ loading=lazy }

    - **Summary:** how many tests, how long. Check boxes filter the table: untick **Passed** to see only the problems.
    - **Results:** one row per test. Failures come first. Click a row to open it.
    - **A failed row** shows the test's code, the error, the captured logs (setup, call, teardown) and any extras, like the screenshot here. [Screenshots and request logs](screenshots-and-request-logs.md) shows how it got there.

    The logs of passing tests aren't in the report: only failures need them, and the file stays small. Every line of every test is in `reports/tests.log`.

3. **Give it a title.** From `tests/conftest.py`:

    ```python
    def pytest_html_report_title(report):
        report.title = "Practice shop: test report"
    ```

    Name the app and the suite, so people know what they're looking at a week later.

4. **Add your own Environment rows.** The report's **Environment** table comes from the pytest-metadata plugin, which pytest-html installs. The template adds the address of the shop under test, once it's known:

    ```python
    from pytest_metadata.plugin import metadata_key
    ```

    ```python
    request.config.stash[metadata_key]["Shop URL"] = url  # shown under Environment
    ```

    Add what helps someone read the results: the environment name, the app's version, the browser. You can also pass rows on the command line: `--metadata "App version" 2.4.1`.

5. **Hide what shouldn't travel.** By default the Environment table lists the Python version, the **Platform** (the operating system and its version) and every installed plugin. That's useful inside your team. Before a report goes to a customer or a public issue, remove rows with the pytest-metadata hook:

    ```python
    def pytest_metadata(metadata):
        metadata.pop("Platform", None)
        metadata.pop("Plugins", None)
    ```

    With it in `conftest.py`, neither row is in the report. Test data is the other thing to check: the report holds whatever your tests and logs wrote, so keep secrets out of logs (see [screenshots and request logs](screenshots-and-request-logs.md)).

    !!! success "Check: you should now be able to"
        Make a self-contained HTML report on every run, filter it to failures, read a failure's error and logs, set its title and Environment rows, and remove rows before sharing it.

## When it goes wrong

- **`pytest: error: unrecognized arguments: --html=reports/report.html --self-contained-html`.** pytest-html isn't installed in the Python that ran pytest. Activate the virtual environment, then `python -m pip install -r requirements.txt`.
- **The report has no styles when someone else opens it.** It was made without `--self-contained-html`, and only `report.html` was sent, not `assets/`. Add the option.
- **The report is huge.** Usually screenshots of every step, or logs at DEBUG of every test. Attach screenshots only to failures, and keep DEBUG in the log file.
- **The report is from an old run.** Each run overwrites `reports/report.html`. In a pipeline, save the file from each run as that run's artifact.

## Common mistakes

!!! warning "Common mistakes"
    - **Sending the terminal output instead of the report.** The report filters, folds and keeps the screenshots.
    - **Committing reports to Git.** They change every run and may hold test data. The template's `.gitignore` lists `reports/`.
    - **Sharing reports outside the team without looking at them.** Check the Environment table and the logs first.

!!! failure "If you see this error"
    **`PermissionError: [Errno 13] Permission denied: '.../reports/report.html'`**, at the end of the run
    The tests ran, but the report can't be written: the folder is read-only, or (on Windows) another program has the file open and locked. Close it, or write somewhere else with `--html=other/report.html`. Without `--self-contained-html`, the same error names `assets` and comes before any test runs.

## Try it yourself

Add a row **Test data: fake (local_only)** to the Environment table, and remove the **Packages** row.

??? success "Solution"
    In `tests/conftest.py`:

    ```python
    def pytest_metadata(metadata):
        metadata["Test data"] = "fake (local_only)"
        metadata.pop("Packages", None)
    ```

    The Environment table then has a **Test data** row, and no **Packages** row. Or add the row from the command line: `python -m pytest --metadata "Test data" "fake (local_only)"`.

## Quick check

1. Why use `--self-contained-html`?

    ??? question "Answer"
        It puts the styles and images in the one HTML file, so you can send that file alone.

2. Where are the logs of a passing test?

    ??? question "Answer"
        Not in the HTML report. In `reports/tests.log`, which has every line of the run.

3. Which hook removes a row from the Environment table?

    ??? question "Answer"
        `pytest_metadata(metadata)`, from pytest-metadata: `metadata.pop("Platform", None)`.

## References

- [pytest-html: User guide](https://pytest-html.readthedocs.io/en/latest/user_guide.html)
- [pytest-metadata](https://github.com/pytest-dev/pytest-metadata)
- [pytest: How to manage logging](https://docs.pytest.org/en/stable/how-to/logging.html)

Written for Python 3.13, pytest 9 and pytest-html 4.2. Outputs captured November 2026. Links checked: November 2026.
