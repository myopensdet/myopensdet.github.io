---
title: "File Upload: Send a File With multipart/form-data"
description: "How APIs take file uploads with multipart/form-data, sending a file and form fields with requests' files= and data=, checking the server got the same file, and the upload cases worth testing."
level: Intermediate
tags:
  - API
  - Python
nav_title: "File upload"
order: 90
summary: "Send a file and form fields, check it arrived the same, and what to test."
updated: "2026-11-22"
---

# File Upload: Send a File With multipart/form-data

Uploads use a different body from JSON: **multipart/form-data**, where the body is split into parts, one for each form field and one for each file. In `requests`, `files=` sends the file and `data=` sends the other fields, and `requests` builds the parts and the header for you.

!!! note "Before you start"
    Read [Headers and JSON](headers-and-json.md) first.

## What you will learn

- What multipart/form-data is
- How to upload a file with a form field
- How to check the server got the same file
- Which upload cases to test

## Why this matters at work

Uploads are where APIs meet files they didn't expect: empty files, huge ones, the wrong type, names with Bengali letters or `../` in them. Profile photos, CSV imports and attachments all go through the same kind of endpoint, and bugs there can be security bugs.

## The idea in plain words

!!! info "In plain words"
    A JSON body is one letter. A multipart body is a parcel with several things inside, each with its own label: "this part is the field `run`", "this part is the file `results.csv`, type text/csv".

## Step by step

1. **Upload a file with a field.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/upload_demo.py"
    ```

    ```bash
    python upload_demo.py
    ```

    ```text
    Status: 200
    Sent as: multipart/form-data
    Form field: {'run': 'nightly'}
    File received: 4 lines, the same as sent: True
    ```

    The file is `results.csv`, a small fake test report next to the example. httpbin's `/post` answers with what it received, so you can check both sides.

2. **Read the `files=` line.** `files={"file": ("results.csv", file, "text/csv")}`:

    - `"file"` is the field name the API expects. Check the docs: it's often `file`, sometimes `upload` or `attachment`.
    - `"results.csv"` is the file name the server sees.
    - `file` is the open file, in binary mode (`"rb"`).
    - `"text/csv"` is the file's type.

3. **Don't set Content-Type yourself.** `requests` sets `multipart/form-data; boundary=...`. The boundary is the line that separates the parts, and only `requests` knows it. Setting the header by hand breaks the upload.

4. **Check the file arrived the same.** The example compares what the server got with the file on disk. At work, the API usually answers with an id or a URL: download the file back and compare, or compare a checksum if the API gives one.

5. **Test the edges.**

    | Case | Expect |
    | --- | --- |
    | A normal file | 200 or 201, and the same file back |
    | An empty file | A clear 400, or accepted if empty is allowed |
    | Just over the size limit | 413 Content Too Large, or a clear 400 |
    | The wrong type, like an `.exe` as a photo | 400 or 415 |
    | A name with Bengali letters or spaces | Saved with the right name |
    | A name like `../../config` | The path is ignored, never used |
    | No file at all | 400, saying the file is missing |

    The `../` case matters for security: if the server uses the name as a path, it may write outside the upload folder. See [security testing](../security-testing/index.md).

    !!! success "Check: you should now be able to"
        Upload a file with a form field, check it arrived the same, and list the upload cases to test.

## When it goes wrong

- **The server says the file is missing.** The field name is wrong. Compare it with the docs, or with a working upload in the browser's network tab.
- **`400` or a broken file after setting `Content-Type` by hand.** Remove the header. Let `requests` set it with the boundary.
- **The file arrives changed, or the count is off.** It was opened in text mode. Open it with `"rb"`.
- **A big upload times out.** Raise the `timeout` for that test only, and ask what the real limit is.

## Common mistakes

!!! warning "Common mistakes"
    - **`json=` together with `files=`.** A multipart body can't also be JSON. Send other fields with `data=`.
    - **Only testing a small, normal file.** The bugs are at the edges.
    - **Real customer files in tests.** Use small fake files kept next to the tests.

!!! failure "If you see this error"
    **`ValueError: read of closed file`**
    The file was closed before the request was sent, often because `requests.post(...)` sits outside the `with open(...)` block. Move the request inside the block.

## Try it yourself

Change the example to upload two files in one request: `results.csv` as `file`, and a second copy as `backup`. How does the server's `files` part change?

??? success "Solution"
    ```python
    with report.open("rb") as first, report.open("rb") as second:
        response = requests.post(
            "https://httpbin.org/post",
            files={
                "file": ("results.csv", first, "text/csv"),
                "backup": ("results.csv", second, "text/csv"),
            },
            timeout=15,
        )
    print(response.json()["files"].keys())
    ```

    The server's `files` now has two keys, `file` and `backup`: one part per field name.

## References

- [Requests: POST a multipart-encoded file](https://requests.readthedocs.io/en/latest/user/quickstart/#post-a-multipart-encoded-file)
- [MDN: Sending form data](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Sending_and_retrieving_form_data)
- [OWASP: File upload cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
