---
title: "Error Guessing: Use Known Trouble Spots to Find Bugs Fast"
description: "How error guessing works, a checklist of inputs that break software again and again, a quick probe script, and two real problems it finds in a simple username rule."
level: Beginner
tags:
  - Test design
  - Templates
  - Security
nav_title: "Error guessing"
order: 60
summary: "Try the inputs and actions that break software again and again."
updated: "2026-11-22"
---

# Error Guessing: Use Known Trouble Spots to Find Bugs Fast

Experienced testers often find a bug in the first five minutes with a new feature. It looks like magic, but it isn't. They try the things that have broken software many times before: a double click, an emoji, a name with an apostrophe, the 29th of February. That habit is called error guessing, and you can learn it on purpose instead of waiting years to pick it up.

!!! note "Before you start"
    Read [Equivalence partitioning](equivalence-partitioning.md) first. Error guessing adds the groups that rules forget to mention.
    To run the examples: `pip install pytest`, then run the commands from the `examples` folder.

## What you will learn

- What error guessing is, and why it works
- A checklist of inputs and actions that break software again and again
- How to probe a feature quickly before writing tests
- What to do when a guess finds something the rules don't cover

## Why this matters at work

The other techniques work from the rules. But many bugs live in what the rules *didn't* say: what about spaces, other alphabets, double clicks? Error guessing covers that gap. It is fast and cheap, and it finds the bugs that make users say "how did nobody try this?"

## The idea in plain words

!!! info "In plain words"
    A mechanic who has fixed a hundred cars knows where to look first: the battery, the tyres, the oil. They aren't guessing at random. They are using a list of what usually goes wrong.
    Error guessing is the tester's version: a list of inputs and actions that often break software, tried on purpose.

The "guess" in the name is a little unfair. Good error guessing isn't random. It is **experience written down as a list**, and the list grows each time your team finds a bug.

## Step by step

