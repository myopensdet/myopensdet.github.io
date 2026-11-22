---
title: "Finding Ambiguity and Missing Cases in Requirements"
description: "How to spot words with two meanings and the cases a requirement forgets, with a vague-word scanner you can run on any story, a list of questions that work on any feature, and how to handle false alarms."
level: Beginner
tags:
  - Reviews
  - Templates
  - Python
nav_title: "Finding ambiguity and missing cases"
order: 30
summary: "Spot words with two meanings, and the cases nobody wrote down."
updated: "2026-11-22"
---

# Finding Ambiguity and Missing Cases in Requirements

Two kinds of problem hide in almost every requirement. **Ambiguity**: words that two people read differently, like "fast" or "recent". And **missing cases**: things nobody wrote down at all, like what happens when the payment fails. The first kind you can partly find with a tool. The second kind needs a person asking the right questions. This lesson gives you both.

!!! note "Before you start"
    Read [Reviewing user stories](reviewing-user-stories.md) first.
    The scanner needs only Python. Run the commands from the `examples` folder.

## What you will learn

- The usual vague words, and the question to ask about each
- How to run the vague-word scanner on any story
- How to handle a word that is flagged but fine
- A short set of questions that finds missing cases in any feature

## Why this matters at work

Ambiguity doesn't cause errors you can see. Everyone reads "fast" and nods. The problem appears weeks later, when the developer's "fast" (one hour) meets the customer's "fast" (right now). Finding these words early is quick, and it stops the most annoying kind of argument: two people who were both right by the text.

## The idea in plain words

!!! info "In plain words"
    "Meet me after lunch" sounds clear, until one person comes at 1 o'clock and the other at 3. Nobody lied. The words just had room for two meanings.
    A requirement full of words like "soon", "some" and "easy" has the same problem, many times over.

## Step by step

1. **Learn the usual suspects.** Most vague words fall into a few groups:

    | Kind | Words | Ask |
    | --- | --- | --- |
    | Speed and time | fast, quickly, soon, recent | Give a number and a unit |
    | Amount | some, many, few, all | How many? Any exceptions? |
    | Must or maybe | should, may, might, if possible | Is it required or not? What happens otherwise? |
    | Open lists | etc, and so on | Write every item |
    | Feelings | easy, simple, user-friendly, intuitive | How will we check it? |
    | Hand-waving | properly, correctly, handle, appropriate | What exactly does the user see? |

