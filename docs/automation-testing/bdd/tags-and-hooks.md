---
title: "Tags and Hooks in behave and pytest-bdd"
description: "Choose which scenarios run with tags like @smoke, handle known bugs with @known_bug, and set things up and clean up with hooks: behave's environment.py and pytest-bdd's fixtures and hook functions."
level: Intermediate
tags:
  - BDD
  - pytest
nav_title: "Tags and hooks"
order: 50
summary: "Pick scenarios with tags; set up and clean up with hooks."
updated: "2026-11-22"
---

# Tags and Hooks in behave and pytest-bdd

**Tags** are labels on scenarios, like `@smoke`. They choose what runs: the five smoke scenarios on every change, everything at night. **Hooks** are code that runs around the scenarios: start the app before everything, give every scenario a fresh cart, take a screenshot when a step fails. Here the two tools differ most, so this lesson shows them side by side.

!!! note "Before you start"
    Read [step definitions](step-definitions.md) and [Fixtures and conftest](../pytest/fixtures-and-conftest.md).

## What you will learn

- How to tag scenarios and run only some of them
- How each tool handles a scenario that fails because of a known bug
- behave's hooks in `environment.py`, and pytest-bdd's fixtures and hooks

## Why this matters at work

A suite with no tags runs everything or nothing. A suite with no hooks repeats setup in every step, leaks state between scenarios, and leaves nothing to look at when a UI test fails at night.

## The idea in plain words

!!! info "In plain words"
    Tags are coloured stickers on folders: "run the red ones first". Hooks are the opening and closing routine of a shop: unlock and switch on before the first customer, tidy after each one, lock up at night.

## Step by step

1. **Tag scenarios.** In the feature files, `@smoke` is on "One book" and "SAVE10 takes 10% off". `@known_bug` is on the scenario that fails because of the planted bug, with the bug id in its description.

2. **Run only the smoke scenarios.**

    === "behave"

        ```bash
        behave --tags=@smoke --format=progress
        ```

        ```text
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 7 skipped
        8 steps passed, 0 failed, 28 skipped
        ```

    === "pytest-bdd"

        ```bash
        python -m pytest -m smoke -v
        ```

        ```text
        collecting ... collected 9 items / 7 deselected / 2 selected
        tests/test_shop.py::test_save10_takes_10_off PASSED                      [ 50%]
        tests/test_shop.py::test_one_book PASSED                                 [100%]
        ======================= 2 passed, 7 deselected in 0.33s ========================
        ```

        Every tag becomes a pytest marker, so `-m` works as usual. With `--strict-markers`, each tag must be listed under `markers` in `pytest.ini`.

3. **Handle a known bug.** The tools differ here.

    === "behave"

        behave has no "expected to fail" result. Its own help suggests leaving such scenarios out with a tag expression. `behave.ini`:

        ```ini
        --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/behave.ini"
        ```

        The normal run skips the scenario. A second run, `behave --tags=@known_bug`, checks the bug is still there:

        ```text
            Then I see the message "Coupon SAVE10 is already applied" # features/steps/shop_steps.py:33
              ASSERT FAILED: Expected message "Coupon SAVE10 is already applied", got "Coupon SAVE10 applied"
        ```

        In the pipeline, run it as its own job that is expected to fail. When it passes, the bug is fixed: remove the tag.

    === "pytest-bdd"

        A hook in `tests/conftest.py` turns the tag into a strict xfail:

        ```python
        def pytest_bdd_apply_tag(tag, function):
            """@known_bug in a feature file becomes a strict xfail that only an assert can satisfy."""
            if tag == "known_bug":
                reason = "Known bug: see the scenario's description"
                pytest.mark.xfail(reason=reason, raises=AssertionError, strict=True)(function)
                return True
            return None  # every other tag becomes a normal marker
        ```

        The normal run shows `XFAIL`. When the bug is fixed, strict makes it fail, so someone removes the tag. `--runxfail` shows the real failure:

        ```text
        E       AssertionError: Expected message "Coupon SAVE10 is already applied", got "Coupon SAVE10 applied"
        ```

