---
title: "Environments in pytest: Local or Staging With One Option, Secrets Kept Out"
description: "How to run the same pytest tests against local and staging: settings per environment in a TOML file, a --env option and TEST_ENV variable in conftest.py, secrets from environment variables, and skipping tests cleanly when a server or token is missing."
level: Beginner
tags:
  - pytest
  - Security
  - CI/CD
nav_title: "Environments"
order: 70
summary: "Run the same tests on local or staging, with secrets kept out of files."
updated: "2026-11-22"
---

# Environments in pytest: Local or Staging With One Option, Secrets Kept Out

The same tests often need to run in several places: on your laptop against a local server, in the pipeline against staging. The tests shouldn't change. Only the settings should: the URL, the timeout, the token. This lesson builds that with a settings file, a `--env` option, and environment variables for secrets, so nothing secret is ever written in the project.

!!! note "Before you start"
    Read [Fixtures and conftest.py](fixtures-and-conftest.md) first. Run the commands from `examples/shop_project`.

## What you will learn

- How to keep settings per environment in a file
- How to add a `--env` option with a `conftest.py` hook
- How to take secrets from environment variables, never from files
- How to skip cleanly when a server or a token isn't there

## Why this matters at work

Tests with `https://staging...` written inside them break when the URL changes, and can't run anywhere else. Tests with a token written inside them leak it the moment the repository is shared. Both are among the most common problems in real test suites, and both are easy to avoid from day one.

## The idea in plain words

!!! info "In plain words"
    The tests are the same play, and the environment is the theatre. The actors don't change their lines in a new theatre. They only need to know the address.
    The keys to the theatre never go in the script. Someone hands them over at the door.

## Step by step

1. **Put the settings in a file.** One section per environment:

    ```toml
    --8<-- "modules/core_automation/pytest_framework/examples/shop_project/config/environments.toml"
    ```

    Note `token_variable`: the file says *where* the token is (an environment variable's name), not what it is.

2. **Add the option in `conftest.py`.** Three hooks do the work: `pytest_addoption` adds `--env`, `pytest_configure` reads the file once and checks the name, and `pytest_report_header` prints the choice at the top of every run:

    ```python
    def pytest_addoption(parser):
        parser.addoption(
            "--env",
            default=os.environ.get("TEST_ENV", "local"),
            help="environment to test, from config/environments.toml (default: local)",
        )
    ```

    The default comes from the `TEST_ENV` variable if it's set, so a pipeline can choose without changing the command.

3. **See which environment a run used.**

    ```bash
    python -m pytest --env staging -m smoke
    ```

    ```text
    environment: staging (https://staging.example.com)
    ```

    That line is near the top of the output, under the Python and pytest versions. When someone asks "which environment was that run on?", the answer is in the log.

4. **Refuse a wrong name clearly.**

    ```bash
    python -m pytest --env prod
    ```

    ```text
    ERROR: Unknown environment 'prod'. Choose one of: local, staging
    ```

    A typo stops the run at once, instead of running everything against the wrong place. Leaving production out of the file on purpose is a good safety habit.

5. **Read secrets from environment variables.** The `api_token` fixture reads the variable named in the file, and skips the test if it isn't set:

    ```python
    @pytest.fixture
    def api_token(env):
        """The token, from an environment variable. Skips the test if it isn't set."""
        token = os.environ.get(env["token_variable"])
        if not token:
            pytest.skip(f"set {env['token_variable']} to run tests that need a token")
        return token
    ```

    On your laptop, set it in the terminal for one run: `SHOP_STAGING_TOKEN=... python -m pytest -m api --env staging` (in PowerShell: `$env:SHOP_STAGING_TOKEN="..."` first). In a pipeline, it comes from the pipeline's secret store. Never print a token, and never write one into a file in the project.

6. **Skip when the server isn't there.** The health test catches the connection error and skips with a reason:

    ```bash
    python -m pytest -m api --env staging
    ```

    ```text
    SKIPPED [1] tests/test_health_api.py:17: no server at https://staging.example.com ([Errno 8] nodename nor servname provided, or not known)
    ====================== 1 skipped, 63 deselected in 0.07s =======================
    ```

    `staging.example.com` doesn't exist, so the test skips, and the reason says why. The text in brackets comes from your system, so it looks a little different on Windows or Linux.

7. **Decide when a skip should be a failure.** On your laptop, "no server" is a reason to skip. In the pipeline's staging job, it's a real problem: staging should be up. A common rule: skip locally, and fail in the pipeline. You can do that with a variable, for example `if os.environ.get("CI"): pytest.fail(...)` instead of `pytest.skip(...)`.

    !!! success "Check: you should now be able to"
        Run the same tests against two environments with `--env`, take a token from an environment variable, and explain when a missing server should skip and when it should fail.

## When it goes wrong

- **Tests ran against the wrong environment.** Look at the `environment:` line in the log. If `TEST_ENV` was set in your terminal from earlier, it changed the default. `echo $TEST_ENV` shows it.
- **The token works on your laptop but not in the pipeline.** The variable has a different name there, or the secret isn't available to that job. Check the name in `environments.toml` against the pipeline's settings.
- **A token appeared in a log.** Someone printed it, or an assert showed it in a failure. Change the token straight away, and remove the print. Don't put secrets into assert messages.
- **Every api test is skipped, always.** Nobody notices skips. Run with `-ra`, read the reasons, and make sure at least one job runs them for real.

## Common mistakes

!!! warning "Common mistakes"
    - **A URL inside a test.** Use the `base_url` fixture.
    - **A password or token in a file in the project**, even "just for testing". Use environment variables.
    - **Production in the environment list** without a very good reason, and a team decision.

!!! failure "If you see this error"
    **`KeyError: 'token_variable'`**
    The environment's section in `environments.toml` is missing a setting the fixtures need. Every section must have the same keys: `base_url`, `timeout` and `token_variable`.

## Try it yourself

Add a third environment, `qa`, with the URL `https://qa.example.com` and the token variable `SHOP_QA_TOKEN`. Run `python -m pytest --env qa -m smoke` and check the header. Then run `--env QA` (capitals). What happens, and is that what you want?

??? success "Solution"
    ```toml
    [qa]
    base_url = "https://qa.example.com"
    timeout = 10
    token_variable = "SHOP_QA_TOKEN"
    ```

    The header says `environment: qa (https://qa.example.com)`. With `--env QA`, the run stops with `Unknown environment 'QA'. Choose one of: local, staging, qa`. Strict is usually right for environment names: a typo should never quietly pick a default.

## Quick check

1. Where should a token come from?

    ??? question "Answer"
        From an environment variable, set in the terminal or by the pipeline's secret store. Never from a file in the project.

2. How does the run show which environment it used?

    ??? question "Answer"
        The `environment:` line in the header, printed by `pytest_report_header`.

3. When should "no server" skip, and when should it fail?

    ??? question "Answer"
        Skip on a laptop, where the server may not be running. Fail in a pipeline job whose whole purpose is to test that server.

## References

- [pytest: Writing hook functions](https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html)
- [pytest: pytest_addoption](https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_addoption)
- [pytest: How to monkeypatch environment variables](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [Python: tomllib](https://docs.python.org/3/library/tomllib.html)
- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
