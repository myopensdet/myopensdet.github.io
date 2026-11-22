---
title: "pytest.ini: The Settings File, Line by Line"
description: "What goes into pytest.ini: testpaths, pythonpath, addopts, markers and xfail_strict, how pytest finds its settings file, and how to check which settings and tests are in use."
level: Beginner
tags:
  - pytest
  - Tools
nav_title: "pytest.ini"
order: 60
summary: "The settings file, line by line, and how to check what's in use."
updated: "2026-11-22"
---

# pytest.ini: The Settings File, Line by Line

`pytest.ini` holds the settings that every run should use: where the tests are, where the code is, which options are always on, and which markers exist. With it, `python -m pytest` does the right thing for everyone, the same way, without a long command. This lesson goes through the example project's file line by line.

!!! note "Before you start"
    Read [Markers](markers.md) first. Run the commands from `examples/shop_project`.

## What you will learn

- What each line of a typical `pytest.ini` does
- How pytest finds the settings file, and why you run from its folder
- How to check which tests would run, without running them
- Where else pytest settings can live

## Why this matters at work

When the options live in people's heads, everyone runs the tests differently, and results differ. When they live in `pytest.ini`, the pipeline and every laptop run the same thing. It's also the first file to read in a project you've just joined.

## The idea in plain words

!!! info "In plain words"
    `pytest.ini` is the settings menu of a phone, saved once. You don't choose the language and the ringtone every time you make a call.

## Step by step

1. **Read the file.**

    ```ini
    --8<-- "modules/core_automation/pytest_framework/examples/shop_project/pytest.ini"
    ```

2. **`[pytest]`** starts the section. Without it, pytest ignores the file.

3. **`testpaths = tests`** tells pytest where to look when you don't name a path. It's faster, and it stops pytest from collecting stray files in other folders.

4. **`pythonpath = src`** adds `src` to the places Python looks for imports, so tests can write `from shop.cart import Cart`. Without it, you'd get `ModuleNotFoundError`.

5. **`addopts`** adds options to every run:

    - `-ra` lists every test that didn't pass at the end, with the reason.
    - `--strict-markers` makes marker typos an error.
    - `-m "not api"` leaves out tests that need a server. A `-m` you type on the command line replaces it: `-m api` runs only those, and `-m ""` runs everything.

6. **`markers =`** registers the markers, one per line, with a description. See [markers](markers.md).

7. **`xfail_strict = true`** turns an unexpected pass of an `xfail` test into a failure, so fixed bugs don't stay marked as broken.

8. **Check what would run.** `--co` (collect only) lists the tests without running them:

    ```bash
    python -m pytest --co -q
    ```

    ```text
    63/64 tests collected (1 deselected) in 0.01s
    ```

    The `-m "not api"` in `addopts` deselected the health check. Use `--co` whenever you change `testpaths`, markers or `-k`, to check before a long run.

9. **Know where settings can live.** pytest looks for its settings in `pytest.ini`, `pyproject.toml` (under `[tool.pytest.ini_options]`), `tox.ini` or `setup.cfg`, starting from the folders of the paths you give it and moving up. The first one it finds wins, and its folder becomes the rootdir. The header of a normal run shows which one: `configfile: pytest.ini`. One settings file per project avoids surprises.

    !!! success "Check: you should now be able to"
        Explain each line of a `pytest.ini`, check which tests would run with `--co`, and find which settings file pytest is using.

## When it goes wrong

- **pytest ignores your settings.** You ran it from another folder, or another settings file higher up was found first. Look at the `rootdir:` and `configfile:` lines at the top of a normal run.
- **An option in `addopts` is wrong, and every run fails.** pytest stops with `error: unrecognized arguments`. Check the spelling, and whether that option needs a plugin you haven't installed.
- **`-m` on the command line doesn't add to the one in `addopts`.** That's how it works: the last `-m` wins. If you want both, write them together: `-m "smoke and not api"`.
- **Tests from a `venv` or `node_modules` folder are collected.** Set `testpaths`, so pytest only looks where your tests are.

## Common mistakes

!!! warning "Common mistakes"
    - **Forgetting `[pytest]`.** Then the file is ignored, quietly.
    - **Settings in two files.** `pytest.ini` and `pyproject.toml` both with settings confuse everyone. Pick one.
    - **A huge `addopts`.** Keep options that every run needs. Put the rest in the README.

!!! failure "If you see this error"
    **`python -m pytest: error: unrecognized arguments: --strict-marker`**
    An option in `addopts` or on the command line is misspelled (`--strict-marker` instead of `--strict-markers`), or belongs to a plugin that isn't installed. Fix the spelling, or install the plugin.

## Try it yourself

Change the example's `pytest.ini` so smoke tests are the default selection, instead of "not api". Check with `--co -q` how many tests are collected. Then put it back.

??? success "Solution"
    Change the `addopts` line to `addopts = -ra --strict-markers -m smoke`. Then `python -m pytest --co -q` shows `2/64 tests collected (62 deselected)`. That's a quick default for a pre-push check, but most teams keep the default wide and choose smoke in the pipeline instead.

## Quick check

1. What does `testpaths = tests` do?

    ??? question "Answer"
        It tells pytest to look for tests in `tests` when no path is given.

2. Why put `--strict-markers` in `addopts`?

    ??? question "Answer"
        So every run treats marker typos as errors, not only when someone remembers the option.

3. How do you see which tests would run, without running them?

    ??? question "Answer"
        `python -m pytest --co -q`.

## References

- [pytest: Configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [pytest: Configuration options reference](https://docs.pytest.org/en/stable/reference/reference.html#ini-options-ref)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
