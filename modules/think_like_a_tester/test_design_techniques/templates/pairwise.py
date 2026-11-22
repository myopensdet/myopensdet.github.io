# Template from myOpenSDET: https://myopensdet.github.io/
"""Pick a small set of test combinations that still covers every pair of values.

    python pairwise.py Browser=Chrome,Firefox,Safari Device=Desktop,Phone Payment=Card,PayPal

Each setting is NAME=value,value,... Put quotes around a setting with spaces:
    python pairwise.py "Payment=Card,Gift card"

Why pairs? Most bugs that depend on settings need only two of them to line up
(for example Safari with PayPal). Testing every pair catches those, with far
fewer tests than every full combination.
"""

import itertools
import sys

MAX_COMBINATIONS = 100_000  # above this, the simple search below gets slow


def parse(args: list[str]) -> dict[str, list[str]]:
    settings = {}
    for arg in args:
        name, sep, values = arg.partition("=")
        if not sep or not name or not values:
            raise ValueError(f"Expected NAME=value,value but got: {arg}")
        settings[name] = [v.strip() for v in values.split(",") if v.strip()]
    return settings


def pairs_in(row: tuple[str, ...]) -> set[tuple[int, str, int, str]]:
    return {(i, row[i], j, row[j]) for i, j in itertools.combinations(range(len(row)), 2)}


def all_pairs(settings: dict[str, list[str]]) -> set[tuple[int, str, int, str]]:
    values = list(settings.values())
    pairs = set()
    for i, j in itertools.combinations(range(len(values)), 2):
        for a in values[i]:
            for b in values[j]:
                pairs.add((i, a, j, b))
    return pairs


def pairwise(settings: dict[str, list[str]]) -> list[tuple[str, ...]]:
    """Return rows that cover every pair of values at least once."""
    candidates = list(itertools.product(*settings.values()))
    if len(candidates) > MAX_COMBINATIONS:
        raise ValueError(f"{len(candidates)} combinations is too many for this script")
    if len(settings) < 2:
        return candidates
    missing = all_pairs(settings)
    rows = []
    while missing:
        # Take the combination that covers the most pairs not covered yet.
        best = max(candidates, key=lambda row: len(pairs_in(row) & missing))
        rows.append(best)
        missing -= pairs_in(best)
    return rows


def main(args: list[str]) -> int:
    if len(args) < 2:
        print("Usage: python pairwise.py NAME=value,value NAME=value,value ...")
        return 2
    settings = parse(args)
    rows = pairwise(settings)
    every = 1
    for values in settings.values():
        every *= len(values)
    print("| # | " + " | ".join(settings) + " |")
    print("| --- | " + " | ".join("---" for _ in settings) + " |")
    for number, row in enumerate(rows, start=1):
        print(f"| {number} | " + " | ".join(row) + " |")
    print(f"\n{len(rows)} tests cover every pair. Every combination would be {every} tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
