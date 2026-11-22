---
title: "How to Test File Uploads and CSV Imports, Step by Step"
description: "A step-by-step guide to testing file uploads and CSV imports at work: get the rules, try them by hand with curl, plan, and copy ready pytest tests for file types, size limits, renamed files, unsafe names, Excel CSV files, bad rows and encodings. Then run them, read the results and fix the common errors."
level: Beginner
tags:
  - API
  - Test data
  - Templates
nav_title: "Test file upload and import, step by step"
order: 45
summary: "Get the rules, try by hand, plan, copy upload and import tests, run, read."
updated: "2026-11-22"
code: "work_playbooks/test_file_upload_and_import"
---

# How to Test File Uploads and CSV Imports, Step by Step

"Users can now upload a profile photo." "Sales can import customers from a spreadsheet." Both sound small, and both break in the same ways: files that are too big, files that aren't what their name says, spreadsheets saved the "wrong" way, and imports that save half a file. This guide takes you from nothing to automated upload and import tests, with ready templates to copy. Follow the steps in order.

!!! example "The situation"
    **Your lead:** "We're releasing document upload and the customer import next week. Can you test both and automate the checks?"

You'll practise on a **small practice API** that runs on your own computer. It has an upload and a CSV import, with three bugs of the kind real apps ship. It keeps files in memory, never on disk. When you finish, you point the same tests at your own app.

## Step 1: Install what you need

You need **Python 3.13** and **VS Code**. If you don't have them, follow [environment setup](../../getting-started/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/test_file_upload_and_import/templates). Then open the `upload_tests` folder in VS Code (**File → Open Folder**).

2. **Open a terminal** in VS Code (**Terminal → New Terminal**), make a virtual environment and install pytest and requests:

    === "macOS / Linux"

        ```bash
        python3.13 -m venv .venv
        source .venv/bin/activate
        python -m pip install -r requirements.txt
        ```

    === "Windows"

        ```powershell
        py -3.13 -m venv .venv
        .venv\Scripts\Activate.ps1
        python -m pip install -r requirements.txt
        ```

3. **Start the practice API** in this terminal:

    ```bash
    python practice_api.py
    ```

    ```text
    Practice API (with planted bugs) on http://127.0.0.1:8780  (Ctrl+C to stop)
    ```

    Leave it running. Open a **second terminal** (the **+** in the terminal panel) and activate `.venv` there too.

## Step 2: Get the rules, then try them by hand

Upload and import bugs hide in rules nobody wrote down. **Get these answers first**, from the spec or the developer:

| Ask | Practice API |
| --- | --- |
| **Which types are allowed?** Checked by the name only, or by the content too? | PNG, JPEG, PDF. Content should be checked |
| **The size limit.** Is a file of exactly that size allowed? | 5 MB, and exactly 5 MB is allowed |
| **The form field name** | `file` |
| **Import: which columns**, which are required | `email,name`, both required |
| **Import: what happens with one bad row?** Whole file refused, good rows saved, or bad rows skipped? | Whole file refused, with the row number |
| **Import: which encoding?** | UTF-8. Excel's "CSV UTF-8" works too |

The "one bad row" answer matters most. If nobody knows, that's your first bug: the team hasn't decided.

**Then try it by hand.** Make a tiny PNG (just the 8 bytes every PNG starts with, plus 4 more):

```bash
python -c "open('photo.png', 'wb').write(b'\x89PNG\r\n\x1a\n0000')"
```

Upload it with curl. `-F "file=@photo.png"` sends the file `photo.png` in the form field `file`:

```bash
curl -i -F "file=@photo.png" http://127.0.0.1:8780/api/files
```

```text
HTTP/1.1 201 Created
Content-Type: application/json
Content-Length: 42

{"id": 1, "name": "photo.png", "size": 12}
```

Now import a CSV with one bad row in it. In VS Code, make a new file `customers.csv` with these lines (row 3 is bad):

```text
email,name
arshad.test@example.com,Arshad Test
not-an-email,Mia Khan
```

```bash
curl -F "file=@customers.csv" http://127.0.0.1:8780/api/import/customers
```

```text
{"imported": 0, "errors": [{"row": 3, "error": "Not an email: 'not-an-email'"}]}
```

Good: it says nothing was imported and names row 3. **But don't trust the answer. Check what was saved:**

```bash
curl http://127.0.0.1:8780/api/customers
```

```text
[{"email": "arshad.test@example.com", "name": "Arshad Test"}]
```

Row 2 was saved, although the answer said `"imported": 0`. **That's a bug, found by hand in two minutes.** Always read back what an import saved.

