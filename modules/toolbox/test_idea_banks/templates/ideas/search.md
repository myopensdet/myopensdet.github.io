<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Search: test ideas

## Works as it should

- An exact name finds the item, at or near the top
- Part of a word finds it ("book" finds "Practice book")
- Upper and lower case give the same results
- Filters and sorting work with the search, and together
- The result count matches the number of results you can page through
- The search words stay in the box after searching, and in the address for sharing

## Refuses bad input

- Empty search: a clear rule (all items, or a message), not an error
- Only spaces
- Special characters: % _ ' " < > & *
- Text that looks like a database command: x' OR '1'='1

## Edges and limits

- No results: a helpful message, and suggestions if the app has them
- One result, and exactly one page of results
- The last page, and a page number after the last (?page=999)
- Very long search text
- Accents and other alphabets (José finds Jose, if it should)
- Plurals and typos, if the app promises to handle them
- A new item can be found (how long until it shows up?), a deleted one can't

## Security

- Search only returns what this user may see (other customers' orders, hidden items)
- Script tags in the search box are shown as text, never run
- Very many searches per second are slowed down

## People, devices and failures

- Fast with real data amounts: time it with the biggest realistic data
- Typing fast with suggestions: the suggestions match the latest text, not an older one
- The search service is down: the rest of the page still works
