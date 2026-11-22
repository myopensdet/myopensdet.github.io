<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# pytest commands you will use every day

Run them from the folder that has `pytest.ini`. `python -m pytest` uses the pytest of the Python you're running.

## Choose what runs

| Command | Runs |
| --- | --- |
| `python -m pytest` | Everything in `testpaths` |
| `python -m pytest tests/test_cart.py` | One file |
| `python -m pytest tests/test_cart.py::test_total_of_two_items` | One test |
| `python -m pytest -k coupon` | Tests with "coupon" in the name |
| `python -m pytest -k "coupon and not refused"` | Names can be combined with and, or, not |
| `python -m pytest -m smoke` | Tests with the smoke marker |
| `python -m pytest -m "not nightly"` | Everything except nightly tests |
| `python -m pytest -m ""` | Every test, ignoring `-m` in `pytest.ini` |
| `python -m pytest --lf` | Only the tests that failed last time |

## See more, or less

| Command | Shows |
| --- | --- |
| `-v` | One line per test, with its name |
| `-q` | Only dots and the summary |
| `-ra` | Why each test was skipped, failed or xfailed, at the end |
| `-x` | Stops at the first failure |
| `-s` | Your `print()` output, as it happens |
| `-vv` | Full differences in failed asserts |
| `--co -q` | Which tests would run, without running them |
| `--setup-show` | Which fixtures run, and when they are torn down |
| `--fixtures` | Every fixture you can use, with its docstring |
| `--markers` | Every marker, with its description |
| `--durations=5` | The 5 slowest tests |

## When something is wrong

| You see | Try |
| --- | --- |
| `ModuleNotFoundError` for your own code | `pythonpath = src` in `pytest.ini`, and run with `python -m pytest` |
| `fixture 'x' not found` | Is the fixture in a `conftest.py` in the same folder or above? Check the spelling |
| `'smok' not found in markers` | A typo, or add the marker to `markers =` in `pytest.ini` |
| `no tests ran` | File names must start with `test_`, and test functions with `test` |
| A test passes alone but fails with the others | Tests share state. Look for data a fixture doesn't clean up |
