# Template from myOpenSDET: https://myopensdet.github.io/
"""API key, Basic, Bearer and a token login. Run: python auth_demo.py

The keys and passwords here are fake, or the public demo accounts the APIs publish.
"""

import requests

H = "https://httpbin.org"

seen = requests.get(f"{H}/headers", headers={"X-API-Key": "test-key-123"}, timeout=15)
print("API key   ", seen.status_code, "server got", seen.json()["headers"]["X-Api-Key"])

good = requests.get(f"{H}/basic-auth/tester/s3cret", auth=("tester", "s3cret"), timeout=15)
bad = requests.get(f"{H}/basic-auth/tester/s3cret", auth=("tester", "wrong"), timeout=15)
print(
    "Basic     ",
    good.status_code,
    good.json()["authenticated"],
    "| wrong password:",
    bad.status_code,
)

with_token = requests.get(f"{H}/bearer", headers={"Authorization": "Bearer abc123"}, timeout=15)
without = requests.get(f"{H}/bearer", timeout=15)
print(
    "Bearer    ",
    with_token.status_code,
    with_token.json()["authenticated"],
    "| no token:",
    without.status_code,
)

# A login that returns a token, then the token on the next call (DummyJSON's demo user).
login = requests.post(
    "https://dummyjson.com/auth/login",
    json={"username": "emilys", "password": "emilyspass", "expiresInMins": 5},
    timeout=15,
)
token = login.json()["accessToken"]
me = requests.get(
    "https://dummyjson.com/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=15
)
print("Login     ", login.status_code, "then /auth/me:", me.status_code, me.json()["username"])
fake = requests.get(
    "https://dummyjson.com/auth/me", headers={"Authorization": "Bearer nonsense"}, timeout=15
)
print("Bad token ", fake.status_code, fake.json())
