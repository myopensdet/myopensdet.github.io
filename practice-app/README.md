# Practice App: Bookshelf

A small online shop with bugs planted on purpose. Every lesson on
[myOpenSDET](https://arshaduzzaman-sm.github.io/myopensdet/) tests this app.

> [!WARNING]
> For practice on your own computer (or your own private Codespace) only. Every
> port listens on `127.0.0.1`. Never deploy it to the internet.

**Version 1.0.** The web shop, the API, three databases, email (Mailpit),
picture uploads, invoice PDFs and a starter set of planted bugs. The plan,
features and data model are in [DESIGN.md](DESIGN.md).

## Start it with one command (Docker)

You need [Docker Desktop](https://docs.docker.com/get-started/get-docker/)
(macOS, Windows or Linux). From the repository folder:

```bash
cd practice-app
docker compose up -d
```

The first start downloads and builds everything (a few minutes). Later starts
take about half a minute. Then open:

| What | Address |
| --- | --- |
| The shop | <http://127.0.0.1:8080> |
| API docs (try every endpoint in the browser) | <http://127.0.0.1:8080/docs> |
| Status: is every part running? | <http://127.0.0.1:8080/status> |
| Mailpit: every email the app sends | <http://127.0.0.1:58025> |

`docker compose down` stops it (your data stays). `docker compose down -v` also
deletes the data. You do not need a `.env` file; copy `.env.example` to `.env`
only if you want to change a setting.

## Start it in the cloud (GitHub Codespaces)

No Docker on your computer? Open the repository in a Codespace: your own
private copy, in the browser, with nothing to install.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/arshaduzzaman-sm/myopensdet?quickstart=1)

1. Click the button, then **Create codespace**. The first start takes a few minutes.
2. The Practice App starts by itself. Open the **Ports** tab and click the globe
   icon next to port **8080** for the shop, or **58025** for Mailpit.
3. Ports are private: only you can open them. Never change a port to **Public**.

GitHub gives every personal account some free Codespace hours each month.
Stop the Codespace when you finish (it also stops by itself after 30 idle minutes).

## Start it without Docker

You need Python 3.13 and the project set up as in
[CONTRIBUTING.md](../CONTRIBUTING.md). Then, from the repository root:

```bash
cd practice-app
../.venv/bin/python -m bookshelf
```

The shop and API are at the same addresses. Instead of three databases, the
app uses SQLite files in `practice-app/data/` (never committed), and every email
is printed in the terminal. Press `Ctrl+C` to stop. If the Docker app is running
too, stop it first (`docker compose stop app`): both use port 8080.

When a new version of the app changes the tables, it rebuilds the practice data
from the seed on its next start (the terminal says so).

## Reset the data

Put every database back to the seed data and delete uploaded pictures:

| How you started it | Command |
| --- | --- |
| Docker or Codespaces | `docker compose exec app python -m bookshelf reset` |
| Without Docker | `../.venv/bin/python -m bookshelf reset` |

Or log in as `admin` and use **Reset all data** on the admin page
(`POST /api/admin/reset` in the API).

## Connect to the databases (Docker)

Use any database client, from your own computer only:

| Database | Address | User | Password | Database name |
| --- | --- | --- | --- | --- |
| PostgreSQL | `127.0.0.1:55432` | `bookshelf` | `local_only_password` | `bookshelf` |
| MySQL | `127.0.0.1:53306` | `bookshelf` | `local_only_password` | `reporting` |
| MongoDB | `127.0.0.1:57017` | `bookshelf` | `local_only_password` | `bookshelf` (auth database: `admin`) |

## Logins to try

| Username | Password | Role |
| --- | --- | --- |
| `arshad` | `Test@1234` | customer |
| `maria` | `Test@1234` | customer |
| `admin` | `local_only_password` | admin |

All fake. There are also 40 customers made by Faker (password `Test@1234` too),
with orders and reviews. The data is the same on every computer. To change any
of this, copy `.env.example` to `.env` and edit it.

## Emails and sign-up codes

The app sends a sign-up code, a password reset code and an order confirmation.

- **With Docker:** open Mailpit at <http://127.0.0.1:58025> to read every email
  (in a Codespace: port 58025 in the **Ports** tab). Nothing reaches a real inbox.
  Tests can read them with Mailpit's API, for example
  `http://127.0.0.1:58025/api/v1/search?query=to:you@example.com`.
- **Without Docker:** every email is printed in the terminal where the app runs,
  and saved as a text file in `practice-app/data/outbox/`.

## Pictures and invoices

- **Profile picture:** on <http://127.0.0.1:8080/profile>, or `POST /api/users/me/avatar`.
- **Product image (admin):** on the admin page, or `POST /api/products/{id}/image`.
- Send the file as form data in a field named `file`: JPEG or PNG, up to 2 MB.
  Anything else gets a clear error (good practice for negative tests).
- **Invoice PDF:** on an order page, "Download invoice (PDF)", or
  `GET /api/orders/{id}/invoice.pdf`.

## Bug Hunts

The app has bugs planted on purpose. Each topic ends with a Bug Hunt: find them
and write a bug report. Start the app with `PRACTICE_APP_BUGS=off` to see the
correct behavior. The answers are in [BUG_HUNT_ANSWERS.md](BUG_HUNT_ANSWERS.md)
(spoilers).

## Sandbox cards

| Card number | What happens |
| --- | --- |
| `4242 4242 4242 4242` | Payment succeeds |
| `4000 0000 0000 0002` | Declined (402) |
| `4000 0000 0000 9995` | Times out (504, after 3 seconds) |

Any expiry date in the future (`12/30`) and any 3-digit CVC (`123`).

## Safety

- Every port is published on `127.0.0.1`, so other computers cannot reach it.
- The app refuses to start on any other address (for example `HOST=0.0.0.0`)
  while it still uses the fake passwords from `.env.example`. Inside Docker it
  listens on `0.0.0.0`, but only because `docker-compose.yml` publishes its port
  on `127.0.0.1`; keep those two lines as they are.
- The app runs as a normal user inside its container, never as root.

## The app's own tests

```bash
.venv/bin/pytest practice-app/tests
```

These check the app itself. They are not the lesson templates: lessons teach
you to write your own tests against the running app.

By default they use throwaway SQLite databases. To run them against the Docker
databases, set `BOOKSHELF_TEST_DATABASE_URL`, `BOOKSHELF_TEST_REPORTING_URL` and
`BOOKSHELF_TEST_MONGODB_URL` (see `tests/conftest.py`). Careful: this resets
the data in those databases. To also check real Mailpit, set
`BOOKSHELF_TEST_MAILPIT=127.0.0.1:51025:58025`.

The tests check the correct behavior, so the planted Bug Hunt bugs are off
while they run. To see which planted bugs they would catch, set
`BOOKSHELF_TEST_BUGS=on`. Today they catch 3 of the 6 planted bugs.
