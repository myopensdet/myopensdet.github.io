---
title: "Modules and Imports: Use Dates, Paths and JSON From the Standard Library"
description: "How Python imports work: import and from-import, the standard library modules testers use most (datetime, pathlib, json, random), importing your own files, if __name__ == \"__main__\", and fixing ModuleNotFoundError."
level: Beginner
tags:
  - Python
  - Tools
nav_title: "Modules and imports"
order: 50
summary: "Use dates, paths and JSON from the standard library, and your own files."
updated: "2026-11-22"
---

# Modules and Imports: Use Dates, Paths and JSON From the Standard Library

A **module** is a Python file you can use from another file. Python comes with hundreds of them, called the **standard library**: dates, file paths, JSON, CSV, random numbers. `import` brings one in. Your own files are modules too, which is how tests use the code they test. This lesson covers the modules testers use every week, and the error everyone meets: `ModuleNotFoundError`.

!!! note "Before you start"
    Read [Functions](functions.md) first.

## What you will learn

- The two ways to import: `import json` and `from datetime import date`
- Four standard library modules testers use often
- How to import your own file, and what `if __name__ == "__main__":` is for
- How to fix `ModuleNotFoundError`

## Why this matters at work

Date limits ("refund within 30 days"), file paths for test data, JSON responses and repeatable random data are in almost every test suite. Knowing that Python already has a tool for each saves you from writing your own, slower and buggier.

## The idea in plain words

!!! info "In plain words"
    The standard library is a toolbox that comes with Python. `import` is taking a tool out of the box.
    You don't build a screwdriver every time you need one.

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/modules_demo.py"
    ```

    ```bash
    python modules_demo.py
    ```

    ```text
    2026-11-15
    31
    .json nightly.json
    {"ok": true}
    18 73
    ```

2. **Two ways to import.** `import json` brings in the whole module, and you write `json.dumps(...)`. `from datetime import date, timedelta` brings in just those names, and you write `date(...)`. Both are fine. Pick the one that reads more clearly.

3. **Dates.** `date(2026, 10, 16) + timedelta(days=30)` is the last day of a 30-day refund window: 15 November. Subtracting two dates gives the days between them: 31. Never count days by hand in a test. Months have different lengths, and leap years exist.

4. **Paths.** `Path` from `pathlib` understands file paths on every system. `.suffix` is the extension, `.name` the file name. You'll use `Path` in the [files lesson](file-handling.md).

5. **Repeatable random data.** `random.seed(1)` makes the "random" numbers the same on every run. Random test data is useful, but a failure you can't repeat is hard to fix. Seed it, and print the seed when a test fails. For passwords and tokens, use the `secrets` module instead: `random` isn't safe for those.

6. **Import your own file.** If `shop.py` has a function `delivery_fee`, then `from shop import delivery_fee` works from any file in the same folder. Code at the bottom of `shop.py` that should run only when you start it directly goes under `if __name__ == "__main__":`. Then a test can import the file without running that code. Every [starter script](index.md#templates) in this topic ends that way.

    !!! success "Check: you should now be able to"
        Import from the standard library both ways, work with dates and paths, and import a function from your own file.

## When it goes wrong

- **`ModuleNotFoundError: No module named 'shop'`.** Python can't find the file. Run Python from the folder that has `shop.py` in it, and use `python -m pytest`, which adds the current folder to the places Python looks.
- **`ModuleNotFoundError: No module named 'requests'`.** It's not in the standard library. Install it in your virtual environment: see [Virtual environments and pip](virtual-environments-and-pip.md).
- **`ImportError: cannot import name 'delivery_fees' from 'shop'`.** The file is found, but that name isn't in it. Check the spelling against the `def` line.
- **Your file is called `json.py` or `random.py`, and imports break.** Your file hides the standard one. Rename your file to something like `json_checks.py`.

## Common mistakes

!!! warning "Common mistakes"
    - **Naming your file like a standard module.** `test.py`, `json.py`, `csv.py` cause strange errors.
    - **Counting days by hand.** Use `datetime`.
    - **Unseeded random data in tests.** Seed it, so failures can be repeated.

!!! failure "If you see this error"
    **`AttributeError: module 'datetime' has no attribute 'fromisoformat'`**
    You wrote `import datetime`, so `datetime` is the module, not the class. Either write `datetime.date.fromisoformat(...)`, or import the class: `from datetime import date`, then `date.fromisoformat(...)`.

## Try it yourself

Open `exercises/ex05_modules.py`. Write `days_between("2026-10-16", "2026-11-16")`, which returns `31`. `date.fromisoformat()` turns text like `"2026-10-16"` into a date. Run `python -m pytest tests/test_ex05_modules.py`.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex05_modules.py"
    ```

    One of the tests crosses 29 February 2028. Code that counts days by hand usually gets that wrong.

## Quick check

1. What is the standard library?

    ??? question "Answer"
        The modules that come with Python, like `json`, `datetime`, `pathlib`, `csv` and `random`.

2. Why seed random test data?

    ??? question "Answer"
        So the same data comes out every run, and a failure can be repeated.

3. What is `if __name__ == "__main__":` for?

    ??? question "Answer"
        Code under it runs only when you start the file directly, not when another file imports it.

## References

- [Python Tutorial: Modules](https://docs.python.org/3/tutorial/modules.html)
- [Python: datetime](https://docs.python.org/3/library/datetime.html)
- [Python: pathlib](https://docs.python.org/3/library/pathlib.html)
- [Python: random](https://docs.python.org/3/library/random.html) and [secrets](https://docs.python.org/3/library/secrets.html)

Written for Python 3.13. Links checked: November 2026.