1. **Start from the checklist.** Copy the [error guessing checklist](index.md#templates). It groups the usual trouble spots: text, numbers, dates, actions and files. Here is the text part:

    ```markdown
    ## Text

    - [ ] Empty, and only spaces
    - [ ] Spaces before or after (pasted text often has them)
    - [ ] Very long text (1,000 characters, or the database column's limit + 1)
    - [ ] Letters with accents (José), other alphabets (আরশাদ, 李), right-to-left text (سلام)
    - [ ] Emoji, and characters that look like others (ａｄｍｉｎ, Cyrillic а instead of a)
    - [ ] Quotes and special characters: ' " < > & ; %
    - [ ] HTML and script tags: <b>hi</b>, <script>
    - [ ] Text that looks like a database command: x' OR '1'='1
    ```

2. **Pick the guesses that fit the feature.** For a username, all the text guesses make sense. For an age field, the number guesses do. Cross out the ones that don't apply, so it is clear you thought about them.

3. **Probe before you write tests.** Don't write a test for every guess yet. First, try them all quickly and look at what happens. A tiny script is enough. This one runs the guesses through the sign-up rules from the [equivalence partitioning](equivalence-partitioning.md) lesson:

    ```python
    --8<-- "modules/think_like_a_tester/test_design_techniques/examples/try_guesses.py"
    ```

    ```bash
    python try_guesses.py
    ```

    You should see:

    ```text
    spaces around                    Username can only use letters and numbers
    only spaces                      Username can only use letters and numbers
    a tab inside                     Username can only use letters and numbers
    a quote                          Username can only use letters and numbers
    HTML                             Username can only use letters and numbers
    SQL-looking                      Username can only use letters and numbers
    emoji                            Username can only use letters and numbers
    an accent                        accepted
    a Bengali name                   Username can only use letters and numbers
    wide letters (look like admin)   accepted
    digits only                      accepted
    exactly 20 letters               accepted
    ```

4. **Read the results like a tester.** Most lines are fine: spaces, HTML and SQL-looking text are refused. But two lines should stop you:

    - **"José" is accepted, but the Bengali name "আরশাদ" is refused.** The rule says "letters and numbers only". Python's `isalnum()` counts "é" as a letter, but not the Bengali vowel sign "া". So the same rule accepts one language and refuses another. For a shop with Bengali-speaking customers, that is a serious problem.
    - **"ａｄｍｉｎ" is accepted.** These are "wide" letters, which look almost the same as "admin". Someone could sign up as a name that looks like the shop's admin, and message customers. This trick is well known. Unicode even publishes a [list of characters that look alike](https://util.unicode.org/UnicodeJsps/confusables.jsp).

    Neither problem was in the rules, and no other technique in this topic would have found them.

5. **Ask before you test.** You don't know the right answer for these two. Should usernames allow every alphabet? Should look-alike characters be refused, or turned into normal ones? That is a product decision, so write it up as a question with the evidence:

    ```text
    Question: which alphabets may usernames use?
    Today: "José" is accepted, "আরশাদ" is refused ("Username can only
    use letters and numbers"). Also "ａｄｍｉｎ" (wide letters) is accepted,
    and looks like "admin".
    Suggest: allow all alphabets, and refuse names that look like an
    existing name after normalising (see Unicode confusables).
    ```

6. **Turn the agreed guesses into tests.** The guesses with a clear answer become tests now. The open questions wait for a decision, with a note in the file:

    ```python
    --8<-- "modules/think_like_a_tester/test_design_techniques/examples/tests/test_error_guesses.py"
    ```

    ```bash
    python -m pytest tests/test_error_guesses.py -q
    ```

    ```text
    7 passed in 0.02s
    ```

7. **Add your team's own bugs to the list.** The last section of the checklist is "Our team's past bugs". After each bug report, ask: "What input caused this? Would it break something else too?" Add it. In a year, your list will be better than any list online.

    !!! success "Check: you should now be able to"
        Pick guesses from the checklist, probe a feature quickly, spot the results that matter, and turn agreed ones into tests.

## When it goes wrong

- **A guess finds something, and the developer says "nobody would type that".** Show who would: a customer who pastes their name from an email (spaces), a customer named O'Brien (a quote), every Bengali-speaking customer. A real person behind the input makes the bug real.
- **A guess crashes the app.** Stop guessing and write a bug report straight away, with the exact input. A crash from typed input is often a security problem too, and may need to go to the security contact, not only the bug list.
- **You run out of ideas.** Look at the [Big List of Naughty Strings](https://github.com/minimaxir/big-list-of-naughty-strings), a public list of text that has broken real software. Use it as a source of ideas, not as a list to paste everywhere.
- **The probe output is long and confusing.** Sort it: refused as expected, accepted as expected, and "surprised me". Only the last group needs your time.

## Common mistakes

!!! warning "Common mistakes"
    - **Guessing at random.** Use the checklist, and your team's past bugs. Random typing finds little.
    - **Writing a test for an undecided behaviour.** You lock in today's answer, which may be wrong. Ask first.
    - **Testing only text.** Actions break things too: double clicks, the Back button, two tabs, an expired login.

!!! failure "If you see this error"
    **`SyntaxError` or strange characters like `Ã©` in the output**
    Your editor or terminal isn't using UTF-8, so characters like é and আ get mixed up. Save the file as UTF-8, and on Windows run `chcp 65001` in the terminal first, or use Windows Terminal, which uses UTF-8 by default.

## Try it yourself

A booking form has a "date of arrival" field and a "Book now" button. Using the checklist, write five guesses you would try first, and say what could go wrong with each.

??? success "Solution"
    One good set:

    | Guess | What could go wrong |
    | --- | --- |
    | 29 February in a leap year, and in a year that isn't | The date is refused when valid, or accepted when it doesn't exist |
    | Today's date, just before midnight | The server is in another time zone and thinks it is already tomorrow, or yesterday |
    | A date in the past | A booking for last week is accepted |
    | Double click on "Book now" | Two bookings, and two payments |
    | Press Back after booking, then "Book now" again | A second booking without warning |

    The last two are actions, not input. Many testers forget them, and they cause some of the most expensive bugs: paying twice.

## References

- [Big List of Naughty Strings](https://github.com/minimaxir/big-list-of-naughty-strings): text that has broken real software
- [Unicode confusables](https://util.unicode.org/UnicodeJsps/confusables.jsp): characters that look like others
- [Python: str.isalnum](https://docs.python.org/3/library/stdtypes.html#str.isalnum): what Python counts as a letter or number
- [OWASP: Cross Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html): why HTML in input matters

Written for Python 3.13 and pytest 9. Links checked: November 2026.
