---
title: "Decision Table Testing: When the Result Depends on Several Conditions"
description: "How to build a decision table from a business rule, find the missing cases before any code exists, and turn each row into a pytest test, with a delivery fee example and a table generator."
level: Beginner
tags:
  - Test design
  - pytest
  - Templates
nav_title: "Decision tables"
order: 30
summary: "List every mix of conditions in a table, so no combination is missed."
updated: "2026-11-22"
---

# Decision Table Testing: When the Result Depends on Several Conditions

Some rules are not about one value. They are about a mix: "free delivery for members, or for big orders, but not for express". Read that sentence twice, and you will still not be sure what happens to a member who orders express. A decision table writes every mix down, so nobody has to guess.

!!! note "Before you start"
    You should know what a test case is. [Equivalence partitioning](equivalence-partitioning.md) helps, but is not needed.
    To run the examples: `pip install pytest`, then run the commands from the `examples` folder.

## What you will learn

- What a decision table is, and when to use one
- How to build one from a rule written in plain words
- How a table finds missing rules before any code exists
- How to turn each row into a test

## Why this matters at work

Rules with "and", "or" and "unless" are where stories go wrong. The product owner had one picture in mind, the developer built another, and the tester tests a third. A decision table is something all three can look at and agree on. It is one of the most useful things you can bring to a planning meeting.

## The idea in plain words

!!! info "In plain words"
    Think of a parent deciding if a child can go out to play. Is the homework done? Is it raining? Is it after dark? Each answer is yes or no. Three questions give eight possible mixes, and the parent has an answer for each one, even if they never wrote it down.
    A decision table writes all eight down. Then you can see if any answer is missing, or if two people would give different ones.

The count is simple. Each yes/no condition doubles the rows: 2 conditions give 4 rows, 3 give 8, 4 give 16.

## Step by step

The delivery rules, as the product owner wrote them in the story:

> Standard delivery is free for members, and free for orders of $50.00 or more. Otherwise it costs $4.99. Express delivery costs $9.99. Members pay $4.99.

1. **List the conditions.** Look for every "if" in the rule, written or hidden. Here there are three, each yes or no:

    - Is the customer a member?
    - Is the order $50.00 or more?
    - Is it express delivery?

