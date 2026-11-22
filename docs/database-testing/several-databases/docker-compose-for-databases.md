---
title: "Run MySQL, PostgreSQL and MongoDB for Tests With Docker Compose"
description: "Start three test databases with one command: a docker-compose.yml with pinned images, passwords from .env, ports open only to your own computer, and health checks that wait until each database is ready."
level: Intermediate
tags:
  - Database
  - Docker
nav_title: "Docker Compose for test databases"
order: 20
summary: "Start PostgreSQL, MySQL and MongoDB with one command, safely."
updated: "2026-11-22"
---

# Run MySQL, PostgreSQL and MongoDB for Tests With Docker Compose

To test four databases you need four databases. Installing each one on your computer is slow, and each install is a little different. **Docker Compose** starts them all from one file, the same way on every computer and in the pipeline. SQLite needs no server: it's a file, and the tests make it.

!!! note "Before you start"
    Install [Docker Desktop](https://docs.docker.com/get-started/get-docker/) (or Docker Engine on Linux). `docker compose version` should print a version.

## What you will learn

- How a `docker-compose.yml` for test databases is built
- Four safety rules for test databases
- How to start, check and delete them
- What to do when a port is already taken

## Why this matters at work

"Works on my machine" often means "my database is a different version". Pinned images in a Compose file give everyone, and the pipeline, the same databases. Get the safety rules right on day one: test databases with known passwords, open to the whole network, are a common way in for attackers.

## The idea in plain words

!!! info "In plain words"
    A Compose file is a shopping list for a kitchen. It names each appliance, the exact model, and where it plugs in. Hand it to any kitchen and you get the same setup.

## Step by step

1. **Read the file.** The template's `docker-compose.yml`:

    ```yaml
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/docker-compose.yml"
    ```

2. **Check the four safety rules in it.**

    - **Ports only on `127.0.0.1`.** `"127.0.0.1:5432:5432"` opens the port to your own computer only. A plain `"5432:5432"` opens it to every computer on your network, including coffee-shop Wi-Fi.
    - **Passwords from `.env`, never in the file.** `${POSTGRES_PASSWORD:?...}` stops with a message if it's missing, instead of starting with an empty password.
    - **Images pinned to a version and a digest.** `postgres:17.12@sha256:...` is the exact same image every time. `postgres:latest` changes without warning.
    - **No root password anyone knows.** MySQL's root account gets a random password (`MYSQL_RANDOM_ROOT_PASSWORD`). The tests use their own user.

3. **Make the `.env` file.** Copy the example, then change the passwords:

    ```bash
    cp config/.env.example .env
    ```

    ```text
    --8<-- "modules/core_automation/multi_database_testing/templates/multi_db_tests/config/.env.example"
    ```

    `.env` is in `.gitignore`, so it never reaches git. Without it, Compose refuses to start:

    ```text
    error while interpolating services.postgres.environment.POSTGRES_PASSWORD: required variable POSTGRES_PASSWORD is missing a value: Copy config/.env.example to .env first
    ```

4. **Start them, and wait until they're ready.** `--wait` waits for each health check, so the tests don't start against a database that's still booting:

    ```bash
    docker compose up -d --wait
    ```

    ```text
     ...
     Container multi-db-tests-postgres-1 Started
     Container multi-db-tests-mysql-1 Started
     Container multi-db-tests-mongo-1 Started
     Container multi-db-tests-mongo-1 Waiting
     Container multi-db-tests-postgres-1 Waiting
     Container multi-db-tests-mysql-1 Waiting
     Container multi-db-tests-postgres-1 Healthy
     Container multi-db-tests-mongo-1 Healthy
     Container multi-db-tests-mysql-1 Healthy
    ```

5. **Check them.**

    ```bash
    docker compose ps
    ```

    ```text
    NAME                        STATUS                   PORTS
    multi-db-tests-mongo-1      Up 6 seconds (healthy)   127.0.0.1:27017->27017/tcp
    multi-db-tests-mysql-1      Up 6 seconds (healthy)   127.0.0.1:3307->3306/tcp
    multi-db-tests-postgres-1   Up 6 seconds (healthy)   127.0.0.1:5432->5432/tcp
    ```

    Every port starts with `127.0.0.1`. MySQL is on 3307 here because 3306 was taken (see "When it goes wrong").

6. **Delete them when you're done.** `docker compose down -v` stops the databases and deletes their data (`-v` removes the volumes). Next time, they start empty.

    !!! success "Check: you should now be able to"
        Read a Compose file for test databases, check the four safety rules, and start, check and delete the databases.

## When it goes wrong

- **`ports are not available ... bind: address already in use`.** Something on your computer already uses that port, often a database you installed earlier:

    ```text
    Error response from daemon: ports are not available: exposing port TCP 127.0.0.1:3306 -> 127.0.0.1:0: listen tcp4 127.0.0.1:3306: bind: address already in use
    ```

    Don't stop the other program. Pick another port in `.env`: `MYSQL_PORT=3307`. The Compose file and the tests both read it.

- **A container stays "Waiting" and never gets "Healthy".** Look at its log: `docker compose logs mysql`. MySQL's first start takes the longest, often 20 to 30 seconds.
- **The password in `.env` changed, but login still fails.** A database sets its password only on the first start, when its data is empty. Run `docker compose down -v` and start again.

## Common mistakes

!!! warning "Common mistakes"
    - **`"3306:3306"` without `127.0.0.1:`.** The database is open to your whole network.
    - **`image: mysql:latest`.** A new version arrives without warning and the tests change under you.
    - **Committing `.env`.** Check `git status` before every commit.

!!! failure "If you see this error"
    **`required variable POSTGRES_PASSWORD is missing a value`**
    There's no `.env` file in the folder you ran the command from, or the line is missing. Run `cp config/.env.example .env` in the project folder.

## Try it yourself

How would you check, from the output above, that no database is open to other computers?

??? success "Solution"
    In `docker compose ps`, every port begins with `127.0.0.1:`. A port that shows `0.0.0.0:` or no address is open to the network.

## References

- [Docker Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Docker Compose: environment variables and .env](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)
- [Docker Compose: startup order and health checks](https://docs.docker.com/compose/how-tos/startup-order/)
- Official images: [postgres](https://hub.docker.com/_/postgres), [mysql](https://hub.docker.com/_/mysql), [mongo](https://hub.docker.com/_/mongo)

Written for Docker Compose v2, PostgreSQL 17, MySQL 8.4 and MongoDB 8.0. Outputs captured November 2026. Links checked: November 2026.