2. **Run the scanner.** The [ambiguity_scan.py](index.md#templates) template has these words, each with its question. Point it at a story file:

    ```bash
    python ambiguity_scan.py story_refund_request.md
    ```

    ```text
    line 4: "quickly"  How quickly? Give a number and a unit, for example: within 5 working days.
    line 8: "recent"  How recent? Give a number of days.
    line 9: "should"  Must it, or is it optional? Write 'must' or 'can'.
    line 9: "fast"  How fast? Give a number and a unit, for example: within 2 seconds.
    line 11: "may"  Is it allowed, or not? Who decides, and how?
    line 12: "etc"  What else is on the list? Write every item.
    line 13: "properly"  What does 'properly' look like? What is the expected result?

    7 vague words found. Ask about each one before testing.
    ```

    It ends with exit code 1 when it finds something, so you can run it in a pipeline on every story file. It also reads from the keyboard or a pipe, so you can paste a story straight in: `python ambiguity_scan.py < story.md`.

3. **Turn each flag into a question, or decide it's fine.** Not every flag is a problem. After the review, the reviewed story still has one:

    ```bash
    python ambiguity_scan.py story_refund_request_reviewed.md
    ```

    ```text
    line 4: "support"  Support how? Which cases exactly?

    1 vague words found. Ask about each one before testing.
    ```

    The line says "without calling support", meaning the support team. That's clear. Leave it. The scanner points; you decide. This is also why it says "vague words found", not "errors found".

4. **Now look for what is missing.** No tool can find a sentence that isn't there. For that, ask the same five questions about any feature. They work because most stories describe only the success path:

    | Question | For refunds, it finds |
    | --- | --- |
    | What happens when it goes wrong? | The card is expired, or the payment provider refuses |
    | What happens at the limits? | Day 30 and day 31 after delivery |
    | What about other states? | Orders not delivered yet, items already refunded |
    | Who must NOT be able to do it? | Another customer, using someone else's order number |
    | What happens to what exists today? | Refund requests made before this feature existed |

5. **Check the states, too.** If the feature has a status (requested, approved, refused, paid), draw it as in [State transitions](../test-design/state-transitions.md). Every missing arrow is a missing rule. "Can a refused request be requested again?" is a question that only shows up once you draw it.

6. **Add your team's words to the list.** Every team has its own vague words. Maybe "standard" means three different things in your company, or "active user" has never been defined. Add them to the `VAGUE` list in the script, with your question:

    ```python
    "standard": "Which standard? Link to it.",
    "active user": "Active by what rule? Logged in within how many days?",
    ```

    !!! success "Check: you should now be able to"
        Name the six kinds of vague words, run the scanner and explain its output, and find at least three missing cases with the five questions.

## When it goes wrong

- **The scanner flags too much.** A long spec can give 50 flags. Don't send 50 questions. Sort them: fix the ones in acceptance criteria first, because those become tests. Flags in background text can wait.
- **A word is a false alarm again and again**, like "may" in "the 3rd of May". Leave it in the list, but skim past it. Or, if your stories never use the word in its vague sense, remove it from `VAGUE`. It's your team's list.
- **The product owner answers with another vague word.** "Fast" becomes "really quick". Offer numbers to choose from: "Within 1 hour, 1 day, or 2 working days?" A choice is easier to answer than a blank.
- **Nobody knows the answer.** That is a real finding. Write it down as "Open: who decides the refund limit?" with a name and a date. The feature shouldn't start until it has an owner.

## Common mistakes

!!! warning "Common mistakes"
    - **Treating the scanner's silence as "the story is fine".** It only finds words. Missing cases need the five questions.
    - **Fixing the word instead of the meaning.** Changing "fast" to "quickly" fixes nothing. Replace it with a number.
    - **Asking about every flag in background text.** Spend your questions on the acceptance criteria.

!!! failure "If you see this error"
    **`FileNotFoundError: [Errno 2] No such file or directory: 'story.md'`**
    The scanner can't find the file. Check the name and the folder, or give the full path. You can also paste the story instead: run `python ambiguity_scan.py`, paste the text, then press Ctrl+D (Mac and Linux) or Ctrl+Z then Enter (Windows).

## Try it yourself

Find the vague words and two missing cases in this criterion: "Search should return relevant results quickly, and handle typos appropriately."

??? success "Solution"
    Vague words: "should", "relevant", "quickly", "handle", "appropriately". The scanner flags four of them. "Relevant" isn't on its list, which shows why you still read the text yourself. You could add it to your team's list.

    Questions to ask:

    - Is it a must? How fast: within 1 second for 95 out of 100 searches?
    - What does "relevant" mean: exact name matches first, then descriptions?
    - Which typos: one wrong letter, swapped letters? What does the user see, "Did you mean..."?

    Missing cases: an empty search, a search with no results, and a very long search text.

## Quick check

1. What is the difference between ambiguity and a missing case?

    ??? question "Answer"
        Ambiguity is a word with more than one meaning. A missing case is something nobody wrote down at all.

2. Can the scanner find missing cases?

    ??? question "Answer"
        No. It only finds words. Missing cases need a person asking questions like "what happens when it goes wrong?"

3. What should replace "fast" in a requirement?

    ??? question "Answer"
        A number with a unit, like "within 2 working days" or "within 2 seconds".

## References

- [ISTQB Glossary: ambiguity, requirement](https://glossary.istqb.org/)
- [Python re module](https://docs.python.org/3/library/re.html): the word matching the scanner uses

Written for Python 3.13. Links checked: November 2026.
