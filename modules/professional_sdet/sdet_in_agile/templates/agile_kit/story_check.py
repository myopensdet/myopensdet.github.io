# Template from myOpenSDET: https://myopensdet.github.io/
"""Check a user story before the sprint: find vague words in the acceptance criteria,
and the areas the story never mentions. Prints the questions to ask at refinement.

    python story_check.py stories/SHOP-420.md
"""

import re
import sys
from pathlib import Path

# CHANGE: add the vague words your team uses. Word pattern, then the question to ask.
VAGUE = {
    r"\b(fast|quickly|slow|instantly)\b":
        "How fast, in seconds? For how many users at once?",
    r"\b(properly|correctly|appropriately|as expected)\b":
        "What exactly should happen? Which message, which status?",
    r"\b(handle[ds]?|handling)\b":
        "Handled how? Show an error, ignore it, or log it?",
    r"\b(easy|easily|user-friendly|intuitive|simple)\b":
        "How will we check it? What exactly does the user do?",
    r"\b(etc|and so on|and more)\b":
        "What else, exactly? List every item.",
    r"\b(some|many|few|several|large)\b":
        "How many, exactly?",
    r"\b(valid|invalid)\b":
        "What makes it valid? Give one example of each.",
}  # fmt: skip
# CHANGE: the areas every story in your product should think about.
# Name: (words that show the story thought about it, the question to ask if not).
AREAS = {
    "errors": (r"error|invalid|fail|reject|wrong|expired",
               "What does the user see when it goes wrong?"),
    "empty or missing input": (r"empty|blank|missing|without",
                               "What if the field is left empty?"),
    "limits": (r"\bmax|\bmin|limit|at most|at least|up to|characters",
               "Are there limits (length, amount, count)?"),
    "who can do it": (r"permission|role|admin|logged in|signed in|guest",
                      "Who may do this? Guests too?"),
    "repeats": (r"twice|again|more than one|already|repeat|duplicate",
                "What if the user does it twice?"),
}  # fmt: skip
STORY_SENTENCE = r"\bas an?\b.*\bi want\b.*\bso that\b"


def criteria(text: str) -> list[str]:
    """The list items under the 'Acceptance criteria' heading."""
    found, inside = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            inside = "acceptance" in line.lower()
        elif inside and re.match(r"\s*([-*]|\d+\.)\s+", line):
            found.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", line).strip())
    return found


def main() -> int:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        print("Usage: python story_check.py <story file>")
        return 2
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    title = next(
        (line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("# ")),
        sys.argv[1],
    )
    items = criteria(text)
    print(f"== {title}")
    if not re.search(STORY_SENTENCE, text, re.I | re.S):
        print("   No 'As a ..., I want ..., so that ...' sentence: who is it for, and why?")
    if not items:
        print("   No acceptance criteria found. Add a '## Acceptance criteria' list first.")
        return 1
    questions = 0
    print(f"\n== {len(items)} acceptance criteria")
    for number, item in enumerate(items, 1):
        print(f"AC{number}  {item}")
        for pattern, question in VAGUE.items():
            word = re.search(pattern, item, re.I)
            if word:
                print(f'      "{word.group(0)}" -> {question}')
                questions += 1
        if not re.search(r"\d|e\.g\.|for example|\bgiven\b", item, re.I):
            print("      no example -> Add one real example with values.")
            questions += 1
    print("\n== Not mentioned anywhere in the story")
    missing = [
        (area, q) for area, (pattern, q) in AREAS.items() if not re.search(pattern, text, re.I)
    ]
    for area, question in missing:
        print(f"   {area:<24} {question}")
    if not missing:
        print("   nothing: every area is covered")
    total = questions + len(missing)
    print(f"\n{total} questions for refinement." if total else "\nReady for the sprint.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
