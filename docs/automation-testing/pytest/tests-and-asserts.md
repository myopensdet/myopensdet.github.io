---
title: "Tests and Asserts in pytest: Write a Test, Read a Failure"
description: "How to write pytest tests with plain assert, name them so a failure explains itself, check errors with pytest.raises, run tests in different ways, and read pytest's failure output line by line."
level: Beginner
tags:
  - pytest
  - Python
nav_title: "Tests and asserts"
order: 20
summary: "Write a test with assert, check errors, and read a failure line by line."
updated: "2026-11-22"
---

# Tests and Asserts in pytest: Write a Test, Read a Failure

A pytest test is a function whose name starts with `test`, with one or more `assert` lines. If every `assert` is true, the test passes. If one is false, pytest stops that test and shows exactly what the values were. That's all there is to the basics. The skill is in writing tests that say one clear thing, and in reading failures fast.

!!! note "Before you start"
    Read [Project layout](project-layout.md) first. Run the commands from `examples/shop_project`.

## What you will learn

- How to write a test with `assert`
- How to name tests so failures explain themselves
- How to check that code raises the right error
- How to read pytest's failure output

## Why this matters at work

Most of your day with tests is reading results. A well-named test with a clear assert tells you what broke before you open a file. A vague one ("test_cart_2 failed") sends you digging.

## The idea in plain words

!!! info "In plain words"
    An assert is a sentence that must be true: "the total is 10.00". pytest reads every sentence. If one is false, it shows you what it found instead.

## Step by step

1. **Read the tests.**

    ```python
    --8<-- "modules/core_automation/pytest_framework/examples/shop_project/tests/test_cart.py"
    ```

    Each test name is a sentence about the cart: `test_quantity_zero_is_refused`. Prices are in whole cents, so `1000` is 10.00. The arguments, like `cart_with_items`, are **fixtures**: ready-made setup from `conftest.py`. The [next lesson](fixtures-and-conftest.md) explains them.

2. **Run them with `-v`** to see every name:

    ```bash
    python -m pytest -v tests/test_cart.py
    ```

    ```text
    tests/test_cart.py::test_new_cart_is_empty PASSED                        [ 20%]
    tests/test_cart.py::test_total_of_two_items PASSED                       [ 40%]
    tests/test_cart.py::test_items_keep_their_order PASSED                   [ 60%]
    tests/test_cart.py::test_quantity_zero_is_refused PASSED                 [ 80%]
    tests/test_cart.py::test_saved_order_is_in_the_store PASSED              [100%]

    ============================== 5 passed in 0.02s ===============================
    ```

3. **Check errors with `pytest.raises`.** `test_quantity_zero_is_refused` passes only if `add` raises `ValueError`, and `match=` checks the message too. Without `match`, a `ValueError` for the wrong reason would also pass.

4. **Read a failure.** The `assert_demo` folder has two tests that fail on purpose:

    ```bash
    cd ../assert_demo
    python -m pytest
    ```

    ```text
        def test_total_is_wrong():
            total = 425 * 2 + 150
    >       assert total == 1100
    E       assert 1000 == 1100
    ```

    The `>` marks the line that failed. The `E` line shows the real values: `total` was `1000`, not `1100`. pytest rewrites your `assert` to show this, so you don't need special methods like `assertEqual`.

5. **Read a failure on a dictionary.** The second test compares two API-like responses:

    ```text
    E       AssertionError: assert {'id': 7, 'na... 'price': 450} == {'id': 7, 'na... 'price': 425}
    E  
    E         Omitting 2 identical items, use -vv to show
    E         Differing items:
    E         {'price': 450} != {'price': 425}
    ```

    pytest skips the parts that match and shows only `price`. With `-vv`, it shows everything. Put the real value on the left and the expected value on the right, and keep doing it the same way, so failures always read the same.

6. **Choose what runs.** One file: `python -m pytest tests/test_cart.py`. One test: add `::test_total_of_two_items`. By name: `-k refused` runs every test with "refused" in its name. Stop at the first failure: `-x`.

    !!! success "Check: you should now be able to"
        Write a test with a clear name and assert, check an error with `pytest.raises`, and read a failure from its `>` and `E` lines.

## When it goes wrong

- **A test passes but checks nothing.** A test with no `assert` always passes. Every test needs at least one check. If you can't think of one, ask what the test is for.
- **One test has ten asserts.** When the first fails, the rest never run, and you only see one problem. Split it into tests that each check one thing.
- **The failure shows `'...'` and you can't see the difference.** Run that test with `-vv` for the full values.
- **`assert` on a float fails by a tiny amount.** Use whole cents like this project, or `pytest.approx`: `assert total == pytest.approx(10.0)`.

## Common mistakes

!!! warning "Common mistakes"
    - **Printing instead of asserting.** pytest can't read a printed "OK".
    - **Names like `test_1` or `test_cart_2`.** Say what should be true.
    - **`pytest.raises` without `match`.** The right error type for the wrong reason still passes.

!!! failure "If you see this error"
    **`PytestAssertRewriteWarning: assertion is always true, perhaps remove parentheses?`**
    You wrote `assert (total == 1100, "total is wrong")`. The brackets make a tuple, and a tuple with something in it is always true, so the test can never fail. Write it without brackets: `assert total == 1100, "total is wrong"`.

## Try it yourself

Write a test in `tests/test_cart.py` that checks a negative price is refused with the message "Price can't be negative, got -1". Run it with `-k negative`.

??? success "Solution"
    ```python
    def test_negative_price_is_refused(cart):
        with pytest.raises(ValueError, match="Price can't be negative, got -1"):
            cart.add("Pen", -1)
    ```

    `python -m pytest -k negative -v` should show one test, passed.

## Quick check

1. What do the `>` and `E` lines in a failure mean?

    ??? question "Answer"
        `>` is the line that failed. `E` shows the error, with the real values.

2. Why add `match=` to `pytest.raises`?

    ??? question "Answer"
        So the test passes only for the right error message, not any error of that type.

3. How do you run only the tests with "refused" in their name?

    ??? question "Answer"
        `python -m pytest -k refused`.

## References

- [pytest: How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- [pytest: pytest.raises](https://docs.pytest.org/en/stable/reference/reference.html#pytest-raises)
- [pytest: pytest.approx](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
