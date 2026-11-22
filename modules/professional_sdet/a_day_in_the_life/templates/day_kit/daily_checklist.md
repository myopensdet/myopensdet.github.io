<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# My testing day

## First 30 minutes (before stand-up)

- [ ] Last night's run: `python morning_triage.py reports/junit.xml --known known_issues.txt`
- [ ] Every NEW failure: real bug, test problem, or environment? One line each
- [ ] Is the test environment up? (log in, open the main page)
- [ ] Anything blocking today's tickets?

## Stand-up (2 minutes, not 10)

- [ ] What I finished, what I'm on today, what blocks me
- [ ] Say the release risk out loud if there is one

## Main work (protect 2 to 3 hours of it)

- [ ] One ticket at a time: questions → test ideas → automate → run → report
- [ ] Bugs reported with steps, expected, actual, evidence
- [ ] Tests pushed with the change, not "later"

## Reviews

- [ ] Pull requests waiting for me (app code and test code)
- [ ] Answered questions from developers and the product owner

## Last 15 minutes

- [ ] Tickets updated: status and a short comment
- [ ] Note for tomorrow: what's half done, what I'm waiting for
- [ ] `known_issues.txt` up to date (remove fixed tickets)
