---
title: "Reading Other People's Code: Find Your Way Around a Test Suite You Didn't Write"
description: "A method for reading unfamiliar Python code: start from the tests and the entry point, read names before details, predict then run, use print and breakpoint, and ask good questions, with a small file to practise on."
level: Beginner
tags:
  - Python
  - Debugging
nav_title: "Reading other people's code"
order: 110
summary: "Find your way around code you didn't write: predict, run, and check."
updated: "2026-11-22"
---

# Reading Other People's Code: Find Your Way Around a Test Suite You Didn't Write

On a new team, you'll read far more code than you write. Someone else's test suite, someone else's framework, the app's code when you're hunting a bug. Nobody reads it top to bottom like a book. This lesson gives you a method: start from what runs, read names before details, guess what happens, then run it and check your guess.

!!! note "Before you start"
    Do the earlier lessons first, especially [Functions](functions.md) and [If and loops](conditions-and-loops.md).

## What you will learn

- Where to start reading in an unfamiliar project
- How to read a function quickly: name, inputs, output, then body
- The "predict, then run" habit
- How to look inside running code with `print` and `breakpoint()`

## Why this matters at work

When a test fails, you need to understand the test and the code it checks, often written by people who have left. The faster you can read, the faster you can say "this is a real bug" or "this test is wrong". The [learning from code and examples](../working-as-a-qa/learning-a-new-area/learning-from-code-and-examples.md) lesson covers the same habit for whole projects.

## The idea in plain words

!!! info "In plain words"
    Reading code is like visiting a new city. You don't walk every street. You find the station, the main road and the place you need, and look at the rest when you get there.

## Step by step

1. **Start from what runs.** In a test project, that's the tests. Read the test names first: `test_refund_is_refused_on_day_31` tells you what the code should do before you read a line of it. In a script, find `if __name__ == "__main__":` at the bottom and follow what it calls.

2. **Read a function from the outside in.** Name first, then the inputs, then what it returns. Only then the body. Often the outside is enough to move on.

3. **Predict, then run.** Read this file and write down what you think it prints:

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/mystery.py"
    ```

    Then run it:

    ```bash
    python mystery.py
    ```

    ??? success "What it prints"
        ```text
        10 ok
        31 too late
        5 already refunded
        5 sale items only if faulty
        ```

        Three things to notice. `check` returns `None` when everything is fine, and `None or "ok"` gives `"ok"`. The order of the `if`s matters: "already refunded" is checked before the date. And `check(*case)` hands the four values in the tuple to the four parameters.

    Where your guess was wrong is exactly where you learned something.

4. **Look inside while it runs.** Add `print(repr(value))` where you're unsure, or put `breakpoint()` on a line. Python stops there, and you can type variable names to see their values. Type `n` to go to the next line, `c` to continue, `q` to quit. Remove both before you commit.

5. **Use your editor.** In VS Code, hover over a name to see its docstring, and use "Go to Definition" (F12) to jump to where a function is written. "Find All References" (Shift+F12) shows everywhere it's used.

6. **Write down what you learned.** A short note, like "refund checks: order matters, refunded first", saves you an hour next month. A [learning log](../working-as-a-qa/learning-a-new-area/index.md#templates) is made for this.

    !!! success "Check: you should now be able to"
        Start reading an unfamiliar project from its tests or entry point, predict what a piece of code does, then check it by running it.

## When it goes wrong

- **The code is huge and you don't know where to start.** Pick one test that fails, or one feature you need to test, and follow only that path. Ignore everything else for now.
- **The names don't tell you anything.** `do_stuff(x, y)` happens. Run it with simple inputs and see what comes out. Then suggest a better name in a review.
- **You've read the same function five times and still don't get it.** Copy it into a new file, give it tiny inputs, and print each step. Or ask the person who wrote it, with a precise question: "Why is refunded checked before the date?"
- **The code uses something you've never seen**, like a decorator or `yield`. Search the exact word with "python", and read the official tutorial's section on it. Then come back.

## Common mistakes

!!! warning "Common mistakes"
    - **Reading every line from the top.** Start from what runs, and follow one path.
    - **Guessing without checking.** Predict, then run. Your guesses get better quickly.
    - **Leaving `breakpoint()` or debug prints in the code.** Remove them before you commit.

!!! failure "If you see this error"
    **The test run stops and waits, showing `(Pdb)`.**
    That's a `breakpoint()` someone left in the code. Type `c` and press Enter to continue, then find and remove the line. Searching the project for `breakpoint(` finds it quickly.

## Try it yourself

Open `templates/run_summary.py` from this topic. Without running it, answer: what does it print if the results file has no failed tests? What exit code does it end with? Then change `nightly_results.json` (a copy) so nothing fails, and run it to check.

??? success "Solution"
    In `summary()`, the "Failed:" part is only added `if failed:`, so it doesn't appear at all. The counts and the slowest tests still print. In `main()`, the last line returns `1 if any(...) == "failed" else 0`, so the exit code is 0.

    You answered by reading two small parts, `summary()` and the end of `main()`, not the whole file. That's the method.

## References

- [Python: pdb, the debugger](https://docs.python.org/3/library/pdb.html)
- [Python: breakpoint()](https://docs.python.org/3/library/functions.html#breakpoint)
- [VS Code: Navigate code](https://code.visualstudio.com/docs/editing/editingevolved)

Written for Python 3.13. Links checked: November 2026.
