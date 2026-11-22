---
title: "Parametrize in pytest: One Test, Many Rows of Data"
description: "How to run one pytest test with many inputs using pytest.mark.parametrize, give each case a readable id with pytest.param, separate passing and refused cases, and use parametrize with fixtures and boundary values."
level: Beginner
tags:
  - pytest
  - Test design
nav_title: "Parametrize"
order: 40
summary: "One test, many rows of data, each with a readable name."
updated: "2026-11-22"
---

# Parametrize in pytest: One Test, Many Rows of Data

Many rules need the same check with different data: WELCOME5 at the minimum, above it, with spaces, in lower case. Instead of five copied tests, `@pytest.mark.parametrize` runs one test once per row. Each row shows up as its own test in the results, so one failing row doesn't hide the others. It's the natural home for [boundary values](../../manual-testing/test-design/boundary-values.md) and [decision tables](../../manual-testing/test-design/decision-tables.md).

!!! note "Before you start"
    Read [Fixtures and conftest.py](fixtures-and-conftest.md) first. Run the commands from `examples/shop_project`.

## What you will learn

- How to write a parametrized test
- How to name each row with `pytest.param(..., id=...)`
- Why passing and refused cases go in separate tests
- How parametrize works together with fixtures

## Why this matters at work

Test design gives you tables of cases. Parametrize turns a table into tests almost line by line. And when a new case comes up, like "what about lower case?", you add one row, not one test.

## The idea in plain words

!!! info "In plain words"
    A form letter: "Dear ___, your order of ___ has shipped." You write it once and fill it in for each customer.
    A parametrized test is a form letter, and each row of data fills in the blanks.

## Step by step

1. **Read the coupon tests.**

    ```python
    --8<-- "modules/core_automation/pytest_framework/examples/shop_project/tests/test_coupons.py"
    ```

2. **Read the decorator.** The first argument names the parameters: `("subtotal", "code", "expected_total")`. The second is the list of rows. pytest runs the test once per row, with those values as arguments.

3. **Name every row.** `pytest.param(2000, "WELCOME5", 1500, id="welcome5-at-the-minimum")` gives the row a name. Run it:

    ```bash
    python -m pytest -v tests/test_coupons.py -m "not nightly"
    ```

    ```text
    tests/test_coupons.py::test_coupon_lowers_the_total[welcome5-at-the-minimum] PASSED [ 12%]
    tests/test_coupons.py::test_coupon_lowers_the_total[welcome5-above-the-minimum] PASSED [ 25%]
    tests/test_coupons.py::test_coupon_lowers_the_total[save10] PASSED       [ 37%]
    tests/test_coupons.py::test_coupon_lowers_the_total[save10-rounds-in-the-shop's-favour] PASSED [ 50%]
    tests/test_coupons.py::test_coupon_lowers_the_total[spaces-and-lower-case] PASSED [ 62%]
    tests/test_coupons.py::test_coupon_is_refused[1999-WELCOME5-WELCOME5 needs an order of at least 20.00] PASSED [ 75%]
    tests/test_coupons.py::test_coupon_is_refused[2000-WELCOME10-Unknown coupon: WELCOME10] PASSED [ 87%]
    tests/test_coupons.py::test_coupon_is_refused[2000--Unknown coupon: ] PASSED [100%]

    ======================= 8 passed, 50 deselected in 0.02s =======================
    ```

    Compare the two styles. The first test's names say what each case is about. The second test has no ids, so pytest builds names from the values, which are long and get messy with spaces and empty strings. Use ids when the values don't explain themselves.

4. **Keep passing and refused cases apart.** `test_coupon_lowers_the_total` checks the total. `test_coupon_is_refused` checks the error and that the total didn't change. Mixing them with `if expected_error:` inside one test makes it hard to read. Two simple tests beat one clever one.

5. **Use fixtures too.** Each row gets a fresh `cart` from the fixture. Parameters and fixtures mix freely in the argument list.

6. **Look at the edge rows.** `1999` and `2000` are the two sides of the WELCOME5 minimum. `155` with SAVE10 checks rounding: 10% of 1.55 is 15.5 cents, and the shop rounds down the discount, so the total is 1.40. Rows like these come straight from [boundary value analysis](../../manual-testing/test-design/boundary-values.md).

7. **Many rows from a range.** `@pytest.mark.parametrize("quantity", range(1, 51))` makes 50 tests. That's what the `nightly` marker on that test is for: big tables can run once a night instead of on every push. See [markers](markers.md).

    !!! success "Check: you should now be able to"
        Write a parametrized test with named rows, keep refused cases in their own test, and add a new case as one row.

## When it goes wrong

- **`In tests/test_coupons.py::test_coupon_lowers_the_total: function uses no argument 'expected'`.** A parameter name in the decorator doesn't match the test's arguments. Make the names the same.
- **`in "parametrize" the number of names (3) ... must be equal to the number of values (2)`.** A row has more or fewer values than there are names. Count them.
- **The test names are unreadable.** Add `id=` to each `pytest.param`, or pass `ids=[...]` to the decorator.
- **One failing row and you want to rerun only it.** Copy its full name from the output: `python -m pytest "tests/test_coupons.py::test_coupon_lowers_the_total[save10]"`. Use quotes, because of the brackets.

## Common mistakes

!!! warning "Common mistakes"
    - **`if` statements inside a parametrized test.** Split it into two tests.
    - **Copying the code's logic into the expected values**, like `expected = subtotal - 500`. Write the number you expect: `1500`.
    - **Hundreds of rows on every push.** Mark big tables `nightly`.

!!! failure "If you see this error"
    **`duplicate parametrization of 'code'`**
    Two `parametrize` decorators on the same test use the same name. Rename one, or merge them into one table.

## Try it yourself

Add two rows to `test_coupon_is_refused`: the code `"SAVE 10"` (with a space) and the code `"WELCOME5"` on a subtotal of `0`. What messages do you expect? Run them.

??? success "Solution"
    ```python
    (2000, "SAVE 10", "Unknown coupon: SAVE 10"),
    (0, "WELCOME5", "WELCOME5 needs an order of at least 20.00"),
    ```

    Both pass. The first one is worth a question to the product owner: should a space inside the code be accepted, like spaces around it are?

## Quick check

1. What does the first argument of `parametrize` say?

    ??? question "Answer"
        The names of the parameters, which must match the test's arguments.

2. Why give rows an `id`?

    ??? question "Answer"
        So each case has a readable name in the results.

3. Why separate passing and refused cases?

    ??? question "Answer"
        They check different things. Two simple tests are easier to read than one with `if` inside.

## References

- [pytest: How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest: pytest.param](https://docs.pytest.org/en/stable/reference/reference.html#pytest-param)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
