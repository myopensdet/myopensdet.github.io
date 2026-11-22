<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# API test plan: Booking API

Fill this in before you write tests. Post it in the ticket so the developer can check it.

## 1. The basics

| Question | Answer |
| --- | --- |
| API address (test environment) | `https://restful-booker.herokuapp.com` |
| Where the spec is | `https://restful-booker.herokuapp.com/apidoc/index.html` |
| How to log in | `POST /auth` with username and password, gives a token. Send it as a cookie: `token=...` |
| Test account | From the team. Never written in a file |
| Who to ask | ? |

## 2. Endpoints and the tests for each

| Endpoint | What it does | Login? | Tests | Done |
| --- | --- | --- | --- | --- |
| `GET /booking/{id}` | Read one booking | No | exists: 200 and the data; missing id: 404; text id: 400 or 404 | [ ] |
| `GET /booking` | List booking ids | No | 200, and a new booking is in the list | [ ] |
| `POST /booking` | Create a booking | No | valid: 200 and the same data back; missing field: 400; wrong type: 400; checkout before checkin: 400 | [ ] |
| `PUT /booking/{id}` | Replace a booking | Yes | changes and is saved; no login: 403; missing id: 404; incomplete body: 400 | [ ] |
| `DELETE /booking/{id}` | Delete a booking | Yes | gone afterwards (GET gives 404); no login: 403 and still there; twice: 404 | [ ] |

## 3. Questions for the developer

1. What should a missing required field answer? (The docs don't say.)
2. Is a checkout date before the checkin date allowed?
3. What should PUT and DELETE answer for an id that doesn't exist?

## 4. Not in this plan

- Speed and load
- The web pages that use this API
