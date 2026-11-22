---
title: "Static Analysis Tools: Let a Tool Read Your Test Code First"
description: "How static analysis tools like Ruff and gitleaks find bugs without running code, a real test file where pytest says 3 passed while Ruff finds 5 mistakes, and a pre-commit setup to run the checks before every commit."
level: Beginner
tags:
  - Reviews
  - Tools
  - Python
nav_title: "Static analysis tools"
order: 50
summary: "Tools that read your code and find bugs in seconds, before any test runs."
updated: "2026-11-22"
---

# Static Analysis Tools: Let a Tool Read Your Test Code First

Some bugs are easy for a tool and hard for a person. An unused import, a variable name with a typo, an `assert` that can never fail. A person reading 500 lines will miss a few. A tool reads them all in less than a second, every time. Static analysis tools do this: they read code without running it, and point at the lines that look wrong. This lesson shows what they catch in real test code, and how to make them run automatically.

!!! note "Before you start"
    Read [What static testing is](what-is-static-testing.md) first. Knowing a little Python and pytest helps.
    To run the examples: `pip install pytest ruff`, then run the commands from the `examples/static_analysis` folder.

## What you will learn

- What a static analysis tool is, and the main kinds
- A real test file where pytest says "3 passed" but five things are wrong
- How to read Ruff's output, and fix what it finds
- How to run the checks before every commit with pre-commit

## Why this matters at work

Test code has bugs too, and bugs in tests are sneaky: a broken test often *passes*, so nobody looks at it. A static analysis tool finds many of these for free. It also ends whole categories of review comments ("unused import", "use `is None`"), so people can spend review time on things only people can judge.

## The idea in plain words

!!! info "In plain words"
    A spell checker underlines a word before you send your email. It doesn't know what you meant to say, but it knows "recieve" is wrong.
    A static analysis tool is a spell checker for code. It doesn't know what your test should check, but it knows `assert (x == 2, "message")` can never fail.

The main kinds you will meet:

