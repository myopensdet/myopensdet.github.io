---
title: "Anatomy of a Test Case: The Parts That Make It Clear and Repeatable"
description: "The parts of a good test case: ID, title, covers, preconditions, test data, steps and expected result, a bad test case rewritten step by step, and the same case as an automated pytest test."
level: Beginner
tags:
  - Test design
  - Templates
nav_title: "Anatomy of a test case"
order: 10
summary: "The parts of a good test case, and a vague one rewritten until anyone can run it."
updated: "2026-11-22"
---

# Anatomy of a Test Case: The Parts That Make It Clear and Repeatable

Most bad test cases aren't wrong. They're just unclear: "Test refund. Should work." Two people run that and do different things, and both say it passed. This lesson takes the parts of a test case one by one, shows why each exists, and rewrites a vague case until anyone could run it.

!!! note "Before you start"
    It helps to know what acceptance criteria are. If not, read [Reviewing user stories](../reviews/reviewing-user-stories.md) first.
    You don't need to install anything for this lesson.

## What you will learn

- The parts of a test case, and why each one is there
- How to write an expected result nobody can argue with
- How to fix a vague test case, step by step
- How the same case looks as an automated test

## Why this matters at work

Test cases are read by more people than you think: a teammate running the release check, a developer trying to reproduce a failure, a new tester in a year. A clear case saves each of them time. A vague one gets run differently every time, which means it tells you nothing.

## The idea in plain words

!!! info "In plain words"
    A good test case is like directions to a friend's house: start here, turn left at the bakery, it is the blue door. You don't write "find the house, it should be easy".
    Each part of a test case answers one question the person running it would otherwise have to guess.

## Step by step

1. **Start from a vague case.** This is the kind you will find in many real projects:

    ```text
    Test refund
    Steps: Try to refund an old item.
    Expected: Should not work.
    ```

    Questions anyone running it would have: how old is "old"? Which item, which customer? What exactly should "not work" look like: an error, a hidden button, a crash?

2. **Give it an ID and a title that says what is checked.** The ID lets people talk about it ("TC-06 failed"). The title should read like a sentence, and say the result, not just the feature:

    | Weak title | Strong title |
    | --- | --- |
    | Test refund | Refund on day 31 is refused |
    | Refund check 2 | An item cannot be refunded twice |

    When a strong title fails in a report, you already know what broke.

3. **Say what it covers.** Write the ID of the criterion it checks: **Covers: REF-1**. That one field is what makes [traceability](traceability.md) possible, so you can answer "is every requirement tested?"

4. **Write the preconditions and the test data.** Preconditions are the state the system must be in before step 1. Test data is the exact values. Be specific enough that two people set up the same thing:

    - **Precondition:** a customer with one item delivered exactly 31 days ago, not refunded before.
    - **Test data:** delivered on 2026-10-16, test date 2026-11-16, reason "too small".

    Exact dates matter here. "An old item" might be 40 days to one person and 31 to another, and 31 is the edge that matters.

5. **Write short steps, one action each.**

    ```text
    1. Log in as the customer.
    2. Open My orders.
    3. Choose Refund on the item.
    4. Pick the reason "too small", and send.
    ```

    If a step has "and" in it twice, split it. If the case has more than about ten steps, it is probably checking several things. Split the case.

6. **Write an expected result nobody can argue with.** This is the most important line. Say exactly what should appear, and what must *not* happen:

    ```text
    Expected:
    - The message "Refunds are possible up to 30 days after delivery" is shown.
    - No refund request is saved, and no email is sent.
    ```

    Compare that with "should not work". Now a tester can't pass it by accident, and a developer can't argue about it.

7. **Put it together.** Here is the [Markdown template](index.md#templates), and the rewritten case in the [CSV](index.md#templates), as TC-06:

    ```markdown
    --8<-- "modules/think_like_a_tester/test_cases/templates/test_case.md"
    ```

8. **See the same case as an automated test.** A good manual case turns into a test almost line by line. The precondition becomes the setup, the steps become the call, and the expected result becomes the `assert`:

    ```python
    @pytest.mark.covers("REF-1")
    def test_tc06_refund_is_refused_on_day_31():
        problem = refund_problem(item(delivered_on=date(2026, 10, 16)), TODAY, "too small")
        assert problem == "Refunds are possible up to 30 days after delivery"
    ```

    The test name starts with the case ID, so a failure in the pipeline points straight at TC-06.

    !!! success "Check: you should now be able to"
        Name the parts of a test case, explain why each exists, and rewrite a vague case so anyone can run it.

## When it goes wrong

- **Your test cases are too long to keep up to date.** Long cases usually check many things. Split them, and move common setup ("log in as a customer with one delivered item") into a shared precondition you write once.
- **The expected result depends on today's date.** Write it with fixed dates in the test data, and say how to set them up, or make the dates relative: "delivered 31 days before today". Cases with real dates break silently next month.
- **People pass a case without really checking.** Make the expected result something you have to look at: exact text, an exact amount, a status. "Page looks fine" is easy to tick without looking.
- **You don't know the exact message text.** Ask, or check the design. If nobody knows, that's a finding: the message hasn't been decided, so users might see anything.

## Common mistakes

!!! warning "Common mistakes"
    - **"Works as expected" as the expected result.** Write what you expect, exactly.
    - **One test case checking five things.** When it fails, nobody knows which part broke.
    - **No test data.** "An old item" isn't data. "Delivered 2026-10-16" is.

!!! failure "If you see this error"
    **A test case "passes" for one person and "fails" for another.**
    The case is ambiguous. Compare what each person did: different data, different starting state, or a different reading of the expected result. Fix the case so only one reading is possible, then run it again.

## Try it yourself

Rewrite this case so anyone can run it: "Login test. Enter wrong password a few times. Account should be locked."

??? success "Solution"
    ```text
    TC-21: Account is locked after 3 wrong passwords
    Covers: AUTH-4
    Precondition: an active account, user@example.com, with no failed logins today.
    Test data: wrong password "wrong-1"
    Steps:
    1. Open the login page.
    2. Log in as user@example.com with "wrong-1". Repeat 3 times.
    3. Log in with the correct password.
    Expected:
    - After the 3rd try: "Your account is locked. Check your email to unlock it."
    - Step 3 is refused with the same message.
    - One "account locked" email arrives.
    ```

    Notice how "a few times" became 3. If you don't know the real number, that's a question for the product owner, not a guess.

## Quick check

1. What is the most important part of a test case?

    ??? question "Answer"
        The expected result: exactly what should happen, and what must not.

2. Why put the requirement ID in the Covers field?

    ??? question "Answer"
        So you can check that every requirement has a test, and see which rule failed when a test fails.

3. A case has 18 steps. What should you do?

    ??? question "Answer"
        It is probably checking several things. Split it into smaller cases, each with one check.

## References

- [ISTQB Glossary: test case, precondition, expected result](https://glossary.istqb.org/)

Links checked: November 2026.
