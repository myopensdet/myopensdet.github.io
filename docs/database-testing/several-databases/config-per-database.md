---
title: "Database Test Config: One YAML File, Passwords From .env"
description: "Keep the settings for every test database in one YAML file, with passwords in environment variables, and choose which databases a run uses with TEST_DATABASES."
level: Intermediate
tags:
  - Database
  - Python
  - Security
nav_title: "Config per database"
order: 30
summary: "One YAML file for every database, passwords kept out of it."
updated: "2026-11-22"
---

# Database Test Config: One YAML File, Passwords From .env

Four databases means four hosts, ports, names and passwords. Spread through the code, they're impossible to change. In one config file they're easy to read, easy to change for another environment, and easy to keep secrets out of. The rule: **the config file says where, the environment says the password.**

!!! note "Before you start"
    Read [Docker Compose for test databases](docker-compose-for-databases.md). You need the `.env` file from there.

## What you will learn

- How `config/databases.yaml` describes each database
- Why the password isn't in it, and where it comes from instead
- How to choose which databases a run uses
- Why `yaml.safe_load`, never `yaml.load`

## Why this matters at work

The same tests run on your computer, in the pipeline and against staging. Only the settings change. A config file plus environment variables lets one test suite run everywhere, without anyone pasting a password into code.

## The idea in plain words

!!! info "In plain words"
    The config file is the address book: street, house number, name on the door. The password is the key, and keys don't go in the address book. Each person carries their own (the environment).

## Step by step

1. **Read the config file.**

    ```yaml
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/config/databases.yaml"
    ```

    Each database names its `driver`, where to find it, and `password_env`: the name of the variable that holds the password, never the password itself. `port_env` lets `.env` change a port without editing this file. `compare` says which database is the source of truth, and the key column of each table.

2. **See how it's read.** `db_clients/__init__.py`:

    ```python
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/db_clients/__init__.py"
    ```

    - `read_env_file()` loads `.env` into the environment. Real environment variables win, so the pipeline can set its own.
    - `yaml.safe_load` reads plain data only. `yaml.load` with the wrong loader can be made to run code from the file.
    - `make_client()` swaps `password_env` for the real password, and fails with a clear message if it's missing.

3. **Choose which databases run.** By default, all four. Two environment variables change that:

    ```bash
    TEST_DATABASES=sqlite python -m pytest
    ```

    ```text
    SKIPPED [2] tests/test_cross_db_compare.py:26: got empty parameter set for (target)
    SKIPPED [2] tests/test_cross_db_compare.py:31: got empty parameter set for (target)
    8 passed, 4 skipped in 0.03s
    ```

    SQLite alone needs no Docker at all, so it's a quick check on any computer. The comparisons are skipped: they need the source database, PostgreSQL, and this run leaves it out. `LOAD_TEST_DATA` says which databases get fresh test data. The [migration lesson](migration-and-etl-validation.md) uses it to load only the source.

4. **See what happens without passwords.** Each database with no password is skipped, with the reason:

    ```text
    SKIPPED [1] tests/test_data_integrity.py:14: Set POSTGRES_PASSWORD in .env or the environment to test postgres
    SKIPPED [1] tests/test_data_integrity.py:14: Set MYSQL_PASSWORD in .env or the environment to test mysql
    SKIPPED [1] tests/test_data_integrity.py:14: Set MONGO_PASSWORD in .env or the environment to test mongo
    ...
    8 passed, 36 skipped in 0.04s
    ```

    The 8 that passed are the SQLite tests. A database that *has* a password but can't be reached fails instead. In the pipeline, a missing database must never pass quietly.

    !!! success "Check: you should now be able to"
        Describe a database in the config file, keep its password in the environment, and choose which databases a run uses.

## When it goes wrong

- **`pytest.UsageError: TEST_DATABASES: unknown database ['oracle']`.** The name isn't in `config/databases.yaml`. Check the spelling, or add the database.
- **Every test is skipped.** No `.env` in the project folder, or you ran pytest from another folder. The skip reason says which variable is missing.
- **A port in `.env` is ignored.** The line is commented out with `#`, or the database's block in the config has no `port_env`.

## Common mistakes

!!! warning "Common mistakes"
    - **A password in the YAML file.** It goes to git with the file. Use `password_env`.
    - **`yaml.load(f)` without a safe loader.** Use `yaml.safe_load`.
    - **Printing the settings dict in a log or a failure.** It holds the password after `make_client`. The clients print only their name.

!!! failure "If you see this error"
    **`LookupError: Set MYSQL_PASSWORD in .env or the environment to test mysql`**
    Outside pytest, `make_client` raises this instead of skipping. Copy `config/.env.example` to `.env`, or `export MYSQL_PASSWORD=...` in the terminal.

## Try it yourself

Add a second PostgreSQL called `staging`, on host `staging-db.example.com`, port 5432, with its password in `STAGING_DB_PASSWORD`. Then run only it.

??? success "Solution"
    In `config/databases.yaml`:

    ```yaml
      staging:
        driver: postgres
        host: staging-db.example.com
        port: 5432
        database: shop
        user: shop_tester
        password_env: STAGING_DB_PASSWORD
    ```

    Then `TEST_DATABASES=staging LOAD_TEST_DATA=none python -m pytest`. `LOAD_TEST_DATA=none` matters: loading test data drops and re-creates the tables, which you must never do on a shared database.

## References

- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [The Twelve-Factor App: Config](https://12factor.net/config)

Written for Python 3.13, pytest 9.2 and PyYAML 6.0. Outputs captured November 2026. Links checked: November 2026.
