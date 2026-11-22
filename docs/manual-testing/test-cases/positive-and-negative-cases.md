---
title: "Positive and Negative Test Cases: Test What Works and What Must Be Refused"
description: "How to write positive and negative test cases for every acceptance criterion, why negative cases find more serious bugs, and a full set of automated refund tests in pytest."
level: Beginner
tags:
  - Test design
  - pytest
nav_title: "Positive and negative cases"
order: 20
summary: "For every rule, test what must work and what must be refused."
updated: "2026-11-22"
---

# Positive and Negative Test Cases: Test What Works and What Must Be Refused

A **positive** test case checks that something works when it should: a refund within 30 days goes through. A **negative** test case checks that something is refused when it should be: a refund on day 31 doesn't. Beginners write mostly positive cases, because that's how stories are written. But the serious bugs, like money paid out twice or a door left open, usually live on the negative side.

!!! note "Before you start"
    Read [Anatomy of a test case](anatomy-of-a-test-case.md) first. [Boundary values](../test-design/boundary-values.md) helps for the limits.
    To run the examples: `pip install pytest`, then run the commands from the `examples` folder.

## What you will learn

- What positive and negative cases are
- How to find the negative cases for any criterion
- Why negative cases often matter more
- A full set of automated refund tests, both kinds

## Why this matters at work

A feature that works for the happy customer and fails open for everyone else is a security and money problem. "Can a customer refund an item twice?" is a negative case. If nobody writes it, the first person to find out might be someone looking for free money.

## The idea in plain words

!!! info "In plain words"
    Testing a door lock: the positive test is "the right key opens it". The negative tests are "the wrong key doesn't", "no key doesn't", and "kicking it doesn't".
    A lock that passes only the positive test isn't a lock.

## Step by step

1. **List the criteria.** From the reviewed refund story:

    ```text
    --8<-- "modules/think_like_a_tester/test_cases/examples/refund_requirements.txt"
    ```

2. **Write the positive case for each.** The positive case is usually what the criterion already says. REF-1: "an item delivered 15 days ago can be refunded."

3. **Find the negative cases with three questions.** For each criterion, ask:

    - **What is just outside the limit?** REF-1 allows 30 days. Day 31 must be refused.
    - **What has already happened?** REF-2: an item already refunded must be refused.
    - **What doesn't meet the condition?** REF-4: a sale item that isn't faulty must be refused.

    Here's the full list for refunds:

    | Criterion | Positive | Negative |
    | --- | --- | --- |
    | REF-1 30 days | Day 15 allowed, day 30 allowed | Day 31 refused |
    | REF-2 Once only | (first refund works: in REF-1) | Second refund refused |
    | REF-4 Sale items | Faulty sale item allowed | Not-faulty sale item refused |
    | REF-5 Where money goes | Card and PayPal to same account; gift card to credit | (none: every payment has a destination) |
    | REF-6 Expired card | (none: this rule is itself the "failure" case) | Expired card gets store credit |
    | REF-7 Not delivered | (none) | Not delivered refused, link to Cancel order |

    Some criteria have no natural negative case, and some *are* the negative case. That's fine. The point is to ask the question every time.

4. **Write them as automated tests.** Here are the refund rules:

    ```python
    --8<-- "modules/think_like_a_tester/test_cases/examples/refunds.py"
    ```

    And the test cases, positive first, then negative. Each test name starts with its case ID, and each is marked with the criterion it covers:

    ```python
    --8<-- "modules/think_like_a_tester/test_cases/examples/tests/test_refunds.py"
    ```

    ```bash
    python -m pytest -q
    ```

    ```text
    11 passed in 0.02s
    ```

    Ten test cases, eleven tests: TC-04 runs twice, for card and PayPal, with `parametrize`.

5. **Check negative cases check the right reason.** Look at the negative tests: each one checks the exact message, not just "something was refused". That matters. If TC-06 only checked "a problem was returned", it would still pass if the item was refused for the wrong reason, like "already refunded". Checking the reason proves the right rule did the refusing.

6. **Watch the balance.** In this set, 5 cases are positive and 5 negative. There's no rule for the right mix, but if you see 20 positive cases and 1 negative, the negative side has been forgotten. A quick count is a useful habit.

    !!! success "Check: you should now be able to"
        Write a positive and a negative case for a criterion, using the three questions, and explain why a negative test should check the reason.

## When it goes wrong

- **The story only describes success.** Most stories do. Use the three questions anyway, and send the answers to the product owner as a check: "I'm testing that day 31 is refused. Right?"
- **You don't know what the error should say.** Write the case with "an error is shown" for now, add a question, and update the expected result when you have the answer. Don't leave it vague for good.
- **A negative case finds that nothing is refused.** That's a real bug, often a serious one. Report it straight away with the exact steps. If it involves money or someone else's data, tell your lead too, not only the bug tracker.
- **The team says negative cases are "edge cases" for later.** Show them the most expensive one: "a customer can refund the same item twice". Money leaving the company usually moves it up the list.

## Common mistakes

!!! warning "Common mistakes"
    - **Only positive cases.** The story's text guides you there. Ask the three questions on purpose.
    - **Negative tests that don't check the reason.** Refused for the wrong reason is still a bug.
    - **Calling negative cases "error tests" and skipping them when short of time.** They are often the most important ones.

!!! failure "If you see this error"
    **`ModuleNotFoundError: No module named 'refunds'`**
    Run pytest from the `examples` folder (the one with `refunds.py` in it), and use `python -m pytest`, which adds the current folder to the places Python looks.

## Try it yourself

A coupon rule: "The code WELCOME5 gives $5 off a first order of $20 or more." Write two positive and three negative cases.

??? success "Solution"
    Positive:

    - First order of $20.00 with WELCOME5: $5 off (at the edge).
    - First order of $35.00 with WELCOME5: $5 off.

    Negative:

    - First order of $19.99 with WELCOME5: refused, with a message about the $20 minimum.
    - Second order with WELCOME5: refused, "only for your first order".
    - The code used on two first orders at the same time, in two tabs: only one gets the discount.

    The last one is the kind of negative case that finds real money bugs.

## Quick check

1. What is a negative test case?

    ??? question "Answer"
        One that checks the app refuses something it must refuse, like a refund on day 31.

2. What are the three questions for finding negative cases?

    ??? question "Answer"
        What is just outside the limit? What has already happened? What doesn't meet the condition?

3. Why should a negative test check the exact reason?

    ??? question "Answer"
        To prove the right rule did the refusing. Refused for the wrong reason is still a bug.

## References

- [ISTQB Glossary: negative testing](https://glossary.istqb.org/)
- [pytest: How to parametrize tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
