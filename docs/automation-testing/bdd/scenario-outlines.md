---
title: "Scenario Outlines and Examples Tables in behave and pytest-bdd"
description: "Run one Gherkin scenario with every row of an Examples table: placeholders, how behave and pytest-bdd name each row, and what a misspelt column does in each tool."
level: Intermediate
tags:
  - BDD
  - Test data
nav_title: "Scenario outlines"
order: 40
summary: "One scenario, one run per row of an Examples table."
updated: "2026-11-22"
---

# Scenario Outlines and Examples Tables in behave and pytest-bdd

Some rules need the same scenario with different numbers: 2 copies, 3 copies, 10 copies. A **Scenario Outline** writes the scenario once, with `<placeholders>`, and an **Examples** table gives one row per run. It's [data-driven testing](../data-driven/index.md) inside a feature file, in a form the business can read and add rows to.

!!! note "Before you start"
    Read [step definitions](step-definitions.md).

## What you will learn

- How `<placeholders>` and the `Examples:` table work
- How each tool names and reports each row
- What happens when a placeholder and a column don't match

## Why this matters at work

Price tables, limits and rules with many cases are where business people know the edges best. An Examples table lets them check the edges and add a row, without touching code.

## The idea in plain words

!!! info "In plain words"
    A form letter: "Dear `<name>`, your order of `<copies>` books costs `<total>`." The table is the mailing list. One letter goes out per row.

## Step by step

1. **Read the outline.** From `features/cart.feature`:

    ```gherkin
    Scenario Outline: Several copies of one book
      When I add <copies> copies of "<book>"
      Then the cart total is <total>

      Examples:
        | copies | book               | total  |
        | 2      | Python for Testers | 49.98  |
        | 3      | SQL in a Week      | 58.50  |
        | 10     | SQL in a Week      | 195.00 |
    ```

    Before each run, every `<copies>` is replaced by that row's value. The step `When I add 2 copies of "Python for Testers"` then matches the normal step definition. Nothing special is needed in the code.

2. **See how each tool reports the rows.**

    === "behave"

        ```text
          Scenario Outline: Several copies of one book -- @1.1   # features/cart.feature:26
            Given an empty cart                                  # features/steps/shop_steps.py:9
            When I add 2 copies of "Python for Testers"          # features/steps/shop_steps.py:14
            Then the cart total is 49.98                         # features/steps/shop_steps.py:27

          Scenario Outline: Several copies of one book -- @1.2   # features/cart.feature:27
            Given an empty cart                                  # features/steps/shop_steps.py:9
            When I add 3 copies of "SQL in a Week"               # features/steps/shop_steps.py:14
            Then the cart total is 58.50                         # features/steps/shop_steps.py:27
        ```

        `@1.2` means table 1, row 2. The line number points at the row in the feature file.

    === "pytest-bdd"

        ```text
        tests/test_shop.py::test_several_copies_of_one_book[2-Python for Testers-49.98] PASSED [ 66%]
        tests/test_shop.py::test_several_copies_of_one_book[3-SQL in a Week-58.50] PASSED [ 77%]
        tests/test_shop.py::test_several_copies_of_one_book[10-SQL in a Week-195.00] PASSED [ 88%]
        ```

        Each row is its own pytest test, named by its values. `-k "58.50"` runs one row.

3. **Choose the rows.** Same rule as any data-driven test: the edges. Here 10 is the largest allowed amount. 11 is outside the rule, so it's its own scenario, "More than 10 copies is refused", because the behaviour is different: a message, and no change to the total.

    !!! success "Check: you should now be able to"
        Write a Scenario Outline with an Examples table, and find a failing row in each tool's report.

## When it goes wrong

- **A column is misspelt.** The table says `copy`, the step says `<copies>`. The placeholder isn't replaced, so the step text keeps `<copies>`, and no step matches:

    === "behave"

        ```text
        Errored scenarios:
          features/cart.feature:26  Several copies of one book -- @1.1
          features/cart.feature:27  Several copies of one book -- @1.2
          features/cart.feature:28  Several copies of one book -- @1.3
        ```

    === "pytest-bdd"

        ```text
        E   pytest_bdd.exceptions.StepDefinitionNotFoundError: Step definition is not found: When "I add <copies> copies of "Python for Testers"". Line 21 in scenario "Several copies of one book" in the feature ".../features/cart.feature"
        ```

    The pytest-bdd message shows the step text with `<copies>` still in it. That's the clue.

- **Every row fails the same way.** The step or the driver is wrong, not the table.
- **One row fails.** Work its value out by hand. Either the row or the app is wrong, and the product owner decides which.

## Common mistakes

!!! warning "Common mistakes"
    - **Rows with different behaviour in one table.** Refused amounts, errors and successes need different `Then` steps. Give each behaviour its own scenario.
    - **Fifty rows of the same kind.** A few edges say more. Long tables belong in a data file.
    - **Placeholders in the scenario's name only.** They must be in the steps to change anything.

!!! failure "If you see this error"
    **A step with `<something>` still in its text**
    The column name and the placeholder don't match. They must be spelt the same, including case.

## Try it yourself

Add a row: 1 copy of "SQL in a Week". What's the total? Does "1 copies" read badly, and does it matter?

??? success "Solution"
    ```gherkin
    | 1      | SQL in a Week      | 19.50  |
    ```

    The step text becomes `I add 1 copies of "SQL in a Week"`. It still matches the "copies" pattern, so it runs. It reads a bit oddly; that's the price of a table. The single-book case already has its own scenario with "1 copy".

## Quick check

1. What happens to `<copies>` before a row runs?

    ??? question "Answer"
        It's replaced by that row's value from the `copies` column.

2. Why is "11 copies" its own scenario, not a row?

    ??? question "Answer"
        Its behaviour is different: a message, and no change. Different behaviour, different scenario.

## References

- [Cucumber: Scenario Outline](https://cucumber.io/docs/gherkin/reference/#scenario-outline)
- [behave: Scenario Outlines](https://behave.readthedocs.io/en/latest/tutorial/#scenario-outlines)
- [pytest-bdd: Scenario outlines](https://pytest-bdd.readthedocs.io/en/stable/#scenario-outlines)

Written for behave 1.3 and pytest-bdd 9.0. Outputs captured November 2026. Links checked: November 2026.
