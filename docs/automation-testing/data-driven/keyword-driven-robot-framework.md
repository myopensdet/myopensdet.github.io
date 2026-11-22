---
title: "Keyword-Driven Testing With Robot Framework"
description: "Tests as readable steps: write keywords in Python, then build tests from them in Robot Framework. Data-driven tests with Test Template, keyword-driven tests anyone can read, and known bugs with --skiponfailure."
level: Intermediate
tags:
  - Robot Framework
  - Test data
  - Python
nav_title: "Keyword-driven: Robot Framework"
order: 60
summary: "Tests as readable steps, with the code behind them in Python."
updated: "2026-11-22"
---

# Keyword-Driven Testing With Robot Framework

In keyword-driven testing, a test is a list of steps written in plain words: "Start an order of 30.00", "Apply coupon SAVE10", "Total should be 25.65". Each step is a **keyword**. Engineers write the keywords once in code; anyone on the team can read, review and write tests from them. **Robot Framework** is the best-known tool for this, and it runs the same data-driven rows you've seen with pytest.

!!! note "Before you start"
    Read [one test, many rows](one-test-many-rows.md). The template needs `robotframework` (in its `requirements.txt`).

## What you will learn

- How Python methods become Robot Framework keywords
- A data-driven suite with `Test Template`
- A keyword-driven suite, and a keyword built from other keywords
- How to run it, read the results, and mark a known bug

## Why this matters at work

Many companies use Robot Framework, especially where testers, business analysts and developers share one test suite. It also pays off when the people who know the rules best don't write Python: they can read every test, and often write new ones from existing keywords.

## The idea in plain words

!!! info "In plain words"
    A recipe card says "whisk two eggs" and "fold in the flour". It doesn't explain how to whisk. Somebody taught that once. Keywords are the "whisk" and "fold"; the Python code is the lesson behind them.

## Step by step

1. **Write keywords in Python.** `robot/ShopKeywords.py`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/robot/ShopKeywords.py"
    ```

    Each method is a keyword: `total_should_be` becomes `Total Should Be`. The type hints matter: Robot Framework turns the text `30.00` into a `Decimal` and `18` into an `int` before calling the method. `ROBOT_LIBRARY_SCOPE = "TEST"` gives each test a fresh object, so one test's order never leaks into the next.

2. **Data-driven: one keyword, many rows.** `robot/signup_rules.robot`:

    ```robotframework
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/robot/signup_rules.robot"
    ```

    `Test Template` says which keyword every test calls. Each test is one row: its name, then the keyword's arguments. `${EMPTY}` is an empty value. "Exactly 18" carries the tag `known-bug`.

3. **Keyword-driven: steps anyone can read.** `robot/checkout.robot`:

    ```robotframework
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/robot/checkout.robot"
    ```

    The first two tests are steps from Python keywords. The third uses a keyword made in Robot Framework itself, from other keywords, with its arguments inside its name.

4. **Run it.** From the template folder:

    ```bash
    robot --pythonpath . --outputdir results --skiponfailure known-bug robot
    ```

    ```text
    ==============================================================================
    Robot
    ==============================================================================
    Robot.Checkout :: Keyword-driven: each test is a list of steps anyone on th...
    ==============================================================================
    Member With A Coupon Pays The Lowest Price                            | PASS |
    ------------------------------------------------------------------------------
    Welcome Coupon Needs A Subtotal Of 20                                 | PASS |
    ------------------------------------------------------------------------------
    Welcome Coupon At Exactly 20                                          | PASS |
    ------------------------------------------------------------------------------
    Robot.Checkout :: Keyword-driven: each test is a list of steps any... | PASS |
    3 tests, 3 passed, 0 failed
    ==============================================================================
    Robot.Signup Rules :: Data-driven: one keyword, one row of data per test. T...
    ==============================================================================
    Valid adult                                                           | PASS |
    ------------------------------------------------------------------------------
    Exactly 18                                                            | SKIP |
    Failed test skipped using 'known-bug' tag.

    Original failure:
    Expected problems '', got 'age'
    ------------------------------------------------------------------------------
    One day under 18                                                      | PASS |
    ------------------------------------------------------------------------------
    Password 7 characters                                                 | PASS |
    ------------------------------------------------------------------------------
    Password 8 characters                                                 | PASS |
    ------------------------------------------------------------------------------
    Email without @                                                       | PASS |
    ------------------------------------------------------------------------------
    Everything wrong                                                      | PASS |
    ------------------------------------------------------------------------------
    Robot.Signup Rules :: Data-driven: one keyword, one row of data pe... | PASS |
    7 tests, 6 passed, 0 failed, 1 skipped
    ==============================================================================
    Robot                                                                 | PASS |
    10 tests, 9 passed, 0 failed, 1 skipped
    ==============================================================================
    ```

    - `--pythonpath .` lets `ShopKeywords.py` import the code under test from the template folder.
    - `--outputdir results` puts `output.xml`, `log.html` and `report.html` in `results/`. Open `log.html` in a browser to see every keyword each test ran. `results/` is in `.gitignore`.
    - `--skiponfailure known-bug` turns a failure in a test tagged `known-bug` into a skip, and keeps the original failure in the report. Without it, the run fails: `7 tests, 6 passed, 1 failed`, and `robot` exits with 1.

    !!! success "Check: you should now be able to"
        Write Python keywords, build data-driven and keyword-driven tests from them, run them, and mark a known bug.

## When it goes wrong

- **`Importing library '.../robot/ShopKeywords.py' failed: ModuleNotFoundError: No module named 'app'`, then `No keyword with name 'Start An Order Of' found.`** Robot couldn't import the library, so none of its keywords exist. Run from the template folder with `--pythonpath .`.
- **`No keyword with name '...' found.` and the library imported fine.** A typo in the step, or the method is missing. Keyword names ignore case and spaces, so `total should be` works, but `Total Must Be` doesn't.
- **A comparison fails with `Expected total 85.50, got 85.50`.** The method has no type hint, so it got the text `"85.50"`, and text is never equal to a number. Add `: Decimal`.

## Common mistakes

!!! warning "Common mistakes"
    - **Logic in `.robot` files.** Loops and `IF` blocks in Robot Framework are hard to read and test. Put logic in Python keywords; keep `.robot` files as steps.
    - **Keywords named after code, like `Call Order Total Api`.** Name them after what the user or business does: `Apply Coupon`.
    - **Committing `results/`.** Reports are made on every run. Keep them out of git; in a pipeline, save them as build artifacts.

!!! failure "If you see this error"
    **`[ ERROR ] Suite 'Empty' contains no tests or tasks.`**
    The suite is named after the folder you gave, here `empty`. That folder has no `.robot` files, or the tests have a typo in `*** Test Cases ***`. Check the folder name, and that the section header has three stars on both sides.

## Try it yourself

Add a keyword-driven test: an order of 100.00 with SAVE10 for a member should cost 85.50.

??? success "Solution"
    In `robot/checkout.robot`, under `*** Test Cases ***`:

    ```robotframework
    Big Member Order With A Coupon
        Start An Order Of    100.00
        Apply Coupon    SAVE10
        Customer Is A Member
        Total Should Be    85.50
    ```

    100 × 0.90 = 90, × 0.95 = 85.50. The combined keyword has no member step, so it suits non-members: `Order Of 100.00 With SAVE10 Should Cost 90.00`.

## References

- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Robot Framework: Creating test libraries](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#creating-test-libraries)
- [Robot Framework: Test templates](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#test-templates)

Written for Python 3.13 and Robot Framework 7.5. Outputs captured November 2026. Links checked: November 2026.
