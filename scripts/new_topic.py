"""Add a new topic: a "Coming soon" page, its code folders, and the menu entry.

Example (from the repository root):

    .venv/bin/python scripts/new_topic.py \\
        --section api-testing --slug graphql --title "API testing" \\
        --level Intermediate --group "API and databases" --after pytest-framework \\
        --tags API Python \\
        --summary "Send requests from Python and check status codes, JSON, headers and auth."

Creates
    docs/<section>/<slug>/index.md                    status: draft, "Coming soon"
    modules/<section_>/<slug_>/{templates,examples,exercises,solutions,tests}/
then runs scripts/build_nav.py so the menu and the section overview are updated.

It never overwrites anything: if the topic already exists, it stops.
See _new_topic_template/README.md for stage 2 (writing the real pages).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import build_nav  # same folder; shares the rules for sections, groups and order
import build_reference  # same folder; the list of allowed tags

DOCS = build_nav.DOCS
MODULES = Path("modules")
LEVELS = ["Beginner", "Intermediate", "Advanced"]
SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
CODE_FOLDERS = ["templates", "examples", "exercises", "solutions", "tests"]

PAGE = """---
title: {title}
description: {description}
level: {level}
status: draft
tags:
{tag_lines}nav_title: {title}
order: {order}
{group_line}summary: {summary}
code: {code}
---

# {plain_title}

!!! info "Coming soon"
    This topic is being written. Here is what it will teach you.

## What you will learn

- <!-- TODO: what a reader can do after this topic -->

## Templates you will get

- <!-- TODO: the ready-to-copy files this topic will include -->
"""


def fail(message: str) -> None:
    print(f"new_topic: {message}", file=sys.stderr)
    sys.exit(1)


def pick_order(topics: list[build_nav.Page], after: str | None) -> int:
    """Put the topic last, or just after another topic, leaving room for more."""
    orders = sorted(int(t.meta.get("order", 0)) for t in topics)
    if after is None:
        return (orders[-1] if orders else 0) + 10
    by_slug = {t.path.parent.name if t.path.name == "index.md" else t.path.stem: t for t in topics}
    if after not in by_slug:
        fail(
            f"--after {after}: no such topic in this section. Topics: {', '.join(sorted(by_slug))}"
        )
    start = int(by_slug[after].meta["order"])
    bigger = [o for o in orders if o > start]
    if not bigger:
        return start + 10
    gap = bigger[0] - start
    if gap < 2:
        fail(
            f"no room between order {start} and {bigger[0]}. Renumber the section's "
            "`order:` values with bigger gaps (10, 20, 30 ...) and try again."
        )
    return start + gap // 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a new topic to myOpenSDET.")
    parser.add_argument("--section", required=True, help="section folder, e.g. core-automation")
    parser.add_argument("--slug", required=True, help="topic folder name, e.g. api-testing")
    parser.add_argument("--title", required=True, help='menu and page title, e.g. "API testing"')
    parser.add_argument("--level", required=True, choices=LEVELS)
    parser.add_argument("--summary", required=True, help="one plain sentence for the overview card")
    parser.add_argument("--description", help="for search engines (default: built from the title)")
    parser.add_argument("--group", help="menu group (required in sections that use groups)")
    parser.add_argument(
        "--new-group", action="store_true", help="allow a group name that does not exist yet"
    )
    parser.add_argument("--after", help="put the topic right after this topic (its folder name)")
    parser.add_argument(
        "--tags",
        nargs="+",
        required=True,
        metavar="TAG",
        help=f"1 to {build_reference.MAX_TAGS} tags from data/tags.yml, e.g. --tags API Python",
    )
    args = parser.parse_args()

    allowed = [t["name"] for t in build_reference.load_list(build_reference.TAGS_DATA, ("name",))]
    unknown = [t for t in args.tags if t not in allowed]
    if unknown:
        fail(f"--tags {unknown}: not in data/tags.yml. Tags: {', '.join(allowed)}")
    if len(args.tags) > build_reference.MAX_TAGS:
        fail(f"--tags: use at most {build_reference.MAX_TAGS} tags.")

    if not SLUG.match(args.slug):
        fail(
            f"--slug {args.slug!r}: use lowercase words joined by '-', starting with a letter "
            "(no numbers in front: the order lives in the front matter)."
        )

    sections = {s.path.parent.name: (s, topics) for s, topics in build_nav.load_sections()}
    if args.section not in sections:
        fail(f"--section {args.section}: no such section. Sections: {', '.join(sections)}")
    section, topics = sections[args.section]

    groups = [g for g, _ in build_nav.grouped(section, topics) if g is not None]
    if groups and not args.group:
        fail(f"this section uses groups, add --group. Groups: {', '.join(groups)}")
    if args.group and not groups:
        fail(
            "this section has no groups yet; leave out --group "
            "(or add groups to every topic first)."
        )
    if args.group and args.group not in groups and not args.new_group:
        fail(
            f"--group {args.group!r} does not exist. Groups: {', '.join(groups)}. "
            "Add --new-group to start a new one."
        )

    page_dir = DOCS / args.section / args.slug
    code_dir = MODULES / args.section.replace("-", "_") / args.slug.replace("-", "_")
    for path in (page_dir, code_dir):
        if path.exists():
            fail(f"{path} already exists. Nothing was changed.")

    order = pick_order(topics, args.after)

    def q(text: str) -> str:
        return json.dumps(text, ensure_ascii=False)  # a quoted string that is valid YAML

    description = args.description or (
        f"{args.title}: a free, step-by-step guide for SDETs, "
        "with ready-to-use templates. Coming soon."
    )
    page = PAGE.format(
        title=q(args.title),
        plain_title=args.title,
        description=q(description),
        level=args.level,
        tag_lines="".join(f"  - {q(tag)}\n" for tag in args.tags),
        order=order,
        group_line=f"group: {q(args.group)}\n" if args.group else "",
        summary=q(args.summary),
        code=code_dir.relative_to(MODULES).as_posix(),
    )

    page_dir.mkdir(parents=True)
    (page_dir / "index.md").write_text(page, encoding="utf-8")
    for folder in CODE_FOLDERS:
        (code_dir / folder).mkdir(parents=True)
        (code_dir / folder / ".gitkeep").write_text("", encoding="utf-8")

    print(f"created {page_dir / 'index.md'} (order {order})")
    print(f"created {code_dir}/ with {', '.join(CODE_FOLDERS)}")
    sys.argv = [sys.argv[0]]
    if build_nav.main() != 0 or build_reference.main() != 0:
        fail("the page was created, but the menu could not be built (see the message above).")
    print(
        "Next: fill in 'What you will learn' and 'Templates you will get', "
        "then run .venv/bin/zensical build --strict"
    )


if __name__ == "__main__":
    main()
