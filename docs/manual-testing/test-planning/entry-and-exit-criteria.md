---
title: "Entry and Exit Criteria: When Testing Can Start, and When It's Done"
description: "What entry and exit criteria are, how to write ones you can check, how to keep exit criteria in a file and check them with a small Python script, and what to do when one isn't met on release day."
level: Beginner
tags:
  - Test planning
  - Releases
nav_title: "Entry and exit criteria"
order: 40
summary: "When testing can start, and when it's done, written so you can check them."
updated: "2026-11-22"
---

# Entry and Exit Criteria: When Testing Can Start, and When It's Done

**Entry criteria** say what must be true before testing starts: the story is reviewed, the build is deployed, the test data exists. **Exit criteria** say what must be true before testing is done: no failing tests, no open critical bugs, every requirement tested. Both are agreed before testing begins. That's the point: "done" is decided while nobody is under pressure.

!!! note "Before you start"
    Read [Test plan](test-plan.md) and [Risk-based testing](risk-based-testing.md) first.
    The script needs Python 3.11 or newer. Run the commands from the `examples` folder.

## What you will learn

- What entry and exit criteria are, and why they're agreed early
- How to write criteria you can check, not just feel
- How to keep exit criteria in a file and check them with `exit_check.py`
- What to do when a criterion isn't met on release day

## Why this matters at work

Without entry criteria, you start testing a build that isn't ready, and spend two days reporting bugs that are really "not deployed yet". Without exit criteria, testing ends when the time ends, and "is it ready?" becomes a feeling. Clear criteria turn release day into a short, calm check.

## The idea in plain words

!!! info "In plain words"
    A pilot doesn't take off until the checklist is done: fuel, doors, flaps. That's the entry check. And a plane doesn't "arrive" until it's parked at the gate with the engines off. That's the exit check.
    Nobody decides those rules during the flight.

## Step by step

1. **Write entry criteria as a short checklist.** Things you can see are true or not:

    ```markdown
    - [x] The story has been reviewed, and open questions have answers
    - [x] The build is on staging, and its version is known
    - [x] Test accounts with delivered, sale and undelivered orders are ready
    - [x] The payment sandbox accepts refunds to card, PayPal and gift card
    ```

    If one isn't true, say so the same day: "I can't start refund testing: the payment sandbox isn't set up. Who can help?" A blocked start, said early, protects the release date.

2. **Write exit criteria as numbers with limits.** "Quality is good" can't be checked. "No more than 0 open critical bugs" can. Every line should be something you can count:

    ```toml
    --8<-- "modules/think_like_a_tester/test_strategy_and_planning/templates/exit_criteria.toml"
    ```

    The numbers come from tools you already have: the pytest result, the bug tracker, the [traceability report](../test-cases/traceability.md) and the [risk list](risk-based-testing.md).

3. **Agree them before testing starts.** Put them in the plan, and get them reviewed with the plan. Criteria chosen on the last day always fit the results, which means they check nothing.

4. **Collect the results.** On the release build, write down each number:

    ```toml
    --8<-- "modules/think_like_a_tester/test_strategy_and_planning/examples/refund_results.toml"
    ```

5. **Run the exit check.** The [exit checker](index.md#templates) compares the two files:

    ```bash
    python exit_check.py refund_exit_criteria.toml refund_results.toml
    ```

    ```text
    met      failed_tests: 0 (at most 0)
    met      open_critical_bugs: 0 (at most 0)
    NOT MET  open_major_bugs: 1 (at most 0)
    met      requirements_without_tests: 0 (at most 0)
    met      deep_risks_not_tested: 0 (at most 0)

    1 exit criterion not met. Don't sign off yet, or agree an exception in writing.
    ```

    It ends with exit code 1, so it can also stop a pipeline. If a result is missing from the file, it says `MISSING` and counts it as not met: no number, no sign-off.

6. **Decide what to do with a "not met".** There are only three honest options:

    - **Fix it.** The refund button in Safari gets fixed, you verify it, the number becomes 0, and the check passes.
    - **Release with a written exception.** The team agrees, in writing, to release with this bug, and why: "Safari users are 2% of refunds, and support will refund them by hand until 2.4.1."
    - **Move the date.** If neither is acceptable.

    Lowering the limit to 1 so the check passes is not one of the options. That's choosing the criteria after seeing the results.

    !!! success "Check: you should now be able to"
        Write entry and exit criteria you can check, run `exit_check.py`, and name the three honest options when a criterion isn't met.

## When it goes wrong

- **Entry criteria are never met, and testing starts anyway.** Then write down what was missing, and add it to the test summary. If it keeps happening, bring the list to the retrospective: "4 of the last 5 builds came without test data."
- **The team always grants exceptions.** Then the criteria are wrong, or the dates are. Look at which criterion keeps failing, and talk about that one.
- **Someone asks you alone to "just sign it off".** Don't. Share the exit check output with the team and the product owner. The release decision is theirs, and the facts are yours.
- **`tomllib` is not found.** You're on Python older than 3.11. Upgrade, or install the `tomli` package and change the import.

## Common mistakes

!!! warning "Common mistakes"
    - **Criteria you can't count.** "Good enough" isn't a criterion.
    - **Setting them on the last day.** They will fit whatever happened.
    - **Treating exit criteria as the tester's decision.** You check them. The team decides what to do.

!!! failure "If you see this error"
    **`tomllib.TOMLDecodeError: Expected '=' after a key`**
    A line in the TOML file isn't `name = number`. Often it's a note written without `#` in front. Put `#` before every comment, and make sure each line has one name, one `=` and one number.

## Try it yourself

Rewrite these as exit criteria you can check: "Testing is complete. Most bugs are fixed. Performance is acceptable."

??? success "Solution"
    ```toml
    [exit]
    failed_tests = 0
    open_critical_bugs = 0
    open_major_bugs = 0
    requirements_without_tests = 0
    slow_pages = 0          # pages slower than 2 seconds, from the performance test
    ```

    "Complete" became counts. "Most bugs" became a limit per severity. "Acceptable" became a number from a test, with the limit written down.

## References

- [ISTQB Glossary: entry criteria, exit criteria](https://glossary.istqb.org/)
- [ISTQB Certified Tester Foundation Level v4.0](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): section 5.1
- [Python tomllib](https://docs.python.org/3/library/tomllib.html)

Written for Python 3.13. Links checked: November 2026.
