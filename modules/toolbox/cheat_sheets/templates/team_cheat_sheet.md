<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# <Project name>: tester's cheat sheet

<!-- CHANGE everything in < >. Keep it in the test repository, next to the README, so it changes with the code. -->
<!-- Never write passwords, tokens or customer data here: write WHERE to find them. -->

## Environments

| Name | Address | Data | Who deploys, when |
| --- | --- | --- | --- |
| Dev | `<https://dev.shop.example.com>` | Fake, reset every night | Every merge to main |
| Test / QA | `<https://qa.shop.example.com>` | Fake, kept | <Daily, by the pipeline> |
| Staging | `<https://staging.shop.example.com>` | Copy of production, cleaned | Before each release |
| Production | `<https://shop.example.com>` | **Real customers. Read only for testers** | <Release manager> |

## Logging in

| Account | Role | Where the password is |
| --- | --- | --- |
| `<arshad.test@example.com>` | Customer | `<Password manager: "QA accounts">` |
| `<admin.test@example.com>` | Admin | `<Password manager: "QA accounts">` |

## Run the tests

| You want | Run |
| --- | --- |
| Set up once | `<python -m venv .venv && .venv/bin/pip install -r requirements.txt>` |
| Smoke tests | `<python -m pytest -m smoke>` |
| One area | `<python -m pytest -m checkout>` |
| Against staging | `<BASE_URL=https://staging.shop.example.com python -m pytest>` |
| The nightly results | `<link to the pipeline>` |

## When something fails

| Where | What it has |
| --- | --- |
| `<link to logs, for example Kibana or Grafana>` | Server logs. Search for the request id |
| `<link to the error tracker>` | Errors with stack traces |
| `<link to the board or Jira filter>` | Open bugs, known issues |
| `<team chat channel>` | Ask here first. Developers on call: `<name or rota link>` |

## Database (read-only)

| | |
| --- | --- |
| Settings | Environment variables `<DB_HOST>`, `<DB_NAME>`, `<DB_USER>`, `<DB_PASSWORD>` |
| Read-only user | `<qa_readonly>`. Ask `<who>` for access |
| Main tables | `<customers>`, `<orders>`, `<order_lines>` |

## Words this team uses

| Word | Means here |
| --- | --- |
| `<RC>` | `<Release candidate: the build we test before release>` |
| `<Hotfix>` | `<A fix released outside the normal release, from a release branch>` |
