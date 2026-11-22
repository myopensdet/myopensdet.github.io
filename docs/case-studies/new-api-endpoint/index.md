---
title: "How to Test a New API Endpoint When the Docs Are Thin"
description: "A step-by-step playbook for testing a new REST API endpoint at work with little or no documentation: what to ask in the first 30 minutes, a probe script that sends many cases and shows every answer in one table, a one-page test plan, pytest checks written from the rules, and a results report."
level: Intermediate
tags:
  - API
  - Test planning
  - Templates
nav_title: "Test a new API endpoint"
order: 10
summary: "From \"please test this by Friday\" to a plan, tests and a report."
updated: "2026-11-22"
code: "work_playbooks/new_api_endpoint"
---

# How to Test a New API Endpoint When the Docs Are Thin

A developer finishes an endpoint and hands it to you. There is a ticket with two lines, maybe a Swagger page, and a deadline. Nobody has written down what should happen with bad input. This playbook takes you from that moment to a test plan, automated checks and a report your team can act on, in five steps.

!!! example "The situation"
    **Ticket:** "New endpoint `POST /carts/add` is on staging. It creates a cart for a user. Please test before Friday's release."

    That's all. No list of rules, no examples of errors.

## What you'll have at the end

- A one-page **test plan** with the rules, what you'll test, and your questions for the team
- A **probe table**: a dozen requests and what the endpoint answered to each
- **pytest checks** you can run again after every fix
- A **results report** with the bugs, open questions and a clear "ready or not"

