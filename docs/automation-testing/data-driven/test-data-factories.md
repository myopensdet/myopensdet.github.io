---
title: "Test Data Factories: Valid by Default, One Change per Test"
description: "A factory makes a complete, valid test object in one call, and lets each test change only the field it is about. Plain Python dataclasses and Faker, no extra library. Includes checks over hundreds of generated orders."
level: Intermediate
tags:
  - Test data
  - Python
  - pytest
nav_title: "Test data factories"
order: 50
summary: "A valid object in one call; each test changes only what it's about."
updated: "2026-11-22"
---

# Test Data Factories: Valid by Default, One Change per Test

A signup has a name, an email, a password and an age. A test about age shouldn't have to spell out the other three, and when a fifth field is added, 40 tests shouldn't break. A **factory** makes a complete, valid object in one call. The test changes **only the field it's about**, and the test reads like its title.

!!! note "Before you start"
    Read [fake data with Faker](fake-data-with-faker.md).

## What you will learn

- How to write a factory with a dataclass and Faker
- How "valid by default, one change per test" keeps tests short and clear
- How to check a rule over hundreds of generated objects

## Why this matters at work

Test data is where test suites rot. Every test builds its own objects, a new required field arrives, and dozens of tests need editing. With factories, the new field is added in one place. Tests also say what matters: `make_signup(age=17)` can only be about age.

## The idea in plain words

!!! info "In plain words"
    A bakery has a standard cake. For a birthday, they change only the writing on top. Nobody re-describes the flour, eggs and oven for every order.

## Step by step

1. **Read the factories.** `helpers/factories.py`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/helpers/factories.py"
    ```

    - Each object is a frozen `dataclass`: its fields have names, and a test can't change it by accident.
    - `make_signup()` fills every field with a valid, typical value. `**changes` replaces just the fields a test names.
    - Ages are 21 to 90 on purpose: typical adults. The edges (17, 18) are fixed rows in `signup_cases.csv`, so the factory never hits a bug by luck.

2. **Change one thing per test.** `tests/test_with_factories.py`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/tests/test_with_factories.py"
    ```

    - `test_too_young_is_the_only_problem`: everything else is valid, so `['age']` must be the only problem. If the email were also wrong by accident, the test would say so.
    - `test_members_never_pay_more` and `test_a_total_is_never_negative_or_more_than_the_subtotal`: rules that hold for *every* order. 200 generated orders each, with a mix of coupons and members, checked in milliseconds. `assert ..., order` prints the order that broke the rule.

3. **Run it.**

    ```bash
    python -m pytest tests/test_with_factories.py -v
    ```

    ```text
    fake data seed: 46950 (repeat with TEST_SEED=46950)
    tests/test_with_factories.py::test_a_typical_signup_is_fine PASSED       [ 25%]
    tests/test_with_factories.py::test_too_young_is_the_only_problem PASSED  [ 50%]
    tests/test_with_factories.py::test_members_never_pay_more PASSED         [ 75%]
    tests/test_with_factories.py::test_a_total_is_never_negative_or_more_than_the_subtotal PASSED [100%]
    ============================== 4 passed in 0.01s ===============================
    ```

4. **Know when to reach for a library.** For objects that save to a database or link to each other (an order needs a customer, who needs an address), [factory_boy](https://factoryboy.readthedocs.io/en/stable/) adds sub-factories and saving. For plain test objects, a dataclass and a function are enough, and need nothing new installed.

    !!! success "Check: you should now be able to"
        Write a factory that makes a valid object, change one field per test, and check a rule over many generated objects.

## When it goes wrong

- **`TypeError: Signup.__init__() got an unexpected keyword argument 'agee'. Did you mean 'age'?`** A typo in a change. The dataclass catches it: a plain dict would have quietly added a new key.
- **A factory test fails for a reason the test isn't about.** The factory made an invalid object. Fix the factory's default, never the test.
- **A rule over 200 generated orders fails.** Read the order in the message, then run again with the printed seed. Turn that order into a fixed row in a data file, so it's checked on every run.

## Common mistakes

!!! warning "Common mistakes"
    - **Factories that make edge values by default.** Defaults are typical and valid. Edges are what tests ask for by name.
    - **Building objects by hand in every test.** One new field breaks all of them.
    - **One giant factory with options for every case.** Keep factories small. Tests say what's special.

!!! failure "If you see this error"
    **`dataclasses.FrozenInstanceError: cannot assign to field 'age'`**
    The test tried `signup.age = 17`. Make a new object instead: `make_signup(age=17)`.

## Try it yourself

Add a test: a signup with a 7-character password has only one problem, `password`.

??? success "Solution"
    ```python
    def test_short_password_is_the_only_problem():
        signup = make_signup(password="short12")
        assert check_signup(signup.email, signup.password, signup.age) == ["password"]
    ```

## Quick check

1. What does "valid by default" mean?

    ??? question "Answer"
        Calling the factory with no changes gives an object that passes every rule.

2. Why are the factory's ages 21 to 90, and not 18 to 90?

    ??? question "Answer"
        Edges are tested by fixed rows, on every run. The factory gives typical values, so it never hits a bug by luck.

## References

- [Python: dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Faker documentation](https://faker.readthedocs.io/en/master/)
- [factory_boy documentation](https://factoryboy.readthedocs.io/en/stable/)

Written for Python 3.13, pytest 9.2 and Faker 40.54. Outputs captured November 2026. Links checked: November 2026.
