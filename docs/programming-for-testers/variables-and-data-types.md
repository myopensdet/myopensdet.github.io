---
title: "Variables and Types: Text, Numbers, True and False"
description: "Python variables and the basic types a tester meets every day: str, int, float, bool and None, why text that looks like a number isn't one, and why money should never be compared as a float."
level: Beginner
tags:
  - Python
  - Getting started
nav_title: "Variables and types"
order: 10
summary: "Text, numbers, True and False, and why \"30\" isn't 30."
updated: "2026-11-22"
---

# Variables and Types: Text, Numbers, True and False

A **variable** is a name for a value: `age = 30`. Every value has a **type**, which decides what you can do with it. Text is a `str`, a whole number is an `int`, a number with a decimal point is a `float`, `True` and `False` are a `bool`, and `None` means "nothing here". Two of the most common test bugs come from types: a number that is really text, and money stored as a float.

!!! note "Before you start"
    You need Python 3.11 or newer. Run the example from this topic's `examples` folder.

## What you will learn

- How to make a variable, and print it with an f-string
- The five basic types, and how to check a value's type
- Why `"30"` and `30` are different, and how to convert
- Why you should never compare money with `==` on floats

## Why this matters at work

Forms, files and APIs often send numbers as text. A test that compares `"30"` with `30` fails, and a check that forgets to convert passes the wrong thing. Knowing types is how you read those failures in seconds instead of an hour.

## The idea in plain words

!!! info "In plain words"
    A variable is a label on a box. The type is what kind of thing is in the box: words, a number, a yes or no.
    You can't do maths with a box of words, even if the words are "thirty".

## Step by step

1. **Make variables, and look at their types.** Here's the example:

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/types_demo.py"
    ```

    ```bash
    python types_demo.py
    ```

    ```text
    <class 'str'> <class 'int'> <class 'float'> <class 'bool'> <class 'NoneType'>
    arshad is 30, the notebook costs 4.25
    False True
    0.30000000000000004 False
    True True
    ```

2. **Read the f-string line.** `f"{username} is {age}"` puts the values inside the text. The `f` before the quote turns it on. You'll use it in almost every assertion message and log line.

3. **Look at line three of the output: `False True`.** `"30" == 30` is `False`, because text is never equal to a number. `int("30") == 30` is `True`. When a value comes from a form, a CSV file or a URL, it's text until you convert it with `int()` or `float()`.

4. **Look at line four: `0.30000000000000004`.** Computers store floats in binary, and most decimals, like 0.1, can't be stored exactly. So `0.1 + 0.2 == 0.3` is `False`. For money, either round before comparing, or count in whole cents: `10 + 20 == 30` is always right.

5. **Know `None`.** `None` means "no value": a coupon not entered, a field not filled in. Check for it with `is None`, not `== None`. An API that returns `None` (or `null` in JSON) where you expected a number is a common bug.

    !!! success "Check: you should now be able to"
        Make variables, check their types, convert text to numbers, and explain why money shouldn't be compared as floats.

## When it goes wrong

- **`TypeError: can only concatenate str (not "int") to str`.** You joined text and a number with `+`. Use an f-string instead: `f"Age: {age}"`.
- **`ValueError: invalid literal for int() with base 10: '30.5'`.** `int()` only takes whole numbers. Use `float()` for decimals, or check the input first. A form that sends `"30.5"` for an age might be a bug worth reporting.
- **A test says `assert 4.25 == '4.25'` failed.** One side is a number, the other is text. The API probably sends the price as text. Decide which is right, and report it if the API is wrong.
- **A price total is off by 0.01.** Floats again. Round to 2 places at the end, or use whole cents.

## Common mistakes

!!! warning "Common mistakes"
    - **Forgetting the `f` in an f-string.** `"{age}"` prints the braces as they are.
    - **Comparing floats with `==`.** Round, or use cents.
    - **Using `== None`.** Use `is None`.

!!! failure "If you see this error"
    **`NameError: name 'usename' is not defined`**
    Python doesn't know that name. Usually it's a typo (`usename` for `username`), or the variable is made further down the file than where you use it. When a similar name exists, Python adds a hint like `Did you mean: 'username'?`. Check the spelling first.

## Try it yourself

The exercise file is `exercises/ex01_variables.py`. Write `to_cents("12.50")`, which returns `1250`, and `is_adult(age)`, which is `True` from 18. Then, from the `exercises` folder:

```bash
python -m pytest tests/test_ex01_variables.py
```

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex01_variables.py"
    ```

    `partition(".")` splits `"12.5"` into `"12"`, `"."` and `"5"`. `ljust(2, "0")` turns `"5"` into `"50"`, so `12.5` means 12 and 50 cents, not 5.

## Quick check

1. What type does `"42"` have, and what about `42`?

    ??? question "Answer"
        `"42"` is a `str` (text). `42` is an `int`.

2. Why is `0.1 + 0.2 == 0.3` False?

    ??? question "Answer"
        Floats can't store most decimals exactly, so the sum is 0.30000000000000004.

3. How do you check that a value is None?

    ??? question "Answer"
        With `value is None`.

## References

- [Python Tutorial: Using Python as a calculator](https://docs.python.org/3/tutorial/introduction.html)
- [Python Tutorial: Floating-point arithmetic, issues and limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- [Python: f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals)

Written for Python 3.13. Links checked: November 2026.
