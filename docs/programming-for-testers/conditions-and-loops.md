---
title: "If and Loops: Make Decisions, and Repeat a Check"
description: "Python if, elif and else, for loops over lists, enumerate, list comprehensions, and a retry loop with a limit and break, using HTTP status codes and test steps as examples."
level: Beginner
tags:
  - Python
  - Getting started
nav_title: "Conditions and loops"
order: 30
summary: "Make decisions, do the same check many times, and retry with a limit."
updated: "2026-11-22"
---

# If and Loops: Make Decisions, and Repeat a Check

`if` lets your code choose: if the status is 200, it's fine; otherwise, report it. A `for` loop does the same thing for every item in a list: check every user, every product, every row. Together they cover most of the logic in test helpers. This lesson also shows a retry loop, because waiting for a slow service is a daily task in testing.

!!! note "Before you start"
    Read [Strings, lists and dictionaries](lists-tuples-sets-and-dictionaries.md) first.

## What you will learn

- How to write `if`, `elif` and `else`
- How to loop over a list, with or without a counter
- How to build a list in one line with a comprehension
- How to retry something with a limit, and stop with `break`

## Why this matters at work

A test helper that checks one response is useful. One that checks every response in a list, and groups the failures, is what the team actually needs. Loops are how you go from one to many.

## The idea in plain words

!!! info "In plain words"
    A loop is a teacher marking a pile of homework: take the next one, check it, put it down, repeat until the pile is empty.
    `if` is the marking itself: right, wrong, or "see me".

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/loops_demo.py"
    ```

    ```bash
    python loops_demo.py
    ```

    ```text
    200 ok
    201 ok
    404 client error
    500 server error
    200 ok
    errors: [404, 500]
    step 1: login
    step 2: search
    step 3: pay
    try 1: 503
    try 2: 503
    try 3: 200
    ```

2. **Read the `if`.** Python checks each condition from the top and runs the first one that's true. `elif` means "else if". `else` catches everything left. The indented lines belong to the condition above them. Indentation is how Python knows where a block ends, so keep it at 4 spaces.

3. **Read the `for` loop.** `for code in codes:` takes each item in turn and calls it `code`. The loop body runs once per item: five codes, five lines of output.

4. **Use `enumerate` when you need a number.** `enumerate(steps, start=1)` gives the position and the item together. Handy for "step 3 failed" messages.

5. **Build a list in one line.** `[code for code in codes if code >= 400]` is a **list comprehension**: "every code, for each code in codes, if it's 400 or more". It does the same as a loop with `append`, in one readable line.

6. **Retry with a limit.** The last loop tries up to 5 times, and `break` stops it as soon as the answer is 200. Never retry without a limit: a test that waits forever is worse than one that fails. Python also has `while condition:` loops, which repeat until the condition is false. For retries, a `for` with `range` is safer, because the limit is built in.

    !!! success "Check: you should now be able to"
        Write an `if` with `elif` and `else`, loop over a list, build a filtered list with a comprehension, and write a retry loop with a limit.

## When it goes wrong

- **`IndentationError: expected an indented block after 'if' statement on line 4`.** The line after `if ...:` or `for ...:` must be indented. Use 4 spaces, and let your editor do it.
- **The loop runs, but nothing is printed.** The list may be empty. Print `len(codes)` before the loop. An empty list from an API is often the real finding.
- **The wrong branch runs.** Check the order of your conditions. `if code < 500` before `if code < 300` would call 200 a client error, because the first true condition wins.
- **A loop never ends.** It's almost always a `while` whose condition never becomes false. Press Ctrl+C to stop it, and switch to `for attempt in range(5)`.

## Common mistakes

!!! warning "Common mistakes"
    - **Using `=` instead of `==` in a condition.** `=` assigns, `==` compares.
    - **Changing a list while looping over it.** Build a new list instead, with a comprehension.
    - **Retrying without a limit, or without a pause in real code.** Add both.

!!! failure "If you see this error"
    **`SyntaxError: expected ':'`**
    Every `if`, `elif`, `else` and `for` line ends with a colon. Add it, and check the next line is indented.

## Try it yourself

Open `exercises/ex03_loops.py`. Write `status_group(code)`, which names the group of a status code, and `count_outcomes(outcomes)`, which counts each outcome in a list. Run `python -m pytest tests/test_ex03_loops.py` from the `exercises` folder.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex03_loops.py"
    ```

    `counts.get(outcome, 0) + 1` means "the count so far, or 0 if this is the first one, plus one". You'll see that line in many test reports.

## Quick check

1. In an `if` / `elif` chain, which branch runs?

    ??? question "Answer"
        The first one whose condition is true, from the top.

2. What does `[n for n in numbers if n > 0]` make?

    ??? question "Answer"
        A new list with only the numbers greater than 0.

3. Why should a retry loop have a limit?

    ??? question "Answer"
        Without one, a broken service makes the test wait forever, instead of failing with a clear message.

## References

- [Python Tutorial: if statements and for loops](https://docs.python.org/3/tutorial/controlflow.html)
- [Python Tutorial: List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)

Written for Python 3.13. Links checked: November 2026.
