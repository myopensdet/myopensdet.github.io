---
title: "Environment Setup: Python, VS Code and Docker for Test Automation"
description: "Set up a computer for test automation, step by step, on macOS, Windows or Linux: Python 3.13, a terminal, VS Code, Git and Docker, then download a topic's files, make a virtual environment and run your first tests. Or use GitHub Codespaces with nothing to install."
level: Beginner
tags:
  - Getting started
  - Python
  - Docker
nav_title: "Environment setup"
order: 20
summary: "Install Python, VS Code and Docker, and run your first tests."
updated: "2026-11-22"
---

# Environment Setup: Python, VS Code and Docker for Test Automation

Every lesson on this site runs real code on your computer. This page gets your computer ready, once: **Python 3.13** to run tests, **VS Code** to edit them, **Git** to fetch projects, and **Docker** to run the practice databases and the Practice App. At the end you download the files for one topic and run its tests. If you can do that, you can do every lesson.

!!! note "Before you start"
    - About an hour, and permission to install programs on your computer. On a work laptop, IT may need to do some of it.
    - About 10 GB of free disk space. Most of it is for Docker.
    - No coding experience. Type each command exactly as shown, then compare what you see with the box under it.

## What you will learn

- How to open a terminal and type a command
- How to install Python 3.13, and how to check you're really using it
- How to install VS Code, Git and Docker, and check each one works
- How to download a topic's files, make a virtual environment, and run its tests
- What to do when nothing can be installed: GitHub Codespaces

## Why this matters at work

On your first day in a test team, someone hands you a project and says "get the tests running". The steps are always the same as here: the right Python, a virtual environment, `pip install -r requirements.txt`, Docker for the services, then run. Most "the tests don't work on my machine" problems are a step from this page done differently. Do it right once, and you'll know how to check it every time.

## The idea in plain words

!!! info "In plain words"
    Before cooking, you set up the kitchen: a cooker (Python), a worktop (VS Code), a fridge with the ingredients (Docker runs the databases), and a recipe card for each dish (`requirements.txt`). You set up the kitchen once. After that, each new recipe only takes a minute to start.

## Step by step

### 1. Open a terminal

A **terminal** is a window where you type commands instead of clicking. Every lesson uses one.

=== "macOS"

    Press ++cmd+space++, type `Terminal`, press ++enter++.

=== "Windows"

    Press the ++windows++ key, type `PowerShell`, press ++enter++.

=== "Linux"

    Press ++ctrl+alt+t++ on most systems, or find "Terminal" in your apps.

Type a command, then press ++enter++ to run it. In this site's boxes, the first box is what you type. The `text` box under it is what you should see.

### 2. Install Python 3.13

Python runs your tests. Every output on this site was captured with Python 3.13, so use 3.13 to see the same results.

1. **Check what you already have.** Your computer may already have a Python, but an old one:

    ```bash
    python3 --version
    ```

    ```text
    Python 3.9.6
    ```

    This is macOS's own Python. It's too old for the tools on this site, and macOS needs it for itself, so leave it alone and install 3.13 next to it.

