<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Review comments guide

How to write review comments people act on, for stories, documents and code.
Paste the labels into your team's README so everyone uses the same ones.

## Start each comment with a label

| Label | Means | Example |
| --- | --- | --- |
| **must:** | Has to change before this is done | must: "recent orders" needs a number of days, or we can't test it |
| **question:** | I don't understand, please explain | question: can a refund be partial, for one item of three? |
| **suggest:** | An idea, the author decides | suggest: name the test after the rule, test_refund_needs_reason |
| **nit:** | Tiny and optional | nit: typo in "recieve" |
| **praise:** | Something good, worth keeping | praise: the error table makes the failure cases very clear |

## Write comments that help

- Say what you saw, why it matters, and what you suggest. "This line can crash for guests, because points is never set. Set it to 0 first?"
- Comment on the work, not the person. "This test never fails" instead of "you forgot to assert".
- Ask when you're not sure. A question is not a weakness; it often finds the real bug.
- Keep it to what matters. Five clear comments beat thirty small ones.
- Point to the line, the criterion or the section, so nobody has to search.

## When you receive comments

- Answer every "must" and "question", even with "done" or "agreed".
- If you disagree, say why, once, with a reason. If it stays stuck, talk instead of typing.
- Say thank you. Reviewing takes time.
