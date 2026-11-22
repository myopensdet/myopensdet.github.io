<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Reading a test framework someone else wrote

Write the answer next to each line. In two weeks it becomes the README the team never had.

## Run it before you read it

- [ ] The README says how to run it (or I asked, and wrote it down): <command>
- [ ] I installed it in a fresh virtual environment: `pip install -r requirements.txt`
- [ ] `pytest --collect-only -q` lists the tests: <number> tests
- [ ] One test runs and passes on my computer: <which one>
- [ ] I know the settings it needs (`map_test_suite.py`, "Settings it reads"): <list>

## The map

- [ ] Where the tests are, by area (API, UI, database): <folders>
- [ ] The shared fixtures, and what each gives a test: <conftest.py notes>
- [ ] The helpers (API clients, page objects, data builders): <folders>
- [ ] Where test data comes from: created by the test, fixed accounts, a seeded database
- [ ] The markers and when each set runs (pull request, nightly): <smoke, slow...>
- [ ] How it runs in CI: <workflow file, job name>

## Follow one test end to end

- [ ] I picked one important test: <name>
- [ ] I followed every fixture and helper it uses, to the real request or click
- [ ] I made it fail on purpose (changed one expected value) and read the message
- [ ] I ran it in the debugger once, with a breakpoint

## The health check

- [ ] Skipped tests, each with a reason and a ticket? <count without a reason>
- [ ] Fixed waits (`sleep`, `wait_for_timeout`): <count>, the worst: <file:line>
- [ ] Addresses written in the code instead of settings: <list>
- [ ] Secrets in the code? (if yes: tell the lead privately, today)
- [ ] The slowest tests: `pytest --durations=10`
- [ ] Tests that fail often in CI: <names>

## Don't change yet

- [ ] I wrote my ideas in a list instead of changing them in week 1
- [ ] I asked "why is it like this?" before calling anything wrong
