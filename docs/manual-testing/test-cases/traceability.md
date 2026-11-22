---
title: "Traceability: Link Every Test to a Requirement, and Find the Gaps"
description: "What traceability is, how to build a traceability matrix from a CSV of test cases, how to link automated pytest tests to requirements with a marker, and what to do with the gaps and unknown IDs you find."
level: Beginner
tags:
  - Test design
  - Templates
  - pytest
nav_title: "Traceability"
order: 30
summary: "Link every test to a requirement, and find the rules nobody tested."
updated: "2026-11-22"
---

# Traceability: Link Every Test to a Requirement, and Find the Gaps

Sooner or later, someone asks: "Is every requirement tested?" Without traceability, the honest answer is "I think so". With it, you show a table: every requirement, the test cases for it, and a clear "NONE" where something is missing. This lesson builds that table from a CSV of test cases and from automated tests, and shows what to do when it finds a gap.

!!! note "Before you start"
    Read [Anatomy of a test case](anatomy-of-a-test-case.md) first, especially the "Covers" field.
    To run the examples: `pip install pytest`, then run the commands from the `examples` folder.

## What you will learn

- What traceability and a traceability matrix are
- How to build the matrix from a CSV with `traceability.py`
- How to link automated tests to requirements with a pytest marker
- What to do with gaps and with IDs that don't exist

## Why this matters at work

Traceability answers three questions that come up in every project: "Is everything tested?", "This rule changed: which tests do I update?" and "This test failed: which rule is broken?" In some industries, like banking or health, it is also required by auditors. Everywhere else, it is simply the fastest way to find what nobody tested.

## The idea in plain words

!!! info "In plain words"
    Think of a teacher with a list of pupils and a stack of homework. Matching each homework to a name shows who hasn't handed it in, and also any homework with a name that isn't on the list.
    A traceability matrix matches requirements (the names) with test cases (the homework). The gaps show up on their own.

## Step by step

1. **Give every requirement an ID.** You can't trace what you can't name. Here are the refund criteria as a simple text file, one per line:

    ```text
    --8<-- "modules/think_like_a_tester/test_cases/examples/refund_requirements.txt"
    ```

2. **Put the IDs in your test cases.** Each case in the CSV has a **Covers** column. One case can cover several requirements: write `REF-1;REF-4`.

