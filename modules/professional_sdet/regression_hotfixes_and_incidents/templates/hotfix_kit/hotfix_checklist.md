<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Hotfix test checklist

Hotfix: <TICKET-ID> <one line: what is broken for users>
Fix in: <pull request link>   Tester: <name>   Started: <HH:MM UTC>

## 1. Reproduce first (5 minutes)

- [ ] I saw the bug happen on the current version (evidence: <request id, screenshot>)
- [ ] I know exactly which users, data or steps trigger it

## 2. Test the fix (on the hotfix build)

- [ ] The exact steps from the incident now work
- [ ] The same thing with other data: <2 or 3 other cases>
- [ ] The nearest edge cases: <empty, the limit, a second time>
- [ ] A test that fails on the old version and passes on the fix is added

## 3. Regression for the change

- [ ] `pick_tests.py` on the changed files: `<command it printed>`
- [ ] Those tests pass: <N passed>
- [ ] Smoke tests pass on the hotfix build

## 4. Decide and say it in writing

- [ ] What I tested, what I didn't, and the risk: <one paragraph>
- [ ] Recommendation: release / don't release yet, because <reason>

## 5. After release

- [ ] Smoke check on production (if allowed): <result>
- [ ] Watch errors and logs for 30 to 60 minutes: <result>
- [ ] The test from step 2 is merged to main, so the bug can't come back
