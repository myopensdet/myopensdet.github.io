---
title: "Risk-Based Testing: Score What Could Go Wrong, and Test the Worst First"
description: "How to find risks, score them by likelihood and impact, turn scores into test depth with a small Python script, and use the result to decide what to test first and what to drop when time runs out."
level: Beginner
tags:
  - Test planning
  - Test design
nav_title: "Risk-based testing"
order: 30
summary: "Score what could go wrong, and test the worst first."
updated: "2026-11-22"
---

# Risk-Based Testing: Score What Could Go Wrong, and Test the Worst First

**Risk-based testing** means you spend most of your testing time where a bug would hurt most and is most likely. You list what could go wrong, give each risk two numbers, and test in that order. When time runs out, and it always does, the things you skipped are the ones that mattered least, and you can say so.

!!! note "Before you start"
    Read [Test plan](test-plan.md) first, or keep it open.
    The script needs only Python. Run the commands from the `examples` folder.

## What you will learn

- How to find risks for a feature
- How to score likelihood and impact from 1 to 3
- How to turn scores into test depth with `risk_score.py`
- What to do with the list when time runs out

## Why this matters at work

"Did you test everything?" has no honest yes. "I tested the riskiest things deeply, the rest lightly, and here is what I skipped" is an answer a lead can trust. It also makes your choices visible, so others can say "you scored that too low" before the release, not after.

## The idea in plain words

!!! info "In plain words"
    Before a storm, you don't check every window the same. You check the big ones facing the wind first, because they're most likely to break and would do the most damage.
    Risk is two questions: how likely is it, and how bad would it be?

## Step by step

1. **Find the risks.** Go through the story, rule by rule, and ask "what could go wrong, and for whom?". Then ask three people:

    - **The developer:** "What are you most worried about?"
    - **Support:** "What do customers complain about with refunds today?"
    - **Yourself:** "What broke last time, in something similar?"

    Write each risk as a sentence about users, not about code: "The same item is refunded twice", not "the refund table".

2. **Score likelihood from 1 to 3.** How likely is the bug to exist?

    | Likelihood | Means |
    | --- | --- |
    | 3 | New or complex code, a known weak spot, date or number limits |
    | 2 | Normal new code |
    | 1 | Small change, simple, or already well tested |

3. **Score impact from 1 to 3.** How bad would it be for users or the company?

    | Impact | Means |
    | --- | --- |
    | 3 | Money, data, security, or a main journey blocked |
    | 2 | Wrong but recoverable; customers call support |
    | 1 | Annoying or cosmetic |

    Small scales on purpose. With 1 to 10, people argue whether it's a 6 or a 7. With 1 to 3, the conversation is quick.

4. **Write a reason for each number.** In the Notes column. A number without a reason can't be challenged, and a number nobody can challenge is probably a guess. Here are the refund risks:

    ```text
    --8<-- "modules/think_like_a_tester/test_strategy_and_planning/examples/refund_risks.csv"
    ```

5. **Score and sort them.** Run the [risk scorer](index.md#templates). It multiplies the two numbers and sorts the list:

    ```bash
    python risk_score.py refund_risks.csv
    ```

    ```text
    | Score | Depth | Area | Risk |
    | --- | --- | --- | --- |
    | 6 | deep | Money | The same item is refunded twice (REF-2) |
    | 6 | deep | Money | Money goes back to the wrong place (REF-5) |
    | 6 | deep | Rules | Day 30 or day 31 is handled wrongly (REF-1) |
    | 4 | normal | Email | The approval or refusal email is not sent (REF-3) |
    | 4 | normal | Rules | A sale item is refunded when it is not faulty (REF-4) |
    | 3 | normal | Money | A refund to an expired card is lost (REF-6) |
    | 2 | light | Page | Long Bengali item names break the refund page layout |
    | 1 | light | Page | The Cancel order link is missing for undelivered orders (REF-7) |

    3 deep, 3 normal, 2 light. Test the deep ones first.
    ```

6. **Turn depth into tests.** The depth tells you how much effort each risk gets:

    | Depth | Score | What it gets |
    | --- | --- | --- |
    | Deep | 6 to 9 | Every technique that fits: boundaries, negative cases, two at once. Automated. Reviewed by someone else |
    | Normal | 3 to 4 | The main positive and negative cases |
    | Light | 1 to 2 | One quick check, or a few minutes of exploring |

    For "the same item is refunded twice", deep means: a second refund is refused, two refunds pressed at the same moment, and a refund after a refused one. All three automated.

7. **Use the list when time runs out.** Go down from the top. If you have to stop, stop at a line, and tell the team which risks below it got no testing. That message is part of the job.

    !!! success "Check: you should now be able to"
        Write and score a risk list, run the scorer, and explain what "deep", "normal" and "light" mean for your tests.

## When it goes wrong

- **Everything is a 3.** Ask "if we could only test one of these, which one?" and keep asking. Then move the others down. If everything is high risk, nothing is.
- **Someone disagrees with a score.** Good. Ask for their reason and write it in the Notes column. The final number matters less than the conversation about it.
- **The scorer says "Likelihood must be 1, 2 or 3".** Someone wrote "high" or left it empty. The message names the row. Fix that row and run it again.
- **A light risk turns out to be a real bug.** Fix the score for next time, and add a note: "scored 1, was a real bug, because..." Your scores get better each release.

## Common mistakes

!!! warning "Common mistakes"
    - **Risks about code instead of users.** "The database" isn't a risk. "Refunds are saved twice" is.
    - **Scoring alone.** Ask the developer and support. They see risks you don't.
    - **Writing the list and then testing in story order anyway.** The list is the order.

!!! failure "If you see this error"
    **`KeyError: 'Area'` or `KeyError: 'Risk'`**
    The CSV is missing a column, or its name is different. The first line after the comment must be exactly `Area,Risk,Likelihood,Impact,Notes`. Spreadsheet programs sometimes rename or reorder columns when saving.

## Try it yourself

Score these three risks for a new login page, and put them in order: (a) the "Forgot password" link goes to the wrong page; (b) a wrong password lets you in; (c) the page is slow on old phones.

??? success "Solution"
    - (b) A wrong password lets you in: likelihood 1 (login code is usually well tested), impact 3 (security). Score 3, normal. Many teams would raise this to deep anyway, because the impact is so high. That's a fair choice: write the reason.
    - (c) Slow on old phones: likelihood 2, impact 2. Score 4, normal.
    - (a) Wrong "Forgot password" link: likelihood 2, impact 2 (people call support). Score 4, normal.

    The interesting one is (b): a low score with a very bad impact. Scores help you think. They don't replace thinking.

## References

- [ISTQB Glossary: risk-based testing, risk level](https://glossary.istqb.org/)
- [ISTQB Certified Tester Foundation Level v4.0](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): section 5.2, risk management
- [Python csv module](https://docs.python.org/3/library/csv.html)

Links checked: November 2026.
