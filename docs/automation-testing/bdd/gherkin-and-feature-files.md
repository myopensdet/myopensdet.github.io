---
title: "Gherkin and Feature Files: Given, When, Then"
description: "Write Gherkin feature files that behave and pytest-bdd both read: Feature, description, Background, Scenario, Given/When/Then/And, and how to write scenarios about behaviour instead of clicks."
level: Intermediate
tags:
  - BDD
nav_title: "Gherkin and feature files"
order: 20
summary: "Feature, Background, Scenario, and Given, When, Then."
updated: "2026-11-22"
---

# Gherkin and Feature Files: Given, When, Then

**Gherkin** is the plain-words format BDD scenarios are written in. A **feature file** (`.feature`) holds one feature and its scenarios. behave and pytest-bdd both read the same files, so this lesson is the same for both tools. The hard part isn't the keywords. It's **writing about behaviour, not about the screen**.

!!! note "Before you start"
    Read [what is BDD](what-is-bdd.md). Open `features/cart.feature` in the [template project](index.md#templates).

## What you will learn

- The Gherkin keywords, and what each one is for
- How to share setup with `Background`
- How to write a scenario about behaviour, not clicks

## Why this matters at work

Feature files are read by people who don't code. A good scenario is one a product owner can read in ten seconds and say "yes, that's the rule". A bad one is a list of clicks that breaks every time a button moves.

## The idea in plain words

!!! info "In plain words"
    A scenario is a short story with three parts: how things are (Given), what someone does (When), and what should happen (Then). Like "Given the shop is open, when I pay, then I get a receipt."

## Step by step

1. **Read a whole feature file.** `features/cart.feature`:

    ```gherkin
    --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/features/cart.feature"
    ```

2. **Learn the keywords.**

    | Keyword | What it's for |
    | --- | --- |
    | `Feature:` | the name of the feature. One per file |
    | The lines under it | a description, for people. Often "As a…, I want…, so that…" |
    | `Background:` | steps that run before every scenario in the file |
    | `Scenario:` | one example of the behaviour |
    | `Given` | how things are before: the starting state |
    | `When` | the one thing the user does |
    | `Then` | what should happen: the check |
    | `And`, `But` | another step of the same kind as the one before |
    | `Scenario Outline:` + `Examples:` | one scenario, run with each row of a table. See [scenario outlines](scenario-outlines.md) |
    | `@smoke` | a tag. See [tags and hooks](tags-and-hooks.md) |
    | `#` | a comment, for the people editing the file |

3. **See it run.** behave prints each step next to the code that ran it:

    ```text
      @smoke
      Scenario: One book                          # features/cart.feature:11
        Given an empty cart                       # features/steps/shop_steps.py:9
        When I add 1 copy of "Python for Testers" # features/steps/shop_steps.py:14
        Then the cart total is 24.99              # features/steps/shop_steps.py:27

      Scenario: Two different books               # features/cart.feature:15
        Given an empty cart                       # features/steps/shop_steps.py:9
        When I add 1 copy of "Python for Testers" # features/steps/shop_steps.py:14
        And I add 2 copies of "SQL in a Week"     # features/steps/shop_steps.py:14
        Then the cart total is 63.99              # features/steps/shop_steps.py:27
    ```

    `Given an empty cart` came from the `Background`, and runs in every scenario.

4. **Write behaviour, not clicks.** Compare two versions of the same scenario:

    ```gherkin
    # About the screen: breaks when the page changes, and hides the rule
    Scenario: Coupon
      Given I open "/shop"
      When I select "Python for Testers" in the "Book" list
      And I type "2" into the "Copies" box
      And I click "Add to cart"
      And I type "SAVE10" into the "Coupon" box
      And I click "Apply coupon"
      Then the element "total" shows "44.98"

    # About the behaviour: the rule is plain, and it works for the API too
    Scenario: SAVE10 takes 10% off
      Given an empty cart
      And I add 2 copies of "Python for Testers"
      When I apply the coupon "SAVE10"
      Then the cart total is 44.98
    ```

    The second one is in the template, and the template runs it both through the API and through the web page. Where the buttons are belongs in code, not in the feature file.

    !!! success "Check: you should now be able to"
        Read and write a feature file with a description, a Background and scenarios, and turn a click-by-click scenario into one about behaviour.

## When it goes wrong

- **behave counts a "rule" you didn't mean to write.** A description line that starts with `Rule:` is a Gherkin keyword: it groups the scenarios under it. While writing the template, a line "Rule: one coupon use per order" did exactly that. Start description lines with other words.
- **A step with the wrong keyword can't be found.** behave and pytest-bdd look up `Given` steps and `When` steps separately. See [step definitions](step-definitions.md#when-it-goes-wrong).
- **Scenarios depend on each other.** Each scenario must start from its own `Given`. Never rely on what the scenario above left behind.

## Common mistakes

!!! warning "Common mistakes"
    - **Several `When` steps in one scenario.** One action per scenario. Two actions usually means two scenarios.
    - **Checks in `Given` or `When` steps.** Checks go in `Then`.
    - **A long `Background`.** Everything in it runs before every scenario. Keep it to what every scenario truly needs.

!!! failure "If you see this"
    **A scenario that's longer than the screen**
    It describes a whole journey. Split it into scenarios, one per behaviour, each with its own short `Given`.

## Try it yourself

Rewrite this as a scenario about behaviour:

```gherkin
Scenario: Wrong coupon
  Given I open "/shop"
  When I type "FREE" into the "Coupon" box
  And I click "Apply coupon"
  Then the element with role "status" shows "Unknown coupon: FREE"
```

??? success "Solution"
    ```gherkin
    Scenario: An unknown coupon changes nothing
      When I apply the coupon "FREE"
      Then I see the message "Unknown coupon: FREE"
      And the cart total is 49.98
    ```

    In the template's `coupons.feature`, the `Background` adds the books first. The new last line also checks the rule that matters: the total didn't change.

## References

- [Cucumber: Gherkin reference](https://cucumber.io/docs/gherkin/reference/)
- [Cucumber: Writing better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/)
- [behave: Feature testing setup](https://behave.readthedocs.io/en/latest/gherkin/)

Written for behave 1.3 and pytest-bdd 9.0. Outputs captured November 2026. Links checked: November 2026.
