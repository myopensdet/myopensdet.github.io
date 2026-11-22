# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: if and loops. Run: python loops_demo.py"""

codes = [200, 201, 404, 500, 200]

for code in codes:
    if code < 300:
        group = "ok"
    elif code < 500:
        group = "client error"
    else:
        group = "server error"
    print(code, group)

errors = [code for code in codes if code >= 400]
print("errors:", errors)

for number, name in enumerate(["login", "search", "pay"], start=1):
    print(f"step {number}: {name}")

# Try again until it works, but never forever: a limit, and break when done.
answers = iter([503, 503, 200])  # a pretend server that is slow to start
for attempt in range(1, 6):
    status = next(answers)
    print(f"try {attempt}: {status}")
    if status == 200:
        break
