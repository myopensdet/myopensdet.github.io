<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Test pipeline checklist

Copy this into the ticket when you set up or review a test pipeline.

## When it runs

- [ ] On every pull request (fast tests: smoke, API, unit)
- [ ] On every push to the main branch
- [ ] Every night (the slow tests: full UI, long data checks)
- [ ] By hand, with a "Run workflow" button

## Safety

- [ ] Passwords and tokens are in the CI's **secrets**, never in the code or the workflow file
- [ ] Addresses that are not secret (like `BASE_URL`) are in **variables**
- [ ] The job asks only for the rights it needs (`permissions: contents: read`)
- [ ] Actions are pinned to a full commit SHA, with the version in a comment
- [ ] Tests use test accounts and a test environment, never production

## When tests fail

- [ ] The pipeline turns red, and the pull request can't be merged
- [ ] The summary shows which tests failed, and the first line of each error
- [ ] The report (JUnit XML, screenshots, traces) is kept as an artifact
- [ ] A time limit stops a stuck run (`timeout-minutes`)
- [ ] Someone owns the nightly run and reads it every morning

## Speed

- [ ] Packages are cached between runs
- [ ] A new push cancels the old run of the same branch
- [ ] Slow tests run at night, not on every pull request
- [ ] The pull request run takes under 10 minutes

## Before you push a workflow change

- [ ] `actionlint` finds no problems
- [ ] The same commands pass on your computer, in a new virtual environment
