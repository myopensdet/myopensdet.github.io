---
title: "What Makes a Great Bug Report: Each Part, With a Real Rewrite"
description: "The parts of a bug report developers can act on: title, summary, steps, expected and actual results, environment and evidence, with a vague report rewritten step by step and checked by a script."
level: Beginner
tags:
  - Bug reports
  - Templates
nav_title: "What makes a great bug report"
order: 10
summary: "Each part of a report developers can act on, and a vague one rewritten."
updated: "2026-11-22"
---

# What Makes a Great Bug Report: Each Part, With a Real Rewrite

A great bug report answers every question a developer would ask before they ask it. What's wrong? How do I see it? What should happen instead? Where did you see it? How bad is it? This lesson goes through each part, using a real bug: the sign-up rule that refuses Bengali names.

!!! note "Before you start"
    It helps to have read [Error guessing](../test-design/error-guessing.md), where this bug was found.
    The checker script needs only Python. Run the commands from the `examples` folder.

## What you will learn

- The parts of a bug report, and the question each one answers
- How to write a title that explains the bug on its own
- How to write steps someone else can follow
- How to check a report with a script before you send it

## Why this matters at work

Developers judge testers by their bug reports more than by anything else. A clear report gets fixed fast and builds trust. A vague one wastes everyone's time and teaches people to ignore your reports. The good news: it is a skill you can learn in a week, with a template.

## The idea in plain words

!!! info "In plain words"
    A good bug report is like a good recipe in reverse. A recipe says "do these steps, and you get this cake". A bug report says "do these steps, and you get this broken cake, instead of the right one".
    If someone else follows your steps and gets the same broken cake, your report did its job.

## Step by step

1. **Start from the vague report.**

    ```markdown
    --8<-- "modules/think_like_a_tester/bug_reports/examples/bug_before.md"
    ```

    Read it as the developer. Which Bengali name? What error, exactly? On which version? Is it only Bengali? How many users does it affect? Every one of those is a message back to you, and a delay.

2. **Write steps someone else can follow.** Numbered, one action each, starting from a place anyone can reach. Include the exact input:

    ```markdown
    1. Open the sign-up form on the test environment.
    2. Enter the username "আরশাদ" and age 30.
    3. Press "Create account".
    ```

    Then try your own steps once more, exactly as written. If you needed a step you didn't write down, add it.

3. **Write the expected result, and where it comes from.** "It works" isn't an expected result. Say what should happen, and why you expect it: the story, the spec, or how it worked before. If the rule is unclear, say so. That's useful information, not a weakness:

    ```markdown
    The account is created. The rule says "letters and numbers only".
    "আরশাদ" is made of Bengali letters, and accented Latin letters like
    "é" are already accepted, so Bengali names should be too.
    ```

4. **Write the actual result, copied exactly.** Paste the message. Don't summarise it:

    ```markdown
    The form shows "Username can only use letters and numbers", and no
    account is created. The same steps with "José" create the account.
    ```

    The second sentence is a **comparison**: the same steps with one small change give a different result. It is often the most useful line in a report, because it points straight at the cause.

5. **Add the environment.** Version, where you ran it, browser or client, and which test data. "Works on my machine" arguments are almost always about something in this section. Never paste real customer data, real passwords or tokens. Use test accounts.

6. **Add evidence.** A screenshot, a short screen recording, log lines, or the request and response. If you found the cause, add it, but keep it separate from the facts: "Cause found: Python's `str.isalnum()` returns False for the Bengali vowel sign 'া'". The developer can check it in a minute.

7. **Write the title last.** Now you know exactly what the bug is. A good title says **what is wrong, where, and when**, and makes sense on its own in a list of fifty bugs:

    | Weak | Strong |
    | --- | --- |
    | Signup broken | Sign-up refuses usernames in Bengali, but accepts accented Latin names |
    | Error on refund | Refund on day 30 is refused with "up to 30 days after delivery" |

8. **Check it before you send.** Here's the full rewrite:

    ```markdown
    --8<-- "modules/think_like_a_tester/bug_reports/examples/bug_after.md"
    ```

    Run the [checker](index.md#templates):

    ```bash
    python bug_report_check.py bug_after.md
    ```

    ```text
    Looks ready to send. Read it once more as if you were the developer.
    ```

    The checker only looks for the usual gaps: vague title, missing sections, unnumbered steps, vague results. It can't tell if the steps are *right*. That's why its last line asks you to read it once more.

    !!! success "Check: you should now be able to"
        Name the parts of a bug report, rewrite a vague one, and explain why the comparison with "José" is so useful.

## When it goes wrong

- **The bug only happens sometimes.** Say so, with a number: "3 times out of 10". Add the times it happened and anything that was different. Flaky bugs need more evidence, not less.
- **The steps are long because setup is long.** Put the setup in a "Before you start" line ("a customer with one delivered order"), and keep the numbered steps for the part that shows the bug.
- **You found several bugs at once.** One report each, linked to each other. A report with three bugs gets one fixed and two forgotten.
- **You're not allowed to share the data that causes it.** Make test data with the same shape (same length, same characters, same kind of account), and check it still shows the bug. Then report with that.

## Common mistakes

!!! warning "Common mistakes"
    - **Describing instead of copying.** "Some error" instead of the exact message.
    - **Skipping the expected result.** The developer then has to guess what "right" looks like.
    - **Blaming.** "Someone broke sign-up again" helps nobody. Facts only.

!!! failure "If you see this error"
    **The bug is closed as "can't reproduce".**
    Don't argue. Run your own steps again from a clean start, on the version in the report. If it happens, add what was missing (data, settings, a step) and reopen with "reproduced again, added step 2". If it doesn't, the bug may be fixed or depend on something you didn't notice. Say that too.

## Try it yourself

Rewrite this report: "Checkout is slow. Please fix ASAP!!!"

??? success "Solution"
    One good rewrite:

    ```text
    Title: Checkout takes 8 to 12 seconds to show the order summary on staging

    Steps:
    1. Log in as test customer test-buyer-1 on staging.
    2. Add 3 items to the cart.
    3. Press "Checkout".

    Expected: the order summary appears within 2 seconds (story CHK-4).
    Actual: it appears after 8 to 12 seconds, 5 tries out of 5.
    The /api/cart/totals request takes most of that time (screenshot of
    the browser's network tab attached).

    Environment: staging, build 2.3.1, Chrome 141, Windows 11
    Severity: major, because slow checkout loses sales
    ```

    "ASAP!!!" became a severity with a reason, and "slow" became a number compared with the story's limit.

## References

- [Simon Tatham: How to Report Bugs Effectively](https://www.chiark.greenend.org.uk/~sgtatham/bugs.html)
- [ISTQB Glossary: defect report](https://glossary.istqb.org/)

Links checked: November 2026.
