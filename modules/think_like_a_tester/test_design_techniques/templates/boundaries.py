# Template from myOpenSDET: https://myopensdet.github.io/
"""List the values to test at the edges of a range, so you don't have to work them out by hand.

    python boundaries.py 18 120          # the two values on each side of each edge
    python boundaries.py 18 120 --three  # also the value just inside each edge

Whole numbers only. For money in cents, a step of 1 means one cent.
"""

import sys


def boundary_values(low: int, high: int, three: bool = False) -> list[tuple[int, str]]:
    """Return (value, "inside" or "outside") pairs for the range low..high, edges included."""
    if low > high:
        raise ValueError(f"low ({low}) must not be bigger than high ({high})")
    values = [(low - 1, "outside"), (low, "inside"), (high, "inside"), (high + 1, "outside")]
    if three:
        values[2:2] = [(low + 1, "inside"), (high - 1, "inside")]
    # A very small range (like 5 to 6) gives the same value twice. Keep each value once.
    result = []
    for value, where in values:
        if value not in [v for v, _ in result]:
            result.append((value, where))
    return result


def main(args: list[str]) -> int:
    numbers = [a for a in args if a != "--three"]
    if len(numbers) != 2:
        print("Usage: python boundaries.py LOW HIGH [--three]")
        return 2
    low, high = int(numbers[0]), int(numbers[1])
    print(f"Range {low} to {high}. Test these values:")
    for value, where in boundary_values(low, high, three="--three" in args):
        print(f"  {value:>6}  {where}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