2. **Install 3.13** from the official site: [python.org/downloads](https://www.python.org/downloads/). Pick the newest **3.13** release for your system.

    === "macOS"

        Download the macOS installer and click through it. It adds `python3.13` to your terminal.

    === "Windows"

        Download the Windows installer. On the first screen, tick **Add python.exe to PATH**, then click **Install Now**. Windows also gets the `py` command, which picks a Python version for you.

    === "Linux"

        Use your system's package manager if it offers Python 3.13. If not, see [Using Python on Unix platforms](https://docs.python.org/3.13/using/unix.html).

3. **Check you have it.** Close the terminal, open a new one, and ask for 3.13 by name:

    === "macOS and Linux"

        ```bash
        python3.13 --version
        ```

    === "Windows"

        ```powershell
        py -3.13 --version
        ```

    ```text
    Python 3.13.18
    ```

    Any `3.13.x` is fine. From now on, use `python3.13` (or `py -3.13` on Windows) whenever you make a new virtual environment. That way you never get the old Python by mistake.

### 3. Install VS Code

VS Code is a free editor for code. You can use another editor, but the lessons show VS Code.

1. Download it from [code.visualstudio.com](https://code.visualstudio.com/) and install it.
2. Open it, click the **Extensions** icon on the left, search for **Python** and install the one by Microsoft.
3. Later, when you open a project folder that has a `.venv` folder in it, press ++ctrl+shift+p++ (++cmd+shift+p++ on macOS), type `Python: Select Interpreter`, and pick the one inside `.venv`. Then VS Code uses the same Python as your terminal.

### 4. Install Git

Git downloads projects and keeps track of changes. Check if you already have it:

```bash
git --version
```

```text
git version 2.54.0 (Apple Git-157)
```

Any version is fine. If the command isn't found, install it from [git-scm.com/downloads](https://git-scm.com/downloads). On macOS, running `git --version` the first time may offer to install the developer tools: say yes.

### 5. Install Docker

Docker runs programs in **containers**: sealed boxes with everything the program needs. The lessons use it to start a practice database, or the whole Practice App, with one command, and throw it away afterwards.

1. Install **Docker Desktop** for Windows or macOS from [docs.docker.com/get-started/get-docker](https://docs.docker.com/get-started/get-docker/). On Linux, the same page has Docker Engine.
2. Start Docker Desktop and wait until it says it's running.
3. Check it, in the terminal:

    ```bash
    docker --version
    docker compose version
    ```

    ```text
    Docker version 29.9.2, build a82e528
    Docker Compose version v5.6.1
    ```

4. Run Docker's own test container:

    ```bash
    docker run --rm hello-world
    ```

    ```text
    Unable to find image 'hello-world:latest' locally
    latest: Pulling from library/hello-world
    ...
    Hello from Docker!
    This message shows that your installation appears to be working correctly.
    ```

    `--rm` deletes the container after it finishes, so nothing is left behind.

!!! tip "At work"
    Docker Desktop is free for personal use, learning and small companies. A large company needs a paid plan for it. Ask IT before you install it on a work laptop: many companies already have one, or use a different tool.

### 6. Get the files for a topic

Every topic page has a **Templates** section. Each file is in its own tab, and every code block has a **copy** button in its top-right corner.

- **A few files?** Make a new folder, make each file with the same name, and paste the code in.
- **A bigger project?** Get the whole site's code once, with Git. Every topic's files are then in the `modules/` folder:

    ```bash
    git clone https://github.com/myopensdet/myopensdet.github.io.git myopensdet
    cd myopensdet/modules/core_automation/pytest_framework/templates
    ```

    No Git? On the [project's GitHub page](https://github.com/myopensdet/myopensdet.github.io), click **Code**, then **Download ZIP**.

### 7. Run your first tests

This is the routine for every project, on this site and at work.

1. **Go into the project folder.** `cd` means "change directory". Drag the folder onto the terminal window to paste its path, or type it:

    ```bash
    cd myopensdet/modules/core_automation/pytest_framework/templates/pytest_skeleton
    ```

2. **Make a virtual environment with Python 3.13, and turn it on:**

    === "macOS and Linux"

        ```bash
        python3.13 -m venv .venv
        source .venv/bin/activate
        ```

    === "Windows (PowerShell)"

        ```powershell
        py -3.13 -m venv .venv
        .venv\Scripts\Activate.ps1
        ```

    Your prompt now starts with `(.venv)`. Inside it, `python` means the Python in `.venv`:

    ```bash
    python --version
    ```

    ```text
    Python 3.13.18
    ```

3. **Install what the project needs.** `requirements.txt` lists the packages, with exact versions:

    ```bash
    python -m pip install -r requirements.txt
    ```

    ```text
    Successfully installed iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.2.0
    ```

4. **Run the tests:**

    ```bash
    python -m pytest
    ```

    ```text
    ======================= 3 passed, 1 deselected in 0.01s ========================
    ```

    That's your first passing test run. The deselected test needs a running server, so this project leaves it out unless you ask for it: the [pytest framework](../../core-automation/pytest-framework/index.md) topic explains how.

5. **Next time,** you only need `cd` into the folder and `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`). The packages stay installed. When you're done, type `deactivate`.

[Virtual environments and pip](../python-for-testers/virtual-environments-and-pip.md) explains each of these steps in depth.

### 8. Later: the browser for web page tests

Topics that test web pages use Playwright, which drives a real Chromium browser. Inside the project's virtual environment, once per computer:

```bash
python -m playwright install chromium
```

It downloads about 600 MB, so do it when a topic asks for it, not now.

### 9. Nothing can be installed? Use Codespaces

If you can't install programs, for example on a locked work laptop, use **GitHub Codespaces**: a computer in the cloud that opens in your browser, with Python 3.13, VS Code, Docker and the Practice App already set up. You need a free GitHub account. Open the [project on GitHub](https://github.com/myopensdet/myopensdet.github.io), click **Code**, then **Codespaces**, then **Create codespace on main**.

GitHub gives free accounts a monthly allowance of Codespaces hours. Stop the codespace when you're done, so it doesn't use them up.

!!! success "Check: you should now be able to"
    Open a terminal, check your Python is 3.13, run Docker's test container, get a topic's files, make a virtual environment with 3.13, install its `requirements.txt`, and see `3 passed`.

## When it goes wrong

- **`pip` can't find a version.** You made the virtual environment with an old Python. With macOS's own Python 3.9:

    ```text
    ERROR: Could not find a version that satisfies the requirement pytest==9.2.0 (from versions: 2.0.0, 2.0.1, ..., 8.4.1, 8.4.2)
    ERROR: No matching distribution found for pytest==9.2.0
    ```

    pytest 9 doesn't support Python 3.9, so pip lists only the old versions. Delete the folder (`rm -rf .venv`, or `Remove-Item -Recurse .venv` on Windows) and make it again with `python3.13 -m venv .venv`.
- **`zsh:1: command not found: python`** before you activate. On macOS and Linux the command is `python3` or `python3.13` until a virtual environment is on. After `source .venv/bin/activate`, `python` works.
- **Docker commands fail with `failed to connect to the docker API at unix://.../docker.sock; check if the path is correct and if the daemon is running`.** Docker Desktop isn't running. Start it, wait until it says it's running, and try again.
- **PowerShell says running scripts is disabled.** Windows blocks the activate script by default. Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.
- **`BrowserType.launch: Executable doesn't exist at ...`** in a web page test. The browser isn't downloaded yet. Run `python -m playwright install chromium` in the virtual environment.

## Common mistakes

!!! warning "Common mistakes"
    - **Installing packages with no virtual environment on.** They go into the system's Python, or pip refuses. Look for `(.venv)` at the start of the prompt.
    - **Running commands from the wrong folder.** pip can't find `requirements.txt` (see below). `cd` into the project folder first.
    - **Copying the `.venv` folder to another computer or folder.** It only works where it was made. Make a new one and install from `requirements.txt`.
    - **Uninstalling or upgrading the system Python on macOS or Linux.** The system needs it. Install 3.13 next to it instead.

!!! failure "If you see this error"
    **`ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`**
    You're in the wrong folder. Type `ls` (Windows: `dir`) to see what's here, and `cd` into the folder that has `requirements.txt`.

## Try it yourself

Run the [data-driven testing](../../core-automation/data-driven-testing/index.md#templates) tests in a new virtual environment. In the project you got with Git (step 6), they are in `modules/core_automation/data_driven_testing/templates/data_driven_tests`.

??? success "Solution"
    ```bash
    cd myopensdet/modules/core_automation/data_driven_testing/templates/data_driven_tests
    python3.13 -m venv .venv
    source .venv/bin/activate         # Windows: .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m pytest
    ```

    ```text
    38 passed, 1 xfailed
    ```

    The xfailed test is a bug planted in the practice code on purpose. That topic shows how to find it.

## Quick check

1. Why use `python3.13 -m venv` instead of `python3 -m venv`?

    ??? question "Answer"
        `python3` may be an old system Python. Naming 3.13 makes sure the virtual environment gets the right one.

2. What does `(.venv)` at the start of the prompt tell you?

    ??? question "Answer"
        The virtual environment is on, so `python` and `pip` are the ones inside `.venv`.

3. What do you do in a project folder you've never seen before?

    ??? question "Answer"
        Make a virtual environment, activate it, `python -m pip install -r requirements.txt`, then run the tests.

## References

- [Python downloads](https://www.python.org/downloads/)
- [Python: Using Python on Windows](https://docs.python.org/3.13/using/windows.html)
- [Python: Using Python on macOS](https://docs.python.org/3.13/using/mac.html)
- [VS Code: Python in Visual Studio Code](https://code.visualstudio.com/docs/languages/python)
- [Docker: Get Docker](https://docs.docker.com/get-started/get-docker/)
- [GitHub Docs: Creating a codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository)
- [Playwright for Python: Installation](https://playwright.dev/python/docs/intro)

Written for Python 3.13, Docker 29 and VS Code. Outputs captured November 2026. Links checked: November 2026.
