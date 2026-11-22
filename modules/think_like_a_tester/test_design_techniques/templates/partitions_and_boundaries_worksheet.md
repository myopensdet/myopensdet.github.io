<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Groups and edges worksheet

One sheet per input (a field, a number, a setting). Fill it before you write any tests.

## The input

- **Name:** <for example: age on the sign-up form>
- **The rule, word for word:** <copy it from the story or the spec>
- **Type:** <whole number / money / text / date / list>

## Groups (equivalence partitions)

Every value in a group should be treated the same way. Pick one value from each group.

| Group | Allowed? | Example value | Expected result |
| --- | --- | --- | --- |
| <below the range> | No | <value> | <error message> |
| <inside the range> | Yes | <value> | <accepted> |
| <above the range> | No | <value> | <error message> |
| <wrong type: letters, empty, blank> | No | <value> | <error message> |

## Edges (boundary values)

For each edge: the last value on one side, and the first value on the other.
Tip: `python boundaries.py LOW HIGH` lists them for you.

| Value | Inside or outside | Expected result |
| --- | --- | --- |
| <low - 1> | Outside | <error> |
| <low> | Inside | <accepted> |
| <high> | Inside | <accepted> |
| <high + 1> | Outside | <error> |

## Questions for the team

- [ ] Is the edge itself allowed? ("up to 120": is 120 OK?)
- [ ] What happens with an empty value, or spaces only?
- [ ] Is the same rule checked in the browser and in the API? (Test both edges in both places.)
