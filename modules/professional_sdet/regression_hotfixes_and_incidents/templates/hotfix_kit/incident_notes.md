<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Incident notes (write while it happens)

Incident: <short name>   Started: <YYYY-MM-DD HH:MM UTC>   Severity: <SEV1 / SEV2 / SEV3>
Incident lead: <name>   Notes by: <name>   Channel: <link>

## Impact

Who is affected: <users, regions, customers>
What they can't do: <checkout, log in...>

## Timeline (UTC, newest at the bottom; facts, not blame)

| Time | What happened, or what we did | Who |
| --- | --- | --- |
| <HH:MM> | <first alert / first user report> | |
| <HH:MM> | <we checked X, saw Y> | |
| <HH:MM> | <decided to roll back / hotfix> | |
| <HH:MM> | <fix released> | |
| <HH:MM> | <checked: errors back to normal> | |

## What the tester does during an incident

- Reproduce it, and find the smallest steps that trigger it
- Collect evidence: times, request ids, versions (`evidence.py`)
- Check what is NOT broken (helps narrow it down)
- Test the fix or rollback the moment it's ready
- Keep this timeline, so nobody has to remember later