2. **Make the empty table.** Three conditions give 8 rows. You can type them out, or use the [decision_table.py](index.md#templates) helper:

    ```bash
    python decision_table.py 'Member' 'Order $50 or more' 'Express'
    ```

    You should see:

    ```text
    | # | Member | Order $50 or more | Express | Result |
    | --- | --- | --- | --- | --- |
    | 1 | Yes | Yes | Yes |  |
    | 2 | Yes | Yes | No |  |
    | 3 | Yes | No | Yes |  |
    | 4 | Yes | No | No |  |
    | 5 | No | Yes | Yes |  |
    | 6 | No | Yes | No |  |
    | 7 | No | No | Yes |  |
    | 8 | No | No | No |  |
    ```

    It is Markdown, so you can paste it straight into a ticket or a wiki page. Notice the single quotes around each condition: they matter, as the error box below explains.

3. **Fill the Result column from the rule.** Go row by row. Here is where it gets interesting:

    | # | Member | Order $50 or more | Express | Result |
    | --- | --- | --- | --- | --- |
    | 1 | Yes | Yes | Yes | **?** |
    | 2 | Yes | Yes | No | Free |
    | 3 | Yes | No | Yes | $4.99 |
    | 4 | Yes | No | No | Free |
    | 5 | No | Yes | Yes | **?** |
    | 6 | No | Yes | No | Free |
    | 7 | No | No | Yes | $9.99 |
    | 8 | No | No | No | $4.99 |

    Rows 1 and 5 can't be filled from the story. Is express free for a big order, like standard is? The story doesn't say. **This is the moment the table pays for itself.** You found a missing rule before a single line of code or test was written.

4. **Ask, and write the answer down.** Ask the product owner: "Is express delivery free for orders of $50 or more?" Say the answer is: "No, express is never free." So row 1 is $4.99 (member price) and row 5 is $9.99. Add "Express is never free" to the story, so the developer sees it too.

5. **Turn each row into a test.** With `parametrize`, the test looks almost exactly like the table:

    ```python
    --8<-- "modules/think_like_a_tester/test_design_techniques/examples/tests/test_delivery_table.py"
    ```

    The `row` number in each line matches the table, and the `f"row {row}"` message means a failure tells you which row broke. Here is the code being tested:

    ```python
    --8<-- "modules/think_like_a_tester/test_design_techniques/examples/shop/delivery.py"
    ```

    ```bash
    python -m pytest tests/test_delivery_table.py -q
    ```

    ```text
    8 passed in 0.03s
    ```

6. **See it catch a forgotten condition.** Say a developer changes `if member or subtotal_cents >= FREE_FROM:` to `if subtotal_cents >= FREE_FROM:`, forgetting members. Run the table again:

    ```text
    E       AssertionError: row 4
    E       assert 499 == 0
    E        +  where 499 = delivery_fee(2000, member=True, express=False)

    FAILED tests/test_delivery_table.py::test_delivery_fee_table[4-True-2000-False-0]
    1 failed, 7 passed in 0.03s
    ```

    "Row 4": a member with a small order, standard delivery, was charged $4.99 instead of nothing. You can point to the row in the table, and everyone understands the bug at once.

    !!! success "Check: you should now be able to"
        Turn a rule into conditions, build the full table, spot the rows the rule doesn't answer, and test each row.

## When it goes wrong

- **The table is huge.** 6 conditions give 64 rows, 10 give over a thousand. First, check if the rule can be split: maybe "delivery type" and "member price" are two separate rules. If it is still too big, use [pairwise testing](pairwise-testing.md), which picks a smart, small set of combinations.
- **Some rows can't happen in real life.** For example, "guest" and "member" can't both be yes. Don't delete the row silently. Mark it "impossible" with the reason, so a reader knows you thought about it.
- **A condition isn't yes or no.** Delivery might be standard, express or pick-up. That's fine: the condition gets three values, and the table gets more rows. 3 delivery types × 2 member values × 2 order sizes = 12 rows.
- **The product owner says "just make it work like before".** Ask them to fill one or two of the unclear rows anyway. "Before" often never had this mix, and an answer now saves a bug report later.

## Common mistakes

!!! warning "Common mistakes"
    - **Testing only the rows you thought of.** The point of the table is to list *all* the mixes, so the ones nobody thought of become visible.
    - **Filling unclear rows with a guess.** A guess in the table becomes a guess in the test, and then a bug nobody can explain. Ask.
    - **Not showing the table to anyone.** The table is a conversation tool. Share it before you write the tests.

!!! failure "If you see this error"
    **The table header says `Order  or more`, with the `$50` missing**
    You used double quotes. Inside double quotes, the shell reads `$5` as a variable, finds nothing, and drops it, before Python even starts. Use single quotes around any condition with a `$` in it: `python decision_table.py 'Member' 'Order $50 or more' 'Express'`.

## Try it yourself

A bank app has this rule: "A transfer needs a code by text message if it is over $1,000, or if it goes to a new payee. Business accounts never need the code." Build the decision table.

??? success "Solution"
    Three conditions: over $1,000, new payee, business account. 8 rows:

    | # | Over $1,000 | New payee | Business | Needs a code? |
    | --- | --- | --- | --- | --- |
    | 1 | Yes | Yes | Yes | No |
    | 2 | Yes | Yes | No | Yes |
    | 3 | Yes | No | Yes | No |
    | 4 | Yes | No | No | Yes |
    | 5 | No | Yes | Yes | No |
    | 6 | No | Yes | No | Yes |
    | 7 | No | No | Yes | No |
    | 8 | No | No | No | No |

    Notice that "Business: Yes" gives "No" in every row: rows 1, 3, 5 and 7 behave the same. That is worth a question to the product owner: "Really never? Even $50,000 to a brand new payee?" Rules that say "never" are often wrong in one case.

    And don't forget the boundary: what about exactly $1,000? "Over" means $1,000.00 does *not* need a code, but $1,000.01 does. Test both.

## References

- [ISTQB Glossary: decision table testing](https://glossary.istqb.org/)
- [pytest: How to parametrize tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [Python itertools.product](https://docs.python.org/3/library/itertools.html#itertools.product): how the helper builds every combination

Written for Python 3.13 and pytest 9. Links checked: November 2026.
