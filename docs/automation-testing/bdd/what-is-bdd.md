---
title: "What Is BDD? Behaviour-Driven Development, TDD and ATDD"
description: "BDD is a way for the business, developers and testers to agree on how a feature behaves, written as examples that become tests. How it relates to TDD and ATDD, when it is worth it, and when it isn't."
level: Intermediate
tags:
  - BDD
  - Test design
nav_title: "What is BDD"
order: 10
summary: "Agree on examples first, then let them become the tests."
updated: "2026-11-22"
---

# What Is BDD? Behaviour-Driven Development, TDD and ATDD

**BDD (behaviour-driven development)** is a way of working, not a tool. Before a feature is built, the people who want it, the people who build it and the people who test it agree on **examples** of how it should behave. The examples are written in plain words (Given, When, Then), and then they become automated tests. The tools, behave and pytest-bdd, only do that last part.

!!! note "Before you start"
    Read [Test design techniques](../../manual-testing/test-design/index.md). No code in this lesson.

## What you will learn

- What BDD is, and what it's for
- How TDD, ATDD and BDD relate
- When BDD is worth it, and when it only adds work

## Why this matters at work

"Set up BDD" is a common request, and it often goes wrong: someone installs a tool, rewrites existing tests in Given/When/Then, and nobody outside the test team ever reads them. The tests got longer, nothing else changed. Knowing what BDD is for lets you set it up so it helps.

## The idea in plain words

!!! info "In plain words"
    Before building a house, the owner, the builder and the inspector walk through it on paper: "When I open the front door, I see the stairs." Each sentence they agree on becomes something the inspector checks at the end. BDD is that walk-through, for software.

## Step by step

1. **Know the three test-first ideas.**

    | Approach | Who writes the test first | What it checks | Written in |
    | --- | --- | --- | --- |
    | TDD (test-driven development) | the developer | one small piece of code | code, with pytest |
    | ATDD (acceptance test-driven development) | the team, from the acceptance criteria | a whole feature, as the user sees it | code or tables |
    | BDD (behaviour-driven development) | the team, from examples they agree on | a whole feature, as the user sees it | plain words: Given, When, Then |

    TDD is red, green, refactor: write a failing test, make it pass, tidy the code. ATDD moves the same idea up to features. BDD is ATDD with one more goal: a shared language that the business can read.

2. **See an example become a test.** The product owner says: "A coupon only works once per order." The team turns it into an example:

    ```gherkin
    Scenario: A coupon works only once
      Given an empty cart
      And I add 2 copies of "Python for Testers"
      When I apply the coupon "SAVE10"
      And I apply the coupon "SAVE10"
      Then I see the message "Coupon SAVE10 is already applied"
      And the cart total is 44.98
    ```

    This is from the template project. Run against the practice shop, it fails: the second SAVE10 takes another 10% off. Nobody had to read code to find out what "only once" means.

3. **Know what BDD gives you.**

    - **Fewer misunderstandings.** Writing the examples raises the questions early: "Once per order, or once per customer?"
    - **Living documentation.** The feature files describe what the system does today, and the run proves it.
    - **Tests the business can review.** A product owner can read a scenario and say "that's wrong".

4. **Know when it isn't worth it.** BDD costs time: a feature file, step definitions, and the conversations. It pays off when people outside the test team read and discuss the scenarios. If only engineers will ever read them, plain pytest tests are shorter and easier to change. Unit tests are almost never worth writing in Gherkin.

    !!! success "Check: you should now be able to"
        Explain BDD, TDD and ATDD in one sentence each, and say when BDD is worth setting up.

## When it goes wrong

- **Nobody outside the test team reads the feature files.** BDD has become a slow way to write tests. Bring a scenario to the next refinement meeting, or move back to plain pytest.
- **Scenarios are written after the code, by testers alone.** You get tests, not agreement. Write them before, with the product owner and a developer: see [writing scenarios with the business](writing-scenarios-with-the-business.md).
- **Scenarios full of clicks and field names.** They describe the screen, not the behaviour. See [Gherkin and feature files](gherkin-and-feature-files.md).

## Common mistakes

!!! warning "Common mistakes"
    - **"We do BDD because we use behave."** The tool is the smallest part. The conversations are BDD.
    - **Rewriting every existing test in Gherkin.** Keep Gherkin for behaviour the business cares about.
    - **One giant feature file per app.** One feature file per feature, with a few clear scenarios.

!!! failure "If you hear this"
    **"The BDD tests take longer to write than the code."**
    Check who reads them. If nobody outside engineering does, BDD isn't helping that team. Say so, and suggest plain pytest for those tests.

## Try it yourself

The product owner says: "Shoppers can't buy more than 10 copies of a book." Write it as one scenario.

??? success "Solution"
    ```gherkin
    Scenario: More than 10 copies is refused
      Given an empty cart
      When I add 11 copies of "SQL in a Week"
      Then I see the message "You can add 1 to 10 copies"
      And the cart total is 0.00
    ```

    This is the scenario in the template's `cart.feature`. Writing it raises a question for the product owner: what exactly should the message say?

## Quick check

1. Who writes the examples in BDD?

    ??? question "Answer"
        The team together: business, developers and testers.

2. What's the difference between ATDD and BDD?

    ??? question "Answer"
        BDD adds a shared, plain-words language (Given, When, Then) that the business can read.

3. When is plain pytest the better choice?

    ??? question "Answer"
        When only engineers will read the tests, for example unit tests.

## References

- [Cucumber: Behaviour-Driven Development](https://cucumber.io/docs/bdd/)
- [Dan North: Introducing BDD](https://dannorth.net/introducing-bdd/)
- [Martin Fowler: Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)
- [Martin Fowler: Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

Written for behave 1.3 and pytest-bdd 9.0. Outputs captured November 2026. Links checked: November 2026.
