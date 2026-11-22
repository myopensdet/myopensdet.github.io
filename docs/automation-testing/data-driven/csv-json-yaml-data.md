---
title: "Test Data From CSV, JSON and YAML Files in pytest"
description: "One loader for CSV, JSON and YAML test data, and the traps of each format: CSV gives only text, Excel adds an invisible mark, JSON floats aren't exact money, and YAML reads NO as false."
level: Intermediate
tags:
  - pytest
  - Test data
  - Python
nav_title: "CSV, JSON and YAML data"
order: 20
summary: "One loader for three formats, and the trap in each one."
updated: "2026-11-22"
---

# Test Data From CSV, JSON and YAML Files in pytest

Test data comes in whatever format the team already uses: a CSV from the product owner, a JSON file from the API team, a YAML file next to the config. One small loader reads all three. The hard part isn't reading them. It's **what each format quietly does to your values.**

!!! note "Before you start"
    Read [one test, many rows](one-test-many-rows.md).

## What you will learn

- A loader that turns CSV, JSON and YAML rows into pytest cases
- Which format to choose for which data
- The trap in each format, with the real error it causes

## Why this matters at work

A data-driven test can be wrong without failing. A YAML file turns a country code into `False`, a CSV hands you `"30"` instead of `30`, a float turns 19.99 into 19.989999… The test then checks the wrong thing, or fails with an error that points nowhere near the data file.

## The idea in plain words

!!! info "In plain words"
    Three suppliers send the same goods in different boxes. The loader opens each box the right way. Then you check the goods: one supplier always sends text, one rounds the prices, one swaps "NO" for "false".

## Step by step

1. **Read the loader.** `helpers/data_loaders.py`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/helpers/data_loaders.py"
    ```

    - `load_rows()` picks the reader by the file's ending, and returns a list of dicts.
    - `cases()` turns the rows into `pytest.param` cases, named by `case`. It refuses rows with no name, and two rows with the same name.
    - `to_decimal()`, `to_bool()` and `to_int()` turn text into the types the code needs. They raise a clear error on bad values.

2. **CSV: everything is text.** `csv.DictReader` gives strings, always:

    ```text
    {'case': 'adult', 'age': '30'}
    TypeError: '<=' not supported between instances of 'str' and 'int'
    ```

    That's `check_signup(..., row["age"])` without `to_int`. Convert every value the code doesn't expect as text.

3. **CSV: the invisible mark.** Excel saves "CSV UTF-8" files with an invisible mark at the very start. Read with plain `utf-8`, it sticks to the first column's name:

    ```text
    ['﻿case', 'age']
    KeyError: 'case'
    ```

    The loader opens CSV files with `utf-8-sig`, which drops the mark: `['case', 'age']`.

4. **JSON: write money as text.** `test_data/order_totals.json`:

    ```json
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/test_data/order_totals.json"
    ```

    A JSON number is read as a float, and floats aren't exact:

    ```text
    0.30000000000000004
    ```

    That's `0.1 + 0.2` from JSON. Money as text (`"30.00"`) turned into a `Decimal` stays exact. JSON has no comments, so the credit line sits in a `"$comment"` key, and the cases under `"cases"`. Rows that should fail name the `error` instead of `expected`:

    ```python
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/tests/test_order_totals_json.py"
    ```

5. **YAML: quote codes and numbers.** YAML guesses types, and some guesses are wrong:

    ```text
    country: NO -> {'country': False}
    zip: 01234 -> {'zip': 668}
    zip: 012345678 -> {'zip': '012345678'}
    weight_kg: 1.10 -> {'weight_kg': 1.1}
    on: yes -> {True: True}
    ValueError: We don't ship to False
    ```

    `NO` (Norway) becomes `False`. `01234` is read as an octal number, 668. `1.10` loses its zero. The last line is the shipping test with Norway unquoted: the error names `False`, nowhere near the data file. Quote every code and number. `test_data/shipping_cases.yaml`:

    ```yaml
    --8<-- "modules/core_automation/data_driven_testing/templates/data_driven_tests/test_data/shipping_cases.yaml"
    ```

6. **Run all three.**

    ```bash
    python -m pytest tests/test_signup_csv.py tests/test_order_totals_json.py tests/test_shipping_yaml.py -q
    ```

    ```text
    .x...........................                                            [100%]
    =========================== short test summary info ============================
    XFAIL tests/test_signup_csv.py::test_signup_rules[exactly 18] - Known bug AGE-18
    28 passed, 1 xfailed in 0.03s
    ```

    !!! success "Check: you should now be able to"
        Load test cases from CSV, JSON and YAML, convert their values safely, and avoid the trap in each format.

7. **Choose a format.**

    | Format | Good for | Watch out for |
    | --- | --- | --- |
    | CSV | flat tables that people edit in a spreadsheet | everything is text; the invisible mark |
    | JSON | nested data, API bodies | no comments; floats for money |
    | YAML | nested data that people read and edit | type guessing: quote codes and numbers |

## When it goes wrong

- **`ValueError: cols.csv, data row 2: not the same number of columns`.** A row has one value too many or too few. Often a comma inside a value: wrap that value in double quotes.
- **`ValueError: dup.csv: two cases are called 'adult'`.** Two rows have the same name. pytest would run both, and a failure wouldn't say which. Rename one.
- **A YAML value is `True`, `False` or a strange number.** It wasn't quoted. Quote it.

## Common mistakes

!!! warning "Common mistakes"
    - **`yaml.load` instead of `yaml.safe_load`.** The unsafe loaders can be made to run code from the file.
    - **`Decimal(19.99)`.** It gives 19.989999999999998436805981327779591083526611328125. Use `Decimal("19.99")`, or `Decimal(str(value))` as `to_decimal` does.
    - **`bool("false")`.** It's `True`: any text that isn't empty is. Use `to_bool`.

!!! failure "If you see this error"
    **`KeyError: 'case'` on a CSV that clearly has a `case` column**
    The file starts with Excel's invisible mark. Open it with `encoding="utf-8-sig"`.

## Try it yourself

Add a JSON case: a member with no coupon on a 19.99 order. Work out the expected total by hand first.

??? success "Solution"
    19.99 × 0.95 = 18.9905, rounded half up to the cent: 18.99.

    ```json
    {"case": "member, no coupon", "subtotal": "19.99", "coupon": null, "member": true, "expected": "18.99"}
    ```

## Quick check

1. Why is money written as text in the JSON file?

    ??? question "Answer"
        JSON numbers become floats, and floats aren't exact.

2. What does YAML make of an unquoted `NO`?

    ??? question "Answer"
        `False`.

3. Why `utf-8-sig` for CSV files?

    ??? question "Answer"
        It drops the invisible mark Excel puts at the start.

## References

- [Python: csv](https://docs.python.org/3/library/csv.html)
- [Python: decimal](https://docs.python.org/3/library/decimal.html)
- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [YAML 1.1: boolean values](https://yaml.org/type/bool.html)

Written for Python 3.13, pytest 9.2 and PyYAML 6.0. Outputs captured November 2026. Links checked: November 2026.
