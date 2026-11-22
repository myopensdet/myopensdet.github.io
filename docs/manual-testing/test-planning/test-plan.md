---
title: "Test Plan: Plan One Feature's Testing, With a Full Example"
description: "What goes into a feature test plan: scope, scored risks, approach, entry and exit criteria, who does what, and open questions, with a complete test plan for a refund feature."
level: Beginner
tags:
  - Test planning
  - Templates
nav_title: "Test plan"
order: 20
summary: "Plan one feature's testing: scope, risks, approach, and when it's done."
updated: "2026-11-22"
---

# Test Plan: Plan One Feature's Testing, With a Full Example

A **test plan** says what you will test for one feature or release, in what order, how, by whom, and when you'll call it done. It's short, it's reviewed, and it changes when the feature changes. This lesson writes the plan for the refund feature, section by section.

!!! note "Before you start"
    Read [Test strategy](test-strategy.md) first. If you haven't yet, the [one-page plan](../../working-as-a-qa/learning-a-new-area/index.md#templates) from the first topic is a lighter version of the same idea.
    You don't need to install anything for this lesson.

## What you will learn

- The ten sections of a feature test plan, and what each is for
- How to write scope so nobody is surprised
- How to turn risks into an approach table
- How to get a plan reviewed

## Why this matters at work

A plan is how the team sees your testing before it happens. The developer spots a risk you missed. The product owner says "partial refunds aren't in this release". Each of those comments, made on day one, saves a surprise on release day.

## The idea in plain words

!!! info "In plain words"
    Before a trip, you write: where we're going, what we're not doing this time, what could go wrong, what to pack, and when we'll be home.
    A test plan is the same list, for one feature.

## Step by step

1. **Write what and why, in two sentences.** What changes, and what would hurt if it broke:

    ```markdown
    Customers can now ask for a refund themselves, from My orders. If it breaks,
    money goes out twice or to the wrong place, or customers flood support.
    ```

2. **Write the scope, with reasons.** The "out of scope" column matters most. Each line there is a decision someone might disagree with, so write why:

    | In scope | Out of scope (and why) |
    | --- | --- |
    | The refund rules REF-1 to REF-7 | Partial refunds (not in this release) |
    | Approval and refusal emails | The payment provider itself (tested by them; we test our calls to it) |

3. **Paste the scored risks.** Run the [risk scorer](risk-based-testing.md) and paste its table. It sets the order of everything that follows.

4. **Write the approach, one row per risk or rule.** For each one: which technique, which level, and whether it's automated. Say why when the answer is "no":

    | What | How | Level | Automated? |
    | --- | --- | --- | --- |
    | REF-1 day limit | Boundary values: days 0, 30, 31 | Unit | Yes |
    | REF-3 emails | Check the email arrives and says the right thing | Manual | No: wording needs a human eye |

5. **Add entry and exit criteria.** When you can start, and when you're done. The [entry and exit criteria](entry-and-exit-criteria.md) lesson covers both.

6. **Say who does what, by when.** A small table. If a task has no name next to it, it won't happen.

7. **List open questions.** Anything you still need answered, and who you asked. A plan with open questions is honest. A plan that hides them isn't finished.

8. **Get it reviewed.** Send it to the lead, the developer and the product owner with one line: "This is how I'll test refunds. What did I miss?" Here is the finished plan:

    ```markdown
    --8<-- "modules/think_like_a_tester/test_strategy_and_planning/examples/refund_test_plan.md"
    ```

    The risk table in this plan is the real output of `risk_score.py`. This topic's tests check that the two stay the same.

    !!! success "Check: you should now be able to"
        Write a test plan for a feature with scope, risks, approach, entry and exit criteria, and get it reviewed.

## When it goes wrong

- **Nobody reads the plan.** It's probably too long. Cut it to what someone needs to agree with: scope, risks, approach, exit criteria. Ask for review in a 15-minute call instead of by email.
- **The feature changes halfway.** Update the plan the same day, and say what changed at the top: "Updated: partial refunds added, see REF-8." An old plan is worse than none, because people trust it.
- **You don't know who will do what.** Write the tasks anyway, with "?" for the name, and ask in the review. Empty names are the fastest way to find gaps in a team.
- **The release date moves closer.** Don't squeeze everything. Drop the light risks first, write that down in the plan, and tell the team. That's what the risk order is for.

## Common mistakes

!!! warning "Common mistakes"
    - **Leaving out "out of scope".** Then everyone assumes something different.
    - **An approach that lists tools, not checks.** "pytest and Playwright" says nothing. "Boundary values on days 0, 30, 31" says what you'll do.
    - **Writing the plan after testing.** Then it's a report, not a plan.

!!! failure "If you see this error"
    **"Why didn't you test X?" after the release.**
    Check the plan. If X is in "out of scope" with a reason, point to it calmly: that was agreed. If it isn't in the plan at all, add a line to your own checklist for next time, and add X to the risk list now.

## Try it yourself

The product owner adds one line to the refund story two days before release: "Customers can also refund from the order email." What do you change in the plan?

??? success "Solution"
    - Scope: add "Refund link in the order email" to in scope.
    - Risks: add "The email link opens someone else's order" (likelihood 2, impact 3, score 6, deep) and score it with the others.
    - Approach: add a row, for example "Email link: open with a different logged-in customer, expect a refusal. API and manual. Automated: the API part."
    - Who and when: someone's name, by when.
    - At the top: "Updated: email refund link added." And tell the team the plan changed.

## References

- [ISTQB Glossary: test plan](https://glossary.istqb.org/)
- [ISTQB Certified Tester Foundation Level v4.0](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): chapter 5

Links checked: November 2026.
