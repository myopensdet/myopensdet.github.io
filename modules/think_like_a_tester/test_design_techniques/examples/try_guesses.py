# Template from myOpenSDET: https://myopensdet.github.io/
"""Try a list of tricky usernames on the sign-up rules, and print what happens.

A quick probe like this comes before writing tests: it shows you which
guesses are interesting. Turn the interesting ones into real tests.

    python try_guesses.py
"""

from shop.signup import check_signup

GUESSES = {
    "spaces around": " arshad ",
    "only spaces": "     ",
    "a tab inside": "ars\thad",
    "a quote": "o'brien",
    "HTML": "<b>hi</b>",
    "SQL-looking": "x' OR '1'='1",
    "emoji": "arshad😀",
    "an accent": "José",
    "a Bengali name": "আরশাদ",
    "wide letters (look like admin)": "ａｄｍｉｎ",
    "digits only": "12345",
    "exactly 20 letters": "a" * 20,
}

for label, username in GUESSES.items():
    problems = check_signup(username, 30)
    result = "accepted" if not problems else problems[0]
    print(f"{label:<32} {result}")
