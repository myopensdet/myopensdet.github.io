# Template from myOpenSDET: https://myopensdet.github.io/
"""Read this file and guess what it prints. Then run it: python mystery.py"""

LIMIT = 30


def check(days, refunded, sale, faulty):
    if refunded:
        return "already refunded"
    if days > LIMIT:
        return "too late"
    if sale and not faulty:
        return "sale items only if faulty"
    return None


cases = [
    (10, False, False, False),
    (31, False, False, False),
    (5, True, False, False),
    (5, False, True, False),
]
for case in cases:
    print(case[0], check(*case) or "ok")
