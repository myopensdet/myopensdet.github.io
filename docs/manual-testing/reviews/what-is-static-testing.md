---
title: "What Is Static Testing? Checking Work Without Running It"
description: "Static testing explained: what you can check without running any code, how it differs from dynamic testing, what it finds best, and where it fits in a team's week."
level: Beginner
tags:
  - Reviews
  - Test design
nav_title: "What static testing is"
order: 10
summary: "What you can check without running anything, and why it saves so much time."
updated: "2026-11-22"
---

# What Is Static Testing? Checking Work Without Running It

Most people think testing means running the app and clicking. But a lot of testing happens before there is anything to run. Reading a story and asking "what happens if the card is expired?" is testing. So is a tool that reads your code and says "this line can never be true". This lesson explains static testing, and why it often finds bugs more cheaply than anything else.

!!! note "Before you start"
    You don't need any earlier lesson, and you don't need to install anything.
    A **user story** is a short description of a feature from the user's side, usually with a list of **acceptance criteria**: the things it must do to count as finished.

## What you will learn

- The difference between static and dynamic testing
- What you can test statically: stories, specs, test plans, code
- What static testing finds best, and what it can't find
- Where it fits in a normal week on a team

## Why this matters at work

A gap found in a story costs a message and five minutes. The same gap found after the code is written costs a bug report, a fix, a review and a retest, often days. Found by a customer, it costs all that plus their trust. Teams that review early spend less time on rework, and testers who review early are pulled into planning instead of waiting at the end.

## The idea in plain words

!!! info "In plain words"
    A spell checker reads your letter before you send it. It doesn't need to post the letter to find a typo. That's static checking.
    Sending the letter and seeing if it arrives is dynamic checking. You need both, but the spell checker is faster and cheaper, so it goes first.

| | Static testing | Dynamic testing |
| --- | --- | --- |
| Needs the app running? | No | Yes |
| Works on | Stories, specs, designs, test plans, code | The running app |
| Done by | People reading, and tools that read code | People and automated tests using the app |
| Finds | Unclear rules, missing cases, contradictions, risky code | Wrong behaviour, crashes, slowness |
| When | As early as the first draft | When something runs |

## Step by step

1. **Know what you can test statically.** Almost anything written down:

    | Work | What to look for |
    | --- | --- |
    | User stories | Vague words, missing error cases, criteria you can't test |
    | Specs and API designs | Fields without limits, missing error codes, conflicting rules |
    | Designs and mock-ups | Missing states: empty list, error, loading, very long text |
    | Test plans and test cases | Missing risks, cases that test the same thing twice |
    | Code and test code | Bugs a tool can see: undefined names, unused imports, an `assert` that is always true |

2. **Know what static testing finds best.** It is strongest where dynamic testing is weak:

    - **Missing requirements.** A test can only check what someone thought of. A review asks "what about refunds for orders that weren't delivered?" before anyone builds it.
    - **Two meanings.** "Recent orders" means 7 days to one person and 90 to another. Nothing *runs* wrong until both versions meet.
    - **Contradictions.** One story says "sale items can't be returned", another says "every item can be returned within 30 days".
    - **Code that can never work right**, like a test whose `assert` can never fail. A tool sees it instantly. A test run hides it, because the test passes.

3. **Know what it can't find.** Static testing can't tell you if the page is slow, if the payment provider answers, or if the feature *feels* right to use. For those, you need the running app. Static testing goes first, but it never replaces running the software.

4. **Fit it into the week.** A simple rhythm many teams use:

    | When | Static check | Who |
    | --- | --- | --- |
    | Before planning | Review the stories for the next sprint | Tester, with product owner and a developer |
    | While the code is written | Review the test plan, and the API design | Tester and developer |
    | Before every commit | Tools check the code: Ruff, gitleaks | Automatic |
    | In every pull request | People review code and tests | Developers and testers |

    !!! success "Check: you should now be able to"
        Explain static and dynamic testing in one sentence each, list four things you can test statically, and say one thing static testing can't find.

## When it goes wrong

- **Nobody shows you stories before the sprint.** Ask to join the refinement meeting, or ask the product owner to share stories two days before planning. Offer something back: "I'll send questions, so planning goes faster."
- **Your review comments are seen as "slowing things down".** Keep the first reviews small and useful: three good questions beat twenty small ones. When one of your questions prevents a rework later, point to it.
- **The story is "just an idea" and too early to review.** That's the best time. Ask the big questions now (who, why, what if it fails), and the detailed ones later.

## Common mistakes

!!! warning "Common mistakes"
    - **Waiting for the code to start testing.** By then, the cheapest bugs have become expensive ones.
    - **Reviewing only for typos.** The value is in missing cases and two meanings, not spelling.
    - **Thinking static testing replaces running the app.** It finds different bugs. You need both.

!!! failure "If you see this error"
    **"We'll find it in testing."**
    You will hear this. Answer with cost: "Yes, and then it is a bug, a fix and a retest. If we ask now, it is one message." Then ask the question anyway.

## Try it yourself

Here is one acceptance criterion: "The user can upload a profile photo." Without running anything, write three questions a static review should ask.

??? success "Solution"
    Good questions:

    - Which file types and sizes are allowed, and what does the user see if the file is too big?
    - Which user: any logged-in user, or only verified ones? Can an admin change someone else's photo?
    - What happens to the old photo, and what is shown when there is no photo yet?

    Each one is a case that would otherwise be decided by whoever writes the code, and probably differently from what the product owner wanted.

## References

- [ISTQB Certified Tester Foundation Level](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): chapter 3, "Static Testing"
- [ISTQB Glossary: static testing, dynamic testing](https://glossary.istqb.org/)

Links checked: November 2026.