3. **Build the matrix.** Run the [traceability script](index.md#templates) with both files:

    ```bash
    python traceability.py refund_requirements.txt refund_test_cases.csv
    ```

    ```text
    | Requirement | Test cases | Count |
    | --- | --- | --- |
    | REF-1 | TC-01, TC-02, TC-06 | 3 |
    | REF-2 | TC-07 | 1 |
    | REF-3 | TC-11, TC-12, TC-13 | 3 |
    | REF-4 | TC-03 | 1 |
    | REF-5 | NONE | 0 |
    | REF-6 | TC-14 | 1 |
    | REF-7 | TC-15 | 1 |

    No test case: REF-5 (Card and PayPal back to the same account; gift card becomes store credit)
    TC-16 covers REF-8, which is not in the requirements (typo or new?)
    ```

    The table is Markdown, so you can paste it into a report or a pull request. The script ends with exit code 1 when a requirement has no test case, so it can stop a pipeline.

4. **Read the two findings.** Both are typical:

    - **REF-5 has no test case.** But it *is* tested: TC-04 and TC-05 are automated tests for it. Someone wrote the tests and never added them to the CSV. That's the most common traceability gap of all: two lists that drifted apart.
    - **TC-16 covers REF-8, which doesn't exist.** The case checks that the refund page works in Bengali. Either the ID is a typo, or the team has a real requirement ("the page works in Bengali") that was never written into the story. Both need a fix, but the second is more important: a requirement that only exists in a test case is easy to lose.

5. **Link automated tests too.** For pytest, the [covers plugin](index.md#templates) adds a `covers` marker. Save it as `conftest.py` in your tests folder, and mark each test:

    ```python
    @pytest.mark.covers("REF-1")
    def test_tc06_refund_is_refused_on_day_31():
        ...
    ```

    Then pass the list of IDs:

    ```bash
    python -m pytest -q --requirements REF-1,REF-2,REF-3,REF-4,REF-5,REF-6,REF-7
    ```

    ```text
    ================================= requirements =================================
    REF-1      3 tests
    REF-2      1 test
    REF-3      NO TESTS
    REF-4      2 tests
    REF-5      3 tests
    REF-6      1 test
    REF-7      1 test
    11 passed in 0.02s
    ```

    The automated side shows REF-5 well covered, and REF-3 with nothing, because REF-3 is about emails and timing, tested by hand (TC-11 to TC-13). Put the two reports side by side and every requirement has at least one test. That's the real answer to "is everything tested?"

6. **Let the plugin catch typos.** If a test says `covers("REF2")` instead of `"REF-2"`, the report says so:

    ```text
    REF-2      NO TESTS
    ...
    REF2       not in --requirements (typo?)
    ```

    Without this, the typo would quietly make REF-2 look untested, or worse, make you think a test exists for a rule that has none.

7. **Keep it alive.** Traceability is only useful if it stays true. Two small habits:

    - When a requirement changes, search for its ID in the CSV and the tests. That's your list of cases to update.
    - Run both reports in the pipeline, so a missing link fails the build instead of waiting for an audit.

    !!! success "Check: you should now be able to"
        Build a traceability matrix, explain both findings from step 4, and link pytest tests to requirements with the `covers` marker.

## When it goes wrong

- **Requirements have no IDs.** Add them yourself, in the story or in a separate file, and share the list: "I numbered the criteria REF-1 to REF-7 for testing." Most teams happily adopt the numbers.
- **One requirement has 40 test cases and another has one.** Look at both. Forty might mean the rule is too big and should be split. One might be fine for a small rule, but check it has a negative case.
- **The matrix says everything is covered, but bugs still slip through.** Traceability shows that a test *exists*, not that it's good. A requirement can be "covered" by one weak positive case. Use [positive and negative cases](positive-and-negative-cases.md) and [boundary values](../test-design/boundary-values.md) to make sure each link is worth something.
- **Your team uses a test management tool.** The same idea applies: most tools have a "requirements" or "links" field. The scripts here are for teams that keep test cases next to the code, which is common and free.

## Common mistakes

!!! warning "Common mistakes"
    - **Keeping manual and automated tests in two lists that never meet.** Compare them, like step 5.
    - **Treating "covered" as "well tested".** One test per requirement is a minimum, not a goal.
    - **Ignoring IDs that don't exist.** They point to typos, or to requirements nobody wrote down.

!!! failure "If you see this error"
    **`KeyError: 'Covers'`**
    The CSV has no column called exactly `Covers`. Check the first line of the file (after the comment line): the column names must match the template, including the capital letter. Spreadsheet programs sometimes add spaces or rename columns when saving.

## Try it yourself

A story has criteria LOG-1 to LOG-4. The test cases are: TC-1 covers LOG-1, TC-2 covers LOG-1;LOG-3, TC-3 covers LOG-5. What will the traceability script report?

??? success "Solution"
    ```text
    | Requirement | Test cases | Count |
    | --- | --- | --- |
    | LOG-1 | TC-1, TC-2 | 2 |
    | LOG-2 | NONE | 0 |
    | LOG-3 | TC-2 | 1 |
    | LOG-4 | NONE | 0 |

    No test case: LOG-2 (...)
    No test case: LOG-4 (...)
    TC-3 covers LOG-5, which is not in the requirements (typo or new?)
    ```

    Two gaps, and one case that points nowhere. TC-3 might be the missing test for LOG-2 or LOG-4 with a typo in the ID. Check that first.

## References

- [ISTQB Glossary: traceability](https://glossary.istqb.org/)
- [pytest: Writing hook functions](https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html): the hooks the covers plugin uses
- [pytest: How to use stash](https://docs.pytest.org/en/stable/reference/reference.html#stash): where the plugin keeps its data during a run
- [Python csv module](https://docs.python.org/3/library/csv.html)

Written for Python 3.13 and pytest 9. Links checked: November 2026.
