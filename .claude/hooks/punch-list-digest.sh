#!/usr/bin/env bash
# SessionStart hook: emit a compact digest of docs/PUNCH_LIST.md into session
# context, so a session knows the queue exists and what is at the top of it
# without reading the whole file. Deliberately a few lines: this text is
# resent on every turn of the session.
#
# Fails silently and emits nothing if the punch list is missing or unreadable,
# so a checkout without it still starts cleanly.
set -uo pipefail

root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
file="$root/docs/PUNCH_LIST.md"
[ -r "$file" ] || exit 0

awk '
  # Skip fenced blocks so the entry-format example in the header is not
  # mistaken for a real item.
  /^```/ { fence = !fence; next }
  fence { next }

  /^### PL-/ {
    id = $2
    title = $0
    sub(/^### PL-[0-9]+[ \t]+/, "", title)
    pending = 1
    next
  }

  pending && /^`P[0-9]`/ {
    meta = $0
    gsub(/`/, "", meta)
    n = split(meta, a, / · /)
    pri = a[1]
    eff = a[2]
    status = "?"
    for (i = 1; i <= n; i++) {
      if (a[i] == "ready" || a[i] == "needs-decision" || a[i] == "blocked") status = a[i]
    }
    count[pri]++
    line = id " " title " (" eff ", " status ")"
    if (pri == "P0") p0[++np0] = line
    else if (pri == "P1" && top1 == "") top1 = line
    pending = 0
    next
  }

  END {
    total = count["P0"] + count["P1"] + count["P2"] + count["P3"]
    if (total == 0) exit 0
    printf "Punch list (docs/PUNCH_LIST.md): %d open - %d P0, %d P1, %d P2, %d P3.\n", \
      total, count["P0"], count["P1"], count["P2"], count["P3"]
    for (i = 1; i <= np0; i++) printf "  P0 (hotfix, before feature work): %s\n", p0[i]
    if (top1 != "") printf "  Top P1: %s\n", top1
    print "Read the file before recommending what to work on. Any finding not fixed this session gets an entry there before the session ends."
  }
' "$file"
