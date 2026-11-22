---
title: "pytest Project Layout: Where Tests, Code, Settings and Fixtures Go"
description: "A pytest project layout that a team and a pipeline can run: src for the code under test, tests with conftest.py, pytest.ini, config per environment, requirements.txt and a README, and how pytest finds your tests."
level: Beginner
tags:
  - pytest
  - Python
nav_title: "Project layout"
order: 10
summary: "Where tests, code, settings and fixtures go, and how pytest finds tests."
updated: "2026-11-22"
---

# pytest Project Layout: Where Tests, Code, Settings and Fixtures Go

A good layout means anyone can open the project and know where things are: the tests in `tests`, shared setup in `conftest.py`, settings in `pytest.ini`, URLs in `config`. It also means pytest finds everything without long commands. This lesson walks through the layout of this topic's example project, folder by folder.

!!! note "Before you start"
    Read [Modules and imports](../../programming-for-testers/modules-and-imports.md) if imports are new to you.

## What you will learn

- A layout that works for most test projects
- What each file and folder is for
- How pytest finds test files and test functions
- When to split tests into more folders

## Why this matters at work

You'll often join a team whose tests are in one folder of 200 files, with setup copied into each. A clear layout is the first fix, and it makes every later change cheaper. When you start a new project, the [skeleton](index.md#templates) gives you this layout in one copy.

## The idea in plain words

!!! info "In plain words"
    A kitchen has a place for everything: knives in the drawer, plates in the cupboard, spices on the shelf. A new cook finds things without asking.
    A test project is the same. Everyone knows where to look.

## Step by step

1. **Look at the layout.** This is the example project:

    ```text
    shop_project/
    ├── pytest.ini                 settings and markers
    ├── config/
    │   └── environments.toml      URLs and timeouts per environment
    ├── src/
    │   └── shop/
    │       ├── __init__.py
    │       └── cart.py            the code under test
    └── tests/
        ├── conftest.py            shared fixtures and the --env option
        ├── test_cart.py
        ├── test_coupons.py
        └── test_health_api.py
    ```

    The skeleton adds `requirements.txt`, `.gitignore` and a `README.md`. A real project should have all three.

2. **`src/` holds the code under test.** Here it's a small shop. In many test projects there's no `src` at all, because the tests call an API or a web page instead. Then you only need `tests`.

3. **`tests/` holds the tests.** pytest finds files named `test_*.py` or `*_test.py`, and inside them, functions whose names start with `test`. Name files after what they test: `test_cart.py`, `test_coupons.py`.

4. **`conftest.py` holds shared fixtures.** pytest loads it automatically. You never import it. Fixtures in `tests/conftest.py` can be used by every test under `tests`. The [fixtures lesson](fixtures-and-conftest.md) covers it.

5. **`pytest.ini` holds the settings.** Where the tests are, which markers exist, which options always apply. Its folder is the project's **rootdir**: run pytest from there. The [pytest.ini lesson](pytest-ini.md) goes line by line.

6. **`config/` holds per-environment settings.** URLs and timeouts for local and staging, never passwords. The [environments lesson](environments.md) shows how tests choose one.

7. **Split when it grows.** With a few dozen files, folders by test level or area help: `tests/unit/`, `tests/api/`, `tests/ui/`. Each folder can have its own `conftest.py` for fixtures only it needs. Fixtures from the `conftest.py` above are still available.

    !!! success "Check: you should now be able to"
        Sketch a test project's layout, say what each part is for, and explain how pytest finds tests.

## When it goes wrong

- **pytest says `no tests ran`.** Check the names: `test_cart.py`, not `cart_test.py` (unless configured) or `testcart.py`; and `def test_...`. Also check you're in the folder with `pytest.ini`.
- **`ModuleNotFoundError: No module named 'shop'`.** pytest can't find the code under test. Add `pythonpath = src` to `pytest.ini`, as the example does.
- **Two test files with the same name in different folders clash.** pytest can complain about duplicate module names. Give them different names, or add an empty `__init__.py` to each test folder.
- **The project only runs on one person's machine.** Something is missing from the repository: `requirements.txt`, a config file, or a step in the README. Ask a teammate to set it up from scratch, and write down what they needed.

## Common mistakes

!!! warning "Common mistakes"
    - **Importing from `conftest.py`.** pytest loads it. Use fixtures by naming them as test arguments.
    - **Tests next to the code in random places.** Keep them under `tests`.
    - **No README.** Two lines that say how to install and run save every newcomer an hour.

!!! failure "If you see this error"
    **`ERROR: file or directory not found: tests/test_carts.py`**
    The path in the command doesn't exist. Check the spelling, and check that you're running from the project folder, not from inside `tests`.

## Try it yourself

Your team has a folder with `login_tests.py`, `checkout.py` (which has tests in it) and `helpers.py` with setup that every file copies. Sketch a better layout.

??? success "Solution"
    ```text
    project/
    ├── pytest.ini
    ├── requirements.txt
    ├── README.md
    └── tests/
        ├── conftest.py        the setup from helpers.py, as fixtures
        ├── test_login.py      was login_tests.py
        └── test_checkout.py   the tests from checkout.py
    ```

    The file names now match what pytest looks for, and the shared setup lives in one place.

## References

- [pytest: Good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [pytest: Conventions for Python test discovery](https://docs.pytest.org/en/stable/explanation/goodpractices.html#conventions-for-python-test-discovery)
- [pytest: Initialization, rootdir and configfile](https://docs.pytest.org/en/stable/reference/customize.html)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
