---
title: "Pairwise Testing: Cover Every Pair of Settings With Few Tests"
description: "Why most setting-related bugs need only two settings to line up, how pairwise testing cuts 36 combinations to 9, and a small Python script that builds the table for you."
level: Beginner
tags:
  - Test design
  - Templates
  - Test planning
nav_title: "Pairwise testing"
order: 50
summary: "Cut thousands of setting combinations down to a small set that covers every pair."
updated: "2026-11-22"
---

# Pairwise Testing: Cover Every Pair of Settings With Few Tests

Checkout has to work on three browsers, two kinds of device, three ways to pay and two languages. That is 3 × 2 × 3 × 2 = 36 combinations. Add one more setting and it doubles again. Nobody tests all of them by hand, and running all of them in a browser farm costs real money. Pairwise testing gives you a much smaller set that still catches most of the bugs.

!!! note "Before you start"
    Read [Decision tables](decision-tables.md) first. Pairwise is what you reach for when a decision table gets too big.
    The script needs only Python, no extra packages.

## What you will learn

- Why most setting bugs need only two settings to line up
- What "every pair" means, with a real example
- How to build a pairwise table with the `pairwise.py` script
- When pairwise is the wrong choice

## Why this matters at work

Settings multiply. Browsers, phones, operating systems, languages, payment methods, user roles, feature flags. Teams often pick a few combinations by gut feeling, and the bug ships in the one nobody picked. Pairwise gives you a small set you can defend: "every pair of settings was tested together at least once".

## The idea in plain words

!!! info "In plain words"
    Say a bug only happens on Safari when paying with PayPal. It doesn't matter if the device is a desktop or a phone, or if the page is in English or Bengali. Two settings lined up, and the bug appeared.
    If your tests include Safari with PayPal at least once, you catch it. Pairwise testing makes sure every pair like that, across all your settings, shows up in at least one test.

This isn't a guess. Research by NIST, the US standards institute, found that **most software failures are caused by one or two settings**, with fewer and fewer needing three or more. Pairs catch the biggest share for the smallest cost.

## Step by step

1. **List the settings and their values.** For checkout:

    | Setting | Values |
    | --- | --- |
    | Browser | Chrome, Firefox, Safari |
    | Device | Desktop, Phone |
    | Payment | Card, PayPal, Gift card |
    | Language | English, Bengali |

    Keep the values to the ones that really matter. Use [equivalence partitioning](equivalence-partitioning.md): "Chrome 140" and "Chrome 141" are usually one group.

2. **Build the table with the script.** Copy [pairwise.py](index.md#templates) and run it. Put quotes around a setting that has a space in a value:

    ```bash
    python pairwise.py Browser=Chrome,Firefox,Safari Device=Desktop,Phone "Payment=Card,PayPal,Gift card" Language=English,Bengali
    ```

    You should see:

    ```text
    | # | Browser | Device | Payment | Language |
    | --- | --- | --- | --- | --- |
    | 1 | Chrome | Desktop | Card | English |
    | 2 | Chrome | Phone | PayPal | Bengali |
    | 3 | Firefox | Desktop | Gift card | Bengali |
    | 4 | Safari | Phone | Gift card | English |
    | 5 | Firefox | Desktop | PayPal | English |
    | 6 | Firefox | Phone | Card | Bengali |
    | 7 | Safari | Desktop | Card | Bengali |
    | 8 | Chrome | Desktop | Gift card | English |
    | 9 | Safari | Desktop | PayPal | English |

    9 tests cover every pair. Every combination would be 36 tests.
    ```

    From 36 to 9. And 9 is as low as it can go here: Browser and Payment each have 3 values, so there are 9 browser-and-payment pairs, and each test can hold only one of them.

3. **Check one pair by hand, to trust it.** Find Safari with PayPal: row 9. Phone with Bengali: rows 2 and 6. Gift card with Firefox: row 3. Pick any two values from any two columns, and you will find a row with both. That's the promise.

4. **See how the script works.** It is short enough to read in a few minutes:

    ```python
    --8<-- "modules/think_like_a_tester/test_design_techniques/templates/pairwise.py"
    ```

    It lists every pair that needs covering. Then, again and again, it picks the full combination that covers the most pairs not covered yet, until none are left. This simple method doesn't always find the smallest set, but it is close, and easy to understand. For big real projects, use Microsoft's free [PICT](https://github.com/microsoft/pict) tool, which is fast and lets you add rules like "Safari never runs on Windows".

5. **Add the combinations that matter most.** Pairwise covers pairs, not your business. If most of your customers use Chrome on a phone paying by card, make sure that exact row is in the list, even if it repeats pairs. Add your top real-world combinations on top of the pairwise rows.

    !!! success "Check: you should now be able to"
        List settings and values, build a pairwise table, check a pair by hand, and say why the 9 rows are enough.

## When it goes wrong

- **Some combinations are impossible.** Safari doesn't run on Android, for example. Either remove the value and test that area separately, or use PICT, which supports rules for impossible combinations. Don't just delete rows from the table: you will lose pairs without noticing.
- **A bug needs three settings to line up.** Pairwise can miss it. If a three-setting area is high risk (money, safety), test every combination of those three, and use pairwise for the rest. NIST's research is also why tools offer "3-way" testing.
- **The table changes every time someone adds a value.** That's normal: the rows are rebuilt from the list. Keep the list of settings in the repository, and rebuild the table when it changes, so nobody edits rows by hand.
- **The team doesn't trust a "random-looking" list.** Show them step 3: ask them to name any pair, and find its row together. It takes a minute and settles the doubt.

## Common mistakes

!!! warning "Common mistakes"
    - **Too many values per setting.** Ten browser versions make the table big. Group them first, with equivalence partitioning.
    - **Using pairwise for one rule with conditions.** If the result depends on member, order size and delivery type together, that's a [decision table](decision-tables.md). Pairwise is for settings that should *not* change the result.
    - **Forgetting the real top combinations.** Pairwise rows are a minimum, not your customers' favourite setups.

!!! failure "If you see this error"
    **`ValueError: Expected NAME=value,value but got: card`**
    The shell split a setting at a space. A value like `Gift card` has a space, so put quotes around the whole setting: `"Payment=Card,PayPal,Gift card"`.

## Try it yourself

A mobile app must be tested on: phone (Android, iPhone), screen (small, large), network (Wi-Fi, 4G, slow 3G) and user (guest, member). How many tests would every combination need? Run the script to find a pairwise set.

??? success "Solution"
    Every combination: 2 × 2 × 3 × 2 = 24 tests.

    ```bash
    python pairwise.py Phone=Android,iPhone Screen=Small,Large "Network=Wi-Fi,4G,Slow 3G" User=Guest,Member
    ```

    You should see the last line:

    ```text
    7 tests cover every pair. Every combination would be 24 tests.
    ```

    No set can be smaller than 6 here: Network has 3 values and Phone has 2, so there are 6 network-and-phone pairs, and each test holds only one. The script's simple method finds 7, which is close. A tool like PICT may find 6.

    Then add the most common real setup, for example "iPhone, small screen, 4G, member", if it is not already in the list.

## References

- [NIST: Automated Combinatorial Testing for Software](https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software): the research behind pairwise testing
- [Microsoft PICT](https://github.com/microsoft/pict): a free pairwise tool for real projects
- [Python itertools](https://docs.python.org/3/library/itertools.html): `product` and `combinations`, used in the script

Written for Python 3.13. Links checked: November 2026.
