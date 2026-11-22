---
title: "Schema Validation: Check the Shape of Every Response"
description: "Use JSON Schema and the jsonschema library to check the shape of API responses: required fields, types, formats and extra fields, with every problem listed by its path, and one schema reusing another with $ref."
level: Intermediate
tags:
  - API
  - Python
  - pytest
nav_title: "Schema validation"
order: 70
summary: "Check required fields, types and formats of every response with JSON Schema."
updated: "2026-11-22"
---

# Schema Validation: Check the Shape of Every Response

Checking one or two values is not enough. A response can have the right `firstname` and still be broken: a price sent as text, a date in the wrong format, a missing field, a new field that leaks data. A **JSON Schema** describes the shape a response must have, and the `jsonschema` library checks it in one line, listing every problem with its path.

!!! note "Before you start"
    Read [Headers and JSON](headers-and-json.md) first. The example needs Restful-booker's public demo login: `export BOOKER_USERNAME=admin BOOKER_PASSWORD=password123`.

## What you will learn

- How to write a JSON Schema for a response
- How to check a response and list every problem with its path
- How one schema reuses another with `$ref`
- What schemas catch, and what they don't

## Why this matters at work

Front ends and mobile apps break when a field changes type or goes missing, often in a release nobody thought touched the API. A schema check in every test catches it the first time. And `additionalProperties: false` catches new fields, like a password hash that suddenly appears in a user response.

## The idea in plain words

!!! info "In plain words"
    A schema is a form with rules: "name: text, required", "price: whole number, 0 or more", "check-in: a date". The check reads the response and lists every box filled in wrong.

## Step by step

1. **Write the schema.** This is the template's `schemas/booking.json`:

    ```json
    --8<-- "modules/core_automation/api_testing/templates/booker_api_tests/schemas/booking.json"
    ```

    - `required` lists the fields that must be there.
    - `type` says what each field is: `string`, `integer`, `boolean`, `object`, `array`.
    - `format: date` says the text must be a real date, like `2026-12-01`.
    - `additionalProperties: false` refuses any field the schema doesn't name.

2. **Check a real response, and a broken copy.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/schema_demo.py"
    ```

    ```bash
    python schema_demo.py
    ```

    ```text
    Real booking: matches the schema
    Broken copy:
    - $.bookingdates.checkin: '2026-13-01' is not a 'date'
    - $.bookingdates: 'checkout' is a required property
    - $.totalprice: '120' is not of type 'integer'
    - $: Additional properties are not allowed ('discount' was unexpected)
    ```

    Every problem, with its path. `$` is the whole body, and `$.bookingdates.checkin` is a field inside. A plain `jsonschema.validate()` stops at the first problem. The template's `schema_errors()` collects them all, sorted, so a failure shows everything at once.

3. **Know that formats are off by default.** Without a format checker, `'2026-13-01'` passes as a "date", because it's a string. The template turns it on with `format_checker=Draft202012Validator.FORMAT_CHECKER`. Try it without, and the first line of the broken output disappears.

4. **Reuse schemas with `$ref`.** The create answer wraps a booking: `{"bookingid": 1, "booking": {...}}`. Instead of copying the booking rules, `created_booking.json` points to them:

    ```json
    --8<-- "modules/core_automation/api_testing/templates/booker_api_tests/schemas/created_booking.json"
    ```

    For `"$ref": "booking.json"` to work, the validator needs to know where `booking.json` is. The template's `_registry()` loads every schema in the folder, by its `$id`.

5. **Use it in tests.**

    ```python
    assert_matches_schema(response.json(), load_schema("booking.json"))
    ```

    One line, after the status check. Then check the values that matter, like `assert response.json() == data`. The schema checks the shape. Your asserts check the meaning.

6. **Know what schemas don't catch.** A schema can't tell you the price is *right*, that checkout is after check-in, or that you got *your* booking. Those need asserts. Schemas are a safety net under them.

    !!! success "Check: you should now be able to"
        Write a schema with required fields, types, formats and no extra fields, and check a response with every problem listed.

## When it goes wrong

- **Every response fails with "Additional properties are not allowed".** The API has fields the schema doesn't name. Ask whether they're meant to be there. If yes, add them. If they hold private data, that's a bug.
- **A date check never fails.** The format checker is off. Pass `format_checker=`.
- **The schema passes, but the app still breaks.** The schema is too loose: a field isn't `required`, or a type is `["string", "null"]` when null isn't allowed. Tighten it.
- **The API team has an OpenAPI file.** Its `components/schemas` section holds JSON Schemas already. Reuse them instead of writing your own, and the tests follow the API's contract. See [contract testing](contract-testing/index.md).

## Common mistakes

!!! warning "Common mistakes"
    - **No `required` list.** Then an empty object `{}` passes.
    - **Leaving out `additionalProperties: false`.** New fields slip through, including leaks.
    - **Only checking the schema.** It says the price is a number, not the right number.

!!! failure "If you see this error"
    **`_WrappedReferencingError: Unresolvable: booking.json`**
    A schema uses `"$ref": "booking.json"`, but the validator doesn't know that schema. Pass a registry with every schema in it, like the template's `_registry()`, or use `schema_errors()` from the template.

## Try it yourself

Add a rule to `booking.json` so `firstname` can be at most 50 characters. Then check `{"firstname": "A" * 51, ...}` with `schema_errors()`. What does the problem line say?

??? success "Solution"
    Change the field to `"firstname": {"type": "string", "minLength": 1, "maxLength": 50}`. The check then reports `$.firstname: 'AAAA...' is too long`, with the path first, so you know which field. Ask the API team for the real limit first: the schema should match what the API promises.

## References

- [JSON Schema: Getting started](https://json-schema.org/learn/getting-started-step-by-step)
- [python-jsonschema documentation](https://python-jsonschema.readthedocs.io/en/stable/)
- [OWASP API3:2023 Broken Object Property Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/)

Written for Python 3.13 and jsonschema 4.26. Outputs captured November 2026. Links checked: November 2026.
