# Security policy

myOpenSDET is a public repository and a public website. This page explains
how to report a security problem, and the rules every file and commit follows.

## Report a security problem

Please **do not open a public issue** for a security problem.

Report it privately instead: on GitHub, open the **Security** tab of this
repository and choose **Report a vulnerability**. Only the maintainer can see
the report. You will get an answer as soon as possible, and credit in the fix
if you want it.

Examples of real problems:

- A password, token or key that was committed to the repository
- Personal data (a real email, path, IP address or name) in a page, screenshot or commit
- A problem in the website itself, or in a script in `scripts/`

### Not a security problem: planted bugs in practice code

Some practice code has bugs **on purpose**, so learners can find them: the
sample shop in `practice-app/`, and the small demo servers in `modules/` (for
example a `--bug` mode). These are not vulnerabilities to report. For the same
reason:

- Run practice code only on your own computer. Every server binds to
  `127.0.0.1` (localhost) only.
- Never deploy it to a public server.

## Supported versions

Only the latest version of the `main` branch and the live website are supported.

## Rules for every file, screenshot and commit

### Never publish

| What | Examples | Do this instead |
| --- | --- | --- |
| Passwords, API keys, tokens | Database passwords, GitHub tokens, cloud keys | `.env` (git-ignored) + `.env.example` with fake values |
| Personal details | Emails, phone numbers, addresses | GitHub's no-reply commit email; contact only through the About page links |
| Computer details | Username and machine name in the terminal prompt, `/Users/<name>/...` paths, local IPs, Wi-Fi names | A neutral prompt (for example `$`) and generic paths like `~/projects/myopensdet` |
| Employer or client material | Company code, URLs, data, screenshots, ticket text | The site's own demo servers, `example.com` and public practice APIs |
| Real people's data | Names, emails, any production data | Fake data from Faker |
| Hidden image data | GPS and device info in photos | Strip metadata before adding images |

### Screenshots

- Clean setup: neutral terminal prompt, no personal bookmarks, no notifications, no other tabs or apps.
- Blur or crop any username, email, path, token, IP address or account name.
- Show only `localhost`, `example.com` and public practice sites.
- Remove image metadata before committing.

### Code and repository

- `.gitignore` covers `.env`, `.venv/`, `__pycache__/`, `.DS_Store`, IDE folders, logs, reports, database files and build output.
- Docker Compose uses clearly fake local passwords loaded from `.env`; services bind to `localhost` only.
- **gitleaks runs before every commit** through pre-commit (`pre-commit install` once after cloning).
- A secret that was ever committed stays in git history even after it is deleted. If one is found, it is removed with a history rewrite and the secret is changed.
- Libraries come only from official sources, with pinned versions and hashes (`requirements-docs.txt`).
- Integrations (for example comments) get the smallest permissions they need.

### Checklist before every commit or push

- [ ] gitleaks passes; no secrets in the diff
- [ ] No personal paths, usernames or emails in text, code or screenshots
- [ ] New images cropped, blurred where needed, metadata removed
- [ ] `.env` not staged; `.env.example` holds only fake values
- [ ] No employer or client material
