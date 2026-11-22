---
title: "Virtual Environments and pip: Install Tools for One Project at a Time"
description: "Why every Python test project needs its own virtual environment, how to create and activate one on macOS, Linux and Windows, install packages with pip, pin versions in requirements.txt, and check which Python you're really using."
level: Beginner
tags:
  - Python
  - Tools
nav_title: "Virtual environments and pip"
order: 100
summary: "Give each project its own Python packages, and pin their versions."
updated: "2026-11-22"
---

# Virtual Environments and pip: Install Tools for One Project at a Time

**pip** installs Python packages, like pytest or Playwright. A **virtual environment** is a folder with its own copy of Python and its own packages, for one project. Without one, every project shares the same packages, and upgrading pytest for one project can break another. With one, each project has exactly what it needs, and `requirements.txt` lets anyone rebuild it.

!!! note "Before you start"
    You need Python 3.11 or newer. On macOS and Linux the command may be `python3`; on Windows it is often `py`.

## What you will learn

- Why each project needs its own virtual environment
- How to create and activate one, on each system
- How to install packages, and pin them in `requirements.txt`
- How to check which Python and which packages you're really using

## Why this matters at work

"Works on my machine" often means "my machine has a different version of a package". Teams fix that with a virtual environment per project and pinned versions in a file. The pipeline builds the same environment from the same file, so the tests run the same everywhere.

## The idea in plain words

!!! info "In plain words"
    A virtual environment is a separate toolbox for each job. The plumbing job's box has plumbing tools. The electrics job's box has electrics tools.
    Nobody borrows a tool from one box and forgets to put it back.

## Step by step

1. **Create it, inside your project folder.** The folder is usually called `.venv`:

    ```bash
    python3 -m venv .venv
    ```

2. **Activate it.** This makes `python` and `pip` mean the ones inside `.venv`:

    === "macOS and Linux"

        ```bash
        source .venv/bin/activate
        ```

    === "Windows (PowerShell)"

        ```powershell
        .venv\Scripts\Activate.ps1
        ```

    Your prompt usually shows `(.venv)` at the start. Check it really worked:

    ```bash
    python --version
    python -m pip list
    ```

    ```text
    Python 3.13.18
    Package Version
    ------- -------
    pip     26.3
    ```

    A new environment has only pip. That's the point: nothing from other projects.

3. **Install what the project needs, with a version.**

    ```bash
    python -m pip install "pytest==9.2.0"
    python -m pytest --version
    ```

    ```text
    pytest 9.2.0
    ```

    `python -m pip` makes sure you use the pip of the Python you're running. Writing `==9.2.0` pins the version, so everyone gets the same one.

4. **Write the list down.** `pip freeze` lists everything installed, with exact versions. Save it as `requirements.txt`:

    ```bash
    python -m pip freeze > requirements.txt
    ```

    ```text
    iniconfig==2.3.1
    packaging==26.3
    pluggy==1.7.0
    Pygments==2.21.0
    pytest==9.2.0
    ```

    You asked for one package and got five: pytest needs the other four. Anyone can now rebuild the same environment with `python -m pip install -r requirements.txt`.

5. **Keep `.venv` out of Git.** Add `.venv/` to `.gitignore`. Share `requirements.txt`, not the folder: the folder is big, and it only works on the computer that made it.

6. **Leave it when you're done.** `deactivate` goes back to the normal Python. Next time, activate again before you work.

    !!! success "Check: you should now be able to"
        Create and activate a virtual environment, install a pinned package, save `requirements.txt`, and rebuild from it.

## When it goes wrong

- **`ModuleNotFoundError: No module named 'pytest'`, though you installed it.** You installed it in one Python and ran another. Activate the environment, then use `python -m pytest`. To see which Python runs, use `python -c "import sys; print(sys.executable)"`. It should point into your project's `.venv`.
- **`error: externally-managed-environment`.** Your system protects its own Python from pip. That's the system telling you to use a virtual environment. Make one, activate it, and install there.
- **PowerShell says running scripts is disabled.** Windows blocks the activate script by default. Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use `.venv\Scripts\activate.bat` in Command Prompt.
- **Everything broke after moving the project folder.** Virtual environments don't move well. Delete `.venv`, make a new one, and install from `requirements.txt`.

## Common mistakes

!!! warning "Common mistakes"
    - **Installing with no environment active.** The package goes into the system Python.
    - **No versions in `requirements.txt`.** Tomorrow's install gets different versions.
    - **Committing `.venv` to Git.** Commit `requirements.txt` instead.

!!! failure "If you see this error"
    **`zsh: command not found: python`**
    On many macOS and Linux systems, the command is `python3`, not `python`. Use `python3 -m venv .venv`. After you activate the environment, `python` works too.

## Try it yourself

In a new empty folder: create a virtual environment, activate it, install `pytest==9.2.0`, save `requirements.txt`, and run the exercises from this topic with `python -m pytest`. Then delete the `.venv` folder, make a new one, and rebuild it from `requirements.txt`.

??? success "Solution"
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
    python -m pip install "pytest==9.2.0"
    python -m pip freeze > requirements.txt
    deactivate
    rm -rf .venv                     # Windows: Remove-Item -Recurse .venv
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python -m pytest --version
    ```

    If the last line says `pytest 9.2.0`, the file did its job: you rebuilt the same environment from it.

## Quick check

1. Why does each project get its own virtual environment?

    ??? question "Answer"
        So each project has exactly the packages and versions it needs, without breaking other projects.

2. Why write `python -m pip` instead of just `pip`?

    ??? question "Answer"
        It makes sure you use the pip that belongs to the Python you're running.

3. Which goes into Git: `.venv` or `requirements.txt`?

    ??? question "Answer"
        `requirements.txt`. The `.venv` folder stays out.

## References

- [Python: venv](https://docs.python.org/3/library/venv.html)
- [Python Packaging User Guide: Install packages in a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
- [pip: Requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

Written for Python 3.13 and pip 26. Links checked: November 2026.
