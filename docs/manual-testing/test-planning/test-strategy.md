---
title: "Test Strategy: One Page That Says How Your Team Tests"
description: "What a test strategy is, how it differs from a test plan, the seven sections of a one-page team strategy, and a filled example for a small online shop."
level: Beginner
tags:
  - Test planning
  - Templates
nav_title: "Test strategy"
order: 10
summary: "One page that says how your team tests, every time."
updated: "2026-11-22"
---

# Test Strategy: One Page That Says How Your Team Tests

A **test strategy** is the team's agreement on how testing works, for every feature: which tests exist at which level, who writes them, what gets automated, and what "ready to release" means. It changes rarely. A **test plan** is written for one feature or release, and follows the strategy. This lesson builds a one-page strategy, section by section.

!!! note "Before you start"
    It helps to have read [Test levels and the pyramid](../test-levels/index.md).
    You don't need to install anything for this lesson.

## What you will learn

- The difference between a test strategy and a test plan
- The seven sections of a one-page strategy
- How to write one when your team doesn't have one
- How to keep it short and true

## Why this matters at work

Without a strategy, every feature starts with the same arguments: "do we need UI tests for this?", "who writes the API tests?", "can we release with a major bug open?". A strategy settles those once. New people read one page and know how the team works.

## The idea in plain words

!!! info "In plain words"
    A football team has a way of playing: how they defend, who takes the free kicks. That's the strategy. Before each match, the coach makes a plan for that opponent. The plan changes every week. The way of playing doesn't.

## Step by step

1. **Know which document you're writing.**

    | | Test strategy | Test plan |
    | --- | --- | --- |
    | Covers | The whole team or product | One feature or release |
    | Changes | Rarely, every few months | For every feature |
    | Answers | How do we test, always? | What will we test this time, and how deeply? |
    | Length | One page | One or two pages |

2. **Write what you protect most.** Two or three things that must never break, in the users' words. Everything else in the strategy serves these:

    ```markdown
    - Customers can pay, and are charged the right amount, once.
    - Refunds go to the right place, once.
    ```

3. **Fill the levels table.** For each level, say what it checks, who writes it, which tools, and when it runs. This is the most useful part, because it answers "who tests this?" before anyone asks.

4. **Say what you automate, and what you don't.** One line each. "Automate everything" isn't a strategy. Name what stays manual, and why: looks, email wording, one-off checks. The [what not to automate](what-not-to-automate.md) lesson helps.

5. **Add environments, data and bugs.** Where tests run, what data they use (never real customers), and where bugs go. Link the [severity guide](../bug-reports/severity-and-priority.md) instead of copying it.

6. **Set the default exit criteria.** The release bar for every feature. A test plan can raise it, but not lower it without a written reason. See [entry and exit criteria](entry-and-exit-criteria.md).

7. **Put a review date on it.** A strategy that's two years old describes a team that no longer exists. Here is the finished example for the shop:

    ```markdown
    --8<-- "modules/think_like_a_tester/test_strategy_and_planning/examples/shop_test_strategy.md"
    ```

    !!! success "Check: you should now be able to"
        Explain how a strategy differs from a plan, and write the seven sections of a one-page strategy for your team.

## When it goes wrong

- **Your team has no strategy.** Don't ask for permission to write a big document. Write the one page from what the team already does, share it, and ask "is this right?". People correct a draft much faster than they write one.
- **The strategy says one thing, and the team does another.** Believe the team, then talk. Either the strategy is out of date (update it), or the team skipped something on purpose (write down why).
- **It keeps growing.** Move details into the test plans or linked pages. If the strategy is longer than one or two pages, nobody reads it.
- **Different products need different rules.** Write one short strategy per product, or one strategy with a small table of differences.

## Common mistakes

!!! warning "Common mistakes"
    - **Copying a 40-page template from the internet.** Write what your team really does.
    - **No owner.** Someone's name goes on it, or nobody updates it.
    - **Mixing strategy and plan.** Feature details belong in the plan.

!!! failure "If you see this error"
    **"We don't need a strategy, we're agile."**
    A strategy isn't a heavy process. It's one page that saves the same argument every sprint. Offer to write it in an hour, and to review it in the next retrospective.

## Try it yourself

Your team writes unit tests, but nobody writes API or UI tests, and releases often break the login page. Write the "What we protect most" section and one row of the levels table that would help.

??? success "Solution"
    ```markdown
    ## 1. What we protect most
    - Customers can log in and log out, on phone and laptop.

    | Level | What it checks | Who writes it | Tools | Runs when |
    | --- | --- | --- | --- | --- |
    | UI (end to end) | Log in, log out, wrong password | SDET | Playwright | Every pull request |
    ```

    One journey, checked automatically on every change, is usually enough to stop that kind of break.

## References

- [ISTQB Glossary: test strategy, test plan](https://glossary.istqb.org/)
- [ISTQB Certified Tester Foundation Level v4.0](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): chapter 5

Links checked: November 2026.
