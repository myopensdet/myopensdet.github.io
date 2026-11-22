# Template from myOpenSDET: https://myopensdet.github.io/
"""Find vague words in a user story or requirement, and the question to ask about each.

    python ambiguity_scan.py story.md
    python ambiguity_scan.py < story.md

Ends with exit code 1 if it finds anything, so it can run in a pipeline.
A word on this list is not always wrong. It is a place to stop and ask.
"""

import re
import sys

# word or phrase -> the question to ask
VAGUE = {
    "fast": "How fast? Give a number and a unit, for example: within 2 seconds.",
    "quickly": "How quickly? Give a number and a unit, for example: within 5 working days.",
    "slow": "How slow is too slow? Give a number.",
    "soon": "How soon? Give a time.",
    "recent": "How recent? Give a number of days.",
    "recently": "How recently? Give a number of days.",
    "easy": "Easy for whom? How will we check it?",
    "simple": "Simple for whom? How will we check it?",
    "user-friendly": "What exactly makes it friendly? How will we check it?",
    "intuitive": "How will we check it? For example: a new user does it without help.",
    "should": "Must it, or is it optional? Write 'must' or 'can'.",
    "may": "Is it allowed, or not? Who decides, and how?",
    "might": "Will it, or won't it? Under which conditions?",
    "usually": "What happens in the other cases?",
    "normally": "What happens in the other cases?",
    "sometimes": "When exactly?",
    "etc": "What else is on the list? Write every item.",
    "and so on": "What else is on the list? Write every item.",
    "some": "Which ones, or how many?",
    "many": "How many?",
    "few": "How many?",
    "appropriate": "Appropriate by what rule?",
    "appropriately": "Appropriately by what rule? What does the user see?",
    "reasonable": "Reasonable by what rule? Give a number.",
    "as needed": "Needed when, and decided by whom?",
    "if possible": "What happens when it is not possible?",
    "properly": "What does 'properly' look like? What is the expected result?",
    "correctly": "What does 'correctly' look like? What is the expected result?",
    "handle": "Handle how? What does the user see?",
    "support": "Support how? Which cases exactly?",
    "all": "Really all? Are there exceptions?",
    "always": "Really always? Are there exceptions?",
    "never": "Really never? Are there exceptions?",
    "tbd": "To be decided by whom, and by when?",
}

PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in sorted(VAGUE, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def scan(text: str) -> list[tuple[int, str, str]]:
    """Return (line number, word as written, question) for every vague word."""
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in PATTERN.finditer(line):
            word = match.group(1)
            found.append((number, word, VAGUE[word.lower()]))
    return found


def main(args: list[str]) -> int:
    if args:
        with open(args[0], encoding="utf-8") as file:
            text = file.read()
    else:
        text = sys.stdin.read()
    found = scan(text)
    for number, word, question in found:
        print(f'line {number}: "{word}"  {question}')
    if found:
        print(f"\n{len(found)} vague words found. Ask about each one before testing.")
        return 1
    print("No vague words found. Still read it: this list can't find missing rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
