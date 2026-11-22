<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Should we automate this check?

Answer each question for one check, like "refund on day 31 is refused". Mostly "yes" means automate it. Any "no" in part A means wait or keep it manual.

## A. Can it be automated well?

- [ ] The feature is stable: it hasn't changed in the last few weeks, and no big change is planned.
- [ ] The result is the same every time for the same input (no "looks right", no random waits).
- [ ] We can set up and clean up the test data ourselves.
- [ ] We know the exact expected result.

## B. Is it worth it?

- [ ] It runs often: every pull request, every release, or every night.
- [ ] A person running it by hand is slow, bored or likely to miss something.
- [ ] It protects something important: money, data, security, or a main journey.
- [ ] The payback calculator says it pays back within a few months.

## C. At which level?

- [ ] It can't be checked at a lower, faster level (unit or API) instead.
- [ ] If it is a UI test, it checks a journey, not a rule that a unit test could check.

## Keep it manual when

- It needs a human eye: layout, colours, wording, how it feels to use.
- It is a one-off: a data migration checked once, a launch-day check.
- The feature changes every week, so the test would be rewritten every week.
- Setting it up automatically would take longer than the feature exists.
