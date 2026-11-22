---
title: "Errors and Exceptions: Read a Traceback, and Handle What Can Go Wrong"
description: "How to read a Python traceback from the bottom up, catch specific exceptions with try and except, raise your own with a clear message, use finally for cleanup, and check errors in tests with pytest.raises."
level: Beginner
tags:
  - Python
  - Debugging
nav_title: "Errors and exceptions"
order: 70
summary: "Read a traceback fast, and handle what can go wrong."
updated: "2026-11-22"
---

# Errors and Exceptions: Read a Traceback, and Handle What Can Go Wrong

When something goes wrong, Python raises an **exception** and prints a **traceback**: the error, and the path the code took to get there. Testers read tracebacks all day, from their own code and from failing tests. This lesson shows how to read one in seconds, how to handle errors you expect with `try` and `except`, and how to raise your own errors with messages people can act on.

!!! note "Before you start"
    Read [Functions](functions.md) first.

## What you will learn

- How to read a traceback, starting from the bottom
- How to catch a specific error with `try` and `except`
- How to raise your own error with a clear message
- How to test that code raises the right error, with `pytest.raises`

## Why this matters at work

A failing test in the pipeline is a traceback. The faster you read it, the faster you know whether it's a real bug, a test bug or a broken environment. And when you write helpers, clear error messages save your teammates the same time.

## The idea in plain words

!!! info "In plain words"
    An exception is a fire alarm. It stops everything and says what's wrong. A traceback is the list of rooms the alarm went through.
    `try` and `except` is a plan for one kind of alarm: "if the toast burns, open the window". Not for every alarm.

## Step by step

1. **Read a traceback from the bottom.** Here's a real one, from code that asked a product for its price:

    ```text
    Traceback (most recent call last):
      File ".../check_price.py", line 9, in <module>
        print(total(product))
              ~~~~~^^^^^^^^^
      File ".../check_price.py", line 5, in total
        return product["price"] * 2
               ~~~~~~~^^^^^^^^^
    KeyError: 'price'
    ```

    The last line says **what**: there is no `"price"` key. The lines above say **where**: line 5, in `total`, which was called from line 9. Read the last line first, then the last file of *your* code. Most of the time, that's enough.

2. **Handle the errors you expect.** Run the example:

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/errors_demo.py"
    ```

    ```bash
    python errors_demo.py
    ```

    ```text
    4.25
    Not a price: 'four'
    0.0
    Missing key: 'price'
    This line runs either way, like cleanup after a test.
    ```

    `float("four")` raises `ValueError`, and the `except ValueError:` handles it. Catch the specific error you expect. A bare `except:` would also hide typos and real bugs.

3. **Use `finally` for cleanup.** The code under `finally` runs whether there was an error or not. Tests use the same idea to delete test data or close a browser, even when the test fails. pytest fixtures do this for you, as you'll see in the [pytest framework](../automation-testing/pytest/index.md) topic.

4. **Raise your own errors, with a message.** In a helper, when input is wrong, say exactly what's wrong:

    ```python
    raise ValueError(f"Age must be a whole number, got '{text}'")
    ```

    "Age must be a whole number, got 'abc'" tells the reader what to fix. A bare `ValueError` doesn't.

5. **Test the error.** `pytest.raises` checks that code raises the right error, and `match` checks the message:

    ```python
    with pytest.raises(ValueError, match="Age must be a whole number"):
        parse_age("abc")
    ```

    That's a [negative test](../manual-testing/test-cases/positive-and-negative-cases.md) that checks the reason, not just "something failed".

    !!! success "Check: you should now be able to"
        Read a traceback from the bottom, catch a specific exception, raise one with a clear message, and test it with `pytest.raises`.

## When it goes wrong

- **The traceback is 50 lines long.** Most of it is library code. Find the lines with your own file names. The last of those is usually where to look.
- **The error is caught, but now nothing tells you something went wrong.** An `except` that only says `pass` hides problems. At least print or log what happened.
- **The error happens only in the pipeline.** Look at the bottom line: is it about a missing file, a missing package or a connection? Those point to the environment, not your code.
- **`pytest.raises` passes, but for the wrong reason.** Add `match=` with part of the expected message, so a different error with the same type doesn't pass.

## Common mistakes

!!! warning "Common mistakes"
    - **Bare `except:`** catches everything, including typos. Name the error.
    - **Reading tracebacks from the top.** The answer is at the bottom.
    - **Error messages without the value.** Include what you got: `got 'abc'`.

!!! failure "If you see this error"
    **`Failed: DID NOT RAISE ValueError`**
    pytest expected an error, and none came. The code accepted the bad input. That's either a bug in the code (report it) or a wrong test (the input wasn't as bad as you thought).

## Try it yourself

Open `exercises/ex07_errors.py`. Write `parse_age(text)`, which raises `ValueError` with the message "Age must be a whole number, got '...'", and `safe_int(text, default=0)`. Run `python -m pytest tests/test_ex07_errors.py`.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex07_errors.py"
    ```

    `from None` hides Python's own error under yours, so the reader sees only the clear message.

## Quick check

1. Which line of a traceback do you read first?

    ??? question "Answer"
        The last one. It says what went wrong.

2. Why catch `ValueError` instead of using a bare `except:`?

    ??? question "Answer"
        A bare `except:` also hides other errors, like typos and real bugs.

3. What does `finally` do?

    ??? question "Answer"
        Its code runs whether there was an error or not, which makes it right for cleanup.

## References

- [Python Tutorial: Errors and exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python: Built-in exceptions](https://docs.python.org/3/library/exceptions.html)
- [pytest: Assertions about expected exceptions](https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
