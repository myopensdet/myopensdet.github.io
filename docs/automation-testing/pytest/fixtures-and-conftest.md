---
title: "Fixtures and conftest.py: Shared Setup and Cleanup Without Copy and Paste"
description: "How pytest fixtures work: asking for a fixture by name, fixtures that use other fixtures, cleanup with yield, fixture scope, built-in fixtures like tmp_path and monkeypatch, and sharing fixtures in conftest.py."
level: Beginner
tags:
  - pytest
  - Test data
nav_title: "Fixtures and conftest.py"
order: 30
summary: "Shared setup and cleanup, without copy and paste."
updated: "2026-11-22"
---

# Fixtures and conftest.py: Shared Setup and Cleanup Without Copy and Paste

A **fixture** is setup that a test asks for by name. Write `def test_total(cart_with_items):`, and pytest builds a cart with items, hands it to the test, and cleans up afterwards. Fixtures can use other fixtures, clean up after themselves with `yield`, and live in `conftest.py` so every test can use them. They're the most important pytest feature after `assert`.

!!! note "Before you start"
    Read [Tests and asserts](tests-and-asserts.md) first. Run the commands from `examples/shop_project`.

## What you will learn

- How to write a fixture, and how a test asks for one
- How fixtures build on each other
- How to clean up after a test with `yield`
- What scope means, and the built-in fixtures you'll use most

## Why this matters at work

Real tests need setup: a logged-in user, test data in a database, a browser. Without fixtures, that setup is copied into every test, and every copy drifts a little. With fixtures, it's written once, cleaned up every time, and tests stay short enough to read.

## The idea in plain words

!!! info "In plain words"
    A fixture is like a hotel room service. The test says "I need a cart with items", and it arrives ready. When the test leaves, someone tidies the room.
    The test never has to know how the room was set up.

## Step by step

1. **Read the fixtures.** These are from `tests/conftest.py`:

    ```python
    @pytest.fixture
    def cart():
        """A new, empty cart for each test."""
        return Cart()

    @pytest.fixture
    def cart_with_items(cart):
        """A cart with two notebooks and a pen: 10.00 in total."""
        cart.add("Pocket notebook", 425, quantity=2)
        cart.add("Pen", 150)
        return cart

    @pytest.fixture
    def order_store():
        """A pretend order database. Everything saved in a test is removed after it."""
        store = []
        yield store
        store.clear()
    ```

2. **A test asks by name.** `def test_saved_order_is_in_the_store(cart_with_items, order_store):` asks for two fixtures. pytest sees the names, runs the fixtures, and passes in what they return. You never call a fixture yourself.

3. **Fixtures use fixtures.** `cart_with_items` asks for `cart`, then adds items. Small fixtures that build on each other are easier to change than one big one.

4. **Clean up with `yield`.** Everything before `yield` is setup. What it yields goes to the test. Everything after runs when the test is done, even if it failed. That's where you delete test data, log out, or close a browser.

5. **Watch it happen.** `--setup-show` prints every setup and teardown:

    ```bash
    python -m pytest -q --setup-show "tests/test_cart.py::test_saved_order_is_in_the_store"
    ```

    ```text
            SETUP    F cart
            SETUP    F cart_with_items (fixtures used: cart)
            SETUP    F order_store
            tests/test_cart.py::test_saved_order_is_in_the_store (fixtures used: cart, cart_with_items, order_store) .
            TEARDOWN F order_store
            TEARDOWN F cart_with_items
            TEARDOWN F cart
    1 passed in 0.00s
    ```

    Setup goes in order, and teardown in reverse. The `F` means **function scope**: a fresh one for each test.

6. **Choose a scope.** `@pytest.fixture(scope="session")` runs once for the whole run. The `env` and `base_url` fixtures in the example use it, because reading the settings file once is enough. Use session scope for things that are slow and never change, like settings or a shared browser. Keep anything a test changes, like a cart or test data, at function scope, so tests can't affect each other.

7. **Use the built-in fixtures.** pytest comes with many:

    | Fixture | Gives you |
    | --- | --- |
    | `tmp_path` | A new empty folder for this test, as a `Path` |
    | `monkeypatch` | Change an environment variable or a function for one test, undone after |
    | `capsys` | What the test printed, so you can assert on it |
    | `request` | Information about the running test, and the command-line options |

    `python -m pytest --fixtures` lists every fixture you can use, with its docstring.

    !!! success "Check: you should now be able to"
        Write a fixture, use it in a test, clean up with `yield`, and choose between function and session scope.

## When it goes wrong

- **`fixture 'carts' not found`.** A typo, or the fixture is in a `conftest.py` that isn't in the test's folder or above. pytest lists the fixtures it does know:

    ```text
    E       fixture 'carts' not found
    >       available fixtures: api_token, base_url, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, cart, cart_with_items, doctest_namespace, env, monkeypatch, order_store, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, subtests, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
    ```

- **Tests pass alone but fail together.** A fixture with a wide scope is shared, and one test changed it. Make it function scope, or make it read-only.
- **Cleanup doesn't run.** Code after `return` never runs. Use `yield` for fixtures that need cleanup.
- **The setup is slow.** Look at `--durations=5`. If the same slow setup runs for every test and nothing changes it, a wider scope may help.

## Common mistakes

!!! warning "Common mistakes"
    - **Calling a fixture like a function**, `cart()`, inside a test. Ask for it as an argument.
    - **Session scope for things tests change.** One test's changes leak into the next.
    - **One huge fixture that sets up everything.** Build small ones that use each other.

!!! failure "If you see this error"
    **`ScopeMismatch: You tried to access the function scoped fixture cart with a session scoped request object`**
    A session fixture asked for a function fixture. A long-lived fixture can't use a short-lived one. Widen the inner fixture's scope, or narrow the outer one.

## Try it yourself

Write a fixture `cart_with_welcome5` that uses `cart`, adds an item worth 2500, and applies WELCOME5. Then write a test that checks the total is 2000.

??? success "Solution"
    ```python
    @pytest.fixture
    def cart_with_welcome5(cart):
        cart.add("Gift card", 2500)
        cart.apply_coupon("WELCOME5")
        return cart

    def test_welcome5_takes_five_off(cart_with_welcome5):
        assert cart_with_welcome5.total() == 2000
    ```

    Put the fixture in `tests/conftest.py` if other files will need it, or in the test file if only that file does.

## References

- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest: Fixtures reference](https://docs.pytest.org/en/stable/reference/fixtures.html)
- [pytest: Built-in fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html#built-in-fixtures)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
