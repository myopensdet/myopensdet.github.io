# Template from myOpenSDET: https://myopensdet.github.io/
"""Sign-up rules for the shop's new member accounts."""

USERNAME_MIN = 3
USERNAME_MAX = 20
MIN_AGE = 18
MAX_AGE = 120


def check_signup(username: str, age: int) -> list[str]:
    """Return the problems with a sign-up. An empty list means it is OK."""
    problems = []
    if not USERNAME_MIN <= len(username) <= USERNAME_MAX:
        problems.append(f"Username must be {USERNAME_MIN} to {USERNAME_MAX} characters")
    elif not username.isalnum():
        problems.append("Username can only use letters and numbers")
    if not MIN_AGE <= age <= MAX_AGE:
        problems.append(f"Age must be {MIN_AGE} to {MAX_AGE}")
    return problems
