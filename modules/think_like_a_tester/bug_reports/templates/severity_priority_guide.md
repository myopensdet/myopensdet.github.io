<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Severity, priority and bug states

Agree this once as a team, and link it from every bug report.

## Severity: how badly it hurts (set by the reporter)

| Severity | Means | Example |
| --- | --- | --- |
| Critical | Data loss, money lost, a security hole, or nobody can use a main feature | Customers are charged twice |
| Major | A main feature is broken for many users, with no easy workaround | Bengali names can't sign up |
| Minor | It works, but wrongly, or there is a workaround | The refund email shows the wrong date |
| Trivial | Cosmetic | A typo on the help page |

## Priority: how soon to fix it (set by the team)

| Priority | Means |
| --- | --- |
| High | Fix now, or before the next release |
| Medium | Fix in a normal sprint |
| Low | Fix when there is time, or never |

Severity and priority are often the same, but not always:
- High severity, low priority: the app crashes on a browser almost nobody uses.
- Low severity, high priority: the company name is misspelled on the home page, the day before a launch.

## Bug states

| State | Means | Next |
| --- | --- | --- |
| New | Reported, nobody has looked yet | Triaged, Duplicate, Not a bug |
| Triaged | Checked, severity and priority set | In progress, Won't fix |
| In progress | Someone is fixing it | Fixed |
| Fixed | A fix is ready | Verified, Reopened |
| Verified | The reporter or a tester checked the fix | Closed |
| Reopened | The fix didn't work, or the bug came back | In progress |
| Closed | Done | Reopened |
| Duplicate | Already reported (link the other bug) | Closed |
| Not a bug | Works as designed (link the rule) | Closed |
| Won't fix | A real bug, but the team chose not to fix it (say why) | Closed |
