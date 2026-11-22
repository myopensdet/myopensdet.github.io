<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# HTTP cheat sheet for testers

## Methods

| Method | Does | Body? | Safe to repeat? |
| --- | --- | --- | --- |
| `GET` | Read | No | Yes: changes nothing |
| `POST` | Create, or start an action | Yes | **No**: twice can mean two orders |
| `PUT` | Replace the whole thing | Yes | Yes: the result is the same |
| `PATCH` | Change some fields | Yes | Usually, but not always |
| `DELETE` | Remove | Rarely | Yes: gone is gone (the second time may answer 404) |
| `HEAD` | Like GET, headers only | No | Yes |
| `OPTIONS` | What's allowed here (browsers send it before CORS requests) | No | Yes |

## Status codes

| Code | Name | What it means for a tester |
| --- | --- | --- |
| 200 | OK | It worked. Check the body too: some APIs answer 200 with an error inside |
| 201 | Created | Created. A `Location` header often says where |
| 204 | No Content | Worked, nothing to send back (typical for DELETE) |
| 301 | Moved Permanently | The address changed for good |
| 302 | Found | A temporary redirect, often to a login page |
| 304 | Not Modified | Use your cached copy |
| 400 | Bad Request | The request is wrong: a missing field, bad JSON |
| 401 | Unauthorized | Not logged in, or the token is wrong or expired |
| 403 | Forbidden | Logged in, but not allowed |
| 404 | Not Found | Nothing at that address (or hidden from you on purpose) |
| 405 | Method Not Allowed | That method isn't allowed on that address |
| 409 | Conflict | Clashes with what's there: a duplicate, an old version |
| 415 | Unsupported Media Type | Wrong `Content-Type` for the body |
| 422 | Unprocessable Content | The JSON is fine, the values aren't (a validation error) |
| 429 | Too Many Requests | Slow down. `Retry-After` says how long |
| 500 | Internal Server Error | The server broke. Always a bug: report it with the request id |
| 502 | Bad Gateway | A server in front got a bad answer from the app behind it |
| 503 | Service Unavailable | Down or overloaded, often during a deploy |
| 504 | Gateway Timeout | The app behind took too long to answer |

**4xx: the client (your request) is wrong. 5xx: the server is wrong.** A 5xx for bad input is a bug: the server should answer 4xx.

## Headers you'll use

| Header | Sent by | Example |
| --- | --- | --- |
| `Content-Type` | Both | `application/json`: what the body is |
| `Accept` | You | `application/json`: what you want back |
| `Authorization` | You | `Bearer <token>` |
| `Cookie` / `Set-Cookie` | You / server | Logins in browsers |
| `Location` | Server | Where the new thing is (201), or where to go (3xx) |
| `Cache-Control` | Server | `no-store`: don't keep a copy (pages with personal data) |
| `Retry-After` | Server | Seconds to wait (429, 503) |
| `X-Request-Id` (name varies) | Server | Put it in every bug report |

## curl

| You want | Write |
| --- | --- |
| A GET, with headers in the answer | `curl -i https://api.example.com/orders/7` |
| A POST with JSON | `curl -i -X POST https://api.example.com/orders -H "Content-Type: application/json" -d '{"item": 1}'` |
| The same, shorter (curl 7.82 or newer) | `curl -i --json '{"item": 1}' https://api.example.com/orders` |
| Send a token | `curl -i -H "Authorization: Bearer $API_TOKEN" https://api.example.com/me` |
| Only the status code | `curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/health` |
| Follow redirects | `curl -iL https://example.com/old-page` |
| See everything (connect, TLS, headers) | `curl -v https://api.example.com/orders/7` |
| Time it | `curl -s -o /dev/null -w "%{time_total}s\n" https://api.example.com/orders` |
| Give up after 10 seconds | `curl --max-time 10 https://api.example.com/orders` |

Keep tokens in an environment variable (`$API_TOKEN`), never typed into a command you paste into a ticket.

## Python requests

```python
import os

import requests

BASE = os.environ.get("API_URL", "https://api.example.com")
headers = {"Authorization": f"Bearer {os.environ['API_TOKEN']}"}

r = requests.post(f"{BASE}/orders", json={"item": 1}, headers=headers, timeout=10)
assert r.status_code == 201, r.text
order = r.json()
```

Always set `timeout=`: without it, a test can wait forever.
