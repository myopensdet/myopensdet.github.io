---
title: "What Not to Automate: A Checklist and a Payback Calculator"
description: "How to decide whether a check should be automated, kept manual, or moved to a lower test level, with an automation checklist and a small Python calculator that shows how long an automated test takes to pay back."
level: Beginner
tags:
  - Test planning
  - Templates
nav_title: "What not to automate"
order: 50
summary: "Decide what to automate, what to keep manual, and how long automation takes to pay back."
updated: "2026-11-22"
---

# What Not to Automate: A Checklist and a Payback Calculator

Automation is the core of an SDET's job, which is exactly why you need to know when *not* to automate. An automated test costs time to write and time to keep working. If it runs rarely, checks something a human eye does better, or tests a feature that changes every week, it costs more than it saves. This lesson gives you a checklist and a small calculator, so the decision is quick and easy to explain.

!!! note "Before you start"
    It helps to have read [Choosing the right level](../test-levels/choosing-the-right-level.md).
    The calculator needs only Python. Run the commands from the `templates` folder.

## What you will learn

- What makes a check a good or a bad candidate for automation
- How to work out the payback time with `automation_roi.py`
- When to move a check to a lower level instead
- How to explain "we won't automate this" to your team

## Why this matters at work

Teams that "automate everything" end up with slow, flaky suites that nobody trusts, and spend their days fixing tests instead of finding bugs. Teams that automate the right things have a fast suite that catches real problems. The difference is decisions like the ones in this lesson.

## The idea in plain words

!!! info "In plain words"
    A dishwasher is great for the plates you use every day. You don't buy one to wash a single vase once a year, and you don't put your grandmother's painted teacup in it.
    Automate the everyday plates. Wash the vase and the teacup by hand.

## Step by step

1. **Go through the checklist.** For each check you might automate, answer the questions in the [automation checklist](index.md#templates):

    ```markdown
    --8<-- "modules/think_like_a_tester/test_strategy_and_planning/templates/automation_roi_checklist.md"
    ```

    Part A is about whether it *can* be automated well. Any "no" there means wait or keep it manual, however useful it would be.

2. **Work out the payback.** The refund rules are checked by hand before every release and on many pull requests: about 30 minutes, 20 times a month. Automating them takes about 16 hours, and keeping them working about 2 hours a month:

    ```bash
    python automation_roi.py --manual-minutes 30 --runs-per-month 20 --build-hours 16 --upkeep-hours 2
    ```

    ```text
    Manual time saved per month:  10.0 hours
    Upkeep per month:              2.0 hours
    Net saving per month:          8.0 hours
    Building it takes:            16.0 hours
    Pays back after:               2.0 months
    Pays back fast. Worth automating, if the checklist agrees.
    ```

    The checklist agrees too: stable rules, exact results, money involved. Automate it.

3. **Try one that doesn't pay back.** Checking that long Bengali item names look right on the refund page: 5 minutes, about twice a month. An automated screenshot comparison would take 6 hours to build and about an hour a month to keep up, because small design changes break it:

    ```bash
    python automation_roi.py --manual-minutes 5 --runs-per-month 2 --build-hours 6 --upkeep-hours 1
    ```

    ```text
    Manual time saved per month:   0.2 hours
    Upkeep per month:              1.0 hours
    Net saving per month:         -0.8 hours
    Building it takes:             6.0 hours
    Never pays back on time alone: keeping it working costs more than it saves.
    ```

    And the checklist says "needs a human eye". Keep it manual, as a short [exploratory charter](../test-design/exploratory-testing.md).

4. **Watch for the slow ones.** A 20-minute check run twice a month, that takes 24 hours to automate:

    ```bash
    python automation_roi.py --manual-minutes 20 --runs-per-month 2 --build-hours 24 --upkeep-hours 0.5
    ```

    ```text
    Manual time saved per month:   0.7 hours
    Upkeep per month:              0.5 hours
    Net saving per month:          0.2 hours
    Building it takes:            24.0 hours
    Pays back after:             144.0 months
    Takes over a year to pay back. Probably keep it manual, or test it at a lower level.
    ```

    Twelve years. But before you give up, ask: why does it take 24 hours? Often it's because it's a UI test for something a unit or API test could check in an hour. Moving down a level changes the numbers completely.

5. **Remember what the numbers leave out.** Time isn't the only reason to automate. A check that protects money, runs at 3 in the morning, or is too boring for a person to do carefully can be worth it even with a slow payback. That's why the calculator's verdict says "if the checklist agrees".

6. **Write the decision in the plan.** One line, with the reason, in the approach table: "Bengali layout: manual, needs a human eye, doesn't pay back." Then nobody asks again next sprint.

    !!! success "Check: you should now be able to"
        Use the checklist and the calculator to decide whether to automate a check, and explain the decision in one line.

## When it goes wrong

- **Your manager wants "100% automation".** Ask what they want it for: faster releases, fewer bugs, less manual work? Then show the payback for a few checks. Most people care about the goal, not the number.
- **You don't know the numbers.** Guess them, and say they're guesses. Even rough numbers show whether payback is two months or ten years. That difference rarely depends on precision.
- **A test you automated keeps breaking.** Count the upkeep honestly for a month, and run the calculator again with the real number. If it doesn't pay back any more, move it to a lower level or delete it (with the team's agreement).
- **Everything feels too hard to automate.** The problem may be the app, not the tests: no test data API, no stable IDs on buttons. Write those down as requests to the developers. They make every future test cheaper.

## Common mistakes

!!! warning "Common mistakes"
    - **Automating a feature that changes every week.** Wait until it settles.
    - **Forgetting upkeep.** A test costs time every month, not just once.
    - **Automating at the UI level by default.** Check whether a lower level can do it first.

!!! failure "If you see this error"
    **`error: the following arguments are required: --upkeep-hours`**
    The calculator needs all four numbers. If you don't know the upkeep, start with a guess like `--upkeep-hours 1`, and write down that it's a guess.

## Try it yourself

A check takes 15 minutes by hand and runs on every pull request, about 60 times a month. Automating it takes 10 hours, and upkeep is about 1 hour a month. Work out the payback, then run the calculator to check.

??? success "Solution"
    Saved: 15 × 60 = 900 minutes = 15 hours a month. Net: 15 − 1 = 14 hours a month. Payback: 10 ÷ 14 ≈ 0.7 months, under three weeks.

    ```bash
    python automation_roi.py --manual-minutes 15 --runs-per-month 60 --build-hours 10 --upkeep-hours 1
    ```

    The calculator says "Pays back fast". Checks that run on every pull request almost always do.

## References

- [Martin Fowler: The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [ISTQB Certified Tester Advanced Level Test Automation Engineering v2.0](https://istqb.org/certifications/certified-tester-advanced-level-test-automation-engineering-ctal-tae-v2-0/)
- [Python argparse](https://docs.python.org/3/library/argparse.html)

Written for Python 3.13. Links checked: November 2026.
