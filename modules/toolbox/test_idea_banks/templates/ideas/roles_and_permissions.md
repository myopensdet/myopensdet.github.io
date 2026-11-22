<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Roles and permissions: test ideas

Make a table first: every role down the side, every action across the top, and what's allowed in each cell. Then test each cell.

## Works as it should

- Each role can do everything it should
- Each role sees only the menu items and buttons it may use
- Giving a user a new role works at once (or after the next login, as the rule says)
- Removing a role takes the access away

## Refuses bad input

- Each role is refused for each action it may not do: a 403, not a 500
- Hidden buttons: the action is still refused when called directly through the API
- A user can't give themselves a higher role

## Edges and limits

- A user with two roles gets the access of both, not just one
- The last admin can't be removed or downgraded
- A user who is removed while logged in loses access on the next request
- Access to data of other teams, shops or customers (change the id in the address)

## Security

- Change ids in addresses and requests: each object checks who owns it
- Old tokens of a removed user are refused
- Every change of roles is in the audit log: who changed what, when
- Admin pages aren't reachable by guessing their address

## People, devices and failures

- The "not allowed" message is clear, and says who to ask
- The permissions table in the docs matches what the app does