4. **Read the hooks.**

    === "behave"

        `features/environment.py`:

        ```python
        --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/features/environment.py"
        ```

        | Hook | Runs | Here it |
        | --- | --- | --- |
        | `before_all` | once, first | starts the shop, and the browser for the UI |
        | `before_scenario` | before each scenario | makes a fresh driver, so no cart leaks between scenarios |
        | `after_scenario` | after each scenario, pass or fail | takes a screenshot if it failed, then closes |
        | `after_all` | once, last | closes the browser and stops the shop |

        There are also `before_feature`, `before_step`, `before_tag` and their `after_` partners.

    === "pytest-bdd"

        `tests/conftest.py`:

        ```python
        --8<-- "modules/core_automation/bdd_testing/templates/bdd_tests/tests/conftest.py"
        ```

        - Fixtures do the setup and clean-up: `base_url` (once per run) starts the shop, `browser` starts Chromium for `--target=ui`, `shop` gives each scenario a fresh driver.
        - `pytest_bdd_step_error` is a pytest-bdd hook: it runs when a step fails, and takes the screenshot.
        - `pytest_bdd_apply_tag` turns tags into markers.

    !!! success "Check: you should now be able to"
        Tag scenarios and run a subset, handle a known bug in each tool, and set up and clean up with hooks.

## When it goes wrong

- **pytest-bdd stops before running anything.** A new tag `@wip` that isn't listed in `pytest.ini`:

    ```text
    'wip' not found in `markers` configuration option
    ERROR tests/test_shop.py - Failed: 'wip' not found in `markers` configuration...
    ```

    Add it under `markers`, or remove the tag.
- **One scenario passes alone and fails in the full run.** State leaks between scenarios. Make it in `before_scenario` or a function-scoped fixture, never in `before_all` or a session fixture.
- **A hook error hides the real error.** The first version of the template's `after_all` closed the shop and the browser without checking they had started. With a wrong target, `before_all` stopped early, and behave showed two errors:

    ```text
    HOOK-ERROR in before_all: ValueError: -D target must be one of ('api', 'ui'), not 'web'
    HOOK-ERROR in after_all: AttributeError: 'Context' object has no attribute 'background_shop'
    ```

    The second one is noise. Clean-up hooks must close only what was started: the template now sets every attribute first in `before_all`, and checks each one in `after_all`.
- **A failed UI scenario has no screenshot.** The hook ran after the page was closed. Take the screenshot before closing, as the template does.

## Common mistakes

!!! warning "Common mistakes"
    - **Tags for everything.** `@cart @coupon @regression @sprint42`: nobody keeps them up to date. A few tags with clear meanings.
    - **Deleting a failing scenario because it's a known bug.** Tag it, and link the bug. When the bug is fixed, you'll know.
    - **Setup in steps that every scenario repeats.** If every scenario needs it and it isn't part of the behaviour, it's a hook.

!!! failure "If you see this error"
    **`0 scenarios passed, 0 failed, 9 skipped`**
    behave ran nothing: a `default_tags` or `--tags` expression matches no scenario. This one was `--tags=@known-bug`. Check the spelling: `@known_bug` and `@known-bug` are different tags.

## Try it yourself

Tag "An unknown coupon changes nothing" with `@smoke` too, and run the smoke scenarios in both tools. How many run now?

??? success "Solution"
    Three in each tool. In behave: `3 scenarios passed, 0 failed, 6 skipped`. In pytest-bdd: `3 passed, 6 deselected`. `smoke` is already listed in `pytest.ini`, so no change is needed there.

## Quick check

1. How do you run only `@smoke` scenarios in each tool?

    ??? question "Answer"
        behave: `--tags=@smoke`. pytest-bdd: `-m smoke`.

2. How does each tool handle `@known_bug` in this template?

    ??? question "Answer"
        behave leaves it out of the normal run and checks it in a second run. pytest-bdd turns it into a strict xfail.

3. Where does a fresh driver for each scenario come from?

    ??? question "Answer"
        behave: `before_scenario`. pytest-bdd: the function-scoped `shop` fixture.

## References

- [behave: Environmental controls (hooks)](https://behave.readthedocs.io/en/latest/tutorial/#environmental-controls)
- [behave: Tag expressions](https://behave.readthedocs.io/en/latest/tag_expressions/)
- [pytest-bdd: Organizing your scenarios, tags and hooks](https://pytest-bdd.readthedocs.io/en/stable/#organizing-your-scenarios)
- [pytest: How to use markers](https://docs.pytest.org/en/stable/how-to/mark.html)

Written for Python 3.13, behave 1.3 and pytest-bdd 9.0. Outputs captured November 2026. Links checked: November 2026.
