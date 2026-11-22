---
title: "JUnit XML Test Reports for CI Pipelines With pytest"
description: "Write JUnit XML from pytest with --junitxml, the format GitLab, Jenkins, Azure DevOps and GitHub Actions tools read: what is in the file, how failures and xfails look, suite names, logs and properties, and the computer details it contains."
level: Intermediate
tags:
  - Reporting
  - pytest
  - CI/CD
nav_title: "JUnit XML for pipelines"
order: 30
summary: "The XML file every pipeline tool reads, and what's in it."
updated: "2026-11-22"
---

# JUnit XML Test Reports for CI Pipelines With pytest

People read the HTML report. Pipeline tools read **JUnit XML**: a plain file with one entry per test, its time, and its failure message. Nearly every CI tool understands it, and turns it into a test tab, a list of failures on the merge request, or a chart of test times. pytest writes it with one option, and needs no plugin.

!!! note "Before you start"
    Read [HTML reports with pytest-html](html-reports-with-pytest-html.md). Have the [template project](index.md#templates) open.

## What you will learn

- How to write JUnit XML on every run
- What's in the file: suites, test cases, failures, skips
- How to name the suite, add logs and add your own properties
- What the file says about your computer

## Why this matters at work

When a merge request's pipeline fails, people want to see which tests failed right there, not dig through a 5,000-line job log. That view comes from JUnit XML. Most teams' pipelines already expect it. Knowing what's in it also helps when the pipeline shows "0 tests" and nobody knows why.

## The idea in plain words

!!! info "In plain words"
    The HTML report is a letter for a person. JUnit XML is a form for a machine: the same boxes in the same places, every time, so any office can process it.

## Step by step

1. **Write it on every run.** From the template's `pytest.ini`:

    ```ini
    addopts = -ra --strict-markers
        --html=reports/report.html --self-contained-html
        --junitxml=reports/junit.xml
    ```

    At the end of each run pytest says where it wrote it: `- generated xml file: .../reports/junit.xml -`.

2. **Read the file.** A run of `tests/test_pages.py` with `--runxfail`, so one test fails (the `timestamp` and `hostname` values are shortened to `...`, see step 6):

    ```xml
    <?xml version="1.0" encoding="utf-8"?><testsuites name="pytest tests"><testsuite name="pytest" errors="0" failures="1" skipped="0" tests="2" time="6.703" timestamp="..." hostname="..."><testcase classname="tests.test_pages" name="test_cart_page_shows_the_total" time="1.225" /><testcase classname="tests.test_pages" name="test_remove_updates_the_cart_count" time="5.357"><failure message="AssertionError: Locator expected to have text '1'&#10;Actual value: 3 &#10;Call log:...
    ```

    | Part | Means |
    | --- | --- |
    | `<testsuite ... failures="1" tests="2">` | The totals for the run |
    | `<testcase classname="tests.test_pages" name="...">` | One test: its file as `classname`, its name, its time in seconds |
    | `<failure message="...">` | The error message; the full traceback follows inside it |
    | `<skipped type="pytest.xfail" ...>` | In a normal run, the known bug is reported as skipped, with its reason |

    A passing test is just an empty `<testcase ... />`.

3. **Name the suite.** Every run's suite is called `pytest` unless you name it. With several suites in one pipeline (API, UI), give each a name in its `pytest.ini`:

    ```ini
    junit_suite_name = shop-api
    ```

    The file then starts `<testsuite name="shop-api" ...>`.

4. **Add the logs.** With `junit_logging = all`, each test case also gets its captured logs and output:

    ```xml
    <system-out>--------------------------------- Captured Log ---------------------------------
    20:05:23 INFO    tests: ---- tests/test_tmp_junit.py::test_with_property
    20:05:23 INFO    tests: Testing the shop at http://127.0.0.1:53868
    20:05:23 INFO    shop.api: POST /api/login -&gt; 200 in 12 ms
    20:05:24 INFO    shop.api: GET /api/books?q=sql -&gt; 200 in 803 ms
    ```

    Some CI tools show it next to each failure. It makes the file bigger: use `junit_logging = system-out` or leave it off if your tool doesn't show it.

5. **Add your own properties, carefully.** `record_property` adds a name and value to a test case, for example the bug it covers:

    ```python
    def test_with_property(record_property):
        record_property("bug", "SHOP-123")
    ```

    With pytest's default format, `xunit2`, that warns:

    ```text
    PytestWarning: record_property is incompatible with junit_family 'xunit2' (use 'legacy' or 'xunit1')
    ```

    Some tools reject properties on test cases in the xunit2 format. Set `junit_family = xunit1` only if your CI tool reads those properties; otherwise leave them out.

6. **Know what the file says about your computer.** Every file has two attributes from the machine that ran the tests:

    - `hostname`: the computer's name, like `someones-laptop.local`.
    - `timestamp`: the start time, with the computer's time zone, in a form like `2026-11-16T09:30:00.000000+01:00` (here `+01:00`).

    Inside your company's pipeline that's harmless. Before you paste a JUnit file into a public issue or a forum, remove or shorten them, as on this page.

7. **Hand it to the pipeline.** Each CI tool has its own setting for "here are my JUnit files": GitLab's `artifacts:reports:junit`, Jenkins' JUnit step, Azure DevOps' Publish Test Results task. [CI/CD](../../devops-for-qa/ci-cd/index.md) sets one up.

    !!! success "Check: you should now be able to"
        Write JUnit XML on every run, read its test cases and failures, name the suite, add logs, and say what the file reveals about the computer that made it.

## When it goes wrong

- **The pipeline says "no test results found".** The path in the CI setting doesn't match where pytest wrote the file, or the job ran from another folder. Compare it with the `generated xml file` line in the job log.
- **The pipeline shows a test as skipped, but it's an expected failure.** That's how JUnit XML reports pytest's xfail: as `<skipped type="pytest.xfail">`. The reason is in the message.
- **`PytestWarning: record_property is incompatible with junit_family 'xunit2'`.** See step 5: switch to `xunit1`, or don't use properties.
- **Two jobs overwrite each other's file.** Give each job its own path, like `--junitxml=reports/junit-api.xml`.

## Common mistakes

!!! warning "Common mistakes"
    - **Only an HTML report in the pipeline.** The CI tool can't read it. Write both.
    - **Saving the file only when tests pass.** Most CI settings skip artifacts of failed jobs unless you say "always". Failed runs are the ones you need.
    - **Pasting the file publicly as it is.** It has the computer's name and time zone.

!!! failure "If you see this error"
    **`python -m pytest: error: argument --junitxml/--junit-xml: expected one argument`**
    `--junitxml` needs a path, written with `=` or after a space: `--junitxml=reports/junit.xml`.

## Try it yourself

Name the template's suite `shop-tests`, and add the captured logs to each test case. Run the tests, and find the suite name and a `Captured Log` section in `reports/junit.xml`.

??? success "Solution"
    In `pytest.ini`, under `[pytest]`:

    ```ini
    junit_suite_name = shop-tests
    junit_logging = all
    ```

    The file then starts with `<testsuite name="shop-tests"`, and each test case has a `<system-out>` with `Captured Log`.

## References

- [pytest: Creating JUnitXML format files](https://docs.pytest.org/en/stable/how-to/output.html#creating-junitxml-format-files)
- [pytest: Configuration options (junit_*)](https://docs.pytest.org/en/stable/reference/reference.html#confval-junit_family)
- [GitLab: Unit test reports](https://docs.gitlab.com/ci/testing/unit_test_reports/)
- [Jenkins: JUnit plugin](https://plugins.jenkins.io/junit/)

Written for Python 3.13 and pytest 9. Outputs captured November 2026. Links checked: November 2026.
