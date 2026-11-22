#!/usr/bin/env bash
# Run every check before a push. Same checks CI will run from Phase 9.
#
# Usage (from anywhere in the repository):
#   scripts/check.sh              # all checks, internal links only (about 10 seconds)
#   scripts/check.sh --external   # also visit every external link (needs internet)
#
# Every check runs even if an earlier one fails, then a summary is printed.
# "warn" checks give advice and never fail the run.

set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
EXTERNAL=""
[ "${1:-}" = "--external" ] && EXTERNAL="--external"

if [ ! -x "$PY" ]; then
  echo "No .venv found. Set up first (see CONTRIBUTING.md):"
  echo "  uv venv --python 3.13 && uv pip sync --require-hashes requirements-docs.txt requirements.txt practice-app/requirements.txt"
  exit 1
fi

failed=()
warned=()

# run NAME KIND COMMAND...   (KIND is "must" or "warn")
run() {
  local name="$1" kind="$2"
  shift 2
  printf '\n== %s\n' "$name"
  if "$@"; then
    printf -- '-- ok: %s\n' "$name"
  elif [ "$kind" = "warn" ]; then
    printf -- '-- warning: %s\n' "$name"
    warned+=("$name")
  else
    printf -- '-- FAILED: %s\n' "$name"
    failed+=("$name")
  fi
}

secrets() {
  if ! command -v gitleaks >/dev/null 2>&1; then
    echo "gitleaks is not installed: https://github.com/gitleaks/gitleaks#installing"
    return 1
  fi
  gitleaks git --no-banner --redact --log-level warn &&
    gitleaks git --staged --no-banner --redact --log-level warn &&
    gitleaks git --pre-commit --no-banner --redact --log-level warn
}

run "Secrets (gitleaks: history, staged and unstaged changes)" must secrets
run "Python lint (ruff check)" must .venv/bin/ruff check .
run "Python format (ruff format --check)" must .venv/bin/ruff format --check .
run "Menu and overview pages up to date" must "$PY" scripts/build_nav.py --check
run "Glossary, tags and hover explanations up to date" must "$PY" scripts/build_reference.py --check
run "Template index up to date" must "$PY" scripts/build_template_index.py --check
run "Hidden page dates up to date" warn "$PY" scripts/update_page_dates.py --check
run "Website builds with no warnings" must .venv/bin/zensical build --strict
run "Share images for every page" must "$PY" scripts/build_share_images.py
run "Built site works at / like on GitHub Pages" must "$PY" scripts/check_built_site.py
run "Links" must "$PY" scripts/check_links.py $EXTERNAL
run "Tests (pytest)" must .venv/bin/pytest -q
run "Credit line in every template" must "$PY" scripts/check_credit_lines.py
run "Readability (grade 8 or lower)" warn "$PY" scripts/check_readability.py --strict

printf '\n================ Summary ================\n'
if [ ${#warned[@]} -gt 0 ]; then
  printf 'Warnings: %s\n' "${warned[@]}"
fi
if [ ${#failed[@]} -gt 0 ]; then
  printf 'FAILED:   %s\n' "${failed[@]}"
  echo "Fix the failures above before you push."
  exit 1
fi
echo "All checks passed."
