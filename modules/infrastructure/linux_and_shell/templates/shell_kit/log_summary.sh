#!/usr/bin/env bash
# Template from myOpenSDET: https://myopensdet.github.io/
# Summarise a log file: lines per level, the most common errors, the slowest requests.
#
#   ./log_summary.sh logs/app.log
#   ./log_summary.sh logs/app.log 10      # show 10 instead of 5
#
# CHANGE: the patterns below match lines like
#   2026-11-18T02:00:00Z ERROR req-01000 GET /api/orders status=500 took_ms=37 error=...
set -euo pipefail

file="${1:?Usage: ./log_summary.sh <log file> [how many]}"
top="${2:-5}"
[ -r "$file" ] || { echo "Can't read $file" >&2; exit 1; }

echo "== $file: $(wc -l < "$file" | tr -d ' ') lines"
echo
echo "== Lines per level"
awk '{print $2}' "$file" | sort | uniq -c | sort -rn
echo
echo "== Most common errors"
grep -o 'error=[^ ]*' "$file" | sort | uniq -c | sort -rn | head -n "$top" || echo "   none"
echo
echo "== Slowest requests (ms, request id, path)"
sed -n 's/.* \(req-[0-9]*\) [A-Z]* \([^ ]*\) .*took_ms=\([0-9]*\).*/\3 \1 \2/p' "$file" |
  sort -rn | head -n "$top"
