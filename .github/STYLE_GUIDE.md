# Style guide

How every page and every template on myOpenSDET is written. These rules come
from the project brief (sections 7 and 8); keep both in step when one changes.

Contents: [Content standards](#7-content-standards) ·
[Writing style](#8-writing-style) ·
[Site conventions](#site-conventions)

## 7. Content standards

### 7.1 Topic playbook: "First time? Start here"

Every topic's `index.md` is a playbook for someone doing this for the first time at work. It walks through one realistic request (for example, "Your manager says: we're adding BDD, can you set it up?") from start to finish, in these steps:

1. **Understand the ask.** Questions to ask your lead on day one: what system, why now, what "done" means, deadline, environments, access.
2. **Picture the system.** A simple diagram of what you are testing and where the data flows.
3. **Learn just enough.** A 30–60 minute reading path through the official docs, in order, with what to skip for now.
4. **Get something running.** Copy the topic's template and run a first test within an hour.
5. **Decide what to test.** Test ideas specific to this area, sorted by risk, using the test design techniques.
6. **Write a one-page plan** with the test plan template, and share it before building.
7. **Build in small steps.** Smoke test, then happy path, then negative cases, then edge cases.
8. **Report and get feedback.** What to show your team, and how.
9. **Keep learning on your own.** What to read next, practice ideas, and official docs to bookmark.

Each playbook also has a **"How an experienced SDET thinks about this"** box, a **"Red flags"** box (signs the plan is going wrong), a **"Jump to what you need"** link list, and an **"Official resources"** list at the end.

### 7.2 Lesson page template (top to bottom)

Updated 2026-11-22. The Python lessons follow it; older lessons move to it as they are rewritten. The starting file is `_new_topic_template/docs/lesson.md`.

1. Title, and two to four plain sentences: what the idea is and why a tester meets it.
2. **"Before you start"** box: prerequisites as links, the tool version, and the example file.
3. **"Why testers need this":** a real work situation with realistic (fake) test data, and what goes wrong without the idea.
4. **"How it works":** a short explanation and at least one diagram, with a one-line caption. Diagrams must read on a phone: three columns at most, or top to bottom.
5. **"The code":** pulled from `modules/`, with the command to run it and the real output. The topic test checks the output on the page.
6. **"Line by line":** the lines a beginner would stop at, grouped by part.
7. **"How it is used in a real QA project":** where it shows up at work, with links onwards.
8. **"Your task":** an exercise with a test, and the solution in a collapsed block.
9. **"When it goes wrong":** real error messages, reproduced on the stated version, each with its meaning and fix.
10. **References:** every source used, plus the tool version and the date the links were checked.
11. Footer: previous / next, "Edit this page on GitHub", feedback widget, author line.

No quizzes or "Quick check" sections, and no "What you will learn" list: they repeat the page. Define a term once, link it to the Glossary, and don't repeat the definition.

### 7.3 Teaching method

- Start with a picture or everyday comparison, then the real thing. Example: "An API is like a waiter who takes your order to the kitchen and brings back your food."
- Show, then do: a diagram of the idea, then a guided walkthrough, then the reader does it alone.
- One new idea at a time. If a page needs three new ideas, it becomes three pages.
- After every few steps, a **"Check: you should now see…"** line with a screenshot.
- When something can go wrong, show the real error and the fix.

### 7.4 Install and setup steps (every tool)

- Tabs for **macOS, Windows and Linux**.
- The exact version used, with a link to the **official** download page only.
- The command to type, then a **verify command** with its expected output (for example `python3 --version` → `Python 3.12.x`).
- A screenshot of every installer screen and settings window, with the right button highlighted.
- A **Troubleshooting** box for the most common problems.
- A folder tree showing where each file goes, before the reader creates it.
- How to uninstall or clean up.

### 7.5 Visuals checklist (every page)

- At least one **Mermaid diagram** for any flow, architecture or sequence.
- A **screenshot** for every step in a UI (VS Code, browser DevTools, database tools, GitHub), with arrows or highlights.
- A **terminal output** block for every command.
- **Alt text** on every image.
- Images at `docs/assets/images/<topic>/<page>-<n>.png`, compressed under 300 KB.
- Where a screenshot is still needed, add a placeholder image link and list it in `docs/assets/images/IMAGES_NEEDED.md` with a description of exactly what to capture. I will take the screenshots myself.
- One illustrated **cheat sheet image** per topic that people can save and share.

### 7.6 References and sources

- Official sources first: the tool's own documentation (for example docs.pytest.org, the Requests docs, the MySQL and PostgreSQL manuals, the Cucumber Gherkin reference), standards bodies (W3C for accessibility, OWASP for security, the ISTQB glossary for testing terms), and original authors' articles.
- Link inline, right where a fact or rule is used.
- End every page with a **References** list.
- Run a link check locally before each push (in `scripts/check.sh`). From Phase 9, also weekly in CI.
- Never link to pirated books, copied content or low-quality sites.

### 7.7 Code rules

- Every example runs and has a test.
- No passwords or keys in code: use `.env` plus `.env.example`.
- Pin library versions.
- Format and lint with `ruff`. Use type hints and short comments that explain **why**, not what.
- Use Python 3.12+ and pytest as the base for all templates. Exceptions, where the tool has its own runner: behave (BDD), Robot Framework, Locust, k6 and JMeter. Their templates still have a check that `scripts/check.sh` runs.
- Every template file starts with one credit comment line: `# Template from myOpenSDET: <site URL>`.
  Other file types use their own comment style (`//` in JavaScript, `--` in SQL, `<!-- -->` in XML).
  `scripts/check_credit_lines.py` checks every file in a `templates/` folder, and `--fix` adds the line.

### 7.8 Example names and data

- The main example person in the site is **Arshad** (first name only). Use him wherever an example needs a person:
  - Main test user: name `Arshad Test`, email `arshad@example.com`, password `local_only_password` (clearly fake).
  - Code: `create_user(name="Arshad")`, `assert response.json()["name"] == "Arshad"`.
  - Gherkin: `Given Arshad is logged in`, `When Arshad adds 2 books to the cart`.
  - SQL: `INSERT INTO customers (name) VALUES ('Arshad');`
  - No story character. Arshad is a test-data name only (users, rows, Gherkin steps), never a person whose day the reader follows (owner decision, 2026-11-16: a cartoon-like hero looks childish on a public repo).
  - Work situations are written straight to the reader, the way a senior engineer explains a real job: "Your team launches member accounts on Friday. Your lead asks: …", "Ask the product owner…", "A common mistake here is…". Plain, practical, no characters.
- **Never** use a full name, a real email, phone number, birth date, address or any password pattern I really use. Emails always end in `@example.com`.
- Arshad is not the only person: second users, admins and customer lists use other names (Faker or common names from many countries), for example "Arshad must not be able to see Maria's order".

## 8. Writing style

Write like an experienced human teacher sitting next to one learner.

- Use "you" and "we", in plain English that a 10-year-old could follow.
- Explain **why** before **how**.
- Define every new word the first time it appears on a page, and add it to the Glossary.
- Use real work situations. Example: "Your team moved customer data from MySQL to PostgreSQL. How do you prove nothing was lost?"
- **Never invent personal stories, fake experience, fake statistics or fake quotes.**
- Mix short and long sentences. Be warm, direct, and honest about what is hard.
- Keep paragraphs short. Use lists only for real lists or steps.
- Every command shows what you type **and** what you should see.
- **Banned phrases:** "In today's fast-paced world", "Let's dive in", "dive deep", "It's not X, it's Y", "Moreover", "Furthermore", "In conclusion", "Unlock", "Seamless", "Robust", "Leverage", "Game-changer", "Delve". No emoji spam.
- Read each page aloud once. If it sounds like a robot or a sales page, rewrite it.

### 8B. Sound like a real teacher (owner decision, 2026-11-16)

Every page should read as if a real person wrote it from their own work and research. It should not sound like a machine wrote it.

- Talk the way a good teacher talks: "Here is the trick", "This part trips most people up", "Don't worry if this feels slow at first".
- Explain how to **think**, not only what to type: what you notice first, what you ask, what you try when the first idea fails.
- Every topic answers "What do I do when this goes wrong at work?" with concrete steps, not general advice.
- Prefer one worked example from a real work situation over a list of abstract points. Tell it straight to the reader ("Your team…", "You ask…"), the way a senior engineer explains a job to a new colleague. No made-up story characters (owner decision, 2026-11-16).
- Use plain, everyday English. No stiff or showy words such as "utilize", "facilitate", "comprehensive", "crucial", "landscape", "ensure that", "it is important to note". Say "use", "help", "full", "important", "make sure".
- Don't open every section the same way, or end every paragraph with a neat summary line. Real writing varies.
- Point to real resources (official docs, well-known articles, tools) where they help, and say what each one is good for.
- Still never invent personal stories, fake experience, fake statistics or fake quotes (section 8).

### 8A. The 10-year-old test

Every explanation must make sense to a curious 10-year-old reading it with no help. Technical words are allowed, but only after they are explained.

- Each concept page opens with an **"In plain words"** box: two or three sentences and an everyday comparison, before any technical detail. Example: "A database is like a giant, super-organized notebook. Each table is one page, and each row is one line on that page."
- Every concept gets a **picture**: a diagram, an illustration or an annotated screenshot.
- Sentences stay short (aim for under 20 words). One idea per paragraph.
- No unexplained abbreviations. Write "API (Application Programming Interface): a way for two programs to talk" the first time on every page.
- Explanations aim for a reading level around school grade 6–8. `scripts/check.sh` runs a readability check (for example with the `textstat` library) on the prose of each page, skipping code blocks, and lists pages that score too hard.
- Before a page is done, read it as if you had never heard of the topic. Anything you would have to look up is explained on the page or linked.

## Site conventions

Rules that come from how the site is built.

### Front matter on every page

```yaml
---
title: "API testing"                   # page title (also the browser tab and search result)
description: "One or two sentences."   # search engines and link previews
level: Intermediate                    # Beginner, Intermediate, Advanced or Senior
status: draft                          # remove when the page is finished
tags:                                  # 1 to 3, only from data/tags.yml
  - API
  - Python
nav_title: "API testing"               # short label in the menu
order: 20                              # position in its section (10, 20, 30 ... leave gaps)
group: "API and databases"             # only in sections that use groups
summary: "One plain sentence for the card on the section overview."
---
```

The menu and the section overview cards are built from these fields by
`scripts/build_nav.py`. Never edit the `nav` block in `zensical.toml` by hand.

### Progress tracker

Every finished page with a `level` (not a draft) gets a "Mark this lesson as
done" button at the end, and links to finished lessons get a check mark across
the site. It is saved only in the reader's browser (`docs/assets/javascripts/progress.js`);
nothing is sent anywhere. To turn the button off on one page, add
`hide: [progress]` to its front matter (the Skills Matrix does this, because it
has its own tick boxes).

### Tags

Tags say what a page is **about** (API, Database, Debugging), not where it sits
in the menu. Every page in the menu has 1 to 3 tags, and only tags listed in
`data/tags.yml` are allowed, so the Tags page never ends up with "API", "api"
and "APIs" side by side. Need a new tag? Add it to `data/tags.yml` with one
plain sentence, in the same pull request.

### Glossary

Every testing word lives in `data/glossary.yml`: the term, a plain meaning, and
the page that teaches it. `scripts/build_reference.py` builds the A to Z
[Glossary](../docs/glossary.md) from it. For short forms (API, BDD, CI/CD) add
`stands_for:` and the meaning appears on hover everywhere the short form is
used on the site, with nothing to add to the page.

Link a word to the Glossary the first time it appears on a page:
`[fixture](../../glossary.md#fixture)`. The anchor is the term in lowercase with
spaces as `-`.

### Boxes (admonitions)

| Box | Use it for |
| --- | --- |
| `!!! info "In plain words"` | The everyday explanation at the top of a concept page |
| `!!! tip` | A shortcut or a good habit |
| `!!! warning` | Something that can go wrong or cost time |
| `!!! danger` | Something that can lose data or leak a secret |
| `??? success "Solution"` | Exercise answers, folded by default |

### Dates

Pages show no "last updated" date (an old date makes a correct page look
abandoned). Each lesson shows the tool versions it was tested with instead.
`scripts/update_page_dates.py` keeps a hidden date for search engines.