## Step 3: Decide which tests you need

Almost every upload and import needs the same tests:

| Kind | Common tests |
| --- | --- |
| **Upload: good files** | Each allowed type is accepted, and the saved size is right |
| **Upload: limits** | A file **exactly at** the limit is accepted. **One byte over** is refused. An empty file is refused |
| **Upload: types** | Types not on the list are refused. A **text file renamed to `.png`** is refused. A double name like `photo.png.exe` is refused |
| **Upload: names** | Folder parts like `../../photo.png` are dropped, so nobody can write outside the upload folder |
| **Import: good files** | Every row is saved. A file saved by Excel (with a hidden BOM, and names like `Zoë`) works |
| **Import: bad files** | One bad row does what the rule says, and names the row. Wrong columns and a wrong encoding give a clear message |

Two ideas behind these:

- **Test at the edge.** For a 5 MB limit, test exactly 5 MB and 5 MB + 1 byte. That's where "bigger than" vs "bigger or equal" bugs live.
- **Names lie.** Anyone can rename `virus.exe` to `photo.png`. A safe app looks at the first bytes of the file (the "magic bytes"): every PNG starts the same way, every PDF starts with `%PDF-`.

## Step 4: Write a one-page plan

Copy `test_plan.md` from the project and fill it in: **the rules** (step 2), **the checks** (step 3), **questions for the team**, and **what's not in this plan** (virus scanning, very large imports). Post it in the ticket.

```markdown
| Rule | Value |
| --- | --- |
| Size limit | 5 MB. Is exactly 5 MB allowed? ask |
| One bad row | whole file refused / good rows saved / bad rows skipped |
```

## Step 5: Set up the project

```text
upload_tests/
├── requirements.txt       pytest and requests
├── pytest.ini             pytest settings
├── test_plan.md           your plan (step 4)
├── practice_api.py        the practice API (not needed for your own app)
└── tests/
    ├── conftest.py        your paths and limits, and helpers that make test files
    ├── test_upload.py     file upload
    └── test_import.py     CSV import
```

`tests/conftest.py` holds everything about **your** app. You don't need a folder of sample files: the tests **make each file in code**, exactly the size and content they need.

```python
--8<-- "modules/work_playbooks/test_file_upload_and_import/templates/upload_tests/tests/conftest.py"
```

| Part | What it is |
| --- | --- |
| `upload()` | Sends one file in the form field, like `curl -F` |
| `PNG`, `PDF` | The real first bytes of a PNG and a PDF, so a careful server accepts them |
| `csv_file()` | Makes a CSV from lines. `bom=True` makes it look like Excel's "CSV UTF-8" |
| `count_rows()` | Reads back how many rows are saved: the check from step 2 |

## Step 6: Copy the test templates

=== "Upload"

    ```python
    --8<-- "modules/work_playbooks/test_file_upload_and_import/templates/upload_tests/tests/test_upload.py"
    ```

=== "Import"

    ```python
    --8<-- "modules/work_playbooks/test_file_upload_and_import/templates/upload_tests/tests/test_import.py"
    ```

    Every run uses new emails, made with `uuid`, so you can run the tests again and again without "already exists" errors.

## Step 7: Run the tests

```bash
python -m pytest
```

```text
tests/test_import.py::test_good_file_imports_every_row PASSED            [  6%]
tests/test_import.py::test_excel_style_file_with_bom_and_accents_imports PASSED [ 12%]
tests/test_import.py::test_bad_row_rejects_the_whole_file_and_names_the_row FAILED [ 18%]
tests/test_import.py::test_wrong_columns_are_refused PASSED              [ 25%]
tests/test_import.py::test_file_that_is_not_utf8_is_refused_clearly PASSED [ 31%]
tests/test_upload.py::test_allowed_file_is_accepted[png] PASSED          [ 37%]
tests/test_upload.py::test_allowed_file_is_accepted[pdf] PASSED          [ 43%]
tests/test_upload.py::test_file_exactly_at_the_limit_is_accepted PASSED  [ 50%]
tests/test_upload.py::test_file_one_byte_over_the_limit_is_refused FAILED [ 56%]
tests/test_upload.py::test_empty_file_is_refused PASSED                  [ 62%]
tests/test_upload.py::test_file_type_not_on_the_list_is_refused[notes.txt] PASSED [ 68%]
tests/test_upload.py::test_file_type_not_on_the_list_is_refused[setup.exe] PASSED [ 75%]
tests/test_upload.py::test_file_type_not_on_the_list_is_refused[photo.png.exe] PASSED [ 81%]
tests/test_upload.py::test_file_type_not_on_the_list_is_refused[page.html] PASSED [ 87%]
tests/test_upload.py::test_file_with_a_false_name_is_refused FAILED      [ 93%]
tests/test_upload.py::test_folder_part_of_the_name_is_dropped PASSED     [100%]
...
========================= 3 failed, 13 passed in 0.14s =========================
```

