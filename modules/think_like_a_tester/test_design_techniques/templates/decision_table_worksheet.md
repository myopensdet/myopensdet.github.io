<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Decision table worksheet

Use this when the result depends on several conditions together.
Tip: `python decision_table.py "Condition one" "Condition two"` prints the empty table for you.

## The rule, word for word

<copy it from the story or the spec>

## Conditions and results

- **Conditions** (each one yes or no): <condition 1>, <condition 2>, <condition 3>
- **Possible results:** <result A>, <result B>

## The table

| # | <condition 1> | <condition 2> | <condition 3> | Result |
| --- | --- | --- | --- | --- |
| 1 | Yes | Yes | Yes | |
| 2 | Yes | Yes | No | |
| 3 | Yes | No | Yes | |
| 4 | Yes | No | No | |
| 5 | No | Yes | Yes | |
| 6 | No | Yes | No | |
| 7 | No | No | Yes | |
| 8 | No | No | No | |

## Check the table

- [ ] Every row has a result. A row you can't fill is a question for the product owner.
- [ ] Rows that can't happen in real life are marked "impossible", with the reason.
- [ ] The product owner agreed the filled table.
- [ ] Each row is one test case (or one row in `pytest.mark.parametrize`).
