---
title: "SDET vs QA vs Developer: Who Does What with the Same Bug"
description: "The difference between an SDET, a QA tester and a developer, shown with one shop bug: who finds it, who checks it, and who makes sure it never comes back."
level: Beginner
tags:
  - Career
  - Teamwork
nav_title: "SDET vs QA vs developer"
order: 20
summary: "Three roles, one bug: what each person does, and where the jobs overlap."
updated: "2026-11-22"
---

# SDET vs QA vs Developer: Who Does What with the Same Bug

This lesson compares the three roles by following one bug through a team, so you can see where each job starts and stops.

!!! note "Before you start"
    Read [What an SDET does](what-an-sdet-does.md) first.
    **QA** means Quality Assurance. In job ads it usually means a tester who mostly tests by hand.

## What you will learn

- What a developer, a QA tester and an SDET each do
- Where the three jobs overlap
- How the same bug looks to each of them
- How to tell from a job ad which role it really is

## Why this matters at work

Job titles are messy. One company's "QA Engineer" writes code all day; another's "SDET" mostly tests by hand. If you know what the work is, you can ask the right questions in an interview, and you know which skills to grow.

## The idea in plain words

!!! info "In plain words"
    Think of a restaurant. The cook makes the food and tastes it. The food inspector checks plates by looking, smelling and tasting.
    An SDET is like an inspector who also builds a machine that checks every plate for the right temperature, all night.
    All three care about good food. They just check it in different ways.

```mermaid
flowchart TB
    subgraph Dev["Developer"]
        D1["Builds features"]
        D2["Writes unit tests<br/>for their own code"]
    end
    subgraph QA["QA tester"]
        Q1["Tests features by hand"]
        Q2["Explores and reports bugs"]
    end
    subgraph SDET["SDET"]
        S1["Tests by hand too"]
        S2["Builds automated tests<br/>for the whole system"]
    end
    D2 -. "both write test code" .- S2
    Q2 -. "both explore and report" .- S1
```

## Step by step

We follow one real kind of bug through a team. The user story says: "Orders of $50.00 or more ship free." A customer orders exactly $50.00 worth of books and is charged $4.99 for shipping.

1. **The QA tester finds it by hand.** They test the edges of the rule on purpose: $49.99, $50.00 and $50.01. At exactly $50.00, shipping says $4.99. They write a bug report with the steps, what they expected and what they saw.

2. **The developer fixes it, and adds a unit test.** A **unit test** checks one small piece of code on its own, like the function that works out shipping. The developer's code used `>` where the story needs `>=`. They fix it and add a test for 49.99, 50.00 and 50.01 (the full test is on [What an SDET does](what-an-sdet-does.md)). It runs in milliseconds:

    ```bash
    python -m pytest test_shipping.py -q
    ```

    You should see:

    ```text
    5 passed in 0.02s
    ```

3. **The SDET makes sure it can't come back unseen.** A test only protects you if it runs. The SDET adds the tests to the team's pipeline, so they run on every change, before anyone can merge it. On GitHub, that is a short file like this:

    ```yaml
    name: tests
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v5
          - uses: actions/setup-python@v6
            with:
              python-version: "3.13"
          - run: pip install pytest
          - run: python -m pytest -q
    ```

    The last line is the same command you just ran. Now, if anyone changes `>=` back to `>`, the pipeline goes red and names the test. The SDET also asks a bigger question: "Where else does the $50 rule live?" The checkout page, the order email and the invoice may each show shipping. They add one end-to-end test that places a real $50.00 order and checks the total the customer sees. The [CI/CD](../../devops-for-qa/ci-cd/index.md) and [API testing](../../api-testing/index.md) topics teach both.

4. **Compare the three jobs side by side.**

    | | Developer | QA tester | SDET |
    | --- | --- | --- | --- |
    | Main goal | Build the feature | Find what is wrong | Find what is wrong, and stop it coming back |
    | Tests by hand | A little | Most of the time | Often, for new features |
    | Writes test code | Unit tests for their code | Sometimes, or never | Every week, for the whole system |
    | Typical tests | Unit tests | Manual test cases, exploring | API, UI and end-to-end tests |
    | Asks most often | "Does my code work?" | "What can go wrong for the user?" | "How do we know it keeps working?" |

5. **Read a job ad the right way.** Ignore the title. Look at the tasks. "Write and maintain automated tests in Python" means SDET work, whatever the title says. "Execute test cases and log defects" means mostly manual QA work.

    !!! success "Check: you should now be able to"
        Say what each role does with the same bug, and spot from the tasks in a job ad which role it is.

## When it goes wrong

- **The developer says "it works on my machine".** Share the exact steps, the environment and the data you used. Then try it together on one screen for five minutes. Most "works for me" arguments end the moment both people see the same thing.
- **Nobody owns the automated tests.** Failures pile up and everyone ignores them. Raise it with your lead: every test suite needs a named owner, and someone who looks at failures every day.
- **You are asked to do all three jobs at once.** Write down what you can do this sprint, and what will wait. Show it to your lead and let them choose. Saying "yes" to everything usually means doing everything badly.

## Common mistakes

!!! warning "Common mistakes"
    - **Thinking one role is "better".** Teams need all three kinds of thinking. A great manual tester finds bugs nobody thought to automate.
    - **Thinking developers don't test.** Good developers write many tests. The SDET adds tests that cross many parts of the system.
    - **Trusting the job title.** Read the list of tasks. Titles mean different things at different companies.

!!! failure "If you see this error"
    **`python3: No module named pytest`** (the path in front depends on your computer)
    pytest is not installed for the Python you used. Run `python -m pip install pytest`, then the test command again. If you use a virtual environment, turn it on first.

## Try it yourself

Read this job ad task list. Is it mostly developer, QA or SDET work?

```text
- Explore new features and report bugs with clear steps
- Build and maintain API tests in Python with pytest
- Add the tests to the CI pipeline and keep them stable
- Review user stories with the product owner before sprint start
```

??? success "Solution"
    SDET. It has manual work (explore, report, review stories) and test code for the whole system (API tests, CI, keeping them stable). A QA job would not ask for Python test code. A developer job would talk about building features.

## Quick check

1. What is a unit test?

    ??? question "Answer"
        A test that checks one small piece of code on its own, like one function.

2. The developer's unit test passed. Why does the SDET still test checkout through the API?

    ??? question "Answer"
        A correct function can still be used the wrong way. API tests check that the parts work together, the way a user uses them.

3. A job is called "QA Engineer" but the tasks say "build Playwright tests in Python". Which role is it really?

    ??? question "Answer"
        SDET work. The tasks matter more than the title.

## References

- [ISTQB Glossary](https://glossary.istqb.org/): unit testing (component testing), test automation
- [pytest: How to invoke pytest](https://docs.pytest.org/en/stable/how-to/usage.html)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
