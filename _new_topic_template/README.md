# New topic template

Everything a new topic needs, ready to copy. Nothing in this folder is published.

## Stage 1: add the topic (a "Coming soon" page)

One command creates the page, the code folders, and updates the menu:

```bash
.venv/bin/python scripts/new_topic.py \
  --section core-automation \
  --slug api-testing \
  --title "API testing" \
  --level Intermediate \
  --group "API and databases" \
  --after pytest-framework \
  --summary "Send requests from Python and check status codes, JSON, headers and auth."
```

It creates:

```text
docs/core-automation/api-testing/index.md        "Coming soon" page (status: draft)
modules/core_automation/api_testing/
    templates/  examples/  exercises/  solutions/  tests/
```

Then fill in "What you will learn" and "Templates you will get" on the new page.
Run `.venv/bin/python scripts/new_topic.py --help` for every option.

## Stage 2: write the topic

When you start writing, replace the "Coming soon" page with the real pages:

| Copy this | To | What it is |
| --- | --- | --- |
| `docs/index.md` | `docs/<section>/<topic>/index.md` | The "First time? Start here" playbook (Style guide 7.1). Keep the front matter you already have. |
| `docs/lesson.md` | `docs/<section>/<topic>/<lesson>.md` | One lesson page (Style guide 7.2). One concept per page. |
| `modules/templates/example_template.py` | `modules/<section>/<topic>/templates/` | Shows the credit line every template starts with. |
| `modules/tests/test_example_template.py` | `modules/<section>/<topic>/tests/` | Every template has a test. |

Lines in `<!-- ... -->` are notes for the writer. Delete them when the page is done.
Remove `status: draft` from the front matter when the topic is finished, then run
`.venv/bin/python scripts/build_nav.py`.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full checklist.

## The credit line

Every file in a `templates/` folder starts with one comment line that says where
it came from, so teammates who find a copied template can find the lesson too:

```python
# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
```

Other file types use their own comment style (`//` in JavaScript, `--` in SQL,
`<!-- -->` in XML). The commit stops if a template is missing it; add it with:

```bash
.venv/bin/python scripts/check_credit_lines.py --fix
```
