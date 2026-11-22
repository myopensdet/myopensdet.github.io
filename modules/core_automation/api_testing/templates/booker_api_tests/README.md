<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# API tests for the booking API

Tests for [Restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html), a public practice API. Change `BOOKER_URL` and the fixtures to test your own API the same way.

## Set up once

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

The login comes from environment variables, never from a file. Restful-booker's demo account is published in its docs:

```bash
export BOOKER_USERNAME=admin BOOKER_PASSWORD=password123
python -m pytest
```

Without them, the tests that need a login are skipped, with a reason.

## Where things are

| Path | What |
| --- | --- |
| `api/client.py` | `ApiClient`: base URL, headers, timeout and logging in one place; `check_status` |
| `api/auth.py` | API key, Basic, Bearer, OAuth2 and Restful-booker login helpers |
| `api/schema.py` | `assert_matches_schema`: every problem, with its path |
| `schemas/` | JSON Schemas for the responses |
| `tests/conftest.py` | fixtures: the client, the token, and bookings that delete themselves |
| `tests/test_*_booking.py` | one file per method: GET, POST, PUT, PATCH, DELETE |
