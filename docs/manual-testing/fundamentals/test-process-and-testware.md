---
title: "The Test Process and Testware: Seven Activities, Explained Simply"
description: "The seven activities of the test process from the ISTQB Foundation syllabus, from planning to completion, and the testware each one produces, shown with a password reset task."
level: Beginner
tags:
  - Test planning
nav_title: "The test process and testware"
order: 50
summary: "The seven test activities, and what each one leaves behind."
updated: "2026-11-22"
---

# The Test Process and Testware: Seven Activities, Explained Simply

This lesson explains the seven activities that make up testing, and the things each one produces. Those things are called **testware**.

!!! note "Before you start"
    Read [The seven testing principles](seven-testing-principles.md) first.
    It helps to know the [9-step playbook](../../working-as-a-qa/learning-a-new-area/the-9-step-playbook.md): it is the same process, in everyday words.

## What you will learn

- The seven test activities, in order
- What testware is, with an example for each activity
- How the activities match the 9-step playbook
- Why the activities overlap and repeat

## Why this matters at work

Interviews often ask: "Walk me through how you test a feature." Teams also use these words in plans and reports: "We are in test analysis", "Exit criteria are met". Knowing the activities lets you answer clearly and follow those talks.

## The idea in plain words

!!! info "In plain words"
    Building a house has stages: plan it, design it, gather the materials, build it, check it, hand over the keys.
    Each stage leaves something behind: a drawing, a list, a finished wall. Testing has stages too, and what each stage leaves behind is testware.

```mermaid
flowchart LR
    P["1. Planning"] --> A["3. Analysis"] --> D["4. Design"]
    D --> I["5. Implementation"] --> E["6. Execution"] --> C["7. Completion"]
    M["2. Monitoring<br/>and control"] -. "watches all of them" .-> A
    M -.-> E
```

## Step by step

We use the task from the last topic: test password reset in the shop.

1. **Test planning: decide the goal and the approach.** What to test, what not to test, how, and when it is done.
    *Testware:* a test plan. For example, the [one-page test plan](../../working-as-a-qa/learning-a-new-area/index.md#templates).

2. **Test monitoring and control: check progress, and change course.** This runs the whole time. If tests find many bugs in one place, you move time there.
    *Testware:* progress notes, short status reports.

3. **Test analysis: decide what to test.** Read the story and find the things worth testing. ISTQB calls these **test conditions**. Example: "a code older than 10 minutes must not work."
    *Testware:* a list of test conditions, sorted by risk.

4. **Test design: decide how to test each condition.** Turn conditions into test cases with inputs and expected results. Example: "ask for a code, move the clock 11 minutes, use the code; expect `CODE_EXPIRED`."
    *Testware:* test cases and the test data they need.

5. **Test implementation: get everything ready to run.** Write the automated tests, prepare the data, set up the test environment.
    *Testware:* test scripts, test data files, a working test environment.

6. **Test execution: run the tests and compare the results.** Run the tests, and check every result against what you expected. Here we use the shipping tests from [What an SDET does](what-an-sdet-does.md). To rerun only the $49.99 case, type:

    ```bash
    python -m pytest test_shipping.py -v -k 499
    ```

    You should see:

    ```text
    test_shipping.py::test_free_shipping_from_50_dollars[1-499] PASSED       [ 50%]
    test_shipping.py::test_free_shipping_from_50_dollars[4999-499] PASSED    [100%]
    ======================= 2 passed, 3 deselected in 0.03s ========================
    ```

    Two tests ran, not one. `-k` picks every test whose name contains the text, and the values in square brackets are part of the name. So "499" also matched the $0.01 case. Read results with care: always check which tests really ran before you report "passed".
    Then look for what did *not* run. No test checks a coupon that takes an order from $52.00 down to $48.00. Should that order still ship free? That gap goes into the report.
    *Testware:* test results, logs and bug reports.

7. **Test completion: wrap up and learn.** Check the exit criteria, report what was and wasn't tested, save what can be reused, and note what to do better next time.
    *Testware:* a test completion report, and testware stored for the next release.

8. **See how it matches the playbook.** The activities are the same work you did in the [9-step playbook](../../working-as-a-qa/learning-a-new-area/the-9-step-playbook.md), with formal names:

    | Test activity | Playbook step |
    | --- | --- |
    | Planning | 1. Understand the ask, 6. Write a one-page plan |
    | Monitoring and control | 8. Report and get feedback (and all along the way) |
    | Analysis | 2. Picture the system, 5. Decide what to test |
    | Design | 5. Decide what to test |
    | Implementation | 4. Get something running, 7. Build in small steps |
    | Execution | 7. Build in small steps |
    | Completion | 8. Report, 9. Keep learning |

    !!! success "Check: you should now be able to"
        Name the seven activities in order, and give one piece of testware for each.

## When it goes wrong

- **There is no time for planning or analysis.** Do a small version, not none: a five-line plan in the ticket, and a list of test conditions on a sticky note. Skipping them completely is how important cases get missed.
- **The test environment is broken on execution day.** Tell your lead straight away, in writing, with the error. Then work on what you can: design more cases, or review the story. Don't wait silently.
- **Results are messy and hard to report.** Group them into three lists: passed, failed (with bug links), and not run (with the reason). Even a busy manager can read that in one minute.

## Common mistakes

!!! warning "Common mistakes"
    - **Thinking the activities happen once, in a strict line.** They overlap and repeat. In a two-week sprint you may do all seven in a few days.
    - **Thinking testware means only test code.** Plans, test cases, data, results and reports are all testware.
    - **Skipping completion.** Without a short report, the next person can't see what was tested or reuse your work.

!!! failure "If you see this error"
    **`2 passed, 3 deselected in 0.03s`, but you expected a different number of tests**
    `-k` matched more or fewer tests than you thought. Run with `-v` to see the names it picked, then change the text after `-k`. It searches test names (including the values in square brackets), not what the tests do.

## Try it yourself

For the task "test product reviews", write one piece of testware for analysis, design and execution.

??? success "Solution"
    One possible answer:

    | Activity | Testware |
    | --- | --- |
    | Analysis | Test condition: "only people who bought the book can review it" |
    | Design | Test case: log in as a user with no orders, post a review, expect an error |
    | Execution | Result: "error as expected", or a bug report if the review was saved |

## Quick check

1. What is testware?

    ??? question "Answer"
        Everything testing produces: plans, test conditions, test cases, test data, scripts, results and reports.

2. Which activity runs the whole time, alongside the others?

    ??? question "Answer"
        Test monitoring and control.

3. What is the difference between test analysis and test design?

    ??? question "Answer"
        Analysis decides what to test (test conditions). Design decides how to test it (test cases with inputs and expected results).

## References

- [ISTQB Certified Tester Foundation Level v4.0](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): section 1.4, test activities, testware and roles
- [ISTQB Glossary](https://glossary.istqb.org/): testware, test condition, exit criteria
- [pytest: Specifying which tests to run](https://docs.pytest.org/en/stable/how-to/usage.html#specifying-which-tests-to-run)

Written for pytest 9 and the ISTQB CTFL v4.0 syllabus. Links checked: November 2026.
