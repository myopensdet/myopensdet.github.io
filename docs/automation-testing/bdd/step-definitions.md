---
title: "Step Definitions in behave and pytest-bdd"
description: "Connect each Gherkin step to Python code, in behave and in pytest-bdd side by side: matching step text with parse patterns, passing values, sharing state, and keeping steps thin with a driver."
level: Intermediate
tags:
  - BDD
  - Python
nav_title: "Step definitions"
order: 30
summary: "Connect each Gherkin step to Python, in both tools."
updated: "2026-11-22"
---

# Step Definitions in behave and pytest-bdd

A feature file is only words until each step is connected to code. A **step definition** is a Python function with a pattern: when a step's text matches the pattern, the function runs, with the values from the text as arguments. behave and pytest-bdd do this almost the same way. The big difference is **how a step reaches the app**: behave passes a `context` object, pytest-bdd uses fixtures.

!!! note "Before you start"
    Read [Gherkin and feature files](gherkin-and-feature-files.md). Have the [template project](index.md#templates) open.

## What you will learn

- How a step pattern matches a step and pulls out values
- The same steps in behave and in pytest-bdd
- Why steps stay thin, and the work goes in a driver

## Why this matters at work

Step definitions are where BDD suites become hard to keep up: hundreds of steps, many nearly the same, with app details in each. A few general steps that call one driver stay small, and the same steps can test the API and the web page.

## The idea in plain words

!!! info "In plain words"
    The feature file is the menu. Step definitions are the kitchen: each dish on the menu has one recipe. "I add 2 copies of …" matches the recipe "I add {copies} copies of …", with 2 as the amount.

## Step by step

1. **Read the steps in both tools.**

    === "behave"

        `features/steps/shop_steps.py`:

        ```python
        --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/features/steps/shop_steps.py"
        ```

        - behave finds steps in `features/steps/` by itself.
        - Every step gets `context`: one object shared by the steps, the hooks and the whole scenario. `context.shop` is the driver the hooks put there.

    === "pytest-bdd"

        `tests/test_shop.py`:

        ```python
        --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/tests/test_shop.py"
        ```

        - `scenarios(".")` turns every scenario in `features/` into a pytest test. `bdd_features_base_dir = features` in `pytest.ini` says where that is.
        - Steps ask for fixtures by name, like any pytest test: `shop` comes from `tests/conftest.py`.
        - Patterns need `parsers.parse(...)` to pull out values. A plain string must match the step exactly.

2. **Read a pattern.** `'I add {copies:d} copies of "{book}"'` matches `I add 2 copies of "Python for Testers"`:

    - `{book}` takes any text, here `Python for Testers`.
    - `{copies:d}` takes a whole number and turns it into an `int`. Without `:d` it would be the text `"2"`.
    - The words around them must match exactly.

    Both tools use the [parse](https://github.com/r1chardj0n3s/parse) library for this, so the patterns are the same.

3. **Stack patterns for the same action.** "1 copy" and "2 copies" read naturally, so the function has both patterns. It also has both `@given` and `@when`: the `Background` uses `And I add …` after a `Given`, the scenarios use `When I add …`. Each tool looks up a step by its keyword, so one function needs both.

4. **Keep steps thin.** Every step is one or two lines: it calls the driver, or checks what the driver returns. The driver knows URLs, JSON and buttons. That's why the same steps run on both targets (see [BDD for API and UI](bdd-for-api-and-ui.md)).

5. **Run each tool.**

    === "behave"

        ```bash
        behave --format=progress
        ```

        ```text
        USING RUNNER: behave.runner:Runner
        features/cart.feature  ......
        features/coupons.feature  ..

        2 features passed, 0 failed, 0 skipped
        8 scenarios passed, 0 failed, 1 skipped
        30 steps passed, 0 failed, 6 skipped
        ```

    === "pytest-bdd"

        ```bash
        python -m pytest -v
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
        ========================= 8 passed, 1 xfailed in 0.48s =========================
        ```

    The same 9 scenarios. The one scenario that isn't a pass is the planted bug, handled by each tool its own way: see [tags and hooks](tags-and-hooks.md).

    !!! success "Check: you should now be able to"
        Write a step definition with a pattern in both tools, pull typed values out of the step text, and keep the step thin.

## When it goes wrong

- **A step in the feature file has no definition.** A typo, "basket" instead of "cart":

    === "behave"

        ```text
        You can implement step definitions for undefined steps with these snippets:
        @then(u'the basket total is 24.99')
        def step_impl(context):
            raise StepNotImplementedError(u'Then the basket total is 24.99')
        ```

        The scenario counts as an error, and behave prints a starting point for the missing step.

    === "pytest-bdd"

        ```text
        E   pytest_bdd.exceptions.StepDefinitionNotFoundError: Step definition is not found: Then "the basket total is 24.99". Line 13 in scenario "One book" in the feature ".../features/cart.feature"
        ```

- **A step exists, but only for the other keyword.** With the `@given` patterns removed from `step_add_book`, behave can't run `And I add 2 copies of "Python for Testers"` in the `Background`, which follows a `Given`:

    ```text
    @given(u'I add 2 copies of "Python for Testers"')
    ```

    Add the missing decorator to the same function.

- **behave says `ConfigError: No steps directory in '.../features'`.** You ran it from the wrong folder. Run `behave` from the folder that holds `features/`.

## Common mistakes

!!! warning "Common mistakes"
    - **A step for every wording.** "I add a book", "I put a book in", "a book is added": pick one wording, and use it everywhere.
    - **App details in steps.** URLs, JSON keys and button names belong in the driver.
    - **Forgetting `:d`.** The value arrives as text, and `"2" * price` fails or does the wrong thing.

!!! failure "If you see this error"
    **`behave.step_registry.AmbiguousStep: @then('the cart total is 0.00') has already been defined in`** (then the place of the other step)
    Two step patterns match the same text, for example `the cart total is {amount}` and `the cart total is 0.00`. Remove the specific one, or reword it.

## Try it yourself

Add a step, in both tools, for `Then the cart is empty`, using the total as the check.

??? success "Solution"
    === "behave"

        ```python
        @then("the cart is empty")
        def step_cart_is_empty(context):
            assert context.shop.total() == Decimal("0.00")
        ```

    === "pytest-bdd"

        ```python
        @then("the cart is empty")
        def cart_is_empty(shop):
            assert shop.total() == Decimal("0.00")
        ```

    No `parsers.parse` is needed in pytest-bdd: the text has no values in it.

## Quick check

1. What does `{copies:d}` do?

    ??? question "Answer"
        Matches a whole number, and passes it to the function as an `int`.

2. How does a step reach the app in each tool?

    ??? question "Answer"
        behave: through `context`. pytest-bdd: through fixtures.

## References

- [behave: Python step implementations](https://behave.readthedocs.io/en/latest/tutorial/#python-step-implementations)
- [pytest-bdd documentation](https://pytest-bdd.readthedocs.io/en/stable/)
- [parse: pattern format](https://github.com/r1chardj0n3s/parse#format-specification)

Written for Python 3.13, behave 1.3 and pytest-bdd 9.0. Outputs captured November 2026. Links checked: November 2026.
