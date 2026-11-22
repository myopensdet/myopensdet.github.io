---
title: "Write a Dockerfile for a pytest Test Suite"
description: "Put a pytest suite into its own Docker image: a pinned base image, packages in a cached layer, a normal user instead of root, a .dockerignore that keeps .env out, test reports copied back to your computer, and why localhost inside a container is not your computer."
level: Intermediate
tags:
  - Docker
  - pytest
  - Templates
nav_title: "Dockerfile for a test suite"
order: 20
summary: "Your tests in an image: build it once, run it anywhere."
updated: "2026-11-22"
---

# Write a Dockerfile for a pytest Test Suite

The app is in a container. The database is in a container. Your tests can be too. A **test-runner image** holds your tests, the exact Python and the exact packages they need. Anyone who has the image runs the same tests the same way: on a new laptop, in the pipeline, a year from now. A **Dockerfile** is the recipe for that image.

!!! note "Before you start"
    Read [images and containers](images-and-containers.md). Have the [template project](index.md#templates) open in a terminal.

## What you will learn

- What each line of a test-runner Dockerfile does, and why it's in that order
- How to keep secrets and junk out of the image
- How to build the image, look inside it and run it
- How to get the test reports back onto your computer

## Why this matters at work

Pipelines run tests in containers. If your team has a test image, a new tester runs the suite on day one with one command, and the pipeline runs exactly what you ran. Without it, every computer needs the right Python and packages installed by hand, and "it passes locally" stays a daily argument.

## The idea in plain words

!!! info "In plain words"
    A Dockerfile is a packing list, read from top to bottom: start with this box (the base image), put in these packages, add a user, add the tests, and say what to do when the box is opened. Docker packs it once. Everyone who opens it finds the same things inside.

## Step by step

1. **Read the Dockerfile.** The template's `Dockerfile`:

    ```dockerfile
    --8<-- "modules/infrastructure/docker_for_testers/templates/docker_tests/Dockerfile"
    ```

    | Line | Why |
    | --- | --- |
    | `FROM python:3.13.18-slim-bookworm@sha256:...` | The base image: Debian Linux with Python 3.13.18. `slim` leaves out tools tests don't need. Pinned by digest, so every build starts the same |
    | `ENV ...` | No `.pyc` files, output printed at once, no pip cache in the image |
    | `WORKDIR /tests` | The folder inside the image where everything goes |
    | `COPY requirements.txt .` then `RUN pip install ...` | Packages first, in their own step (see step 5) |
    | `RUN useradd ... tester` | A normal user. Tests don't need root, so they don't get it |
    | `COPY pytest.ini .`, `COPY tests ./tests` | Your tests, last, because they change most |
    | `USER tester` | Everything after this runs as `tester` |
    | `ENTRYPOINT ["python", "-m", "pytest", ...]` | Running the image runs pytest. Words after the image name go to pytest |

2. **Keep things out with `.dockerignore`.** Docker sends the whole folder to the build first. `.dockerignore` says what to leave out:

    ```text
    --8<-- "modules/infrastructure/docker_for_testers/templates/docker_tests/.dockerignore"
    ```

    `.env` holds your passwords: an image can be shared, pushed to a registry and taken apart, so a password in it is a leaked password. `app/` is the app under test: it has its own image.

3. **Build it.** From the template folder:

    ```bash
    docker build -t books-tests:local .
    ```

    `-t` gives the image a name and tag. `.` means "this folder". The build runs each step in order. Shortened to the step lines, the first build looked like this:

    ```text
    #5 [1/7] FROM docker.io/library/python:3.13.18-slim-bookworm@sha256:a5a7...
    #6 [2/7] WORKDIR /tests
    #7 [3/7] COPY requirements.txt .
    #8 [4/7] RUN pip install -r requirements.txt
    #8 DONE 3.3s
    #9 [5/7] RUN useradd --create-home --uid 10001 tester     && mkdir reports     && chown tester:tester reports
    #10 [6/7] COPY pytest.ini .
    #11 [7/7] COPY tests ./tests
    #12 naming to docker.io/library/books-tests:local done
    ```

    It took 5 seconds, with the base image already on the computer. To see every line of the build, add `--progress=plain`.

4. **Look inside before you run it.** Three quick checks:

    ```bash
    docker run --rm books-tests:local --collect-only -q
    ```

    ```text
    tests/test_books_api.py::test_health_says_the_database_is_up
    tests/test_books_api.py::test_a_new_book_can_be_read_back
    tests/test_books_api.py::test_a_new_book_is_saved_in_the_database
    tests/test_books_api.py::test_a_price_of_zero_is_refused
    tests/test_books_api.py::test_an_unknown_book_is_not_found

    5 tests collected in 0.00s
    ```

    `--collect-only -q` went to pytest: the tests are in the image. `--entrypoint` swaps pytest for another command, to list the files and see the user:

    ```bash
    docker run --rm --entrypoint ls books-tests:local -la /tests
    docker run --rm --entrypoint id books-tests:local
    ```

    ```text
    -rw-r--r-- 1 root   root    166 Nov 17 11:23 pytest.ini
    drwxr-xr-x 2 tester tester 4096 Nov 17 11:24 reports
    -rw-r--r-- 1 root   root    208 Nov 17 11:23 requirements.txt
    drwxr-xr-x 2 root   root   4096 Nov 17 11:24 tests
    uid=10001(tester) gid=10001(tester) groups=10001(tester)
    ```

    No `.env`, no `app/`. The tests run as `tester`, who can write only to `reports/`.

5. **See why the order matters.** Each step is a **layer**, and Docker reuses a layer if nothing before it changed. After editing only a test file, the rebuild said:

    ```text
    #7 [4/7] RUN pip install -r requirements.txt
    #7 CACHED
    ...
    #11 [7/7] COPY tests ./tests
    #11 DONE 0.0s
    ```

    0.3 seconds instead of 5. Had `COPY tests` come before `pip install`, every test edit would install every package again. Put what changes least at the top.

6. **Run it, and meet the most common container mistake.** Run the image with nothing else running:

    ```bash
    docker run --rm books-tests:local -x
    ```

    ```text
    E           requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=58180): Max retries exceeded with url: /health (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=58180): Failed to establish a new connection: [Errno 111] Connection refused"))
    ...
    FAILED tests/test_books_api.py::test_health_says_the_database_is_up - request...
    !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
    ============================== 1 failed in 0.04s ===============================
    ```

    The tests' default address is `127.0.0.1`. **Inside a container, `127.0.0.1` and `localhost` mean the container itself**, not your computer. Nothing listens there, so the connection is refused. Even with the app running on your computer, this would fail the same way.

7. **Point it at the app.** Tests read the app's address from `API_URL`, so the same image can test any copy of the app. Start the app and database from the [Compose lesson](compose-test-environments.md) (`docker compose up -d --wait`), then run the image on the same Docker network:

    ```bash
    docker run --rm --network docker-for-testers_default \
      -e API_URL=http://api:8000 \
      books-tests:local -q -k health
    ```

    ```text
    .                                                                        [100%]
    1 passed, 4 deselected in 0.01s
    ```

    On that network, `api` is the app container's name, and Docker turns it into the right address. `-e` sets the setting the tests read.

8. **Get the reports out.** Files written inside the container go away with it. `-v` connects a folder on your computer to a folder inside:

    ```bash
    docker run --rm --network docker-for-testers_default \
      -e API_URL=http://api:8000 \
      -e DATABASE_URL=postgresql://books_tester:local_only_password@db:5432/books \
      -v "$PWD/reports:/tests/reports" \
      books-tests:local
    ```

    ```text
    tests/test_books_api.py .....                                            [100%]

    ----------------- generated xml file: /tests/reports/junit.xml -----------------
    ============================== 5 passed in 0.04s ===============================
    ```

    `reports/junit.xml` is now on your computer. Look at its first line: `hostname` is the container's id, and the time is in UTC (`+00:00`). A report made in a container says nothing about your own computer, unlike the one in [JUnit XML for pipelines](../../automation-testing/reports-and-logs/junit-xml-for-pipelines.md#step-by-step).

    !!! success "Check: you should now be able to"
        Explain each line of a test-runner Dockerfile, keep `.env` out with `.dockerignore`, build the image, check what's inside, explain why `localhost` fails in a container, and run the tests with the app's address and a reports folder.

## When it goes wrong

- **`Connection refused` to `127.0.0.1` or `localhost`.** See step 6: that's the container itself. Use the service name on a Docker network (`http://api:8000`). On Docker Desktop, `http://host.docker.internal:58180` reaches a port on your own computer.
- **`PytestCacheWarning: could not create cache path /tests/.pytest_cache/...: [Errno 13] Permission denied`.** The first version of this template got this on every run: the tests run as `tester`, who can't write to `/tests`. A cache in a thrown-away container is useless anyway, so the `ENTRYPOINT` turns it off with `-p no:cacheprovider`.
- **The build installs every package again after each test edit.** `COPY tests` (or `COPY . .`) comes before `pip install`. Copy `requirements.txt` alone first, as the template does.
- **On Linux, the tests can't write to the reports folder.** The folder on your computer belongs to your user, and `tester` has another user id (10001). Run with your own id: `docker run --user "$(id -u):$(id -g)" ...`. Docker Desktop on macOS and Windows handles this for you.

## Common mistakes

!!! warning "Common mistakes"
    - **`COPY . .` with no `.dockerignore`.** Your `.env`, `.venv` and old reports end up in the image.
    - **Passwords in the Dockerfile** (`ENV DB_PASSWORD=...`). Anyone with the image can read them with `docker image inspect`. Pass them when you run it, with `-e`.
    - **Running as root** because it's the default. Add a user and `USER` it.
    - **A different image for the pipeline and for your laptop.** Build one, and run it in both places.

!!! failure "If you see this error"
    **`ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref ...: "/tests": not found`**
    `COPY tests ./tests` found no `tests` folder in what Docker was sent. You ran `docker build` from the wrong folder, or `.dockerignore` lists `tests/`. Run it from the folder that has the `Dockerfile`.

## Try it yourself

Build the image as `books-tests:try`, and use it to list only the tests with "new_book" in their name, without running them.

??? success "Solution"
    ```bash
    docker build -t books-tests:try .
    docker run --rm books-tests:try --collect-only -q -k new_book
    ```

    ```text
    tests/test_books_api.py::test_a_new_book_can_be_read_back
    tests/test_books_api.py::test_a_new_book_is_saved_in_the_database

    2/5 tests collected (3 deselected) in 0.00s
    ```

    Everything after the image name goes to pytest, so it works the same as on your computer. Careful with `-k book`: it picks all 5, because `-k` also matches the file name, `test_books_api.py`. Remove the image afterwards with `docker image rm books-tests:try`.

## References

- [Docker: Writing a Dockerfile](https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/)
- [Docker: Using the build cache](https://docs.docker.com/get-started/docker-concepts/building-images/using-the-build-cache/)
- [Docker: .dockerignore files](https://docs.docker.com/build/concepts/context/#dockerignore-files)
- [Docker: Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Docker CLI: docker run (env, volumes, network)](https://docs.docker.com/reference/cli/docker/container/run/)

Written for Docker 29, Python 3.13 and pytest 9. Outputs captured November 2026. Links checked: November 2026.
