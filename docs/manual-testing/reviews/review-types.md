---
title: "Review Types: From a Quick Look to a Formal Inspection"
description: "The four review types (informal review, walkthrough, technical review, inspection), when to use each, how to run a short review that works, and how to write review comments people act on."
level: Beginner
tags:
  - Reviews
  - Teamwork
  - Templates
nav_title: "Review types"
order: 40
summary: "Pick the right kind of review, run it well, and write comments people act on."
updated: "2026-11-22"
---

# Review Types: From a Quick Look to a Formal Inspection

"Can you have a look at this?" is a review. So is a two-hour meeting with a checklist, roles and a written report. Both are useful, for different things. Using a big formal review for a small change wastes a morning. Using a quick look for a payment design misses the bugs that matter. This lesson shows the four types, when to pick each, and how to write comments that people actually act on.

!!! note "Before you start"
    Read [What static testing is](what-is-static-testing.md) first.
    You don't need to install anything for this lesson.

## What you will learn

- The four review types, from least to most formal
- How to choose the right one for the work in front of you
- How to run a short review that finds real problems
- How to write review comments that get acted on

## Why this matters at work

You will review stories, test plans, test code and pull requests every week. You will also be reviewed. Teams with a clear review habit catch problems early without slowing down. Teams without one either skip reviews or turn every review into a long argument.

## The idea in plain words

!!! info "In plain words"
    Asking a friend to read your email before you send it is a quick review. Asking a lawyer to check a contract, line by line, with notes, is a formal one.
    Both are reviews. You choose based on how much it costs if something is wrong.

| Type | How it works | Good for |
| --- | --- | --- |
| **Informal review** | Someone reads it and comments. No meeting, no rules | Small stories, test cases, most pull requests |
| **Walkthrough** | The author walks others through it, explaining as they go | Sharing knowledge, a new design, a test plan the team should understand |
| **Technical review** | Experts check it against a standard, and agree on decisions | API designs, a test automation framework, architecture |
| **Inspection** | The most formal: trained roles, a checklist, prepared reviewers, logged findings | High-risk work: payments, safety, security, regulated industries |

## Step by step

1. **Choose the type by the cost of a mistake.** Ask: "If something here is wrong, how bad is it, and how late would we find out?"

    | Work | Mistake would cost | Pick |
    | --- | --- | --- |
    | A test for a button label | Little. Easy to fix later | Informal |
    | A test plan for the next release | A wasted sprint, if the plan is wrong | Walkthrough |
    | The design of a new refund API | Rework across three teams | Technical review |
    | The rules for card payments | Money, legal trouble | Inspection |

    Most of your reviews will be informal. That's fine. Save the formal ones for where they pay off.

2. **Prepare before any meeting.** The biggest waste in reviews is a meeting where people read the document for the first time. For anything bigger than informal, send the work a day before, with one line about what you want: "Please check the error cases in section 3." People find much more when they know where to look.

3. **Run a short review in four parts.** For a walkthrough or technical review, 45 minutes is usually enough:

    | Part | Time | What happens |
    | --- | --- | --- |
    | Goal | 5 minutes | What we are reviewing, and what "done" means for the review |
    | Walk through | 20 minutes | The author explains. Reviewers ask questions, and someone writes them down |
    | Findings | 15 minutes | Go through the list: must fix, question, suggestion |
    | Next steps | 5 minutes | Who fixes what, by when. Is a second look needed? |

    One rule saves a lot of time: **find problems in the meeting, solve them after.** Long design discussions in a review meeting eat the time meant for finding.

4. **Write comments people act on.** The [review comments guide](index.md#templates) uses labels at the start of each comment, so the author knows at once how important it is:

    ```markdown
    --8<-- "modules/think_like_a_tester/static_testing_and_reviews/templates/review_comments_guide.md"
    ```

    Labels like these are common. The [Conventional Comments](https://conventionalcomments.org/) format is one well-known version. Pick one set, and write it in your team's README.

5. **Review test code like product code.** When you review a pull request with tests, check things only a person will catch:

    - Does each test check one thing, and does its name say what?
    - Would the test fail if the feature broke? (Look for missing `assert`s, or an `assert` that can't fail.)
    - Are the expected values from the rules, not copied from what the code returns?
    - Is there test data that will break next month, like a hard-coded date?

    Tools catch the rest: [static analysis tools](static-analysis-tools.md) find unused imports and broken asserts before the review even starts.

    !!! success "Check: you should now be able to"
        Name the four review types, pick one for a given piece of work, and write a labelled comment.

## When it goes wrong

- **Reviews turn into arguments.** Usually someone took a comment personally. Comment on the work, not the person, and use labels: a "suggest:" is easier to hear than a demand. If a thread passes three replies, stop typing and talk for five minutes.
- **Nobody prepares, so meetings are slow.** Cancel and reschedule once, kindly: "Let's move it to tomorrow, so everyone has time to read." People prepare the next time.
- **Pull requests wait days for a review.** Agree a team rule, like "first review within one working day", and keep pull requests small. A 50-line change gets reviewed in minutes. A 2,000-line change gets reviewed "later".
- **You are new and don't feel you can comment on a senior's work.** Ask questions instead: "question: what happens here if the list is empty?" Questions are always welcome, and they often find the real bug.

## Common mistakes

!!! warning "Common mistakes"
    - **Using one review type for everything.** A formal meeting for a typo fix, or a quick look at a payment design.
    - **Solving problems in the review meeting.** Find them in the meeting, solve them after.
    - **Thirty small comments and no important one.** Five clear comments that matter beat a page of nits.

!!! failure "If you see this error"
    **"LGTM" (looks good to me), and nothing else, on every review.**
    That isn't a review. If you approve, say what you checked: "Checked the error cases and the test names. The test for expired cards is missing; fine to add in a follow-up." It shows you read it, and it helps the next reviewer.

## Try it yourself

Pick a review type for each, and say why: (a) a new test case for "password must be 8 characters", (b) the team's first test automation framework, which everyone will use for years, (c) a test plan the whole team will follow for a big release.

??? success "Solution"
    - **(a) Informal.** Small, easy to fix later. One person reading it is enough.
    - **(b) Technical review.** Everyone will build on it for years, so check it against agreed standards with the people who know most. A mistake here gets copied into hundreds of tests.
    - **(c) Walkthrough.** The main goal is that everyone understands the plan and can question it. The author explaining it to the team does exactly that.

## References

- [Google: How to do a code review](https://google.github.io/eng-practices/review/): a public guide many teams use
- [Google: How to write code review comments](https://google.github.io/eng-practices/review/reviewer/comments.html)
- [Conventional Comments](https://conventionalcomments.org/): a common way to label review comments
- [ISTQB Glossary: informal review, walkthrough, technical review, inspection](https://glossary.istqb.org/)

Links checked: November 2026.
