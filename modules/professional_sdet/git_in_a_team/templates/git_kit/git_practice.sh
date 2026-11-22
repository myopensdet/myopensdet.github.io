#!/usr/bin/env bash
# Template from myOpenSDET: https://myopensdet.github.io/
# A safe place to practise team Git: a pretend server and two copies of a small test
# project, "me" and "colleague", all inside one new folder. Nothing else is touched.
#
#   bash git_practice.sh setup        make git-practice/ (server.git, me, colleague)
#   bash git_practice.sh colleague    the colleague changes conftest.py and pushes to main
#   bash git_practice.sh reset        delete git-practice/ and start again
set -euo pipefail

ROOT="git-practice"
# Fake names only, set inside the practice copies. Your own Git settings are not changed.
as_me()        { git -c user.name="Arshad Test" -c user.email="arshad@example.com" "$@"; }
as_colleague() { git -c user.name="Colleague Test" -c user.email="colleague@example.com" "$@"; }

setup() {
  if [ -e "$ROOT" ]; then
    echo "$ROOT already exists. Use it, or run: bash git_practice.sh reset" >&2
    exit 1
  fi
  mkdir -p "$ROOT"
  git init -q --bare -b main "$ROOT/server.git"
  git init -q -b main "$ROOT/start"
  (
    cd "$ROOT/start"
    mkdir tests
    printf 'import os\n\nBASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")\nTIMEOUT = 10\n' > conftest.py
    printf 'def test_login_page_opens():\n    assert True\n' > tests/test_login.py
    printf 'reports/\n.venv/\n.env\n' > .gitignore
    git add .
    as_me commit -q -m "Start the test project"
    git remote add origin ../server.git
    git push -q origin main
  )
  rm -rf "$ROOT/start"
  for who in me colleague; do
    git clone -q "$ROOT/server.git" "$ROOT/$who"
    git -C "$ROOT/$who" remote set-url origin ../server.git
  done
  git -C "$ROOT/me" config user.name "Arshad Test"
  git -C "$ROOT/me" config user.email "arshad@example.com"
  echo "Ready: $ROOT/me is your copy. Next: cd $ROOT/me"
}

colleague() {
  (
    cd "$ROOT/colleague"
    git pull -q origin main
    sed -i.bak 's/TIMEOUT = 10/TIMEOUT = 30  # the staging server is slow/' conftest.py
    rm -f conftest.py.bak
    as_colleague commit -q -am "Raise the timeout for staging"
    git push -q origin main
  )
  echo "Your colleague pushed a change to conftest.py on main."
}

case "${1:-}" in
  setup) setup ;;
  colleague) colleague ;;
  reset) rm -rf "$ROOT" && echo "Deleted $ROOT/" ;;
  *) echo "Usage: bash git_practice.sh setup | colleague | reset" >&2; exit 2 ;;
esac
