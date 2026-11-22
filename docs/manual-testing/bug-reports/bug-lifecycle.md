---
title: "The Bug Lifecycle: From New to Closed, and Your Job at Each Step"
description: "The states a bug moves through, from new to triaged, in progress, fixed, verified and closed, what the tester does at each step, how to verify a fix, and when to reopen."
level: Beginner
tags:
  - Bug reports
  - Teamwork
nav_title: "The bug lifecycle"
order: 30
summary: "The states a bug moves through, and what you do at each one."
updated: "2026-11-22"
---

# The Bug Lifecycle: From New to Closed, and Your Job at Each Step

A bug doesn't end when you file it. It moves through states: someone checks it, someone fixes it, someone checks the fix. Each state has a job, and two of those jobs are yours: the report at the start, and the check at the end. This lesson walks through the states, and what to do at each one.

!!! note "Before you start"
    Read [What makes a great bug report](what-makes-a-great-bug-report.md) and [Severity and priority](severity-and-priority.md) first.
    You don't need to install anything for this lesson.

## What you will learn

- The usual bug states, and what moves a bug from one to the next
- What the tester does when a bug is "Fixed"
- When to reopen a bug, and when to file a new one
- What "Duplicate", "Not a bug" and "Won't fix" really mean

## Why this matters at work

Most bug trackers are full of bugs that are "fixed" but nobody checked, and bugs that are "new" but nobody looked at. Both hide risk. A tester who follows bugs to the end is the one who can honestly say "everything we fixed this sprint really works".

## The idea in plain words

!!! info "In plain words"
    Think of sending a parcel. It is posted, sorted, sent out, and delivered. You only relax when someone signs for it.
    A bug is "delivered" when it's fixed. It is only done when someone has checked the fix.

## Step by step

1. **See the whole path.** Names differ between teams and tools, but most look like this:

    ```mermaid
    stateDiagram-v2
        [*] --> New
        New --> Triaged
        New --> Duplicate
        New --> NotABug: Not a bug
        Triaged --> InProgress: In progress
        Triaged --> WontFix: Won't fix
        InProgress --> Fixed
        Fixed --> Verified
        Fixed --> Reopened
        Reopened --> InProgress
        Verified --> Closed
        Duplicate --> Closed
        NotABug --> Closed
        WontFix --> Closed
        Closed --> Reopened
        Closed --> [*]
    ```

    The same states, with what each one means, are in the [severity, priority and states guide](index.md#templates).

2. **New: you file it.** The report is your work. Use the [template](index.md#templates), run the checker, and tell the developer on duty with one line and a link.

3. **Triaged: the team decides.** In triage, someone reads the report, checks the severity, and sets a priority. Watch for questions in the comments. Answer them in the report itself, so the next reader doesn't need the comments.

4. **In progress: stay reachable.** The developer may ask for data, a log or a call. A fast answer here is worth more than anything else you do that day.

5. **Fixed: check the fix.** This is your second job. "Fixed" means the developer believes it's fixed. Now check:

    - **Run your own steps again**, exactly as written, on the build that has the fix.
    - **Try the comparison too.** "আরশাদ" should now be accepted, and "José" must still be accepted.
    - **Look around the fix.** Try a few nearby cases: another Bengali name, a name with a Bengali number, a name that is too long. Fixes often break their neighbours.
    - **Check there's a test.** Ask for an automated test that would have caught the bug, so it can't come back quietly:

    ```python
    def test_bengali_username_is_accepted():
        # Bug: "Sign-up refuses usernames in Bengali, but accepts accented Latin names"
        assert check_signup("আরশাদ", 30) == []
    ```

    Today, before the fix, this test fails with "Username can only use letters and numbers". After the fix, it passes. That's the clearest proof of all.

6. **Verified, then Closed.** Write one line in the bug saying what you checked and on which build: "Verified on 1.4.3: আরশাদ and বাংলা১২ accepted, José still accepted, test added." Then close it, or let the team close it, depending on how your team works.

7. **Reopened: only for the same bug.** If your original steps still fail, reopen it, and say what you saw on which build. If you find a *different* problem while checking, file a new bug and link the two. A bug that keeps growing never gets closed.

8. **The three "no" endings.**

    - **Duplicate:** someone already reported it. Check the link really is the same bug, then add anything your report has that theirs doesn't.
    - **Not a bug:** it works as designed. Ask for the rule it follows. If the rule is wrong for users, raise that with the product owner, not in the bug.
    - **Won't fix:** a real bug the team chose to leave. That's a valid choice. Make sure the reason is written down, so nobody files it again next month.

    !!! success "Check: you should now be able to"
        Name the bug states, explain what you check when a bug is "Fixed", and decide between reopening a bug and filing a new one.

## When it goes wrong

- **Bugs sit in "New" for weeks.** Nobody owns triage. Ask your lead who looks at new bugs, and how often. Even fifteen minutes twice a week is enough to start.
- **Fixed bugs are closed without anyone checking.** Ask the team to add "Verified" as a state, or a rule that the reporter closes the bug. Then check your own fixed bugs every morning.
- **The fix works on the developer's machine but not on staging.** Check that staging really has the build with the fix. Often it doesn't yet. If it does, reopen with the build number and what you saw.
- **The same bug keeps coming back.** There's no automated test for it. Ask for one before the bug is closed this time.

## Common mistakes

!!! warning "Common mistakes"
    - **Treating "Fixed" as "done".** It is done after someone checks it.
    - **Reopening a bug for a new problem.** New problem, new bug, with a link.
    - **Arguing about "Not a bug" in the bug.** Ask for the rule, then talk to the product owner if the rule is wrong.

!!! failure "If you see this error"
    **You can't find the build with the fix.**
    Ask the developer for the build number, commit or pull request with the fix, and check where it has been deployed. Don't verify on a build that may not have the fix. A "verified" on the wrong build is worse than no check at all.

## Try it yourself

You are checking a fixed bug: "Refund on day 30 is refused". On the new build, day 30 is now accepted, but day 29 is refused. What do you do?

??? success "Solution"
    Your original steps (day 30) now pass, so this bug's own check passes. But day 29 was working before and now fails, so the fix broke a neighbour.

    The usual way: file a new bug, "Refund on day 29 is refused after the day-30 fix", link it to the first one, and mark it at least major. Some teams prefer to reopen the first bug because the fix caused it. Either is fine, as long as the link is there and nobody closes it as "verified" without a note.

## Quick check

1. What does "Fixed" mean, and what does "Verified" mean?

    ??? question "Answer"
        Fixed: the developer believes it's fixed. Verified: someone checked the fix on a real build.

2. While checking a fix, you find a different problem. Reopen or new bug?

    ??? question "Answer"
        A new bug, linked to the first one.

3. Why ask for an automated test before closing a bug?

    ??? question "Answer"
        So the bug can't come back quietly. The test fails if it ever does.

## References

- [ISTQB Glossary: defect management](https://glossary.istqb.org/)
- [GitHub: About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)
- [Mermaid: State diagrams](https://mermaid.js.org/syntax/stateDiagram.html)

Links checked: November 2026.
