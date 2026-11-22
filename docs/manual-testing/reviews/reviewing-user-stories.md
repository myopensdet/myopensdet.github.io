---
title: "Reviewing User Stories: Turn a Vague Story Into a Testable One"
description: "How to review a user story with a worksheet: who, what and why, testable acceptance criteria, missing cases, and how to send questions the product owner answers fast, with a full before-and-after example."
level: Beginner
tags:
  - Reviews
  - Templates
  - Test design
nav_title: "Reviewing user stories"
order: 20
summary: "A worksheet that turns a vague story into one the team can build and test."
updated: "2026-11-22"
---

# Reviewing User Stories: Turn a Vague Story Into a Testable One

A story review is the most useful hour a tester can spend in a sprint. You read the story before anyone builds it, ask the questions it doesn't answer, and help turn "refunds should be fast" into "refunds are approved or refused within 2 working days". This lesson walks through a full review, with the worksheet, from the first read to the finished story.

!!! note "Before you start"
    Read [What static testing is](what-is-static-testing.md) first.
    You don't need to install anything. The vague-word scanner in step 2 is optional, and needs only Python.

## What you will learn

- How to read a story in three passes
- What makes an acceptance criterion testable
- How to find the cases a story doesn't mention
- How to send questions that get fast answers

## Why this matters at work

"The story didn't say" is one of the most common sentences in software teams, and it always arrives too late: in a bug report, a demo, or from a customer. A review moves that sentence to before the sprint, where fixing it costs a message.

## The idea in plain words

!!! info "In plain words"
    Think of a recipe that says "add some salt and bake until done". An experienced cook can guess. A new cook can't, and two cooks will make two different cakes.
    A story is a recipe for a feature. Reviewing it means asking "how much salt? how long?" before anyone starts cooking.

## Step by step

Here is the story, as it arrived:

```markdown
--8<-- "modules/think_like_a_tester/static_testing_and_reviews/examples/story_refund_request.md"
```

1. **First pass: read it once, like a customer.** Don't take notes yet. Ask yourself: do I understand what the customer gets, and why they want it? Here, yes: a customer wants money back for an order, without hassle. Good. If you can't say it in one sentence, that is your first question.

2. **Second pass: check every criterion can pass or fail.** For each line, ask: "How would I test this? What exactly would I check?"

    | Criterion | Can you test it? |
    | --- | --- |
    | Refund for recent orders | No. How recent? |
    | Refunds should be processed fast | No. How fast, and is it a must? |
    | Email when the refund is approved | Yes. But what about refused? |
    | Sale items may not be refundable | No. Are they, or not? |
    | Money back to card, PayPal, etc | Partly. What is "etc"? |
    | Errors are handled properly | No. Which errors, and what does the customer see? |

    Only one criterion out of six can be tested as written. That's normal for a first draft. The [vague-word scanner](finding-ambiguity-and-missing-cases.md) finds most of these words for you, in a second.

3. **Third pass: look for what is missing.** This is where the [user story review worksheet](index.md#templates) helps most. Its "Missing cases" section asks the same questions for every story:

    ```markdown
    ## 3. Missing cases

    - [ ] What happens when it goes wrong? (errors, refusals, timeouts)
    - [ ] What happens at the limits? (first, last, zero, maximum)
    - [ ] What about other states? (cancelled, already done, logged out)
    - [ ] Who must NOT be able to do it?
    - [ ] What happens to existing data and existing users?
    ```

    Applied to refunds, those questions find three things the story never mentions:

    - **Partial refunds:** can a customer refund one item out of three?
    - **Already done:** can the same item be refunded twice?
    - **Other states:** what about an order that hasn't been delivered yet?

    None of these were in the story. All three would have become bugs, or arguments, later.

4. **Send the questions, numbered, with your best guess.** A list of open questions waits days. A list of guesses gets answered in minutes, because the product owner only has to say yes or no:

    ```text
    Refund story, 9 questions before planning. My guess in brackets.
    1. "Recent orders": how many days after delivery? (30 days)
    2. "Processed fast": by when? (approved or refused in 2 working days)
    3. Email when refused, too? (yes, with the reason)
    ...
    7. Can a customer refund one item of an order? (yes)
    ```

    The [example review](index.md#templates) has all nine questions with the answers.

5. **Update the story, and check it again.** Write each answer into the story itself, not only in a chat. Here is the result:

    ```markdown
    --8<-- "modules/think_like_a_tester/static_testing_and_reviews/examples/story_refund_request_reviewed.md"
    ```

    Every criterion now has a number, a limit or a clear result. Criteria 2 and 7 come from the missing-cases questions. And notice criterion 6: "errors are handled properly" became one concrete error, with what the customer gets. That one sentence is now three test cases.

    !!! success "Check: you should now be able to"
        Review a story in three passes, say which criteria can't be tested and why, and find at least two missing cases with the worksheet.

## When it goes wrong

- **The product owner says "use common sense".** Common sense differs between people, which is exactly the problem. Reply with your guess written down: "OK, I'll test 30 days. Please say if that's wrong." Now it's a decision, not a guess.
- **The answers change the story so much it no longer fits the sprint.** That is a success, not a failure: the team found out before starting, not halfway through. Suggest splitting it: the basic refund this sprint, partial refunds next.
- **You get an answer in chat, but the story stays the same.** Ask for the story to be updated, or update it yourself if you're allowed. Answers in chat are lost by next week.
- **The developer has already started.** Review anyway. Send the questions to the developer too. Finding a gap on day one of coding is still much cheaper than finding it in testing.

## Common mistakes

!!! warning "Common mistakes"
    - **Only checking the criteria that are written.** The most important cases are usually the missing ones.
    - **Sending twenty questions at once, unsorted.** Put the ones that block testing first, and keep "nice to know" for later.
    - **Rewriting the story yourself without asking.** Suggest wording, but the product owner decides what the feature is.

!!! failure "If you see this error"
    **"That's an edge case, we'll handle it later."**
    Sometimes that's fine. Then ask for it to be written down: "Refunding twice: not handled in this story, follow-up story created." A known gap is a decision. An unknown gap is a bug.

## Try it yourself

Review this story: "As a customer, I want to save items for later, so that I can buy them another time. The saved list should keep items for a while. Users can remove items easily." Write the criteria that can't be tested, and two missing cases.

??? success "Solution"
    Can't be tested as written:

    - "Keep items for a while": how long? Forever, 30 days, until the item is sold out?
    - "Remove items easily": easy how? One click? Is there an undo?
    - "Users": logged-in customers only, or guests too?

    Missing cases, for example:

    - What happens when a saved item goes out of stock, or its price changes? Is the customer told?
    - Is there a limit on how many items can be saved? What happens at the limit?
    - What happens to a guest's saved list when they log in?

## References

- [Agile Alliance: INVEST](https://www.agilealliance.org/glossary/invest/): six things a good story has
- [Agile Alliance: Three Amigos](https://www.agilealliance.org/glossary/three-amigos/): reviewing a story with a product owner, a developer and a tester together

Links checked: November 2026.
