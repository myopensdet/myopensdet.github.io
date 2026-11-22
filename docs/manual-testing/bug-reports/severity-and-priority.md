---
title: "Severity and Priority: How Bad a Bug Is, and How Soon to Fix It"
description: "The difference between severity and priority in bug reports, how to choose a severity from facts about users, how to suggest a priority, and what to do when the team disagrees."
level: Beginner
tags:
  - Bug reports
  - Teamwork
nav_title: "Severity and priority"
order: 20
summary: "How bad it is and how soon to fix it are two different questions."
updated: "2026-11-22"
---

# Severity and Priority: How Bad a Bug Is, and How Soon to Fix It

Every bug report gets two labels. **Severity** says how badly the bug hurts the people who use the app. **Priority** says how soon the team will fix it. They sound alike, and they are often the same, but they answer different questions and are set by different people. Mixing them up is how every bug ends up "critical", and then none of them are.

!!! note "Before you start"
    Read [What makes a great bug report](what-makes-a-great-bug-report.md) first.
    You don't need to install anything for this lesson.

## What you will learn

- What severity and priority mean, and who sets each one
- How to choose a severity from facts, not feelings
- Why high severity and low priority can both be right at once
- What to do when the team disagrees with you

## Why this matters at work

In triage, the team has an hour and fifty new bugs. Severity and priority are how they decide what to look at first. If your severities are honest, people trust them, and your critical bugs get fixed the same day. If everything you file is "critical", people stop reading the label.

## The idea in plain words

!!! info "In plain words"
    Think of a hospital. How ill a patient is, is a fact the nurse writes down. Which patient the doctor sees first is a decision, which also depends on who else is waiting and which doctor is free.
    Severity is the nurse's note. Priority is the doctor's order.

## Step by step

1. **Know the scale your team uses.** Here is the [severity, priority and states guide](index.md#templates) from this topic's templates. Most teams use something close to it:

    ```markdown
    --8<-- "modules/think_like_a_tester/bug_reports/templates/severity_priority_guide.md"
    ```

2. **Choose the severity from what happens to users.** Ask three questions:

    - **What is lost?** Money, data, privacy, or only time?
    - **How many people are hit?** Everyone, one group, or almost nobody?
    - **Is there a workaround?** Can people still finish what they came to do?

    For the Bengali names bug: nothing is lost, but a whole group of customers can't sign up at all, and there is no workaround except typing a different name. That is **major**: a main feature is broken for many users.

3. **Write the reason next to the label.** A label alone invites argument. A label with a fact is easy to agree with:

    ```markdown
    - Severity: major, because every customer with a Bengali name is blocked from signing up
    ```

4. **Suggest a priority, and say why.** Priority depends on things you may not know: the release date, other work, how many customers write their names in Bengali. So you suggest, and the team decides in triage:

    ```markdown
    - Suggested priority: high, because many of our customers write their names in Bengali
    ```

    If you don't know how many people are affected, say that, and say how someone could find out ("the sign-up error count in the logs would show it").

5. **Spot the cases where the two differ.** These are the ones that teach the difference:

    | Bug | Severity | Priority | Why |
    | --- | --- | --- | --- |
    | The app crashes on a browser almost nobody uses | Critical | Low | Very bad, but for very few people |
    | The company name is misspelled on the home page, the day before launch | Trivial | High | Harmless, but everyone sees it tomorrow |
    | A refund email shows the wrong date | Minor | Medium | Confusing, and support will get questions |

6. **Let severity stay a fact.** If the team gives a critical bug low priority, that's their call. Don't lower the severity to match. The severity is what tells someone next year that this bug was dangerous and only waited because of the browser numbers.

    !!! success "Check: you should now be able to"
        Explain the difference between severity and priority, choose a severity with a reason, and give one example where they differ.

## When it goes wrong

- **Everything you report comes back as "low".** Look at your reasons. "Bengali names fail" is weaker than "every customer with a Bengali name is blocked". Add who is affected and how much, with a number if you can get one.
- **Someone changes your severity without saying why.** Ask, kindly, in the bug: "I set this as major because there is no workaround. Did I miss one?" Either you learn something, or they look again.
- **Your team has no scale at all.** Copy the guide above, agree it in one short meeting, and link it from the bug form. Ten minutes once saves arguments every week.
- **A bug is a security hole.** Don't describe how to use it in a public issue. Mark it critical and tell your lead directly, so the team can handle it privately.

## Common mistakes

!!! warning "Common mistakes"
    - **Setting severity by how annoyed you are.** Use what happens to users.
    - **Setting the priority yourself and not saying it's a suggestion.** Priority belongs to the team.
    - **Lowering severity to match a low priority.** Keep the fact, even when the team waits.

!!! failure "If you see this error"
    **The triage meeting spends ten minutes arguing about one label.**
    The bug is missing a fact. Stop arguing, write down the question ("how many users are on that browser?"), and give someone the task of finding out. Decide next time, with the number.

## Try it yourself

Give each bug a severity and a suggested priority, with a one-line reason:

1. The "Pay" button does nothing on phones. It works on laptops.
2. The footer shows last year.
3. Two customers who press "Refund" at the same moment can both get the same item refunded.

??? success "Solution"
    1. **Critical, high.** Customers on phones can't pay at all, and that is often most of them.
    2. **Trivial, low.** Nobody is stopped from doing anything. Fix it with the next small change.
    3. **Critical, high.** Money leaves the company. It needs two people at once, which makes it rare, not harmless. Also tell your lead directly: someone could do it on purpose.

## References

- [ISTQB Glossary: severity, priority](https://glossary.istqb.org/)
- [Simon Tatham: How to Report Bugs Effectively](https://www.chiark.greenend.org.uk/~sgtatham/bugs.html)

Links checked: November 2026.
