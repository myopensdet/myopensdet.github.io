---
title: "Checklist-Based Testing: Never Forget the Basics Again"
description: "How to use test checklists well, ready-to-use checklists for web forms and API endpoints, and how to keep a checklist short, useful and up to date."
level: Beginner
tags:
  - Test design
  - Templates
  - API
nav_title: "Checklist-based testing"
order: 80
summary: "Short, living checklists for web forms and APIs, so the basics are always checked."
updated: "2026-11-22"
---

# Checklist-Based Testing: Never Forget the Basics Again

Pilots use checklists before every flight, even after twenty years of flying. Not because they forget how to fly, but because a tired or busy expert skips small steps. Testing is the same. A short checklist makes sure the basics, like "the error appears next to the field" or "one user can't see another user's data", get checked every time, by everyone.

!!! note "Before you start"
    Read [Error guessing](error-guessing.md) first. A checklist is error guessing that your team has agreed on.
    You don't need to install anything for this lesson.

## What you will learn

- What checklist-based testing is, and when it helps
- Two ready-to-use checklists: web forms and API endpoints
- How to adapt a checklist to one feature
- How to keep a checklist short and up to date

## Why this matters at work

Most bugs that reach users aren't clever. They are basics someone forgot under time pressure: a missing error message, a page that breaks on a phone, an endpoint that works without a login. A checklist costs five minutes per feature and catches exactly those. It also helps new people on the team: they get the team's experience on day one.

## The idea in plain words

!!! info "In plain words"
    Before you leave for a trip, you might check: keys, phone, wallet, passport. You know all four, but in a hurry it is easy to forget one. The list takes ten seconds and saves the trip.
    A test checklist is the same: a short list of things that must be true for every feature of one kind.

Checklists are different from test cases. A test case says exactly what to type and what to expect. A checklist item says *what to check*, and leaves the how to you: "every required field refuses empty". That's why one checklist works for many features.

The surgeon Atul Gawande wrote a whole book on why checklists work, *The Checklist Manifesto*. His main point applies to testing: a good checklist is short, covers the steps that are easy to skip, and is used by experts, not only beginners.

## Step by step

1. **Pick the checklist for the kind of feature.** This topic has two you can copy from the [templates](index.md#templates):

    - **Web form checklist:** sign-up, checkout, contact, search. Fields, errors, sending, everyone can use it, safety.
    - **API endpoint checklist:** happy path, bad input, who can do it, repeats, errors and safety.

    Here is the API one:

    ```markdown
    --8<-- "modules/think_like_a_tester/test_design_techniques/templates/api_endpoint_checklist.md"
    ```

2. **Adapt it to the feature, in two minutes.** Copy it into the ticket or test plan. Mark what doesn't apply as "n/a", and say why in a few words. For the cart totals endpoint from [Test levels](../test-levels/the-test-levels.md):

    ```markdown
    ## Who can do it

    - [x] No login token gives 401 (n/a: totals need no login, agreed with the team)
    - [x] One user can't read or change another user's data (n/a: nothing is saved)

    ## Repeat and timing

    - [x] Sending the same request twice doesn't create two of something (n/a: nothing is created)
    ```

    An "n/a" with a reason is as useful as a tick. A reader can see you thought about it.

3. **Work through it, and turn failures into bugs or tests.** Each unticked item is either a bug to report, a test to write, or a question for the team. Many items become automated tests once, and then you just check the test exists. For example, "values past each limit" is exactly what the API test `test_quantity_above_10_is_refused` checks.

4. **Keep it alive.** A checklist that never changes slowly becomes useless. Two simple habits:

    - **After a bug reaches users**, ask: "Would a checklist line have caught this?" If yes, add one.
    - **Every few months**, remove lines that never find anything and are covered by automated tests. Keep the list short enough that people actually use it. One page is a good limit.

    !!! success "Check: you should now be able to"
        Pick a checklist, adapt it to one feature with reasons, and explain how to keep it short and current.

## When it goes wrong

- **People tick everything without checking.** That happens when the list is long and feels like paperwork. Make it shorter. Ask for proof on the important lines: a link to the test, or a screenshot.
- **The checklist grows to five pages.** Split it by kind of feature (forms, APIs, file uploads), and move anything already covered by automated tests into a single line: "automated checks pass".
- **The team says checklists are for beginners.** Point to pilots and surgeons. Checklists exist for experts in a hurry. And an expert's checklist is the fastest way to share what they know with everyone else.
- **A checklist item is vague**, like "the page is fast". Rewrite it until two people would agree on the result: "the page shows its main content in under 2 seconds on the test environment".

## Common mistakes

!!! warning "Common mistakes"
    - **Using a checklist as the only testing.** It covers the basics. You still need the other techniques for the feature's own rules.
    - **Never updating it.** The best lines come from your own team's bugs.
    - **Ticking items that don't apply, with no note.** Write "n/a" and a reason, so nobody thinks they were checked.

!!! failure "If you see this error"
    **"The checklist says it was tested, but the bug still shipped."**
    Look at the line. Was it vague ("errors work")? Then rewrite it. Was it ticked without proof? Then ask for a link to the test next time. A checklist is only as good as its lines.

## Try it yourself

Your team is adding an "upload a profile photo" feature. Using the web form and error guessing checklists, write a short checklist of six lines for it.

??? success "Solution"
    One good list:

    - [ ] A normal JPG and PNG upload, and the photo shows after saving
    - [ ] An empty file and a very large file get a clear error, with the size limit in the message
    - [ ] A file that isn't an image, renamed to `.jpg`, is refused
    - [ ] A file name with spaces and accents works
    - [ ] The upload works with the keyboard alone, and the button has a visible label
    - [ ] One user can't replace another user's photo (try their user ID in the request)

    The last line is from the API checklist, and it is the one most often forgotten. It is also the most serious if it fails.

## Quick check

1. How is a checklist item different from a test case?

    ??? question "Answer"
        A test case says exactly what to do and expect. A checklist item says what to check, and works across many features.

2. What should you do with an item that doesn't apply?

    ??? question "Answer"
        Mark it "n/a" with a short reason, so readers know it was thought about.

3. When should you add a line to a checklist?

    ??? question "Answer"
        After a bug reaches users that a checklist line would have caught.

## References

- [Atul Gawande, *The Checklist Manifesto*](https://atulgawande.com/book/the-checklist-manifesto/): why checklists work for experts
- [OWASP: Cross Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html): the "HTML shows as text" line, explained
- [ISTQB Glossary: checklist-based testing](https://glossary.istqb.org/)

Links checked: November 2026.
