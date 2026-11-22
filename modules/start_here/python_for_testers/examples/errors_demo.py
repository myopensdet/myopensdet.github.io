# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: errors and exceptions. Run: python errors_demo.py"""


def parse_price(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        print(f"Not a price: {text!r}")
        return 0.0


print(parse_price("4.25"))
print(parse_price("four"))

try:
    product = {"name": "Pocket notebook"}
    print(product["price"])
except KeyError as error:
    print("Missing key:", error)
finally:
    print("This line runs either way, like cleanup after a test.")
