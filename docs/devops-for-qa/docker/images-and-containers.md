---
title: "Docker Images and Containers for Testers"
description: "The Docker basics a tester needs: what an image and a container are, how to pin an image by digest, run a one-off command, start a database in the background, read its logs, run commands inside it, and clean up, with the errors you will meet on the way."
level: Intermediate
tags:
  - Docker
  - Tools
nav_title: "Images and containers"
order: 10
summary: "Pull, run, look inside, stop and remove: the daily Docker commands."
updated: "2026-11-22"
---

# Docker Images and Containers for Testers

Your tests need things around them: a database, the app, a certain Python version. Installing all of that by hand is slow, and every computer ends up a little different. **Docker** runs each of them in a **container**: a sealed box made from an **image**. The same image gives the same box on your laptop, your teammate's laptop and the pipeline.

!!! note "Before you start"
    Install [Docker Desktop](https://docs.docker.com/get-started/get-docker/) (or Docker Engine on Linux) and start it. [Environment setup](../../getting-started/environment-setup/index.md#5-install-docker) shows how. `docker --version` should print a version.

## What you will learn

- What an image is, what a container is, and how they differ
- How to pin an image so it never changes by surprise
- How to run a one-off command, and a database in the background
- How to look inside a running container, then stop and remove it

## Why this matters at work

"It passes on my machine" is said every week in most teams. Usually the other machine has a different database version, a different Python, or a missing setting. Containers remove most of that. Almost every test pipeline runs its tests in containers, so you will meet them on day one, even if nobody calls it "Docker".

## The idea in plain words

!!! info "In plain words"
    An image is a recipe card. A container is one cake made from it. You can bake many cakes from one card, eat one, and the card stays the same. When you throw a cake away, anything you put on it is gone too.

## Step by step

1. **Check that Docker runs.**

    ```bash
    docker --version
    ```

    ```text
    Docker version 29.9.2, build a82e528
    ```

    Any recent version works for this topic.

2. **Get an image, pinned.** An image has a name and a tag, like `python:3.13.18-slim-bookworm`. A tag can be moved to a newer image at any time. The **digest** (`@sha256:...`) can't: it names one exact image. Use both, and you know which version you meant and get exactly that one:

    ```bash
    docker pull python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
    ```

    ```text
    docker.io/library/python@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72: Pulling from library/python
    Digest: sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
    Status: Image is up to date for python@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
    ```

    The first pull downloads it (about 46 MB). After that, Docker uses the copy on your computer. `docker image ls python` lists the Python images you have.

3. **Run a one-off command.** `docker run` makes a container from the image, runs one command in it, and `--rm` deletes the container when the command ends:

    ```bash
    docker run --rm python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72 \
      python -c "import sys, platform; print(sys.version); print(platform.system(), platform.machine())"
    ```

    ```text
    3.13.18 (main, Nov  5 2026, 08:07:50) [GCC 12.2.0]
    Linux aarch64
    ```

    This was run on a Mac, but the container says `Linux`. Containers are Linux inside, on every computer. `aarch64` is the chip type of this Mac; on most Windows PCs and in most pipelines it says `x86_64`.

4. **See that a container is thrown away.** Start one in the background (`-d`), write a file inside it with `docker exec`, then remove it and start a fresh one:

    ```bash
    docker run -d --name zts-box python:3.13.18-slim-bookworm@sha256:a5a7... sleep 300
    docker exec zts-box sh -c 'echo "test data" > /tmp/note.txt && cat /tmp/note.txt'
    docker rm -f zts-box
    docker run --rm python:3.13.18-slim-bookworm@sha256:a5a7... cat /tmp/note.txt
    ```

    (`a5a7...` stands for the full digest from step 2.)

    ```text
    test data
    zts-box
    cat: /tmp/note.txt: No such file or directory
    ```

    The new container starts clean from the image. For tests that's the point: **every run starts from the same state**. Data you want to keep goes in a volume or a folder on your computer, as [the Dockerfile lesson](dockerfile-for-a-test-suite.md) does with test reports.

5. **Start a database in the background.** This is what testers do most with Docker:

    ```bash
    docker run -d --name zts-postgres \
      -e POSTGRES_PASSWORD=local_only_password \
      -p 127.0.0.1:58133:5432 \
      postgres:17.12@sha256:0d938e975177bef9f1f61f3f9dbcf2e0aa0a139568f66d3415ed8892eb97f6ac
    ```

    | Part | Means |
    | --- | --- |
    | `-d` | Run in the background, and print the container's id |
    | `--name zts-postgres` | A name to use in the next commands, instead of the id |
    | `-e POSTGRES_PASSWORD=...` | A setting for the program inside: here, the database password |
    | `-p 127.0.0.1:58133:5432` | Port 58133 on your computer leads to port 5432 in the container. `127.0.0.1` keeps it open to your computer only |

    Without `127.0.0.1:`, Docker opens the port to every network your computer is on, with a password everyone can read in your shell history. Always add it.

6. **Look at it.**

    ```bash
    docker ps --filter name=zts-
    ```

    ```text
    CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                       NAMES
    007e9fd70463   postgres:17.12   "docker-entrypoint.s…"   4 seconds ago   Up 4 seconds   127.0.0.1:58133->5432/tcp   zts-postgres
    ```

    `--filter name=zts-` shows only the containers whose name has `zts-` in it. Without it, `docker ps` lists every running container on your computer.

    Read what it printed with `docker logs`:

    ```bash
    docker logs zts-postgres | tail -3
    ```

    ```text
    2026-11-17 11:24:26.284 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
    2026-11-17 11:24:26.286 UTC [62] LOG:  database system was shut down at 2026-11-17 11:24:26 UTC
    2026-11-17 11:24:26.288 UTC [1] LOG:  database system is ready to accept connections
    ```

    `ready to accept connections` is the line to wait for. Before it, tests that connect will fail.

7. **Run a command inside it.** `docker exec` runs a command in a running container. Here, the database's own client:

    ```bash
    docker exec zts-postgres psql -U postgres -c "SELECT version();"
    ```

    ```text
     PostgreSQL 17.12 (Debian 17.12-1.pgdg13+1) on aarch64-unknown-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
    (1 row)
    ```

    You don't need `psql` installed on your computer: it's in the image.

8. **Stop and remove it.**

    ```bash
    docker stop zts-postgres
    docker ps -a --filter name=zts-
    docker rm zts-postgres
    ```

    ```text
    CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS                              PORTS     NAMES
    007e9fd70463   postgres:17.12   "docker-entrypoint.s…"   5 seconds ago   Exited (0) Less than a second ago             zts-postgres
    ```

    A stopped container still exists (`docker ps -a` shows it) and keeps its name and data until `docker rm`. `docker rm -f` stops and removes in one step.

    !!! success "Check: you should now be able to"
        Say how an image and a container differ, pull an image pinned by digest, run a one-off command, start a database with a port open only to your computer, read its logs, run a command inside it, and remove it.

## When it goes wrong

- **`failed to connect to the docker API at unix:///...: ... connect: no such file or directory`.** Docker isn't running. Start Docker Desktop and wait until it says it's running. On Linux: `sudo systemctl start docker`.
- **`Bind for 127.0.0.1:58133 failed: port is already allocated`.** Another container (or program) uses that port on your computer. Pick another, like `-p 127.0.0.1:58134:5432`, or stop the other one. `docker ps` shows which container has it.
- **`The container name "/zts-postgres" is already in use`.** A container with that name still exists, maybe stopped. `docker rm -f zts-postgres`, then run again.
- **`Error: Database is uninitialized and superuser password is not specified.`** The PostgreSQL image needs `-e POSTGRES_PASSWORD=...`. Each image's page on Docker Hub lists the settings it needs.
- **The disk fills up.** Old images and stopped containers add up. `docker system df` shows how much. Remove what you made: `docker rm` and `docker image rm <name>`. Be careful with `docker system prune`: it removes every stopped container on your computer, also ones from other projects.

## Common mistakes

!!! warning "Common mistakes"
    - **Using `latest` or a tag alone.** The image can change under you, and a test fails "for no reason". Pin the digest.
    - **`-p 5432:5432` without `127.0.0.1:`.** The database is open to your whole network.
    - **Keeping test data inside a container** and expecting it next time. A new container starts clean.
    - **Running `docker ps` and stopping containers you don't know.** Other projects on your computer use Docker too. Name yours with a prefix and filter by it.

!!! failure "If you see this error"
    **`docker: Error response from daemon: failed to resolve reference "docker.io/library/python:3.13.99-slim": docker.io/library/python:3.13.99-slim: not found`**
    That tag doesn't exist: a typo, or a version that was never released. Check the image's tags on Docker Hub, and copy the name from there.

## Try it yourself

Start the pinned `python` image in the background with the name `zts-try`, and print the Python version from inside it with `docker exec`. Then remove it and check that it's gone.

??? success "Solution"
    ```bash
    docker run -d --name zts-try python:3.13.18-slim-bookworm@sha256:a5a7... sleep 300
    docker exec zts-try python --version
    docker rm -f zts-try
    docker ps -a --filter name=zts-try
    ```

    `docker exec` prints `Python 3.13.18`. The last command prints only the header line: no container is left.

## References

- [Docker: What is a container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Docker: What is an image?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)
- [Docker CLI: docker run](https://docs.docker.com/reference/cli/docker/container/run/)
- [Docker: Image digests](https://docs.docker.com/reference/cli/docker/image/pull/#pull-an-image-by-digest-immutable-identifier)
- [PostgreSQL image on Docker Hub](https://hub.docker.com/_/postgres)

Written for Docker 29 and Docker Desktop. Outputs captured November 2026. Links checked: November 2026.
