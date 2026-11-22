---
title: "JSON: Read and Write the Format of Almost Every API Response"
description: "How JSON maps to Python dictionaries and lists, json.loads and json.dumps, keeping Bengali text readable with ensure_ascii=False, pretty-printing, and comparing an expected and an actual API response with a small script."
level: Beginner
tags:
  - Python
  - API
nav_title: "JSON"
order: 90
summary: "Read and write JSON, and compare an expected API response with the real one."
updated: "2026-11-22"
---

# JSON: Read and Write the Format of Almost Every API Response

**JSON** is text that describes data: objects with named values, lists, text, numbers, true, false and null. Almost every API sends and receives it, and many tools save their results in it. In Python, JSON becomes dictionaries and lists, which you already know. The `json` module does the conversion both ways, in one line.

!!! note "Before you start"
    Read [Strings, lists and dictionaries](lists-tuples-sets-and-dictionaries.md) and [Reading and writing files](file-handling.md) first.

## What you will learn

- How JSON types map to Python types
- How to turn JSON text into Python, and back
- How to keep Bengali and other non-English text readable
- How to compare an expected response with the real one

## Why this matters at work

API tests read JSON responses and check values inside them. Test data often lives in JSON files. When a response is wrong, you need to see *where* it differs, quickly. All of that is the `json` module plus a dictionary.

## The idea in plain words

!!! info "In plain words"
    JSON is a way of writing a dictionary down on paper, so another program can read it.
    `json.loads` reads the paper into Python. `json.dumps` writes Python onto paper.

## Step by step

1. **Know the mapping.**

    | JSON | Python |
    | --- | --- |
    | `{"name": "Pen"}` (object) | `dict` |
    | `[1, 2]` (array) | `list` |
    | `"text"` | `str` |
    | `42`, `4.25` | `int`, `float` |
    | `true`, `false` | `True`, `False` |
    | `null` | `None` |

2. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/json_demo.py"
    ```

    ```bash
    python json_demo.py
    ```

    ```text
    <class 'dict'> 4.25 None paper
    {"customer": "\u0986\u09b0\u09b6\u09be\u09a6", "items": 2, "paid": true}
    {"customer": "আরশাদ", "items": 2, "paid": true}
    {
      "customer": "আরশাদ",
      "items": 2,
      "paid": true
    }
    ```

3. **Read JSON with `loads`.** `json.loads(body)` turns the text into a dictionary. `null` became `None`, and you reach into lists and dictionaries as usual: `product["tags"][0]`. For a file, use `json.loads(path.read_text(encoding="utf-8"))`.

4. **Write JSON with `dumps`.** By default, `dumps` writes non-English letters as `\u` codes. That's still correct JSON, but nobody can read "আরশাদ" as `\u0986\u09b0...`. Add `ensure_ascii=False`. Add `indent=2` to make it readable in reports and test data files.

5. **Compare an expected response with the real one.** The [compare_json.py](index.md#templates) starter walks through both and prints every difference with its path:

    ```bash
    python compare_json.py expected_product.json actual_product.json
    ```

    ```text
    $.price: expected 4.25, got "4.25"
    $.tags: expected 2 items, got 1
    $.created_at: not expected, got "2026-11-16T09:30:00Z"
    3 difference(s).
    ```

    Three real findings: the price is text instead of a number, a tag is missing, and there's a new field. Values that change on every call, like dates and IDs, can be skipped:

    ```bash
    python compare_json.py expected_product.json actual_product.json --ignore created_at,tags
    ```

    ```text
    $.price: expected 4.25, got "4.25"
    1 difference(s).
    ```

    `"4.25"` instead of `4.25` is a classic API bug. A client that adds prices up would join text instead.

    !!! success "Check: you should now be able to"
        Turn JSON into Python and back, keep non-English text readable, and compare two JSON responses.

## When it goes wrong

- **`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.** The text isn't JSON at all. Often it's empty, or an HTML error page. Print the first 200 characters to see what you really got.
- **`JSONDecodeError: Expecting property name enclosed in double quotes`.** JSON needs double quotes. `{'a': 1}` is Python, not JSON. So is a comma after the last item.
- **`TypeError: Object of type date is not JSON serializable`.** JSON has no date type. Turn dates into text first: `date.isoformat()`.
- **The same data compares as different.** Check the types: `1` and `1.0`, or `4.25` and `"4.25"`, look alike but aren't the same in JSON. `compare_json.py` reports those on purpose.

## Common mistakes

!!! warning "Common mistakes"
    - **Comparing JSON as text.** Key order and spaces differ. Load both, then compare.
    - **Forgetting `ensure_ascii=False`** for files people will read.
    - **Checking only the status code.** The body may still be wrong.

!!! failure "If you see this error"
    **`TypeError: the JSON object must be str, bytes or bytearray, not dict`**
    You called `json.loads` on something that is already a dictionary. Many HTTP libraries give you `response.json()`, which has already done the loading. Use it directly.

## Try it yourself

Open `exercises/ex09_json.py`. Write `failed_tests(text)`, which returns the names of failed tests from a results JSON, and `to_json(data)`, which keeps Bengali letters readable. Run `python -m pytest tests/test_ex09_json.py`.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex09_json.py"
    ```

    `failed_tests` is the heart of the [run summary script](index.md): load the JSON, then loop over the list of tests.

## Quick check

1. What does JSON's `null` become in Python?

    ??? question "Answer"
        `None`.

2. What does `ensure_ascii=False` change?

    ??? question "Answer"
        Non-English letters are written as they are, like "আরশাদ", instead of `\u` codes.

3. Why compare loaded JSON instead of the raw text?

    ??? question "Answer"
        The text can differ in key order and spacing while the data is the same.

## References

- [Python: json](https://docs.python.org/3/library/json.html)
- [JSON.org: Introducing JSON](https://www.json.org/json-en.html)
- [RFC 8259: The JSON data format](https://www.rfc-editor.org/rfc/rfc8259)

Written for Python 3.13. Links checked: November 2026.
