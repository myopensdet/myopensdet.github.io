---
title: "Read Test Data From Excel With openpyxl"
description: "Run the business team's Excel sheet as tests: read a named sheet with openpyxl, skip empty rows, turn Excel numbers into exact money, and handle formulas that come back as None."
level: Intermediate
tags:
  - pytest
  - Test data
  - Python
nav_title: "Excel test data"
order: 30
summary: "Run the business team's spreadsheet as tests."
updated: "2026-11-22"
---

# Read Test Data From Excel With openpyxl

Business teams live in Excel. The discount rules, the price list, the list of edge cases from the last incident: it's all in a sheet. Instead of copying it into code (and letting the copy go stale), **read the sheet itself** and run every row as a test. When they change the sheet, the tests change with it.

!!! note "Before you start"
    Read [CSV, JSON and YAML data](csv-json-yaml-data.md). The template needs `openpyxl` (in its `requirements.txt`).

## What you will learn

- How to read one named sheet with `openpyxl`
- What Excel does to numbers, true/false values and empty cells
- Why a formula cell can come back as `None`, and what to do about it

## Why this matters at work

When the rules and the tests come from the same sheet, nobody argues about whether the test is "right". If a row fails, either the code or the sheet is wrong, and the business team can answer which in one look.

## The idea in plain words

!!! info "In plain words"
    The business team writes the exam questions and answers in their own notebook. You don't copy them out by hand: you read the notebook directly, every time.

## Step by step

1. **Look at the sheet.** `test_data/discount_rules.xlsx`, sheet `Discounts`:

    | rule | subtotal | coupon | member | expected_total |
    | --- | --- | --- | --- | --- |
    | Plain order | 45.5 | | FALSE | 45.5 |
    | Ten percent off | 19.99 | SAVE10 | FALSE | 17.99 |
    | Member price | 19.99 | | TRUE | 18.99 |
    | Ten percent off for a member | 100 | SAVE10 | TRUE | 85.5 |
    | Welcome coupon | 25 | WELCOME5 | FALSE | 20 |
    | Welcome coupon too small | 15 | WELCOME5 | FALSE | 15 |

    The template builds this sample with `tools/make_discount_sheet.py`. At work, you get the file from the business team.

2. **See how it's read.** `_read_excel()` in `helpers/data_loaders.py` opens the file with two options:

    - `read_only=True`: reads row by row, fast and light even for big sheets.
    - `data_only=True`: gives the value a formula showed when the file was last saved in Excel, not the formula text.

    The first row is the header. Rows with every cell empty are skipped: sheets often have formatted but empty rows at the bottom.

3. **Turn Excel's values into the right types.** Excel gives numbers as `int` or `float`, true/false as `bool`, and empty cells as `None`. `tests/test_discounts_excel.py`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/tests/test_discounts_excel.py"
    ```

    `to_decimal` goes through `str()` first, because `Decimal(19.99)` from the float is `19.989999999999998436805981327779591083526611328125`, and `Decimal(str(19.99))` is `19.99`. The empty coupon cell is `None`, which the code reads as "no coupon".

4. **Run it.**

    ```bash
    python -m pytest tests/test_discounts_excel.py -v
    ```

    ```text
    tests/test_discounts_excel.py::test_discount_rule[Plain order] PASSED    [ 16%]
    tests/test_discounts_excel.py::test_discount_rule[Ten percent off] PASSED [ 33%]
    tests/test_discounts_excel.py::test_discount_rule[Member price] PASSED   [ 50%]
    tests/test_discounts_excel.py::test_discount_rule[Ten percent off for a member] PASSED [ 66%]
    tests/test_discounts_excel.py::test_discount_rule[Welcome coupon] PASSED [ 83%]
    tests/test_discounts_excel.py::test_discount_rule[Welcome coupon too small] PASSED [100%]
    ============================== 6 passed in 0.06s ===============================
    ```

    The `rule` column names the tests, with `id_field="rule"`.

5. **Know the formula trap.** If `expected_total` is a formula like `=ROUND(B2*0.9,2)`, `data_only=True` returns the value Excel saved with the file. A file made or changed by a script, and never opened and saved in Excel, has no saved value:

    ```text
    [{'rule': 'Ten percent off', 'subtotal': 19.99, 'coupon': 'SAVE10', 'member': False, 'expected_total': None}]
    ValueError: Not a number: None
    ```

    Ask for expected values typed in by hand, not worked out by a formula. A formula that uses the same rule as the code proves nothing anyway.

    !!! success "Check: you should now be able to"
        Read a named Excel sheet as test cases, convert its numbers and true/false cells safely, and explain why a formula cell can be `None`.

## When it goes wrong

- **`KeyError: 'Worksheet Discount does not exist.'`** The code asked for `Discount`, and the sheet is called `Discounts`. Names must match exactly, spaces too.
- **`ValueError: Not a number: None`.** An empty cell, or a formula with no saved value. Find the row, and ask for a typed value.
- **`ValueError: discount_rules.xlsx, case 7: no 'rule' value`.** A row has something in it but no name. Often a note typed below the table: move notes to another sheet.

## Common mistakes

!!! warning "Common mistakes"
    - **Reading the sheet by position (`workbook.active`) when it has several sheets.** Someone reorders them, and you test the wrong one. Use the sheet's name.
    - **`Decimal(cell_value)` on a float.** Use `Decimal(str(cell_value))`.
    - **Keeping your own copy of the sheet in the repo and never updating it.** Agree with the team where the real file lives, and who changes it.

!!! failure "If you see this error"
    **`zipfile.BadZipFile: File is not a zip file`**
    The file isn't really `.xlsx`. It may be an old `.xls`, or a CSV renamed to `.xlsx`. Ask for "Excel Workbook (.xlsx)", or save it again in that format.

## Try it yourself

The business team adds a row: "Welcome coupon for a member", subtotal 40, coupon WELCOME5, member TRUE. What should `expected_total` be?

??? success "Solution"
    40 − 5 = 35, then 5% off for a member: 35 × 0.95 = 33.25. Add the row with `expected_total` 33.25, typed in, not a formula. You can add it in Excel, or add it to `ROWS` in `tools/make_discount_sheet.py` and run the script.

## Quick check

1. What does `data_only=True` do?

    ??? question "Answer"
        Gives the value a formula showed when the file was last saved in Excel, instead of the formula.

2. Why can a formula cell come back as `None`?

    ??? question "Answer"
        The file was made or changed by a script and never saved in Excel, so it has no saved value.

## References

- [openpyxl documentation](https://openpyxl.readthedocs.io/en/stable/)
- [openpyxl: Read-only mode](https://openpyxl.readthedocs.io/en/stable/optimized.html)

Written for Python 3.13, pytest 9.2 and openpyxl 3.1. Outputs captured November 2026. Links checked: November 2026.
