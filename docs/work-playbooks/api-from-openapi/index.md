---
title: "How to Plan and Test an API From Its Swagger (OpenAPI) File"
description: "A step-by-step playbook for testing a whole API from its Swagger or OpenAPI file: where to find the spec, a script that lists every endpoint and finds gaps in the spec, a test plan written for you, a smoke test that checks status, format, schema and login against the spec, pytest checks for the pipeline, and a report."
level: Intermediate
tags:
  - API
  - Test planning
  - Templates
nav_title: "Test an API from its Swagger file"
order: 20
group: "API work"
summary: "From a Swagger link to a plan, contract checks and a report."
updated: "2026-11-22"
---

# How to Plan and Test an API From Its Swagger (OpenAPI) File

Some APIs come with a **Swagger** page: a list of every endpoint, its inputs and its answers. Behind that page is a file, the **OpenAPI spec**. It's the closest thing to a written contract you'll get. This playbook turns that file into a full list of what to test, a set of questions for the team, and automated checks that tell you when the API stops matching its own contract.

!!! example "The situation"
    **Your lead:** "Here's the Swagger link for the pet service: 19 endpoints. Can you plan the testing and get some automated checks into the pipeline this sprint?"

## What you'll have at the end

- An **inventory**: every endpoint in one table, with who may call it and what it needs
- A list of **gaps in the spec itself**, as questions for the team
- A **test plan**, one row per endpoint, written for you
- A **smoke test** that calls every safe endpoint and checks it against the spec
- **pytest checks** for the pipeline, one per endpoint, that grow by themselves when endpoints are added
- A **report** with bugs, open questions and what's not covered yet

