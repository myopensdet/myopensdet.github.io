---
title: "Fake Test Data With Faker: Realistic, Safe and Repeatable"
description: "Use Faker for realistic names, emails and amounts in tests. Keep it safe (example.com emails, never real people) and repeatable (one seed per run, printed, so any failure can be run again)."
level: Intermediate
tags:
  - Test data
  - Python
  - pytest
nav_title: "Fake data with Faker"
order: 40
summary: "Realistic fake data, safe emails, and a seed to repeat any run."
updated: "2026-11-22"
---

# Fake Test Data With Faker: Realistic, Safe and Repeatable

Typing `test1@test.com` into every test is quick, and it hides bugs: every test uses the same short name, the same plain email, the same round number. **Faker** makes realistic values instead: real-looking names, emails, passwords and prices, different every run. Two rules keep it under control: **the data must be safe, and every run must be repeatable.**

!!! note "Before you start"
    Read [one test, many rows](one-test-many-rows.md). The template needs `faker` (in its `requirements.txt`).

## What you will learn

- When fake data helps, and when fixed rows are better
- Which Faker emails are safe, and which ones look like real inboxes
- How one seed per run makes any failure repeatable

## Why this matters at work

Copying production data into tests puts real people's details where they don't belong: in logs, screenshots, bug reports and laptops. Fake data looks just as real and belongs to nobody. Random fake data also tries values nobody thought to write down, which is how it finds bugs.

## The idea in plain words

!!! info "In plain words"
    A driving instructor doesn't test you on the same street every day. Each lesson picks new streets. If something goes wrong, they write down the route, so you can drive it again.

## Step by step

1. **See what Faker makes.** With the template's factories and a fixed seed:

    ```text
    Signup(full_name='Allison Hill', email='donaldgarcia@example.net', password='#&(WTSnJL8q1', age=56)
    Signup(full_name='Tyler Rogers', email='jamesmichael@example.com', password='g)y4ZnbpUe$4', age=17)
    Order(subtotal=Decimal('117.52'), coupon='SAVE10', member=True)
    Order(subtotal=Decimal('54.41'), coupon='WELCOME5', member=False)
    ```

2. **Use only safe emails.** 300 emails from each Faker function, by domain:

    ```text
    email: [('example.org', 109), ('example.net', 96), ('example.com', 95)]
    safe_email: [('example.net', 112), ('example.org', 101), ('example.com', 87)]
    free_email: [('hotmail.com', 111), ('gmail.com', 100), ('yahoo.com', 89)]
    ```

    `example.com`, `.net` and `.org` are kept for examples, and no mail is ever delivered there. `free_email()` makes addresses at real providers: a test that sends email could reach a real person. The template uses `safe_email()`, which says what it does in its name, and a topic test checks 300 of them.

3. **Seed every run, and print the seed.** `helpers/factories.py` starts with:

    ```python
    # random is fine here: a seed for test data, not a password or a token.
    SEED = int(os.environ.get("TEST_SEED") or random.randrange(1_000_000))  # noqa: S311
    fake = Faker()
    fake.seed_instance(SEED)
    ```

    and `tests/conftest.py` prints it at the top of every run:

    ```text
    fake data seed: 474652 (repeat with TEST_SEED=474652)
    ```

    Each run gets new data. The same seed gives the same data again.

4. **See why the seed matters.** A test that picks any adult age at random:

    ```python
    def test_any_adult_can_sign_up():
        signup = make_signup(age=fake.random_int(min=18, max=90))
        assert check_signup(signup.email, signup.password, signup.age) == []
    ```

    It passed with every seed from 1 to 100. Seed 139 picked age 18, and hit the planted AGE-18 bug:

    ```text
    fake data seed: 139 (repeat with TEST_SEED=139)
    >       assert check_signup(signup.email, signup.password, signup.age) == []
    E       AssertionError: assert ['age'] == []
    ```

    Without the seed, that's a test that failed once in the pipeline and never again: "flaky". With it, `TEST_SEED=139 python -m pytest` fails every time, until the bug is fixed. Then add age 18 as a fixed row in your data file, so it's tested on every run, not only by luck.

    !!! success "Check: you should now be able to"
        Make realistic fake data with Faker, keep its emails safe, and repeat any run with its seed.

## When it goes wrong

- **A test fails once and passes on the next run.** Look for the seed at the top of the failed run, and run again with `TEST_SEED=<seed>`.
- **The same seed gives different data.** Something else uses the same `fake` first, in a different order. Run the one failing test alone with the seed, or give each test its own seeded `Faker`.
- **`faker.exceptions.UniquenessException: Got duplicated values after 1,000 iterations.`** `fake.unique` ran out of new values: you asked for more unique values than Faker can make from that list. Ask for fewer, or drop `unique` where repeats are fine.

## Common mistakes

!!! warning "Common mistakes"
    - **Copying production data into tests.** Real people's details end up in logs and screenshots. Make fake data instead.
    - **No seed, or a seed nobody prints.** A random failure you can't repeat is worse than no test.
    - **Random data for edge cases.** Random values rarely hit exactly 18. Edges belong in fixed rows; Faker is for "any valid value".

!!! failure "If you see this error"
    **An email bounce or a message to someone you don't know, from a test run**
    The tests used real-looking addresses. Use `safe_email()` (or `email()` in Faker 40, which also uses example domains), and check the domains in a test.

## Try it yourself

Make a test that creates 50 signups with `make_signup()` and checks every email is different.

??? success "Solution"
    ```python
    def test_fifty_signups_have_fifty_emails():
        emails = {make_signup().email for _ in range(50)}
        assert len(emails) == 50
    ```

    It passes because the factory uses `fake.unique.safe_email()`. Without `unique`, two fake people can get the same email, and a "same email twice" rule would fail at random.

## References

- [Faker documentation](https://faker.readthedocs.io/en/master/)
- [Faker: Seeding the generator](https://faker.readthedocs.io/en/master/#seeding-the-generator)
- [RFC 2606: Reserved top level DNS names](https://www.rfc-editor.org/rfc/rfc2606)

Written for Python 3.13, pytest 9.2 and Faker 40.54. Outputs captured November 2026. Links checked: November 2026.
