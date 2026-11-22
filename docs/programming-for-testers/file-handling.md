---
title: "Reading and Writing Files: Test Data, CSV Files and Reports"
description: "Reading and writing text files in Python with pathlib and open, why to always set encoding to UTF-8, reading CSV test data with the csv module, and writing a simple report file."
level: Beginner
tags:
  - Python
  - Test data
nav_title: "File handling"
order: 80
summary: "Read test data and CSV files, write reports, and keep Bengali text safe."
updated: "2026-11-22"
---

# Reading and Writing Files: Test Data, CSV Files and Reports

Test data lives in files: a list of users, a CSV export, expected results. Reports go into files too. Python makes both easy with `pathlib` and the `csv` module. One rule matters more than any other: always say `encoding="utf-8"`. Without it, Bengali names, accents and emoji can break on some computers, and the test that fails is the one nobody can reproduce.

!!! note "Before you start"
    Read [Modules and imports](modules-and-imports.md) first.

## What you will learn

- How to read and write a text file with `Path`
- Why `encoding="utf-8"` matters, every time
- How to read CSV test data as dictionaries
- How `with` closes files for you

## Why this matters at work

Data-driven tests read their cases from CSV or JSON. Export checks compare a downloaded file with what's expected. Reports and logs are files. If reading a file is shaky, every test that depends on it is shaky too.

## The idea in plain words

!!! info "In plain words"
    Reading a file is opening a book, reading it, and putting it back. Writing is filling in a notebook.
    The encoding is the alphabet the book is written in. If you read it with the wrong alphabet, the words come out as nonsense.

## Step by step

1. **Look at the data.** `users.csv` has a comment line, then a header, then one user per line:

    ```text
    --8<-- "modules/start_here/python_for_testers/examples/users.csv"
    ```

2. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/files_demo.py"
    ```

    ```bash
    python files_demo.py
    ```

    ```text
    arshad customer
    maria customer
    admin1 admin
    3 users checked
    True report.txt
    ```

3. **Find files next to your script.** `Path(__file__).parent` is the folder the script is in. `here / "users.csv"` joins paths the right way on every system. Then the script works no matter which folder you start it from.

4. **Open with `with`.** `with users_file.open(...) as file:` opens the file and closes it when the block ends, even if there's an error. Always set `encoding="utf-8"`, and for CSV files, `newline=""`, which the `csv` module needs.

5. **Read CSV rows as dictionaries.** `csv.DictReader` uses the header line as keys, so each row is `{"username": "arshad", "role": "customer"}`. The comment line is skipped first, because it isn't part of the table. Every value from a CSV file is text, so convert numbers with `int()`.

6. **Write a file.** `report.write_text("3 users checked\n", encoding="utf-8")` writes the whole file in one line. `mkdir(exist_ok=True)` makes the folder if it isn't there yet. For short files, `read_text()` and `write_text()` are all you need.

    !!! success "Check: you should now be able to"
        Read a text file and a CSV file, write a report file, and explain why every open needs `encoding="utf-8"`.

## When it goes wrong

- **`FileNotFoundError: [Errno 2] No such file or directory: 'users.csv'`.** Python looked in the folder you started from, not the script's folder. Use `Path(__file__).parent / "users.csv"`, or start the script from its own folder.
- **`UnicodeDecodeError: 'charmap' codec can't decode byte ...`.** The file was opened without `encoding="utf-8"`, on a computer whose default isn't UTF-8 (often Windows). Add the encoding.
- **Bengali text shows as `à¦†à¦°`.** The file was saved as UTF-8 but read with another encoding, or the other way round. Read and write with UTF-8 everywhere.
- **The CSV header is `\ufeffusername`.** The file was saved by a spreadsheet program with a hidden marker at the start. Open it with `encoding="utf-8-sig"`, which removes it.

## Common mistakes

!!! warning "Common mistakes"
    - **No encoding.** Works on your laptop, breaks on someone else's.
    - **Paths relative to wherever you started.** Build them from `Path(__file__).parent`.
    - **Forgetting that CSV values are text.** `"30"` isn't `30`.

!!! failure "If you see this error"
    **`KeyError: 'username'` when reading a CSV**
    The header isn't what you think. Print `reader.fieldnames` to see it. Often there's a space (`" username"`), a hidden marker (`"\ufeffusername"`), or the first line is a comment that wasn't skipped.

## Try it yourself

Open `exercises/ex08_files.py`. Write `read_usernames(path)`, which skips empty lines and lines that start with `#`, and `write_report(path, lines)`. The test file includes the Bengali name "আরশাদ". Run `python -m pytest tests/test_ex08_files.py`.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex08_files.py"
    ```

    The tests use pytest's `tmp_path`, a fresh empty folder for each test, so they never leave files behind.

## Quick check

1. Why should you always pass `encoding="utf-8"`?

    ??? question "Answer"
        Without it, Python uses the computer's default, which differs between machines, and non-English text can break.

2. What does `with` do when opening a file?

    ??? question "Answer"
        It closes the file when the block ends, even if there was an error.

3. What type is every value read from a CSV file?

    ??? question "Answer"
        Text (`str`). Convert numbers yourself.

## References

- [Python Tutorial: Reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- [Python: pathlib](https://docs.python.org/3/library/pathlib.html)
- [Python: csv](https://docs.python.org/3/library/csv.html)
- [pytest: tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html)

Written for Python 3.13. Links checked: November 2026.
