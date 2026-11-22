# Template from myOpenSDET: https://myopensdet.github.io/
"""Example template: shows the shape every template follows.

Replace this file with the topic's real template. Keep the credit line above
as the first line of every template file.
"""


def build_greeting(name: str) -> str:
    """Return a greeting for a user (stands in for the template's real job)."""
    # Strip spaces so " Arshad " and "Arshad" give the same result.
    return f"Hello, {name.strip()}!"
