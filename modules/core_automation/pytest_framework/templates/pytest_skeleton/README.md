<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Tests for <your app>

## Set up once

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

| What | Command |
| --- | --- |
| Everything except API tests | `python -m pytest` |
| Only the smoke tests | `python -m pytest -m smoke` |
| Every test, API tests too | `python -m pytest -m ""` |
| Only API tests, on staging | `APP_STAGING_TOKEN=... python -m pytest -m api --env staging` |
| One file, with every test name | `python -m pytest tests/test_example.py -v` |

## Where things are

| Path | What |
| --- | --- |
| `pytest.ini` | pytest settings and the list of markers |
| `config/environments.toml` | URLs and timeouts per environment, never secrets |
| `tests/conftest.py` | shared fixtures and the `--env` option |
| `tests/test_*.py` | the tests |
