---
title: "Writing BDD Scenarios With the Business: Three Amigos and Example Mapping"
description: "Run a short Three Amigos session with a product owner and a developer, use example mapping to find rules, examples and open questions, and turn them into scenarios everyone agrees on."
level: Intermediate
tags:
  - BDD
  - Teamwork
nav_title: "Writing scenarios with the business"
order: 70
summary: "Find the rules and examples together, before anyone builds."
updated: "2026-11-22"
---

# Writing BDD Scenarios With the Business: Three Amigos and Example Mapping

The scenarios are only as good as the conversation behind them. In BDD, that conversation has a name: **Three Amigos**. A product owner, a developer and a tester spend 25 minutes on one story before it's built. **Example mapping** gives that meeting a shape: rules, examples, and questions nobody can answer yet. The scenarios come out of it almost written.

!!! note "Before you start"
    Read [what is BDD](what-is-bdd.md) and [Gherkin and feature files](gherkin-and-feature-files.md).

## What you will learn

- Who comes to a Three Amigos session, and what each person brings
- How to run example mapping in 25 minutes
- How to turn the cards into scenarios, and get them reviewed

## Why this matters at work

Most bugs that reach users aren't coding mistakes. They're rules nobody agreed on: "once per order" meant "once per customer" to someone. Twenty-five minutes before building finds those, when changing them costs nothing.

## The idea in plain words

!!! info "In plain words"
    Before cooking a big dinner, the host, the cook and someone with allergies sit down for a few minutes. "No nuts. Is coconut a nut? Ask the guest." The questions you can't answer go on a list, not into the soup.

## Step by step

1. **Get the three views in one room.**

    | Who | Brings | Asks |
    | --- | --- | --- |
    | Product owner | the why, and the rules | "What problem does this solve?" |
    | Developer | how it can be built | "What about the existing coupons?" |
    | Tester | the edges and the risks | "What happens the second time?" |

    One story, 25 minutes, a timer. If it isn't clear by then, the story isn't ready.

2. **Map the examples.** Use four colours of cards (or sticky notes in an online board):

    - **Yellow: the story.** "Shoppers can use a coupon."
    - **Blue: the rules.** "SAVE10 takes 10% off." "One use per order." "Only coupons the shop knows."
    - **Green: examples under each rule.** "2 books at 24.99 with SAVE10 is 44.98." "SAVE10 twice still gives 44.98." "FREE is refused, the total stays 49.98."
    - **Red: questions.** "Can a member use SAVE10 too?" "What exactly does the message say?"

    Many red cards means the story isn't ready. Many blue cards means it's too big to build at once: split it.

3. **Turn green cards into scenarios.** Each green card is one scenario under its rule:

    ```gherkin
    --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/features/coupons.feature"
    ```

    The scenario names are the examples in plain words. The rule sits in the feature's description. Every value comes from a card the product owner agreed to.

4. **Get the scenarios reviewed.** Send the feature file to the product owner before anything is built: "Is each of these right? Is anything missing?" They read three short scenarios in a minute. Once they say yes, the scenarios are the acceptance criteria.

5. **Keep them alive.** When a rule changes, the scenario changes first, in the same review as the code. When a bug is found, add the scenario that would have caught it, like "A coupon works only once" above.

    !!! success "Check: you should now be able to"
        Run a short example mapping session, and turn its rules and examples into scenarios the product owner has agreed to.

## When it goes wrong

- **The product owner says "just test everything".** Ask for one example instead: "If I buy two books with SAVE10, what do I pay?" Examples are easier to answer than rules.
- **The session goes over time arguing about one rule.** Write a red card, and move on. Someone takes the question away and comes back with an answer.
- **The developer has already built it.** Map the examples anyway. Any example the code gets wrong is a bug found before release.

## Common mistakes

!!! warning "Common mistakes"
    - **The tester writes every scenario alone, after the sprint.** That's test writing, not BDD.
    - **Scenarios as UI scripts.** The product owner can't review clicks. Write the behaviour.
    - **Leaving red cards unanswered.** An open question becomes a guess in the code.

!!! failure "If you hear this"
    **"We don't have time for meetings about every story."**
    Do it for the stories with money, rules or risk: payments, prices, permissions. Twenty-five minutes on those saves days of rework.

## Try it yourself

Map the story "Members get 5% off". Write the rules, two examples per rule, and at least one question.

??? success "One possible answer"
    - **Rule: members pay 5% less.** Example: one book at 24.99 for a member costs 23.74. Example: a guest pays 24.99.
    - **Rule: the member discount comes after a coupon.** Example: 30.00 with SAVE10 for a member costs 25.65.
    - **Questions:** Does it apply to books already on sale? Is it shown as its own line on the receipt?

    The 25.65 example is the same rule as in the [data-driven testing](../data-driven/index.md) template.

## Quick check

1. Who comes to a Three Amigos session?

    ??? question "Answer"
        A product owner, a developer and a tester.

2. What does a red card mean?

    ??? question "Answer"
        A question nobody in the room can answer yet.

3. When does the product owner review the scenarios?

    ??? question "Answer"
        Before the feature is built.

## References

- [Matt Wynne: Introducing Example Mapping](https://cucumber.io/blog/bdd/example-mapping-introduction/)
- [Cucumber: Who does what (Three Amigos)](https://cucumber.io/docs/bdd/who-does-what/)
- [Cucumber: Discovery workshop](https://cucumber.io/docs/bdd/discovery-workshop/)

Written for behave 1.3 and pytest-bdd 9.0. Outputs captured November 2026. Links checked: November 2026.