!!! note "Before you start"
    - Python 3.13 and a virtual environment ([setup](../../getting-started/environment-setup/index.md)).
    - The [kit for this playbook](#templates): `python -m pip install -r requirements.txt`.
    - The endpoint's address on a test environment, and a way to log in (a test account or token). **Never test on production** unless your team says so in writing.

The steps below use DummyJSON's real `POST /carts/add`, a public demo API, so every output on this page is real. It's a demo: it doesn't really save carts. Treat it like an endpoint from a team you've never met.

## Step 1: Spend 30 minutes finding out what it should do

Before sending a single request, collect what already exists. Most of it is somewhere; it's just not in the ticket.

| Where to look | What you get from it |
| --- | --- |
| The ticket and its parent story | Why it exists, who asked for it |
| Swagger / OpenAPI page (often `/docs` or `/swagger`) | Fields, types, required fields, example bodies |
| The merge request (pull request) | What changed, the developer's own tests, validation rules in the code |
| The web page or app that will call it | Real request bodies: open the browser's **Network** tab and click the button |
| Similar endpoints | How errors usually look in this API |

Then ask the developer five short questions. Ask them in writing, in the ticket, so the answers stay:

1. Which fields are required, and what values are allowed?
2. What should happen with bad input: which status, which message?
3. What does it change: database rows, stock, emails, events?
4. Who may call it? What happens without a login?
5. Is there anything you already know is unfinished?

!!! tip "Don't wait for answers"
    Send the questions, then go to step 2. The probe often answers half of them, and gives you better questions for the rest.

## Step 2: Probe it

Now send it a lot of different requests and look at every answer side by side. Doing that by hand in Postman takes an hour and leaves no record. `api_probe.py` does it in seconds. You write the cases in `cases.json`, one per line:

```json
--8<-- "modules/work_playbooks/new_api_endpoint/templates/endpoint_kit/cases.json"
```

The cases follow a pattern you can reuse for any endpoint: one valid body, then each field missing, of the wrong type, at its edges (0, negative, huge), pointing to something that doesn't exist, repeated, and finally a broken body.

Run it, and pick the fields you want to see from each answer:

```bash
python api_probe.py POST https://dummyjson.com/carts/add --cases cases.json \
  --field products.0.quantity --field total
```

```text
POST https://dummyjson.com/carts/add

case                         status     ms  answer
------------------------------------------------------------------------------------------------------------------
valid: one product              201    242  products.0.quantity=4 total=179.96
missing userId                  400    241  {"message":"User id is required"}
userId is text                  400    268  {"message":"Invalid user id 'abc'"}
empty products                  400    221  {"message":"products can not be empty"}
quantity 0                      201    258  products.0.quantity=1 total=44.99
quantity negative               201    231  products.0.quantity=-2 total=-89.98
quantity is text                201    272  products.0.quantity=null total=null
quantity huge                   201    294  products.0.quantity=1000000 total=44990000
unknown product                 201    234  products.0.quantity=- total=0
same product twice              201   1076  products.0.quantity=2 total=89.98
empty JSON object               400    242  {"message":"User id is required"}
not JSON at all                 400    219  {"message":"Unexpected token 'n', \"not json\" is not valid JSON"}
```

Read it row by row and sort each row into one of three groups:

| Group | Rows here | What you do |
| --- | --- | --- |
| **Looks right** | valid, missing userId, userId is text, empty products, empty JSON | Turn into checks so it stays right |
| **Looks wrong** | quantity negative (total −89.98), quantity is text (total `null`), unknown product (201 with an empty cart) | Likely bugs: confirm the rule, then report |
| **Can't tell** | quantity 0 became 1, quantity 1,000,000 accepted, the same product twice merged | Questions for the team |

That third group matters. Not every surprise is a bug: maybe "0 becomes 1" was decided in a meeting you weren't in. Ask before you report.

Useful options:

- `-H "Authorization: Bearer $API_TOKEN"` adds a header. Token values are printed as `***`, so the output is safe to paste in a ticket. Keep the token in an environment variable, not in your shell history.
- `--save probe-results.json` keeps every full answer, for the bug report.
- Without `--cases`, it sends one request, for a quick look: `python api_probe.py GET https://dummyjson.com/carts/1 --field id --field userId --field totalProducts` prints `no body  200  242  id=1 userId=1 totalProducts=4`.

!!! warning "Be gentle with shared environments"
    A probe sends one request per case, one after another. That's fine. Don't loop it thousands of times on a shared staging server, and never on someone else's public API.

## Step 3: Write the plan on one page

Copy `test_plan.md` from the kit and fill it in. It has five parts:

1. **What it is:** endpoint, purpose, ticket, who calls it, how to log in, who to ask.
2. **Rules:** each one written so a test can check it, with where it came from: *ticket*, *developer*, *seen in the probe*, or *my guess, to confirm*.
3. **What to test:** a table of areas that fits almost any endpoint: happy path, required fields, types, boundaries, references, duplicates, format, access, side effects, speed.
4. **Questions** for the team: the "can't tell" rows from step 2.
5. **Not testing, and why:** so nobody assumes you covered it.

Post it in the ticket. A plan the developer has read catches misunderstandings before you've written a single test.

## Step 4: Turn the rules into checks

The checks in `tests/test_endpoint.py` are written from the **rules**, not from what the endpoint does today. That's the whole point: a test that copies today's behaviour will happily pass on a bug.

```python
--8<-- "modules/work_playbooks/new_api_endpoint/templates/endpoint_kit/tests/test_endpoint.py"
```

- `VALID` is one body that should work. Every bad case is `VALID` with one thing changed, so a failure points at that one thing.
- `REFUSED` is a table: add a row for each new rule. pytest runs one test per row, with the row's name in the result.
- The address and token come from `BASE_URL` and `API_TOKEN` (see `tests/conftest.py`), so the same checks run on any environment.

Run them:

```bash
python -m pytest -q
```

```text
FAILED tests/test_endpoint.py::test_bad_input_is_refused[quantity 0] - Assert...
FAILED tests/test_endpoint.py::test_bad_input_is_refused[quantity negative]
FAILED tests/test_endpoint.py::test_bad_input_is_refused[quantity is text] - ...
FAILED tests/test_endpoint.py::test_bad_input_is_refused[unknown product] - A...
4 failed, 4 passed in 1.91s
```

Each failure says exactly what came back:

```text
>       assert response.status_code == 400, f"got {response.status_code}: {response.text[:200]}"
E       AssertionError: got 201: {"id":209,"products":[{"id":144,"title":"Cricket Helmet","price":44.99,"quantity":-2,"total":-89.98,"discountPercentage":9.64,"discountedPrice":-81,"thumbnail":"https://cdn.dummyjson.com/product-image
E       assert 201 == 400
```

The 4 failures are the 4 rows you marked "looks wrong" or "can't tell" in step 2. If the team says "0 becomes 1 is correct", delete that row and add a test that checks it. Either way, the table now holds the agreed rules.

## Step 5: Report what you found

Copy `findings.md` and fill it in. Lead with the answer people want: **ready or not**, and why. Then:

- **Bugs**, one line each, with the exact input and output, and a severity. Link each to its own ticket ([how to write one](../../manual-testing/bug-reports/index.md)).
- **Open questions** that still block a decision.
- **Not tested**, and why: no access, no time, out of scope.
- **How to run the checks again**, so a developer can confirm the fix without you.

For this endpoint, the summary would read: *"The happy path works. Bad input is mostly accepted: negative and text quantities and unknown products give 201 Created with wrong or empty carts. Not ready to release until the first two are fixed."*

## Use it on your own API

1. In `cases.json`, replace the bodies with your endpoint's. Keep the pattern: one valid body, then one change per case.
2. Run the probe with your address, a token from the environment, and the fields you care about.
3. In `tests/test_endpoint.py`, change `ENDPOINT`, `VALID`, the checks in `test_a_valid_cart_is_created`, and the `REFUSED` table.
4. Run with `BASE_URL=https://your-staging... API_TOKEN=... python -m pytest`.
5. Fill in `test_plan.md` and `findings.md`, and paste them into the ticket.

## When it goes wrong

- **Every case answers 401 or 403.** The token is missing, wrong or expired. Check `echo $API_TOKEN` prints something, and that your header is `Authorization: Bearer ...` (some APIs want `X-API-Key` instead: look at a request in the browser's Network tab).
- **Every case answers 400 with the same message.** The body isn't arriving as JSON. The probe sends `Content-Type: application/json`; if you call the endpoint another way, check that header first. (While writing this page, a shell quoting mistake dropped the header, and every case answered `User id is required`, even the valid one.)
- **`ERROR ConnectionError` in the status column.** Wrong address, VPN not connected, or the environment is down. Open the address in a browser first.
- **`A header needs a colon`.** Write headers as `"Name: value"`, in quotes.
- **The tests pass but you know there's a bug.** The check was written from today's behaviour. Rewrite it from the rule.

!!! tip "How an experienced SDET thinks about this"
    - Find out what it *should* do before you look at what it *does*.
    - Change one thing per case, so every answer tells you something.
    - Sort surprises into "wrong" and "can't tell". Ask about the second group before reporting.
    - Write checks from the rules. A check copied from today's output protects the bugs.
    - Put the plan and the results in the ticket, where the next person will look.

!!! warning "Red flags"
    - Testing only the valid body because "that's what the ticket says".
    - Reporting "it accepts 0" as a bug before asking if that's intended.
    - Tokens pasted into bug reports or committed in test files.
    - A report with no "ready or not".
    - Probing production "just to compare".

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/new_api_endpoint/templates).

=== "api_probe.py"

    ```python
    --8<-- "modules/work_playbooks/new_api_endpoint/templates/endpoint_kit/api_probe.py"
    ```

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/new_api_endpoint/templates/endpoint_kit/test_plan.md"
    ```

=== "findings.md"

    ```markdown
    --8<-- "modules/work_playbooks/new_api_endpoint/templates/endpoint_kit/findings.md"
    ```

=== "tests/conftest.py"

    ```python
    --8<-- "modules/work_playbooks/new_api_endpoint/templates/endpoint_kit/tests/conftest.py"
    ```

=== "What's in the kit"

    | File | What it's for |
    | --- | --- |
    | `api_probe.py` | Send many cases, see every answer in one table |
    | `cases.json` | The cases for the probe; replace with yours |
    | `test_plan.md` | The one-page plan |
    | `tests/test_endpoint.py`, `tests/conftest.py` | The checks, and where the API is |
    | `findings.md` | The results report |
    | `requirements.txt`, `pytest.ini`, `.gitignore` | Set-up; `.gitignore` keeps `.env` and saved probe answers out of Git |

## Learn the parts in depth

- [Test an API from its Swagger file](../api-from-openapi/index.md): when you have a whole API to cover, not one endpoint.
- [API testing](../../api-testing/index.md): HTTP methods, status codes, headers, authentication, schema checks.
- [Boundary values](../../manual-testing/test-design/boundary-values.md) and [equivalence partitioning](../../manual-testing/test-design/equivalence-partitioning.md): where the probe's cases come from.
- [Parametrize](../../automation-testing/pytest/parametrize.md): the table behind `REFUSED`.

## References

- [DummyJSON: Carts](https://dummyjson.com/docs/carts)
- [requests: Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [pytest: How to parametrize tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [OWASP: Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

Written for Python 3.13, pytest 9 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
