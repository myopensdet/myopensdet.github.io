---
title: "Markers in pytest: Smoke, Nightly and API, and Choosing What Runs"
description: "How to label pytest tests with markers, register them in pytest.ini, run or leave out groups with -m, use the built-in skip, skipif and xfail markers, and catch marker typos with --strict-markers."
level: Beginner
tags:
  - pytest
  - CI/CD
nav_title: "Markers"
order: 50
summary: "Label tests as smoke, nightly or api, and choose which ones run."
updated: "2026-11-22"
---

# Markers in pytest: Smoke, Nightly and API, and Choosing What Runs

A **marker** is a label on a test: `@pytest.mark.smoke`. With `-m smoke`, only tests with that label run. Teams use markers to run a quick set on every push, a long set every night, and tests that need a server only when there is one. pytest also has built-in markers to skip a test, or to mark a known bug.

!!! note "Before you start"
    Read [Tests and asserts](tests-and-asserts.md) first. Run the commands from `examples/shop_project`.

## What you will learn

- How to mark tests, and register markers in `pytest.ini`
- How to choose what runs with `-m`
- The built-in markers: `skip`, `skipif` and `xfail`
- How `--strict-markers` catches typos

## Why this matters at work

A pipeline that runs every test on every push gets slow, and people stop waiting for it. Markers let the team decide: smoke tests in two minutes on every push, the full set at night, API tests on staging before a release. Same tests, different selections.

## The idea in plain words

!!! info "In plain words"
    Markers are coloured stickers on folders: red for urgent, blue for "end of month".
    When you're in a hurry, you grab only the red ones.

## Step by step

1. **Register your markers.** In `pytest.ini`, each marker gets a line with a short description:

    ```ini
    markers =
        smoke: a few quick checks of the most important things, run on every push
        nightly: long checks, run once a night
        api: needs a running server (run with -m api)
    ```

    `python -m pytest --markers` lists them, at the top:

    ```text
    @pytest.mark.smoke: a few quick checks of the most important things, run on every push

    @pytest.mark.nightly: long checks, run once a night
    ```

2. **Mark tests.** Put the marker above the test: `@pytest.mark.smoke`. A test can have several. A marker above a parametrized test applies to every row.

3. **Run only the smoke tests.**

    ```bash
    python -m pytest -m smoke -v
    ```

    ```text
    tests/test_cart.py::test_new_cart_is_empty PASSED                        [ 50%]
    tests/test_cart.py::test_total_of_two_items PASSED                       [100%]

    ======================= 2 passed, 62 deselected in 0.03s =======================
    ```

    `-m` takes `and`, `or` and `not`: `-m "not nightly"`, `-m "smoke or api"`. "Deselected" means "not chosen this time", not "failed".

4. **Skip with a reason.** `@pytest.mark.skip(reason="...")` always skips. `@pytest.mark.skipif(sys.platform == "win32", reason="...")` skips when the condition is true. Inside a test or fixture, `pytest.skip("...")` skips at run time, which is how the example's `api_token` fixture skips when no token is set. Always give a reason: `-ra` prints it at the end.

5. **Mark a known bug with `xfail`.** `@pytest.mark.xfail(reason="BUG-123: refunds on day 30 refused")` says "this is expected to fail until the bug is fixed". The run stays green, and the report lists it as `XFAIL`. With `xfail_strict = true` in `pytest.ini`, a test marked xfail that starts passing fails the run. Then someone notices the bug is fixed, and removes the marker.

6. **Let `--strict-markers` catch typos.** Without it, `@pytest.mark.smok` quietly makes a new marker, and that test never runs with `-m smoke`. With it, the run stops:

    ```text
    ERROR test_typo.py - Failed: 'smok' not found in `markers` configuration option
    ```

    That's the `typo_demo` folder. The example project has `--strict-markers` in `addopts`, so it's always on.

    !!! success "Check: you should now be able to"
        Register and use markers, run a selection with `-m`, skip a test with a reason, and mark a known bug with `xfail`.

## When it goes wrong

- **`-m smoke` runs nothing.** No test has the marker, or it's spelled differently. `python -m pytest -m smoke --co -q` lists what would run.
- **`PytestUnknownMarkWarning: Unknown pytest.mark.smoke - is this a typo?`** The marker isn't registered. Add it to `markers =` in `pytest.ini`, and turn on `--strict-markers` so it becomes an error next time.
- **Many tests are skipped and nobody knows why.** Run with `-ra` and read the reasons. Skips without reasons, or with old ones, are hidden gaps in testing.
- **An xfail test has been there for a year.** Check its bug. If it's "won't fix", maybe the test is wrong. If it's still open, ask about it in triage.

## Common mistakes

!!! warning "Common mistakes"
    - **Using `skip` for a known bug.** Use `xfail` with the bug's ID, so you hear when it's fixed.
    - **Too many markers.** Three or four that the team really uses beat fifteen.
    - **Smoke tests that take ten minutes.** Smoke means fast. Keep it to the most important few.

!!! failure "If you see this error"
    **`[XPASS(strict)] BUG-123: refunds on day 30 refused`**
    A test marked `xfail` passed, and `xfail_strict` turned that into a failure. Good news: the bug is probably fixed. Check it, then remove the `xfail` marker and close the bug.

## Try it yourself

Mark `test_coupon_is_refused` as `smoke`, then run `python -m pytest -m smoke`. How many tests run now, and why that number?

??? success "Solution"
    Five: the two cart smoke tests, plus the three rows of `test_coupon_is_refused`. A marker on a parametrized test applies to every row.

## References

- [pytest: How to mark test functions with attributes](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest: How to use skip and xfail](https://docs.pytest.org/en/stable/how-to/skipping.html)
- [pytest: Working with custom markers](https://docs.pytest.org/en/stable/example/markers.html)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
