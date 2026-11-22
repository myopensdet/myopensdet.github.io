---
title: "Classes and Objects: The Idea Behind Page Objects and API Clients"
description: "Python classes for testers: class, __init__, self, attributes and methods, making several objects from one class, and why page objects, API clients and test users are written as classes."
level: Beginner
tags:
  - Python
  - Clean code
nav_title: "Classes and objects"
order: 60
summary: "Bundle data and actions together: the idea behind page objects and API clients."
updated: "2026-11-22"
---

# Classes and Objects: The Idea Behind Page Objects and API Clients

A **class** bundles data and the actions that go with it. A test user has a name and a role (data), and can or can't ship orders (an action). The class is the blueprint; each **object** made from it is one real user. You'll meet classes everywhere in test code: page objects for UI tests, API clients, test data builders. This lesson shows the parts, so those frameworks stop looking like magic.

!!! note "Before you start"
    Read [Functions](functions.md) first. A method is a function that belongs to a class.

## What you will learn

- How to write a class with `__init__`, attributes and methods
- What `self` means
- How several objects from one class keep their own data
- Where classes show up in test frameworks

## Why this matters at work

In a UI test suite, a `LoginPage` class knows where the username box is and how to log in. Tests call `login_page.log_in("arshad", "...")` instead of repeating locators everywhere. When the page changes, you fix one class. That's the [Page Object Model](../automation-testing/playwright/index.md), and it's just a class.

## The idea in plain words

!!! info "In plain words"
    A class is a cookie cutter. Each object is a cookie: same shape, but each one can have different icing.
    `self` means "this cookie", the one you're talking about right now.

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/classes_demo.py"
    ```

    ```bash
    python classes_demo.py
    ```

    ```text
    arshad customer False
    admin1 admin True
    [TestUser('arshad', 'customer'), TestUser('admin1', 'admin')]
    ```

2. **`__init__` sets up a new object.** `TestUser("arshad")` runs `__init__` with `name="arshad"`. The lines `self.name = name` store the values on the object. They're called **attributes**.

3. **Methods are functions inside the class.** `can_ship_orders(self)` uses `self.role` to answer. You call it on an object: `admin.can_ship_orders()`. Python passes the object in as `self` for you.

4. **Each object has its own data.** `arshad` and `admin` came from the same class, but have different names and roles, and different answers.

5. **`__repr__` controls how an object prints.** Without it, Python prints something like `<__main__.TestUser object at 0x...>`. With it, a failing test shows `TestUser('arshad', 'customer')`, which you can read at a glance. Worth adding to any class used in tests.

6. **Know when not to write a class.** If it's only data, a dictionary is often enough. If it's only one action, a function is enough. Write a class when data and actions belong together, like a page and the things you can do on it.

    !!! success "Check: you should now be able to"
        Write a class with `__init__`, attributes and a method, make two objects from it, and explain what `self` is.

## When it goes wrong

- **`TypeError: TestUser.__init__() missing 1 required positional argument: 'name'`.** You made an object without giving `__init__` what it needs: `TestUser()` instead of `TestUser("arshad")`.
- **`TypeError: TestUser.can_ship_orders() takes 0 positional arguments but 1 was given`.** You forgot `self` in the method's `def` line. Every method's first parameter is `self`.
- **`AttributeError: 'TestUser' object has no attribute 'rol'. Did you mean: 'role'?`** A typo, or the attribute is never set in `__init__`. Set every attribute there, even if it starts as `None`.
- **Two objects share data they shouldn't.** You put a list in the class body, not in `__init__`. Lists made in `__init__` with `self.items = []` belong to each object.

## Common mistakes

!!! warning "Common mistakes"
    - **Forgetting `self`**, in the `def` line or before an attribute (`name` instead of `self.name`).
    - **Calling the class instead of the object.** `TestUser.can_ship_orders()` instead of `admin.can_ship_orders()`.
    - **A class for everything.** Use one when data and actions belong together.

!!! failure "If you see this error"
    **`NameError: name 'role' is not defined. Did you mean: 'self.role'?`**
    Python's hint is right. Inside a method, the object's data is on `self`. Write `self.role`, not `role`.

## Try it yourself

Open `exercises/ex06_classes.py`. Write a `Cart` class with `add(name, price, quantity=1)`, `count()` and `total()`. One test checks that two carts don't share items. Run `python -m pytest tests/test_ex06_classes.py`.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex06_classes.py"
    ```

    `self.items = []` is in `__init__`, so each cart gets its own list. That's what makes the "two carts" test pass.

## Quick check

1. What is the difference between a class and an object?

    ??? question "Answer"
        The class is the blueprint. An object is one thing made from it, with its own data.

2. What does `self` mean in a method?

    ??? question "Answer"
        The object the method was called on.

3. Name one place classes are used in test automation.

    ??? question "Answer"
        Page objects for UI tests, API clients, or test data builders.

## References

- [Python Tutorial: Classes](https://docs.python.org/3/tutorial/classes.html)
- [Python: object.__repr__](https://docs.python.org/3/reference/datamodel.html#object.__repr__)

Written for Python 3.13. Links checked: November 2026.