!!! note "Before you start"
    - Python 3.13 and a virtual environment ([setup](../../start-here/environment-setup/index.md)).
    - The [kit for this playbook](#templates): `python -m pip install -r requirements.txt`.
    - The Swagger link for a **test environment**, and a test login if the API needs one.

The steps use the **Swagger Petstore**, the public demo that ships with Swagger itself. Every output on this page is from a real run against it.

## Step 1: Get the spec file

The Swagger page is for people. The file behind it is for tools. Common places, by the framework the developers used:

| Built with | Swagger page | Spec file |
| --- | --- | --- |
| FastAPI (Python) | `/docs` | `/openapi.json` |
| Spring Boot with springdoc (Java) | `/swagger-ui.html` | `/v3/api-docs` |
| ASP.NET with Swashbuckle (C#) | `/swagger` | `/swagger/v1/swagger.json` |
| NestJS (Node.js) | `/api` | `/api-json` |
| Anything else | the Swagger page | Open the browser's **Network** tab, reload, and look for a `.json` or `.yaml` file |

Petstore's is at `https://petstore3.swagger.io/api/v3/openapi.json`. Download it into your test project:

```bash
curl -o openapi.json https://petstore3.swagger.io/api/v3/openapi.json
```

Keep this copy in Git, next to your tests. When the developers change the API, `git diff openapi.json` shows you exactly what changed, before any test fails.

## Step 2: List every endpoint

```bash
python openapi_check.py inventory openapi.json --plan endpoint_plan.md
```

```text
Swagger Petstore - OpenAPI 3.0 1.0.27: 19 endpoints

endpoint                             login  needs                answers                  spec gaps
------------------------------------------------------------------------------------------------------------------------
POST /pet                            yes    body                 200,400,422,default      error answers have no body format; needs login, but no 401/403 listed
PUT /pet                             yes    body                 200,400,404,422,default  error answers have no body format; needs login, but no 401/403 listed
GET /pet/findByStatus                yes    status               200,400,default          error answers have no body format; needs login, but no 401/403 listed
GET /pet/findByTags                  yes    tags                 200,400,default          error answers have no body format; needs login, but no 401/403 listed
GET /pet/{petId}                     yes    petId                200,400,404,default      error answers have no body format; needs login, but no 401/403 listed
POST /pet/{petId}                    yes    petId                200,400,default          error answers have no body format; needs login, but no 401/403 listed
DELETE /pet/{petId}                  yes    petId                200,400,default          error answers have no body format; needs login, but no 401/403 listed
POST /pet/{petId}/uploadImage        yes    petId, body          200,400,404,default      error answers have no body format; needs login, but no 401/403 listed
GET /store/inventory                 yes    -                    200,default              needs login, but no 401/403 listed; no error answer listed
POST /store/order                    no     body                 200,400,422,default      error answers have no body format
GET /store/order/{orderId}           no     orderId              200,400,404,default      error answers have no body format
DELETE /store/order/{orderId}        no     orderId              200,400,404,default      error answers have no body format
POST /user                           no     body                 200,default              answer includes password; no error answer listed
POST /user/createWithList            no     body                 200,default              answer includes password; no error answer listed
GET /user/login                      no     -                    200,400,default          error answers have no body format
GET /user/logout                     no     -                    200,default              no error answer listed
GET /user/{username}                 no     username             200,400,404,default      answer includes password; error answers have no body format
PUT /user/{username}                 no     username, body       200,400,404,default      error answers have no body format
DELETE /user/{username}              no     username             200,400,404,default      error answers have no body format

31 spec gaps. Each one is a question for the team.
Plan written to endpoint_plan.md
```

| Column | What it tells you |
| --- | --- |
| `login` | The spec says this endpoint needs a login. Each one needs a "no login" and a "wrong user" test |
| `needs` | Required inputs: path and query values, and `body` if it takes one |
| `answers` | The status codes the spec promises. `default` means "anything else", which promises nothing |
| `spec gaps` | Places where the contract is missing or worrying |

In two minutes you know the size of the job: 19 endpoints, 9 behind a login, 7 that take a body.

## Step 3: Review the spec before you test the API

A gap in the spec is a gap in everyone's understanding: the developers', the front-end team's, and yours. Finding them now is cheaper than finding them as bugs. The script looks for four kinds:

| Gap | Why it matters | Ask |
| --- | --- | --- |
| **needs login, but no 401/403 listed** | Nobody wrote down what happens without a login, so nobody may have tested it | "What do we answer with no login, and with a user who isn't allowed?" |
| **no error answer listed** | The endpoint has no defined way to say "no" | "What happens with bad input here?" |
| **error answers have no body format** | Clients can't show a useful message, and every error may look different | "Is there one error format for the whole API?" |
| **answer includes password** (or token, secret, pin) | A secret in an answer is usually a security bug | "Should this field ever leave the server?" |

Petstore has 31. The `password` in the `User` answer is the one to raise first: it's a security question, not a style question.

Post the gaps in the ticket as questions. Some will turn out fine ("we use a gateway for 401s"); some will become bugs before you send a single request.

## Step 4: Fill in the plan

`--plan` wrote `endpoint_plan.md`, one row per endpoint, with boxes for the four checks almost every endpoint needs:

```text
| Endpoint | Login | Priority | Happy path | Bad input | No / wrong login | Not found | Spec gaps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `POST /pet` | yes | ? | [ ] | [ ] | [ ] | n/a | error answers have no body format; needs login, but no 401/403 listed |
| `PUT /pet` | yes | ? | [ ] | [ ] | [ ] | n/a | error answers have no body format; needs login, but no 401/403 listed |
| `GET /pet/findByStatus` | yes | ? | [ ] | [ ] | [ ] | n/a | error answers have no body format; needs login, but no 401/403 listed |
```

Your job is the **Priority** column. You won't test 19 endpoints deeply this sprint, so decide which ones first:

| Priority | Petstore endpoints | Why |
| --- | --- | --- |
| 1 | `POST /store/order`, the `/user` endpoints, every `DELETE` | Money, personal data (the password), data loss |
| 2 | `POST /pet`, `PUT /pet`, `GET /pet/{petId}`, `GET /pet/findByStatus` | The main flows |
| 3 | `GET /user/logout`, `findByTags`, `uploadImage` | Rarely used, or easy to recover from |

Write the reason next to each priority. When someone asks "why didn't you test logout?", the plan answers.

## Step 5: Smoke-test every safe endpoint

Now check that the running API matches its own contract. `smoke` sends **only GET requests**, so it doesn't change data. It's safe to run on a shared test environment.

```bash
python openapi_check.py smoke openapi.json --base-url https://petstore3.swagger.io/api/v3 \
  --param username=user1 --param petId=1 --param orderId=1 --param tags=tag1
```

```text
Smoke test of https://petstore3.swagger.io/api/v3

endpoint                             status    ms  result
--------------------------------------------------------------------------------------------------------------
GET /pet/findByStatus                   200   759  answered without login
GET /pet/findByTags                     200   755  answered without login
GET /pet/{petId}                        500   732  server error 500; 500 is not listed in the spec
GET /store/inventory                    200   723  answered without login
GET /store/order/{orderId}              404   733  ok
GET /user/login                         200   745  says JSON, but the body isn't JSON
GET /user/logout                        200   747  ok
GET /user/{username}                    200   742  ok

3 ok, 5 with problems, 0 skipped
```

For each endpoint, it checks:

1. **Login:** if the spec says it needs a login and you sent none, it must refuse. Three Petstore endpoints answered anyway. That's a security bug, or a wrong spec: either way, someone must decide.
2. **Status:** 5xx is always a problem, and the status must be listed in the spec. `GET /pet/1` (a pet that doesn't exist) answered **500** where the spec promises 404.
3. **Format:** the `Content-Type` must be one the spec lists, and "JSON" must really be JSON. `GET /user/login` says JSON but answers `Logged in user session: ...` as plain text.
4. **Schema:** the body must match the schema in the spec: required fields, types, allowed values.

`--param` gives values for inputs the spec has no example for. Without them, the endpoint is skipped and the script says which value it needs: `skipped: needs --param petId=...`. Use ids that really exist on your test environment.

With a login, add a header. Its value is never printed:

```bash
python openapi_check.py smoke openapi.json --base-url https://petstore3.swagger.io/api/v3 \
  --param username=user1 --param petId=1 --param orderId=1 --param tags=tag1 \
  -H "api_key: special-key"
```

```text
Smoke test of https://petstore3.swagger.io/api/v3  headers: {'api_key': '***'}
...
6 ok, 2 with problems, 0 skipped
```

(`special-key` is Petstore's published demo key. For your own API, read the token from an environment variable: `-H "Authorization: Bearer $API_TOKEN"`.)

!!! warning "Know what \"ok\" means"
    "ok" means "matches the spec", nothing more. Three examples from this run:

    - `GET /store/order/1` is "ok", but its 404 came back as XML text while other errors are JSON. The spec doesn't say what errors look like, so there's nothing to check against. That's the "error answers have no body format" gap from step 3.
    - `GET /user/{username}` is "ok", and it returns the user's password. The spec lists the field, so the answer "matches". Step 3 caught it; the smoke test can't.
    - `GET /pet/findByStatus` returned an empty list. An empty list matches any list schema. Make sure your test data has records, or the schema check proves little.

The smoke test exits with code 1 when anything is wrong, so a pipeline can run it after every deploy.

## Step 6: Put the checks in the pipeline

`tests/test_contract.py` turns the smoke test into pytest checks, one per GET endpoint, named after the endpoint:

```python
--8<-- "modules/work_playbooks/api_from_openapi/templates/openapi_kit/tests/test_contract.py"
```

It reads the spec, the address, the input values and the login from `tests/conftest.py` and environment variables. Run it:

```bash
python -m pytest -q
```

```text
FAILED tests/test_contract.py::test_get_matches_the_spec[GET /pet/findByStatus]
FAILED tests/test_contract.py::test_get_matches_the_spec[GET /pet/findByTags]
FAILED tests/test_contract.py::test_get_matches_the_spec[GET /pet/{petId}] - ...
FAILED tests/test_contract.py::test_get_matches_the_spec[GET /store/inventory]
FAILED tests/test_contract.py::test_get_matches_the_spec[GET /user/login] - A...
5 failed, 3 passed in 6.82s
```

Each failure says what's wrong:

```text
E       AssertionError: 500: server error 500; 500 is not listed in the spec
E       AssertionError: 200: says JSON, but the body isn't JSON
```

With the demo key (`AUTH_HEADER=api_key AUTH_VALUE=special-key python -m pytest -q`): `2 failed, 6 passed`.

The best part: when developers add an endpoint to the spec, it gets a check on the next run, with no change to the tests. Pair it with [JUnit XML](../../core-automation/reporting-and-logging/junit-xml-for-pipelines.md) and the pipeline shows each endpoint as its own line.

## Step 7: Report

Copy `findings.md` from the kit. Lead with the decision, then bugs, then spec questions, then what isn't covered. For Petstore:

> Three endpoints that the spec says need a login answer without one. One endpoint crashes with 500 for an unknown pet. Users' passwords are part of the user answer. **Security review needed before release.**

Say clearly what the smoke test didn't touch: **POST, PUT and DELETE**. Those change data and need careful, endpoint-by-endpoint tests: use the [new endpoint playbook](../new-api-endpoint/index.md) for each priority 1 endpoint.

## Use it on your own API

1. Download your spec (step 1) into your test project.
2. Run `inventory` with `--plan`. Post the gaps as questions; fill in priorities.
3. Run `smoke` against your **test** environment, with `--base-url`, `--param` for ids that exist there, and `-H` with a token from an environment variable.
4. In `tests/conftest.py`, set `PARAMS` to your ids. Run with `OPENAPI_SPEC`, `BASE_URL`, `AUTH_HEADER` and `AUTH_VALUE` set.
5. Add the pytest run to your pipeline after each deploy.

## When it goes wrong

- **`The spec has no full server address: add --base-url https://...`.** The spec lists a relative server like `/api/v3`, and you gave a file, not a URL. Add `--base-url`.
- **`This spec is YAML: python -m pip install pyyaml`.** The spec is in YAML. Install PyYAML, or download the JSON version if there is one.
- **Every endpoint is "answered without login", but you gave a token.** The header name isn't one the script recognises as a login (`Authorization`, `Cookie`, `X-API-Key`, `api_key`). Check the spec's `securitySchemes` for the name your API uses, and add it to `SECRET_HEADERS` in the script.
- **Every endpoint fails with 401.** The token is wrong or expired, or it belongs in a different header.
- **Lots of "skipped".** Give values with `--param`, or ask the developers to add `example` values to the spec. Examples help every client, not just you.
- **Schema errors on fields that look fine.** Check the spec's version. In OpenAPI 3.0, `nullable: true` means a field may be `null`; this script checks with JSON Schema rules and reports those `null`s. Confirm with the team before reporting a bug.

!!! tip "How an experienced SDET thinks about this"
    - The spec is a contract. Test the API against it, and test the spec itself.
    - Gaps in the spec are cheap to fix today and expensive as bugs next month.
    - Know what "ok" means: matches the spec. A bad spec makes bad answers "ok".
    - Start broad (every endpoint, shallow), then go deep where the risk is.
    - Keep the spec in Git with your tests, and read its diff on every change.

!!! warning "Red flags"
    - "The Swagger page is our documentation" with no error answers in it.
    - Endpoints that need a login, with no 401 or 403 anywhere in the spec.
    - Passwords, tokens or card numbers in answer schemas.
    - Checks written by hand for each endpoint, out of date by next sprint.
    - Running POST and DELETE requests from a smoke test on a shared environment.

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/work_playbooks/api_from_openapi/templates).

=== "openapi_check.py"

    ```python
    --8<-- "modules/work_playbooks/api_from_openapi/templates/openapi_kit/openapi_check.py"
    ```

=== "tests/conftest.py"

    ```python
    --8<-- "modules/work_playbooks/api_from_openapi/templates/openapi_kit/tests/conftest.py"
    ```

=== "findings.md"

    ```markdown
    --8<-- "modules/work_playbooks/api_from_openapi/templates/openapi_kit/findings.md"
    ```

=== "What's in the kit"

    | File | What it's for |
    | --- | --- |
    | `openapi_check.py` | `inventory` (endpoints, spec gaps, plan) and `smoke` (GET checks against the spec) |
    | `tests/test_contract.py`, `tests/conftest.py` | The same checks as pytest tests, one per endpoint |
    | `findings.md` | The report |
    | `requirements.txt`, `pytest.ini`, `.gitignore` | Set-up: pytest, requests and jsonschema |

## Learn the parts in depth

- [Schema validation](../../core-automation/api-testing/schema-validation.md): JSON Schema, and how the checks work.
- [Status codes](../../core-automation/api-testing/status-codes.md) and [authentication](../../core-automation/api-testing/authentication.md).
- [Risk-based testing](../../think-like-a-tester/test-strategy-and-planning/risk-based-testing.md): how to set priorities.

## References

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Swagger Petstore (OpenAPI 3)](https://petstore3.swagger.io/)
- [jsonschema for Python](https://python-jsonschema.readthedocs.io/en/stable/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)

Written for Python 3.13, pytest 9, requests 2.34 and jsonschema 4.26. Outputs captured November 2026. Links checked: November 2026.
