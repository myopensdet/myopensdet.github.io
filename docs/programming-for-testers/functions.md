---
title: "Functions: Name a Piece of Work So You Can Test It"
description: "Python functions for testers: def, parameters and default values, return versus print, type hints and docstrings, and why small functions that return values are easy to test."
level: Beginner
tags:
  - Python
  - Clean code
nav_title: "Functions"
order: 40
summary: "Name a piece of work, so you can test it and use it again."
updated: "2026-11-22"
---

# Functions: Name a Piece of Work So You Can Test It

A **function** is a named piece of work. You give it inputs, called **parameters**, and it gives back a result with `return`. Every pytest test is a function, and so is every helper you write for tests. The most useful habit in this lesson: a function that *returns* its answer can be tested; a function that only *prints* it can't.

!!! note "Before you start"
    Read [If and loops](conditions-and-loops.md) first.

## What you will learn

- How to write a function with `def`, parameters and `return`
- How default values and named arguments work
- The difference between `return` and `print`
- How type hints and docstrings make a function easier to use

## Why this matters at work

Test code repeats itself: log in, make a user, check a total. Functions put each of those in one place, so a change is made once. And when the rules live in small functions, you can test them directly, which is much faster than going through the UI.

## The idea in plain words

!!! info "In plain words"
    A function is a recipe card. "Pancakes: give me flour, eggs and milk, and I'll give you pancakes."
    You don't rewrite the recipe every time. You say "pancakes", hand over the ingredients, and get the result.

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/functions_demo.py"
    ```

    ```bash
    python functions_demo.py
    ```

    ```text
    4.99
    0.0
    0.0
    DONE
    None
    ```

2. **Read the first line of the function.** `def delivery_fee(subtotal: float, member: bool = False) -> float:` says: the name is `delivery_fee`; it takes `subtotal` (a float) and `member` (a bool, `False` if you don't give one); and it returns a float. The `: float` parts are **type hints**. Python doesn't enforce them, but editors and readers use them.

3. **Call it three ways.** `delivery_fee(20)` uses the default `member=False`. `delivery_fee(20, member=True)` names the argument, which makes the call easy to read. `delivery_fee(50)` hits the edge: exactly 50 is free. That's a [boundary value](../manual-testing/test-design/boundary-values.md), and a function makes it trivial to test.

4. **See the difference between `return` and `print`.** `shout("done")` prints `DONE`, but returns nothing, so `result` is `None`. A test can check `delivery_fee(50) == 0.0`. It can't easily check what `shout` printed. Return values; print only at the edges of your program.

5. **Write a docstring.** The text in triple quotes under `def` says what the function does. It shows up when someone hovers over the name in their editor. One clear sentence is enough.

    !!! success "Check: you should now be able to"
        Write a function with parameters, a default value and a return value, and explain why returning is better than printing for testing.

## When it goes wrong

- **The function returns `None` when you expected a value.** You forgot `return`, or one path through the `if` has no `return`. Every path should end with one.
- **`TypeError: delivery_fee() missing 1 required positional argument: 'subtotal'`.** You called it without an argument it needs. Check the `def` line for what it takes.
- **`TypeError: delivery_fee() got an unexpected keyword argument 'is_member'. Did you mean 'member'?`** The name in the call doesn't match the name in the `def`. Python 3.13 even suggests the right one.
- **A function is 80 lines long.** It's doing several jobs. Split it: one function per job, each one easy to test.

## Common mistakes

!!! warning "Common mistakes"
    - **Printing instead of returning.** Tests need values.
    - **A list or dictionary as a default value**, like `def add(item, items=[])`. The same list is shared between calls. Use `items=None`, then `items = items or []` inside.
    - **Names that don't say what happens**, like `do_it()` or `check2()`.

!!! failure "If you see this error"
    **`TypeError: 'NoneType' object is not subscriptable`**
    You used `[...]` on something that is `None`, often the result of a function that forgot to `return`. Find where the value came from, and check that function returns on every path.

## Try it yourself

Open `exercises/ex04_functions.py`. Write `make_user(name, role="customer")`, which builds a test user dictionary, and `percent(part, whole)`, which must not crash when `whole` is 0. Run `python -m pytest tests/test_ex04_functions.py`.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex04_functions.py"
    ```

    The `whole == 0` check is the kind of guard testers think of first: "what if there were no tests at all?"

## Quick check

1. What does a function return if it has no `return` line?

    ??? question "Answer"
        `None`.

2. Why are functions that return values easier to test than ones that print?

    ??? question "Answer"
        A test can compare the returned value with the expected one directly.

3. In `def fee(total, member=False)`, what is `member=False`?

    ??? question "Answer"
        A default value: `member` is `False` unless the caller gives another value.

## References

- [Python Tutorial: Defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [Python Tutorial: Default argument values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- [Python: Type hints (typing)](https://docs.python.org/3/library/typing.html)

Written for Python 3.13. Links checked: November 2026.
