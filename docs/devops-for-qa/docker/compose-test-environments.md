---
title: "Docker Compose Test Environments: App, Database and Test Runner"
description: "Build a whole test environment with Docker Compose: a database, the app under test and a test-runner container in one file, started in the right order with health checks, tests run with one command, service names as addresses, reports saved on your computer, and everything deleted afterwards."
level: Intermediate
tags:
  - Docker
  - Templates
  - CI/CD
nav_title: "Compose test environments"
order: 30
summary: "Database, app and tests in one file, started with one command."
updated: "2026-11-22"
---

# Docker Compose Test Environments: App, Database and Test Runner

A real test run needs several things at once: a database, the app on top of it, and the tests. They must start in the right order, find each other, and disappear afterwards. **Docker Compose** does all of that from one file, `docker-compose.yml`. With it, one command builds the environment and runs the tests, and another deletes it.

!!! note "Before you start"
    Read [the Dockerfile lesson](dockerfile-for-a-test-suite.md). For the database part of Compose in more depth, see [Docker Compose for test databases](../../database-testing/several-databases/docker-compose-for-databases.md). Have the [template project](index.md#templates) open in a terminal.

## What you will learn

- How a Compose file describes an app, its database and a test runner
- How health checks make each part wait until the one before it is ready
- How to run the tests with one command, and why the exit code matters
- How services find each other by name, and how to clean up

## Why this matters at work

"Run the tests" often means: start the database, wait, run migrations, start the app, wait, set five settings, then run pytest. Written in a wiki, it goes out of date. Written as a Compose file, it's the same on every laptop and in the pipeline, and it's checked every time someone runs it.

## The idea in plain words

!!! info "In plain words"
    A Compose file is a stage plan for a play. It lists every actor (database, app, tests), when each walks on (only after the one before is ready), and what each needs. The director (`docker compose`) reads the plan and runs the whole show. When it's over, the stage is cleared.

## Step by step

1. **Read the file.** The template's `docker-compose.yml`:

    ```yaml
    --8<-- "modules/infrastructure/docker_for_testers/templates/docker_tests/docker-compose.yml"
    ```

    | Key | What it does |
    | --- | --- |
    | `name: docker-for-testers` | The project name. Every container, network and volume starts with it, so it never mixes with other projects on your computer |
    | `services:` | One entry per container: `db`, `api`, `tests` |
    | `image: postgres:17.12@sha256:...` | A pinned image from Docker Hub |
    | `build: ./app` and `image: books-api:local` | Build an image from `app/Dockerfile`, and call it `books-api:local` |
    | `${POSTGRES_PASSWORD:?...}` | Read the password from `.env`. Stop with a message if it's missing |
    | `ports: "127.0.0.1:..."` | Open a port on your own computer only, never to the network |
    | `healthcheck:` | A command that says "ready" or "not yet" |
    | `depends_on: ... condition: service_healthy` | Start this one only when that one is healthy |
    | `profiles: ["tests"]` | `tests` starts only when you ask for it |
    | `volumes: ./reports:/tests/reports` | Reports written in the container land in `reports/` on your computer |

2. **Make your `.env`.** The password never goes in the Compose file:

    ```bash
    cp .env.example .env
    ```

    Then change the password in `.env`. Without the file, Compose stops before starting anything:

    ```text
    error while interpolating services.db.environment.POSTGRES_PASSWORD: required variable POSTGRES_PASSWORD is missing a value: Copy .env.example to .env first
    ```

3. **Start the database and the app.**

    ```bash
    docker compose up -d --wait
    ```

    `--wait` returns only when every service is healthy. Shortened, the order was:

    ```text
     Container docker-for-testers-db-1 Started
     Container docker-for-testers-db-1 Waiting
     Container docker-for-testers-db-1 Healthy
     Container docker-for-testers-api-1 Starting
     Container docker-for-testers-api-1 Started
     Container docker-for-testers-api-1 Healthy
    ```

    The app started only after the database was healthy. It took 5 seconds. Check them with `docker compose ps`:

    ```text
    NAME                       IMAGE             ...   SERVICE   STATUS                   PORTS
    docker-for-testers-api-1   books-api:local   ...   api       Up 2 seconds (healthy)   127.0.0.1:58180->8000/tcp
    docker-for-testers-db-1    postgres:17.12... ...   db        Up 5 seconds (healthy)   127.0.0.1:58132->5432/tcp
    ```

    The app answers on your computer too: `curl http://127.0.0.1:58180/health` prints `{"status":"ok","database":"up"}`.

4. **Run the tests.**

    ```bash
    docker compose run --rm tests
    ```

    ```text
     Container docker-for-testers-api-1 Waiting
     Container docker-for-testers-api-1 Healthy
     Container docker-for-testers-tests-run-65c21d7b359b Creating
     Container docker-for-testers-tests-run-65c21d7b359b Created
    ============================= test session starts ==============================
    platform linux -- Python 3.13.18, pytest-9.2.0, pluggy-1.7.0
    rootdir: /tests
    configfile: pytest.ini
    testpaths: tests
    collected 5 items

    tests/test_books_api.py .....                                            [100%]

    ----------------- generated xml file: /tests/reports/junit.xml -----------------
    ============================== 5 passed in 0.05s ===============================
    ```

    - `run` starts a one-off `tests` container. It also starts `db` and `api` first if they aren't running, so `docker compose run --rm tests` alone is enough.
    - `--rm` deletes the test container afterwards.
    - Add `--build` after changing a test. Without it, Compose runs the image it built last time.
    - `reports/junit.xml` is now on your computer.

5. **Know how services find each other.** In the file, the app reaches the database at `db:5432`, and the tests reach the app at `http://api:8000`. Compose puts all services on one network, `docker-for-testers_default`, where **each service's name is its address**. The app's log shows who called it:

    ```bash
    docker compose logs api --tail 4
    ```

    ```text
    api-1  | INFO:     172.20.0.4:40722 - "POST /books HTTP/1.1" 201 Created
    api-1  | INFO:     172.20.0.4:40722 - "GET /books/3 HTTP/1.1" 200 OK
    api-1  | INFO:     172.20.0.4:40722 - "POST /books HTTP/1.1" 422 Unprocessable Content
    api-1  | INFO:     172.20.0.4:40722 - "GET /books/999999 HTTP/1.1" 404 Not Found
    ```

    `172.20.0.4` is the test container's address on that network. You never type it: use the name.

6. **Check the exit code.** Pipelines decide "passed" or "failed" from the exit code, not from the text. Run with a wrong address on purpose:

    ```bash
    docker compose run --rm -e API_URL=http://localhost:8000 tests
    echo $?
    ```

    ```text
    E           requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /health ...
    ...
    ============================== 5 failed in 0.19s ===============================
    1
    ```

    `localhost` is the test container itself, so every test fails, and `docker compose run` passes pytest's exit code on: `1`. With all tests passing, it's `0`. That's how a pipeline knows.

7. **Run the same tests from your computer.** The ports in `.env` are open on `127.0.0.1`, so the tests also run outside Docker, from a virtual environment with `requirements.txt` installed. The tests read both addresses from the environment:

    ```bash
    DATABASE_URL=postgresql://books_tester:local_only_password@127.0.0.1:58132/books python -m pytest -q
    ```

    Use the password from your `.env`. `API_URL` isn't needed: its default is `http://127.0.0.1:58180`. Handy while writing a test: no rebuild after each edit.

8. **Clean up.**

    ```bash
    docker compose down -v
    ```

    ```text
     Container docker-for-testers-api-1 Removed
     Container docker-for-testers-db-1 Removed
     Network docker-for-testers_default Removed
    ```

    `down` removes the containers and the network. `-v` also removes the database's data, so the next run starts empty. Leave `-v` off to keep the data between runs.

9. **One command for a pipeline.** Run the tests, keep their exit code, always clean up, then pass the code on:

    ```bash
    docker compose run --rm --build tests; status=$?
    docker compose down -v
    exit $status
    ```

    In a pipeline, `.env` doesn't exist: set `POSTGRES_PASSWORD` as a secret variable instead, and Compose reads it the same way. [CI/CD](../ci-cd/index.md) builds on this.

    !!! success "Check: you should now be able to"
        Read a Compose file with a database, an app and a test runner, start them in order with health checks, run the tests with one command, explain how services find each other by name, use the exit code, and delete everything afterwards.

## When it goes wrong

- **`required variable POSTGRES_PASSWORD is missing a value`.** No `.env` next to `docker-compose.yml`. `cp .env.example .env`, then set a password.
- **`port is already allocated`.** Something on your computer uses 58180 or 58132. Change `API_PORT` or `DB_PORT` in `.env`. The containers talk to each other inside the network, so only your computer's side changes.
- **The tests run old code.** `docker compose run` reuses the last image. Add `--build`.
- **The app container keeps restarting, or never gets healthy.** Read its log: `docker compose logs api`. A wrong `DATABASE_URL` or a database that isn't ready are the usual reasons.
- **Old data breaks a test.** You ran `down` without `-v`, so the database kept last run's rows. Use `down -v`, or write tests that don't depend on an empty database.

## Common mistakes

!!! warning "Common mistakes"
    - **`depends_on` without `condition: service_healthy`.** It only waits for the container to start, not for the database to be ready. Tests fail now and then, and look flaky.
    - **`localhost` in the URLs between services.** Use the service names.
    - **Passwords written into `docker-compose.yml`.** The file is committed. Use `${VARIABLE}` and `.env`.
    - **Forgetting `down -v` in the pipeline after a failure.** Keep the exit code, clean up, then exit with it.

!!! failure "If you see this error"
    **`no such service: apii`** from `docker compose run --rm tests`
    A service name in `depends_on` doesn't match one under `services:`: here `apii` instead of `api`. Names must match exactly, letter for letter. `docker compose --profile tests config` checks the whole file without starting anything, and names the problem: `service "tests" depends on undefined service "apii"`. Without `--profile tests` it skips the `tests` service and finds nothing wrong.

## Try it yourself

See a test run from the app's side: start the environment, run the tests, then show only the lines of the app's log with `POST` in them. Then clean up.

??? success "Solution"
    ```bash
    docker compose up -d --wait
    docker compose run --rm tests
    docker compose logs api | grep POST
    docker compose down -v
    ```

    You see three `POST /books` lines: two `201 Created` from the tests that add a book, and one `422 Unprocessable Content` from the price-of-zero test.

## References

- [Docker Compose: How Compose works](https://docs.docker.com/compose/intro/compose-application-model/)
- [Docker Compose: Control startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Docker Compose: Networking](https://docs.docker.com/compose/how-tos/networking/)
- [Docker Compose: Profiles](https://docs.docker.com/compose/how-tos/profiles/)
- [Docker CLI: docker compose run](https://docs.docker.com/reference/cli/docker/compose/run/)

Written for Docker 29 and Docker Compose 5. Outputs captured November 2026. Links checked: November 2026.
