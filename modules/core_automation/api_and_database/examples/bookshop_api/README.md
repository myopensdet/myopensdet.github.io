<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Practice bookshop API

The app under test in the API + database lessons. It has two bugs planted on purpose. Run it on your own computer only.

```bash
python -m pip install -r requirements.txt
cp .env.example .env              # then change the password
docker compose up -d --wait
# Use the same password you put in .env:
export DATABASE_URL=postgresql://shop_tester:local_only_password@127.0.0.1:5432/bookshop
uvicorn app:app --host 127.0.0.1 --port 8090
```

Its API docs open at http://127.0.0.1:8090/docs. Add two books once, as the lessons do:

```bash
docker compose exec -T postgres psql -U shop_tester -d bookshop -c \
  "INSERT INTO books (title, price, stock) VALUES ('Python for Testers', 24.99, 10), ('SQL in a Week', 19.50, 3)"
```
