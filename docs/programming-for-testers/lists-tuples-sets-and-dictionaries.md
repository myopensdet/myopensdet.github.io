---
title: "Strings, Lists and Dictionaries: The Shapes Test Data Comes In"
description: "Working with text, lists and dictionaries in Python: strip, lower, split and in for strings; indexes, slices and append for lists; keys, get and items for dictionaries, with examples from real test data."
level: Beginner
tags:
  - Python
  - Test data
nav_title: "Strings, lists and dictionaries"
order: 20
summary: "Text, lists and dictionaries: the three shapes most test data comes in."
updated: "2026-11-22"
---

# Strings, Lists and Dictionaries: The Shapes Test Data Comes In

Almost every piece of test data is one of three things. A **string** is text: an error message, a username, a page title. A **list** is several things in order: users, test results, items in a cart. A **dictionary** is named values: a product with an id, a name and a price, or a whole API response. Learn these three well, and most test code becomes easy to read.

!!! note "Before you start"
    Read [Variables and types](variables-and-data-types.md) first.

## What you will learn

- The string methods testers use most: `strip`, `lower`, `split` and `in`
- How to get items from a list by position, and add to it
- How to read a dictionary safely with `get`
- How to tell which of the three you're looking at

## Why this matters at work

An API response is a dictionary, often with lists inside. An error message is a string you check with `in`. A CSV file is a list of rows. Reading test code means reading these three shapes all day.

## The idea in plain words

!!! info "In plain words"
    A string is a sentence. A list is a numbered queue: first, second, third. A dictionary is a form with labelled boxes: "Name: ...", "Price: ...".
    You get things from a queue by position, and from a form by label.

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/start_here/python_for_testers/examples/collections_demo.py"
    ```

    ```bash
    python collections_demo.py
    ```

    ```text
    Refunds are possible up to 30 days after delivery
    True 3
    ['Refunds', 'are', 'possible']
    4 arshad আরশাদ ['maria', 'admin']
    Pocket notebook None none
    ['id', 'name', 'price', 'in_stock']
    ```

2. **Strings.** `strip()` removes spaces at both ends. Messages from web pages often have them, and `"Saved " == "Saved"` is `False`. `"30 days" in message` checks that one text is inside another, which is often a better check than `==` on a long message. `split(" ")` cuts text into a list of words.

3. **Lists.** Positions start at 0, so `users[0]` is the first. `users[-1]` is the last, whatever the length. `users[1:3]` is a **slice**: from position 1 up to, but not including, 3. `append()` adds to the end, and `len()` counts.

4. **Dictionaries.** `product["name"]` gets a value by its key. If the key might be missing, use `product.get("colour")`, which gives `None` instead of crashing, or `get("colour", "none")` with a default. Assign to add a key: `product["in_stock"] = True`.

5. **Tell them apart.** Square brackets `[...]` with commas make a list. Curly braces `{...}` with `key: value` make a dictionary. Quotes make a string. When you're not sure what you've got, `print(type(value))`.

    !!! success "Check: you should now be able to"
        Clean and search a string, get items from a list by position, and read a dictionary safely with `get`.

## When it goes wrong

- **`IndexError: list index out of range`.** You asked for a position that doesn't exist, like `users[4]` in a list of four. Remember positions start at 0. If the list was empty, that may be the real bug: the API returned no users.
- **`KeyError: 'price'`.** The dictionary has no `"price"` key. Print `product.keys()` to see what it has. Maybe the key is `"Price"`, or the API left it out, which could be a bug to report.
- **A check fails on `"Saved" == "Saved "`.** Hidden spaces. Use `strip()` on text from pages and files.
- **A Bengali or accented name looks wrong.** Python strings handle every language. If the text is broken, the problem is usually how a file was read: see [Reading and writing files](file-handling.md).

## Common mistakes

!!! warning "Common mistakes"
    - **Starting to count from 1.** The first item is `[0]`.
    - **Using `["key"]` when the key may be missing.** Use `get()`.
    - **Checking a long message with `==`.** One small wording change breaks it. Check the part that matters with `in`, if that's enough for the test.

!!! failure "If you see this error"
    **`TypeError: list indices must be integers or slices, not str`**
    You used a name on a list, like `users["name"]`. Lists take positions. You probably have a list of dictionaries: get one first, then its key: `users[0]["name"]`.

## Try it yourself

Open `exercises/ex02_collections.py`. Write `clean_username`, `first_and_last` and `price_of`, then run `python -m pytest tests/test_ex02_collections.py` from the `exercises` folder.

??? success "Solution"
    ```python
    --8<-- "modules/start_here/python_for_testers/solutions/ex02_collections.py"
    ```

    For a list with one item, `items[0]` and `items[-1]` are the same item, so the answer is `("login", "login")`.

## Quick check

1. What does `users[-1]` give you?

    ??? question "Answer"
        The last item of the list.

2. Why use `product.get("price")` instead of `product["price"]`?

    ??? question "Answer"
        `get` gives `None` (or a default) when the key is missing, instead of raising `KeyError`.

3. What does `users[1:3]` give for `["a", "b", "c", "d"]`?

    ??? question "Answer"
        `["b", "c"]`: from position 1 up to, but not including, 3.

## References

- [Python Tutorial: Text](https://docs.python.org/3/tutorial/introduction.html#text)
- [Python Tutorial: Data structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python: String methods](https://docs.python.org/3/library/stdtypes.html#string-methods)

Written for Python 3.13. Links checked: November 2026.
