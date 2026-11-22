<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Postmortem: <incident name>

Date: <YYYY-MM-DD>   Duration: <HH:MM to HH:MM UTC>   Written by: <names>

**Blameless:** we look for what in our system and process let this happen, not who
made a mistake. People did reasonable things with what they knew at the time.

## Summary (three sentences)

<What broke, for whom, for how long. How we fixed it.>

## Impact

- Users affected: <number or %>
- What they couldn't do: <...>
- Data lost or wrong: <none / details>

## Timeline

<Copy the key rows from the incident notes.>

## Root cause: ask "why?" until you reach something we can change

1. Why did <symptom happen>? Because <...>
2. Why <...>? Because <...>
3. Why <...>? Because <...>
4. Why <...>? Because <...>
5. Why <...>? Because <...> **(a gap in a process or a check: that's the root cause)**

## Why our tests didn't catch it

- <Which test should have, and why it didn't exist or didn't fail>

## Actions (each with an owner and a date)

| Action | Owner | Due | Ticket |
| --- | --- | --- | --- |
| <a test that would have caught it> | | | |
| <a monitoring alert that would have shown it sooner> | | | |
| <a process change> | | | |

## What went well

- <Fast detection? Good teamwork? Easy rollback?>
