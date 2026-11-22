# Template from myOpenSDET: https://myopensdet.github.io/
"""Test data factories: a valid, typical object by default. A test changes only what it is about.

make_signup()            # a fine signup with fake details
make_signup(age=17)      # the same, but too young
"""

import os
import random
from dataclasses import dataclass
from decimal import Decimal

from faker import Faker

# One seed per run, printed in pytest's header. TEST_SEED=<number> repeats a run exactly.
# random is fine here: a seed for test data, not a password or a token.
SEED = int(os.environ.get("TEST_SEED") or random.randrange(1_000_000))  # noqa: S311
fake = Faker()
fake.seed_instance(SEED)


@dataclass(frozen=True)
class Signup:
    full_name: str
    email: str
    password: str
    age: int


@dataclass(frozen=True)
class Order:
    subtotal: Decimal
    coupon: str | None
    member: bool


def make_signup(**changes) -> Signup:
    values = {
        "full_name": fake.name(),
        "email": fake.unique.safe_email(),  # example.com/.net/.org only, never a real inbox
        "password": fake.password(length=12),
        "age": fake.random_int(min=21, max=90),  # typical; the edges are in signup_cases.csv
    }
    values.update(changes)
    return Signup(**values)


def make_order(**changes) -> Order:
    values = {
        "subtotal": fake.pydecimal(left_digits=3, right_digits=2, min_value=1, max_value=200),
        "coupon": fake.random_element([None, "SAVE10", "WELCOME5"]),
        "member": fake.pybool(),
    }
    values.update(changes)
    return Order(**values)
