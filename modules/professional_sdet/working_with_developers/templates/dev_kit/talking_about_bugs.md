<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Talking about bugs without blame

The bug is in the code, not in the person. Talk about what you **saw**, what you
**expected**, and what it **means for users**.

| Instead of | Say |
| --- | --- |
| "You broke checkout." | "Checkout returns 500 on every third request since this morning's deploy." |
| "This is obviously wrong." | "The story says 36.00; I get 40.00. Am I reading it right?" |
| "Did you even test this?" | "I found a case the tests don't cover yet: an empty cart." |
| "It doesn't work." | "Order 7 fails 2 times in 6. Evidence and request ids are on the ticket." |
| "Why didn't you fix it?" | "Is this one planned? Users hit it at checkout, so I'd rate it high." |
| "Can't reproduce? Try harder." | "It's intermittent. Want to look at it together for 15 minutes?" |

## Before you raise it

- [ ] I can make it happen again (or I have evidence of each time it happened)
- [ ] I checked it isn't the test data, the environment, or my test
- [ ] I know who's affected, and how badly

## The first message (chat, before the ticket)

> Hi <name>, I think I found something in <feature>: <one sentence of what happens>.
> Evidence: <link or numbers>. Ticket coming; want to look together first?

## When you disagree

1. Find what you agree on: the facts (what happens, when, for whom).
2. Name the real question: is it a bug (story says X), or a missing rule (story says nothing)?
3. Bring the user impact: how many, how often, what it costs them.
4. If you still disagree, ask the product owner to decide. Write down the decision on the ticket.
5. Accept the decision, even if it's "won't fix". Re-raise only with new facts.