| Kind | What it finds | Common tools |
| --- | --- | --- |
| Linter | Bugs and risky patterns: undefined names, unused imports, broken asserts | [Ruff](https://docs.astral.sh/ruff/) (Python), ESLint (JavaScript) |
| Formatter | Layout: spaces, line breaks, quotes. Ends style arguments | Ruff format, Black, Prettier |
| Type checker | Wrong types: passing text where a number is expected | mypy, Pyright |
| Secret scanner | Passwords, keys and tokens in code | [gitleaks](https://github.com/gitleaks/gitleaks) |

## Step by step

1. **Look at a test file with real mistakes.** Each one is common in real projects. Try to spot them before reading on:

    ```python
    --8<-- "modules/think_like_a_tester/static_testing_and_reviews/examples/static_analysis/test_cart_mistakes.py"
    ```

2. **Run the tests, and see what pytest tells you.**

    ```bash
    python -m pytest -q test_cart_mistakes.py
    ```

    Here is the important part of the output:

    ```text
    >       assert cart == ["pen"]
    E       AssertionError: assert ['book', 'pen'] == ['pen']

    test_cart_mistakes.py:14
      .../test_cart_mistakes.py:14: PytestAssertRewriteWarning: assertion is always true, perhaps remove parentheses?
        assert (len(cart) == 2, "the cart should have one item")

    FAILED test_cart_mistakes.py::test_adding_to_a_new_cart - AssertionError: ass...
    1 failed, 3 passed, 1 warning in 0.03s
    ```

    Look at what this means. **Three tests passed**, but none of them really checked anything:

    - `test_adding_one_item` passed, even though it asks for 2 items and the cart has 1. The `assert` is a tuple in brackets, which is always true. pytest prints a warning, but only the first time it reads the file. Run it again and the warning is gone.
    - `test_empty_name_is_refused` passed, but the bare `except: pass` would hide any error, or none.
    - And `test_adding_to_a_new_cart` failed with a confusing message: where did "book" come from? From the *other* test. The default `cart=[]` is created once and shared by every call.

3. **Run Ruff on the same file.**

    ```bash
    ruff check --select E,F,B --output-format concise test_cart_mistakes.py
    ```

    ```text
    test_cart_mistakes.py:4:8: F401 [*] `json` imported but unused
    test_cart_mistakes.py:7:25: B006 Do not use mutable data structures for argument defaults
    test_cart_mistakes.py:14:5: F631 Assert test is a non-empty tuple, which is always `True`
    test_cart_mistakes.py:25:5: E722 Do not use bare `except`
    test_cart_mistakes.py:31:24: E711 Comparison to `None` should be `cond is None`
    Found 5 errors.
    [*] 1 fixable with `--fix` (2 unsafe fixes available with `--fix --unsafe-fixes`).
    ```

    Five problems, with file, line and column, in a fraction of a second, without running a test. Each line is `file:line:column: code message`. The code (like `F631`) has its own page in the [Ruff rules](https://docs.astral.sh/ruff/rules/) list, with an example and the fix. B006 is the shared cart, explained before any test ran.

4. **Fix them, and check again.** `--fix` repairs the safe ones, like the unused import. Fix the rest by hand. Here is the same file, fixed:

    ```python
    --8<-- "modules/think_like_a_tester/static_testing_and_reviews/examples/static_analysis/test_cart_fixed.py"
    ```

    ```bash
    ruff check --select E,F,B test_cart_fixed.py
    python -m pytest -q test_cart_fixed.py
    ```

    ```text
    All checks passed!
    4 passed in 0.02s
    ```

    Now "4 passed" means something. Each test can fail, and each one checks what its name says.

5. **Save the settings, so you don't type them.** Copy the [ruff.toml template](index.md#templates) into your project's main folder, named `ruff.toml`:

    ```toml
    --8<-- "modules/think_like_a_tester/static_testing_and_reviews/templates/ruff_settings.toml"
    ```

    Now plain `ruff check` uses these rules, and so does everyone else on the team.

6. **Run the checks before every commit.** [pre-commit](https://pre-commit.com/) runs tools automatically when you type `git commit`, and stops the commit if something is wrong. Save the [template](index.md#templates) as `.pre-commit-config.yaml`:

    ```yaml
    --8<-- "modules/think_like_a_tester/static_testing_and_reviews/templates/pre-commit-config.yaml"
    ```

    Then, once per computer:

    ```bash
    pip install pre-commit
    pre-commit install
    pre-commit run --all-files
    ```

    From now on, every commit is checked by gitleaks (no passwords or keys), Ruff (bugs and format) and a few small checks. This site uses the same setup, which is how every one of its commits is checked.

    !!! success "Check: you should now be able to"
        Explain why "3 passed" was misleading, read a Ruff line, fix what it finds, and set up pre-commit.

## When it goes wrong

- **Ruff reports hundreds of problems on an old project.** Don't fix them all in one go. Run `ruff check --fix` for the safe ones, then turn on rules a few at a time. Or check only the files you change, so the code gets better a little with every pull request.
- **A rule is wrong for one line.** Add `# noqa: E711` at the end of that line, with a short reason in a comment. Use it rarely. If you need it often, the rule may not fit your team: turn it off in `ruff.toml` instead.
- **pre-commit stops your commit and you're in a hurry.** Read the message first: it is usually a 10-second fix. `git commit --no-verify` skips the checks, but use it only in an emergency. gitleaks is there to stop a password from reaching the repository, and that can't be undone by deleting it later.
- **The team argues about style.** Let the formatter decide. Run `ruff format`, agree to accept its output, and never discuss spaces in a review again.

## Common mistakes

!!! warning "Common mistakes"
    - **Trusting "passed" without reading the test.** A test that can't fail always passes.
    - **Running tools only on your computer.** Put them in pre-commit and in the pipeline, so everyone runs the same checks.
    - **Turning off a rule instead of understanding it.** Read the rule's page first. Most rules exist because of real bugs.

!!! failure "If you see this error"
    **`pre-commit: command not found`**
    pre-commit isn't installed, or not in this virtual environment. Install it with `python -m pip install pre-commit`, then run `python -m pre_commit install`.

## Try it yourself

What would Ruff say about this test, and what is wrong with it?

```python
def test_discount():
    price = 100
    discounted = price * 0.9
    assert (discounted == 90, "10% off")
```

??? success "Solution"
    Ruff reports **F631**: the `assert` is a tuple, so it is always true. The test can never fail, whatever `discounted` is.

    Fix it by removing the brackets: `assert discounted == 90, "10% off"`. Then break it on purpose (change 0.9 to 0.8) and check that it fails. Watching a test fail once is the best proof it can.

## Quick check

1. Why can a broken test be worse than no test?

    ??? question "Answer"
        It passes, so everyone thinks the feature is checked, and nobody looks at it.

2. What does `F631` mean?

    ??? question "Answer"
        The `assert` is a non-empty tuple, so it is always true and can never fail.

3. What does pre-commit do?

    ??? question "Answer"
        It runs the checks automatically on every `git commit`, and stops the commit if something is wrong.

## References

- [Ruff documentation](https://docs.astral.sh/ruff/) and [Ruff rules](https://docs.astral.sh/ruff/rules/)
- [Ruff: assert-tuple (F631)](https://docs.astral.sh/ruff/rules/assert-tuple/) and [mutable-argument-default (B006)](https://docs.astral.sh/ruff/rules/mutable-argument-default/)
- [pre-commit](https://pre-commit.com/): run checks before every commit
- [gitleaks](https://github.com/gitleaks/gitleaks): find passwords and keys before they are committed

Written for Python 3.13, pytest 9 and Ruff 0.17. Links checked: November 2026.
