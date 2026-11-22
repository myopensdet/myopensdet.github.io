<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# State transition worksheet

Use this for anything with a status that changes: an order, an account, a ticket, a payment.

## The thing and its states

- **Thing:** <for example: an order>
- **Starting state:** <for example: placed>
- **All states:** <placed, paid, shipped, ...>
- **All actions (events):** <pay, cancel, ship, ...>

## The diagram

Draw it, even by hand. One box per state, one arrow per allowed action.

## The state table

Rows are states, columns are actions. Write the new state, or "not allowed".

| State now | <action 1> | <action 2> | <action 3> |
| --- | --- | --- | --- |
| <state 1> | <new state> | not allowed | |
| <state 2> | | | |

## Tests to write

- [ ] Each allowed move once (every arrow on the diagram)
- [ ] The happy path from start to end
- [ ] Every "not allowed" cell: the app refuses it, and the state does not change
- [ ] Doing the same action twice (pay twice, cancel twice)
- [ ] Final states: nothing can happen after them, unless the rules say so

## Questions for the team

- [ ] What should the user see when a move is not allowed?
- [ ] Can two people change the same thing at the same time? (For example, the customer cancels while the warehouse ships.)
