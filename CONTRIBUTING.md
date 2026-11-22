# Contributing to myOpenSDET

Thank you for helping. Every fix, however small, makes the site better for the
next learner.

By taking part you agree to the [Code of Conduct](.github/CODE_OF_CONDUCT.md).

## Ways to help

| You want to | Do this |
| --- | --- |
| Fix a typo or a small mistake | Click **Edit this page** (the pencil at the top of any page), change it on GitHub, open a pull request |
| Report something wrong or unclear | Click 👎 under "Was this page helpful?" on the page, or open a **Content error** issue |
| Report a template that does not run | Open a **Template or code problem** issue |
| Report a security problem | Never in a public issue. See [SECURITY.md](.github/SECURITY.md) |
| Add or rewrite a lesson | Read this whole page and the [Style guide](.github/STYLE_GUIDE.md) first |

## Set up your computer

You need [uv](https://docs.astral.sh/uv/) (it installs the right Python for you) and git.

```bash
git clone https://github.com/myopensdet/myopensdet.github.io.git myopensdet
cd myopensdet

uv python install 3.13
uv venv --python 3.13
uv pip sync --require-hashes requirements-docs.txt requirements.txt practice-app/requirements.txt

uv tool install pre-commit
pre-commit install            # runs gitleaks and the other checks before every commit

.venv/bin/zensical serve      # then open http://127.0.0.1:8001/
```

`--require-hashes` makes sure every package is exactly the one that was reviewed.

## Add a new topic

A topic is a folder in a category, for example `docs/api-testing/mocking-and-stubbing/`.
The menu and the section overview cards are **built from the topic's own front
matter**, so there is no list to edit by hand.

**The quick way (recommended):** one command makes the page, the code folders
and the menu entry. It checks the section, group and name for you.

```bash
.venv/bin/python scripts/new_topic.py --section api-testing --slug graphql \
  --title "GraphQL testing" --level Intermediate \
  --after mocking-and-stubbing --tags API Python \
  --summary "Test GraphQL queries, mutations, variables and errors."
```

When you start writing the real pages, copy them from
[`_new_topic_template/`](_new_topic_template/README.md).

**By hand**, if you prefer:

1. Pick the section and a short folder name: lowercase, words joined with `-`,
   **no numbers** (the order lives in the front matter).
2. Create `docs/<section>/<topic>/index.md` with this front matter:

    ```yaml
    ---
    title: "API testing"
    description: "One or two sentences for search engines and link previews."
    level: Intermediate                 # Beginner, Intermediate, Advanced or Senior
    status: draft                       # remove when finished; drafts are listed on the Roadmap, not in the menu
    tags:                               # 1 to 3, only from data/tags.yml
      - API
      - Python
    nav_title: "API testing"            # short label in the menu
    order: 25                           # between the topics at 20 and 30
    summary: "One plain sentence for the card on the section overview."
    code: api_testing/graphql            # the folder in modules/ that holds its code
    ---
    ```

3. Make a folder in `modules/` for the code (underscores instead of `-`,
   for example `modules/api_testing/graphql/`), and name it in `code:`. See [modules/README.md](modules/README.md).
4. Build the menu and the overview cards:

    ```bash
    .venv/bin/python scripts/build_nav.py
    ```

5. Check the site builds with no warnings:

    ```bash
    .venv/bin/zensical build --strict
    ```

If you forget step 4, the commit stops with "menu and overview pages are up to
date ... Failed" and tells you the command to run.

**New words** go in `data/glossary.yml` and **new tags** in `data/tags.yml`, then
run `.venv/bin/python scripts/build_reference.py`. See the
[Style guide](.github/STYLE_GUIDE.md#tags) for the rules.

**Lessons** inside a topic are more `.md` files in the topic folder, each with
`nav_title` and `order`. They appear under the topic in the menu automatically.

**Published addresses never change.** If a page must move, `git mv` it and add a line
`old/address/: new/address/` to `data/redirects.yml`. After the build,
`scripts/build_redirects.py` puts a forwarding page at the old address.

## Check everything before you push

One command runs every check (secrets, Python lint and format, menu, site build,
links, tests, readability) and prints a summary:

```bash
scripts/check.sh              # about 10 seconds
scripts/check.sh --external   # also visits every external link
```

## Before you open a pull request

A lesson is done when:

- [ ] It follows the lesson template ([Style guide 7.2](.github/STYLE_GUIDE.md#72-lesson-page-template-top-to-bottom)), including the "Before you start" box, so it makes sense on its own
- [ ] It follows the writing style ([Style guide 8](.github/STYLE_GUIDE.md#8-writing-style)) and was read aloud once
- [ ] It has at least one diagram, and a screenshot or output block for every step (or a placeholder listed in `docs/assets/images/IMAGES_NEEDED.md`)
- [ ] Every code sample runs, comes from `modules/`, and has a passing test
- [ ] It has real usage at work, a task with a solution, "When it goes wrong" with real error messages, and a References list (no quiz)
- [ ] Every new term is in the Glossary and linked
- [ ] It looks right on phone and desktop, in light and dark mode
- [ ] All links work
- [ ] It is in the menu (`scripts/build_nav.py`), with tags and a level
- [ ] It passes the [security rules](.github/SECURITY.md)
- [ ] It passes the 10-year-old test ([Style guide 8A](.github/STYLE_GUIDE.md#8a-the-10-year-old-test))
- [ ] It is linked from the [Skills Matrix](docs/getting-started/skills-matrix.md)

A topic is done when all its lessons are done, its templates pass locally, its
`index.md` is a complete "First time? Start here" playbook.

## Rules for pull requests

Anyone can suggest a change. Nothing reaches the site until the maintainer has
reviewed and approved it. These rules keep the site correct, safe and free.

### How a change gets in

1. **Small fix?** (typo, broken link, wrong command): open a pull request straight away.
2. **Bigger change?** (new topic, a rewrite, a new tool or package): open an issue
   first and wait for a "yes". It saves you from work that won't fit.
3. Fork the repository and make a branch from `main`, named for what it does:
   `fix/api-testing-port`, `topic/contract-testing`, `docs/clearer-step-3`.
4. Make **one fix or one topic** per pull request. Small pull requests get reviewed fast.
5. Run `scripts/check.sh`. Every check must pass.
6. Open the pull request and fill in every part of the form.
7. The maintainer reviews it. Only the maintainer merges. They may approve it,
   ask for changes, make small edits themselves, or close it with a reason.
8. If changes are asked for and nothing happens for 30 days, the pull request may be
   closed. You can always open it again.

### What every pull request must follow

| Rule | Why |
| --- | --- |
| Every output on a page comes from a **real run**. Run each command yourself. | Learners copy what they see. An invented output wastes their day. |
| Every error in a "When it goes wrong" table was **reproduced**. | Same reason. |
| Write in **your own words**. Link the source; never copy text from books, courses or other sites. | Copyright, and plain words are the point of this site. |
| **No secrets, no real personal data, no employer or client material**: no tokens, real emails, internal addresses, personal paths or screenshots of work tools. | This repository is public. Anything pushed can be copied forever. |
| Only fake data: `@example.com` emails, `local_only_password`. | Same reason. |
| **No ads, affiliate links, tracking or self-promotion.** | The site is free and private for learners. |
| New packages only after an issue says yes. Pinned, with hashes, and released at least two weeks ago. | Protects everyone who installs the templates. |
| Python 3.13 and Playwright for browser tests. | One clear path is easier to learn. |
| Follow the [Style guide](.github/STYLE_GUIDE.md): plain words, short sentences, readability grade 8 or lower. | Many readers use English as a second language. |
| No unrelated changes (reformatting other files, renaming things you didn't need to). | Keeps the review about one thing. |
| If you used an AI tool, you are still responsible for every line. Check and run all of it. | AI tools invent outputs and links. |

### Commit messages

Say what the commit does, in plain words: `Fix the port number in API testing step 3`.
One idea per commit is best.

### Review is about the work, not the person

Every reviewer and contributor follows the [Code of Conduct](.github/CODE_OF_CONDUCT.md).
Questions are welcome. Nobody is expected to know everything.

## Publishing the website

This part is for the maintainer. The website is published with GitHub Pages at
<https://myopensdet.github.io/>. The workflow
`.github/workflows/pages.yml` builds and publishes the site on every push to
`main`. After a push, open the **Actions** tab and check that "Publish website"
turns green.

### What is already checked

- `bash scripts/check.sh` builds the site with `--strict`, so any warning fails.
- `scripts/check_built_site.py` serves the built `site/` folder at `/`, the same path GitHub Pages uses, and opens every page and file. It fails on a broken link, a link that leaves the site's path, or a page that loads a script, style or image from another server.
- Diagrams use our own pinned copy of Mermaid, never `unpkg.com`. On its own, the theme would load Mermaid from `unpkg.com` (at whatever 12.x is newest) and every reader's browser would contact that server. `docs/assets/javascripts/mermaid-loader.js` stops that, and the browser checks the file's SHA-384 hash before running it. The big file loads only on pages that draw a diagram. The built-site check fails if any page lacks the loader or the hash doesn't match. Tested in Chrome with `unpkg.com` blocked: diagrams draw, pages without diagrams don't fetch the file, and a changed file is refused.
- Every page gets a Content-Security-Policy meta tag (`scripts/build_csp.py`, run after the build). The browser then runs only this site's own scripts, plus the theme's small in-page scripts, each allowed by its exact SHA-256 hash. Images, fonts and styles load only from this site; the only outside address the page may call is `api.github.com` (stars and forks in the header). Limits of a meta tag: it can't set `frame-ancestors` or send reports, because GitHub Pages can't add HTTP headers. `zensical serve` (the local preview) has no policy; build and serve `site/` to test with it. Tested in Chrome: search, diagrams, copy buttons, share, "Mark as done", the Skills Matrix, feedback buttons and instant page changes all work with no policy errors.
- No analytics or tracking. The "Was this page helpful?" buttons only show a note on the page (`docs/assets/javascripts/feedback.js`).
- Site address, repo link and "edit this page" link are set in `zensical.toml`.
- A 404 page is built. No file in the site starts with `_`, so nothing is hidden by GitHub.
- Share images use fonts kept in `docs/assets/fonts/`, so they build the same on GitHub's Linux machines.

### Updating Mermaid

Pinned: Mermaid 12.2.0 from npm, MIT licence (`docs/assets/javascripts/vendor/mermaid-LICENSE.txt`). Stay on the major version the theme asks for (search the theme's `bundle.*.min.js` for `mermaid@`).

1. Pick a release at least two weeks old, with no open security advisory: <https://github.com/mermaid-js/mermaid/security/advisories>.
2. Download it from npm and check the tarball against npm's published `integrity` (sha512) before using it.
3. Copy `package/dist/mermaid.min.js` to `docs/assets/javascripts/vendor/mermaid-<version>.min.js`, and delete the old file (ask first).
4. In `mermaid-loader.js`, set `VERSION`, and set `INTEGRITY` to `sha384-` plus the output of `openssl dgst -sha384 -binary <file> | base64`.
5. Run `bash scripts/check.sh`, then open a page with a diagram in the preview.

### Keeping the workflow safe

- Actions are pinned to full commit SHAs. To update one, look up the new release's commit SHA on its GitHub page and change the SHA and the comment together. Never switch back to a plain tag like `@v5`.
- The workflow uses no secrets. If a later change seems to need one, stop and ask first.

## Licenses

By contributing you agree that your code is shared under the [MIT License](LICENSE)
and your text and images under [CC BY 4.0](LICENSE-CC-BY-4.0.txt), the same as the
rest of the project.
