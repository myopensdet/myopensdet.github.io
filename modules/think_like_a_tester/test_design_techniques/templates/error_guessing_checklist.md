<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Error guessing checklist

Inputs and actions that break software again and again. Go through the list for each
field or action, and keep the guesses that make sense for it. Add your own team's
past bugs at the end: they are the best guesses of all.

## Text

- [ ] Empty, and only spaces
- [ ] Spaces before or after (pasted text often has them)
- [ ] Very long text (1,000 characters, or the database column's limit + 1)
- [ ] Letters with accents (José), other alphabets (আরশাদ, 李), right-to-left text (سلام)
- [ ] Emoji, and characters that look like others (ａｄｍｉｎ, Cyrillic а instead of a)
- [ ] Quotes and special characters: ' " < > & ; %
- [ ] HTML and script tags: <b>hi</b>, <script>
- [ ] Text that looks like a database command: x' OR '1'='1

## Numbers

- [ ] 0, negative numbers, decimals where whole numbers are expected
- [ ] Leading zeros (007), plus sign (+5), spaces inside (1 000)
- [ ] Very big numbers, and letters in a number field
- [ ] Money: rounding (0.1 + 0.2), one cent below and above each limit

## Dates and time

- [ ] 29 February, 31st of a 30-day month, the last day of the year
- [ ] Midnight, and the hour the clocks change
- [ ] Another time zone than the server's
- [ ] A date in the past where only future dates make sense

## Actions

- [ ] Click the button twice, fast (double orders, double payments)
- [ ] Press Back after finishing, then submit again
- [ ] Open the same page in two tabs and change both
- [ ] Let the session expire, then submit
- [ ] Lose the network halfway, then try again

## Files

- [ ] An empty file, a huge file, the wrong type with the right extension (a .jpg that is really a .exe)
- [ ] A file name with spaces, accents or very long

## Our team's past bugs

- [ ] <a bug that happened here before, and the input that caused it>
- [ ] <another one>
