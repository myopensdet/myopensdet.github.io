---
title: "Data-Driven Testing: One Test, Many Rows of Data"
description: "Write the check once and feed it rows of data: from pytest.mark.parametrize to a data file the whole team can read and add to. When to move test data out of the code, and how to name each case."
level: Intermediate
tags:
  - pytest
  - Test data
nav_title: "One test, many rows"
order: 10
summary: "Write the check once, then feed it rows of data."
updated: "2026-11-22"
---

# Data-Driven Testing: One Test, Many Rows of Data

Many tests are the same check with different values: this email, this password, this age, and what should happen. Data-driven testing writes **the check once**, and keeps **the values in rows**. Adding a case means adding a row, not writing a test.

!!! note "Before you start"
    Read [Parametrize](../pytest/parametrize.md). Open the [template project](index.md#templates): this lesson uses `app/shop_rules.py` and `test_data/signup_cases.csv`.

## What you will learn

- What data-driven testing is, and when it pays off
- When to keep cases in the code, and when to move them to a file
- How to give every row a name that tells you what failed
- How to mark one row as a known bug

## Why this matters at work

The product owner writes the rules: "password 8 to 64 characters, age 18 or older". The edge cases sit in a spreadsheet, a ticket, or their head. When the cases live in a data file, they can read it, check it and add to it without reading Python. The test code stays small, and nobody copies a test ten times.

## The idea in plain words

!!! info "In plain words"
    A teacher marks 30 answer sheets with one answer key. The key is the check. Each sheet is a row. A new student means one more sheet, not a new key.

## Step by step

1. **Start from the rules.** The signup form has three rules. `app/shop_rules.py` returns the fields that break one:

    ```python
    check_signup("arshad@example.com", "correct-horse-1", 30)   # []
    check_signup("not-an-email", "short", 12)                   # ['email', 'password', 'age']
    ```

2. **Write the cases as rows.** Every edge of every rule gets a row: 7 and 8 characters, 64 and 65, 17 and 18. `test_data/signup_cases.csv`:

    ```text
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/test_data/signup_cases.csv"
    ```

    - `case` names the row. It becomes the test's name.
    - `expected_problems` is what should come back, space-separated. Empty means "no problems".
    - `known_bug` marks a row that fails because of a known bug.

3. **Write the check once.** `tests/test_signup_csv.py`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/tests/test_signup_csv.py"
    ```

    `cases()` reads the file and gives pytest one case per row. The [next lesson](csv-json-yaml-data.md) shows how.

4. **Run it.**

    ```bash
    python -m pytest tests/test_signup_csv.py -v
    ```

    ```text
    tests/test_signup_csv.py::test_signup_rules[valid adult] PASSED          [  9%]
    tests/test_signup_csv.py::test_signup_rules[exactly 18] XFAIL (Known...) [ 18%]
    tests/test_signup_csv.py::test_signup_rules[one day under 18] PASSED     [ 27%]
    tests/test_signup_csv.py::test_signup_rules[password 7 characters] PASSED [ 36%]
    tests/test_signup_csv.py::test_signup_rules[password 8 characters] PASSED [ 45%]
    tests/test_signup_csv.py::test_signup_rules[password 64 characters] PASSED [ 54%]
    tests/test_signup_csv.py::test_signup_rules[password 65 characters] PASSED [ 63%]
    tests/test_signup_csv.py::test_signup_rules[email without @] PASSED      [ 72%]
    tests/test_signup_csv.py::test_signup_rules[email without a dot after @] PASSED [ 81%]
    tests/test_signup_csv.py::test_signup_rules[email with two @] PASSED     [ 90%]
    tests/test_signup_csv.py::test_signup_rules[everything wrong] PASSED     [100%]
    XFAIL tests/test_signup_csv.py::test_signup_rules[exactly 18] - Known bug AGE-18
    ======================== 10 passed, 1 xfailed in 0.02s =========================
    ```

    One function, 11 tests, each named after its row. The row "exactly 18" found the bug planted in the template: the code says `age <= 18` where the rule says 18 is fine. The bug is reported as AGE-18, and the row says so. When it's fixed, the row passes, strict xfail turns that into a failure, and you remove `AGE-18` from the file.

5. **Choose where the cases live.**

    | Keep the cases | When |
    | --- | --- |
    | In the code, with `@pytest.mark.parametrize` | a few cases, only developers read them |
    | In a data file | many cases, or someone who doesn't read Python owns them |
    | Made by code ([factories](test-data-factories.md), [Faker](fake-data-with-faker.md)) | the exact values don't matter, only that they're valid |

    !!! success "Check: you should now be able to"
        Turn a list of rules into rows, write one test that checks every row, and name each row so a failure says what broke.

## When it goes wrong

- **The failure says `test_signup_rules[row3]`.** The rows have no names. Give every row a `case` value: "exactly 18" tells you what broke without opening the file.
- **A new row isn't run.** Check the file you edited is the one the test reads, and that the row isn't a `#` comment line.
- **Every row fails the same way.** The check is wrong, not the data. Fix the test function, not 11 rows.

## Common mistakes

!!! warning "Common mistakes"
    - **An `if` in the test for some rows.** Two kinds of rows means two tests, each with its own data.
    - **Expected values worked out with the same code you're testing.** Write them by hand, from the rule.
    - **Only happy rows.** The value of a data file is the edges: just under, exactly on, just over.

!!! failure "If you see this error"
    **`[XPASS(strict)] Known bug AGE-18`**
    The bug is fixed. Remove `AGE-18` from the `known_bug` column, and the row becomes a normal test again.

## Try it yourself

The product owner adds a rule: age must be 120 or less. Add the rows you need.

??? success "Solution"
    Two rows, one each side of the edge:

    ```text
    age 120,old@example.com,correct-horse-1,120,,
    age 121,old@example.com,correct-horse-1,121,age,
    ```

    The second fails until the developers add the rule: that's the test doing its job.

## Quick check

1. Why does every row have a `case` name?

    ??? question "Answer"
        It becomes the test's name, so a failure says which case broke.

2. When should cases move from the code to a file?

    ??? question "Answer"
        When there are many, or when someone who doesn't read Python owns them.

## References

- [pytest: How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest: pytest.param](https://docs.pytest.org/en/stable/reference/reference.html#pytest-param)

Written for Python 3.13 and pytest 9.2. Outputs captured November 2026. Links checked: November 2026.
