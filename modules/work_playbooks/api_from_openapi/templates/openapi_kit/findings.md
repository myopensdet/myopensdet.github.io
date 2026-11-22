<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# API check: Swagger Petstore 1.0.27

**Tested on:** `https://petstore3.swagger.io/api/v3`, on `YYYY-MM-DD`
**Tested by:** your name
**How:** `openapi_check.py inventory` (19 endpoints, 31 spec gaps) and `smoke` on the 8 GET
endpoints, without and with the API key. Checks in `tests/test_contract.py`.

## Summary

Three endpoints that the spec says need a login answer without one. One endpoint crashes with
500 for an unknown pet. Users' passwords are part of the user answer. **Security review
needed before release.**

## Bugs

| # | What | Severity |
| --- | --- | --- |
| 1 | `GET /pet/findByStatus`, `/pet/findByTags`, `/store/inventory` answer 200 with no login; the spec says they need one | High |
| 2 | `GET /user/{username}` returns the user's `password` (the spec lists it too) | High |
| 3 | `GET /pet/1` (no such pet) answers 500, not 404 | Medium |
| 4 | `GET /user/login` says `application/json` but answers plain text | Low |

## Spec gaps (questions for the team)

1. No endpoint lists 401 or 403. What does "no login" and "not allowed" look like?
2. Error answers have no body format. `GET /store/order/1` answers 404 as XML text, other
   errors as JSON. Which is right?
3. Should `password` be in the `User` answer schema at all?

## Not checked

POST, PUT and DELETE endpoints (the smoke test sends only GET): see the plan for who tests
them and when.

## How to run the checks again

    OPENAPI_SPEC=... BASE_URL=... AUTH_HEADER=api_key AUTH_VALUE=... python -m pytest
