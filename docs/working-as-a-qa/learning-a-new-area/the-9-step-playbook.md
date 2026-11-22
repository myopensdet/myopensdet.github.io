---
title: "The 9-Step Playbook for Testing Something New"
description: "The nine steps every topic on this site follows: understand the ask, picture the system, learn just enough, get something running, decide what to test, plan, build, report and keep learning."
level: Beginner
tags:
  - Test planning
nav_title: "The 9-step playbook"
order: 20
summary: "The nine steps every topic on this site follows, and why they come in that order."
updated: "2026-11-22"
---

# The 9-Step Playbook for Testing Something New

When a task is new, there are two easy ways to waste a week. One is to jump straight into writing tests before you understand anything. The other is to read and read and never start. This lesson gives you nine steps that steer between the two, and explains why they come in this order.

!!! note "Before you start"
    Read [How to approach a task you have never done](how-to-approach-a-new-task.md) first. It covers the first hour.
    A **playbook** is a list of steps a team follows every time, so nobody has to invent the plan again.

## What you will learn

- The nine steps, in order
- What you should have in your hands at the end of each step
- Why the order matters
- Roughly how long each step takes

## Why this matters at work

A fixed set of steps does two things for you. It keeps you moving when you feel lost, because there is always a "next step". And it makes your work easy for your lead to follow: they can see where you are, and help at the right moment. Every topic on this site uses these nine steps, so you will see them again and again.

## The idea in plain words

!!! info "In plain words"
    Think of cooking a recipe you have never made. You read what the dish is, check what is in the fridge, read the recipe once, and taste as you go.
    You don't cook the whole meal and only taste it at the end. Testing works the same way: small steps, checked as you go.

```mermaid
flowchart LR
    s1["1. Understand<br/>the ask"] --> s2["2. Picture<br/>the system"] --> s3["3. Learn<br/>just enough"]
    s3 --> s4["4. Get something<br/>running"] --> s5["5. Decide<br/>what to test"] --> s6["6. Write a<br/>one-page plan"]
    s6 --> s7["7. Build in<br/>small steps"] --> s8["8. Report and<br/>get feedback"] --> s9["9. Keep<br/>learning"]
```

## Step by step

Here is a simple rule that makes the steps work: **each step ends with something you can show.** If you can't show it, the step isn't finished yet.

| Step | What you do | What you have at the end | Usual time |
| --- | --- | --- | --- |
| 1. Understand the ask | Ask your lead what, why, "done", deadline, where | Written answers | 15 to 30 minutes |
| 2. Picture the system | Draw the parts and where the data goes | A simple diagram | 30 minutes |
| 3. Learn just enough | Read the official docs for this task only | Notes and links | 30 to 60 minutes |
| 4. Get something running | Try the feature once, by hand | One real result | Under 1 hour |
| 5. Decide what to test | List test ideas, sort them by risk | A risk list | 1 hour |
| 6. Write a one-page plan | Fill in the plan template, share it | A plan your lead has seen | 1 hour |
| 7. Build in small steps | Smoke test, happy path, negative cases, edge cases | Running tests | Most of the task |
| 8. Report and get feedback | Share results, bugs and open risks | A short summary | 30 minutes |
| 9. Keep learning | Write a learning log entry, pick what to read next | A log | 5 minutes a day |

Treat the times as a rough guide, not a rule. A big task takes longer. A small one might finish steps 1 to 6 in one morning.

### Why this order?

Each step makes the next one cheaper:

- **Ask before you read.** The answers tell you what to read, so you read less.
- **Draw before you test.** The drawing shows you where things can break.
- **Try before you plan.** One real result keeps your plan honest. Plans written without ever touching the feature are often wrong.
- **Plan before you build.** Your lead can fix a wrong idea in five minutes. A wrong test suite takes days to fix.
- **Small steps before big ones.** If the smoke test fails, there is no point running 50 other tests.

### Step 7, a little closer

Four words come up in every topic. They are worth learning now:

- **Smoke test:** the quickest check that the feature works at all. For password reset: asking for a code gives 202.
- **Happy path:** the normal way a user uses the feature, with good data. Ask for a code, use it, log in with the new password.
- **Negative test:** a test with bad input that should be refused. A wrong code gives `INVALID_CODE`.
- **Edge case:** a test right at a limit. A code used at exactly 10 minutes.

!!! success "Check: you should now be able to"
    Name the nine steps in order, and say what you have at the end of each one.

## When it goes wrong

Real tasks don't always follow the plan. Here is what to do when a step stalls:

- **Step 1 stalls: your lead is too busy to answer.** Write your best guess of each answer, send it, and say "I'll go with this unless you tell me otherwise by Wednesday." Most leads reply fast to that.
- **Step 4 stalls: you can't get the feature working.** Don't skip ahead to planning. A plan for something you have never seen work is a guess. Ask for help (see [When to ask for help](when-to-ask-for-help.md)).
- **Step 7 stalls: the tests keep failing for strange reasons.** Go back to the smoke test. If even that fails, the problem is the environment, not your tests.
- **The ask changes halfway.** It happens. Go back to step 1 for the changed part only, update your plan, and tell your lead what moved.

## Common mistakes

!!! warning "Common mistakes"
    - **Skipping step 6 because the task is small.** Even a five-line plan in a chat message counts.
    - **Doing step 7 all at once.** Run each test as soon as you write it. Ten tests written blind fail in ten confusing ways.
    - **Treating step 9 as optional.** A five-minute log entry is how a new area slowly becomes your strength.

!!! failure "If you see this error"
    **`{"error": {"code": "VALIDATION_ERROR", ... "field": "new_password", "message": "String should have at least 8 characters"}}`**
    The shop refused a weak password. If you were testing that on purpose, this is a negative test that passed: write it down as a result. It is not a problem with your setup.

## Try it yourself

Pick one step from the table. For the task "test product reviews in the shop", write what you would have at the end of that step.

??? success "Solution"
    Example for step 2, "Picture the system":

    ```mermaid
    flowchart LR
        U["User"] --> A["Shop API"]
        A --> M[("Reviews<br/>database")]
        A --> P[("Orders<br/>database")]
    ```

    The drawing makes a good question pop out: does the shop check the orders database, so only people who bought the product can review it? You would not think to ask that without the second database in the picture.

## Quick check

1. Why try the feature by hand (step 4) before writing the plan (step 6)?

    ??? question "Answer"
        One real result keeps the plan honest. You find out how the feature really works before you decide what to test.

2. What is the difference between a happy path and a negative test?

    ??? question "Answer"
        A happy path uses the feature the normal way with good data. A negative test uses bad input that the app should refuse.

3. Which step protects you from building the wrong tests for a week?

    ??? question "Answer"
        Step 6: sharing a one-page plan before you build. Your lead can correct a wrong idea in minutes.

## References

- [ISTQB Glossary](https://glossary.istqb.org/): smoke test, negative testing and other terms
- [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html): the security rules behind the password reset examples

Links checked: November 2026.
