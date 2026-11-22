<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Should we automate this test? Checklist

Test or check: <what it checks, in one sentence>
Today it runs: <by hand, how often>
Time per manual run: <minutes>

Answer each question with yes or no. More "yes" answers mean a better first target.

## Is it worth automating?

- [ ] It runs often: every release, every sprint, or more
- [ ] If it breaks, users or money are hurt
- [ ] The feature is stable: its screens or API don't change every sprint
- [ ] The expected result is clear, so code can check it (no "looks nice")

## Can we automate it reliably?

- [ ] Code can create the test data it needs, and clean it up after
- [ ] It can run in our CI pipeline, without a person
- [ ] It doesn't depend on a service we can't control, or that service can be replaced with a fake (mock)
- [ ] It doesn't wait for real time to pass (emails, days, expiry), or we can control the clock

## Rough payback

| Item | Value |
| --- | --- |
| Manual minutes per run | <minutes> |
| Runs per month | <number> |
| Manual hours per month (minutes x runs / 60) | <hours> |
| Hours to build the automated test | <hours> |
| Hours per month to keep it working | <hours> |
| Months to pay back (build hours / (manual hours - upkeep hours)) | <months> |

If the payback is longer than about a year, or the upkeep is bigger than the manual time, keep it manual for now.

## Decision

- [ ] Automate now
- [ ] Automate later, when: <condition>
- [ ] Keep it manual, because: <reason>

Decided by: <name>, on <YYYY-MM-DD>