## Step 8: Read the results

**13 passed:** the allowed types, the empty file, other types, double names, folder parts in names, good imports, Excel files, wrong columns and wrong encodings all behave.

**3 failed:**

```text
E       AssertionError: rows before the bad one were saved
E       assert 4 == 3
E       AssertionError: 201: {"id": 4, "name": "too-big.png", "size": 5242881}
E       AssertionError: accepted: {"id": 5, "name": "photo.png", "size": 25}
```

| Failure | What it means | How bad |
| --- | --- | --- |
| Rows before the bad one were saved | **Half-imports.** The user fixes row 3 and imports again, and now rows before it are saved twice. The answer even says `"imported": 0` | **High.** Report first: it silently corrupts data |
| A 5,242,881-byte file was accepted | **The size limit doesn't work.** One byte over 5 MB went in (the code says 50 MB). Big files fill the disk and slow everyone down | **High** |
| A text file named `photo.png` was accepted | **Only the name is checked.** A script, a web page or a program can be uploaded as a "photo" | **High.** Security: say so in the report |

To see what "fixed" looks like, stop the practice API (**Ctrl+C**), start `python practice_api.py --fixed`, and run again:

```text
============================== 16 passed in 0.13s ==============================
```

### Use it on your own app

1. In `conftest.py`: set `BASE_URL`, the paths, the field name and `MAX_BYTES` from the spec.
2. Allowed types other than PNG and PDF? Add their first bytes (for example JPEG starts with `\xff\xd8\xff`) and a row in `test_allowed_file_is_accepted`.
3. Needs a login? Set `API_AUTH` in the terminal, for example `export API_AUTH="Bearer <token>"`.
4. In `test_import.py`: change `HEADER` and the rows to your columns. Set `test_bad_row_...` to your team's rule from step 2.
5. Nowhere to read rows back? Ask for one. Without it, you can't prove what an import saved.

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `ConnectionError: ... port=8780 ... Failed to establish a new connection` | Nothing is running at `BASE_URL` | Start `python practice_api.py` in the first terminal. For your app, check `BASE_URL` |
| `{"error": "Send the file in a form field called \"file\""}` | The form field has another name | Change `FIELD` in `conftest.py` (and the part before `=` in `curl -F`) |
| `{"error": "Only PNG, JPEG or PDF files"}` from `curl -F "file=photo.png"` | Without `@`, curl sends the **text** "photo.png", not the file | Write `-F "file=@photo.png"` |
| `curl: (26) Failed to open/read local data from file/application` | curl can't find the file | Run curl in the folder where the file is, or give the full path |
| An import fails with an encoding error, but the file "looks fine" | It was saved as plain "CSV" by an old Excel, not "CSV UTF-8" | Save as **CSV UTF-8**. And keep the test: users will do this too |
| Import tests pass once, then fail on the next run | The rows from the first run are still there, so your app refuses them as duplicates | Make values unique each run, like `unique_email()` does |
| `413` from your app even for small files | A proxy in front of the app (nginx, a gateway) has its own, lower limit | Tell the team: the limit must be the same everywhere |

When you're done: **Ctrl+C** in the first terminal stops the practice API.

Still stuck? Go deeper:

- [File upload in API tests](../../api-testing/file-upload.md): multipart forms in more detail
- [Data and ETL testing](../../database-testing/data-and-etl/index.md): bigger imports and data pipelines
- [Check data in a database, step by step](../check-database-data/index.md): check what the import really saved, in the database

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/test_file_upload_and_import/templates).

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/test_file_upload_and_import/templates/upload_tests/test_plan.md"
    ```

=== "practice_api.py"

    ```python
    --8<-- "modules/work_playbooks/test_file_upload_and_import/templates/upload_tests/practice_api.py"
    ```

## References

- [OWASP: File upload cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [Requests: POST a multipart-encoded file](https://requests.readthedocs.io/en/latest/user/quickstart/#post-a-multipart-encoded-file)
- [Python: csv module](https://docs.python.org/3/library/csv.html)
- [curl: the -F option](https://curl.se/docs/manpage.html#-F)
- [MDN: Common MIME types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types)

Written for Python 3.13, pytest 9 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
