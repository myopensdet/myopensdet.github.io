<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Exploratory testing session

## Charter

- **Explore:** cancelling an order (the order status code)
- **With:** actions in the wrong order, repeated actions, and badly typed actions
- **To find out:** whether any order can end up in a wrong status, and whether the messages make sense
- **Time box:** 30 minutes

## Setup

- Version or build tested: the example shop in this topic
- Environment: Python, on a local computer
- Test data: a new order for each try

## Notes (write as you go, with the time)

| Time | What I did | What I saw |
| --- | --- | --- |
| 00:02 | pay, then pay again | Refused: "Can't pay an order that is paid". Good, no double payment |
| 00:05 | cancel, then cancel again | Refused: "Can't cancel an order that is cancelled". Good |
| 00:08 | cancel, then pay | Refused: "Can't pay an order that is cancelled". Good |
| 00:12 | pay, cancel, pay | Refused: "Can't pay an order that is refunded". Good |
| 00:16 | "Pay" with a capital P | Refused: "Can't Pay an order that is placed" |
| 00:19 | "refund", an action that doesn't exist | Refused: "Can't refund an order that is placed" |
| 00:23 | an empty action (None) | Refused: "Can't None an order that is placed" |

## Found

- **Bugs:** an unknown action gets the same message as a known one at the wrong time. "Can't refund an order that is placed" suggests refunds exist and you just picked the wrong moment. The message should say the action is unknown.
- **Questions:** should actions ignore capital letters ("Pay")? Who sends these actions: only our own web page, or other programs too?
- **Ideas:** add a test that an unknown action gives its own clear error. Explore the same actions through the API next, where the input comes straight from users.

## Wrap-up

- What I covered: every action twice in a row, actions after a final status, badly typed actions.
- What I did not cover: two people changing the same order at the same time.
- How it felt: solid. The rules hold. Only the messages need work.
