#!/usr/bin/env bash
# SessionStart hook: emit a short digest of the docket into session context, so
# a session knows the queue exists, what is at the top of it, what is already
# in flight on a branch, and whether anything is waiting to be triaged - all
# without reading the store. The digest is deliberately a few lines: this text
# is resent on every turn of the session.
#
# It also reports where the working branch stands against `origin/main`. That
# is a check rather than a rule for the same reason the rest of this is a
# digest rather than a paragraph in CLAUDE.md: a session that picks up a
# branch whose pull request has already merged stacks new commits on merged
# history, and one starting from a stale base does the work against code that
# has since moved. Both cost a full rework cycle, paid at push time rather
# than at the start, and both are invisible unless something looks.
#
# Fails silently if python3, git, the remote or the store is missing, so a
# checkout without any of them still starts cleanly.
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0

root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
[ -x "$root/bin/docket" ] || exit 0
[ -d "$root/docs/items" ] || exit 0

"$root/bin/docket" digest 2>/dev/null || true

branch_state() {
  command -v git >/dev/null 2>&1 || return 0
  git -C "$root" rev-parse --git-dir >/dev/null 2>&1 || return 0

  local branch counts behind ahead fetch=(git -C "$root" fetch --quiet origin main)
  branch=$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null) || return 0
  [ -n "$branch" ] && [ "$branch" != "HEAD" ] || return 0

  # A fetch that hangs would stall every session start, so it is bounded and
  # its failure is not an error: the counts below then read the last fetch,
  # which is stale by exactly one fetch rather than wrong.
  if command -v timeout >/dev/null 2>&1; then
    timeout 20 "${fetch[@]}" >/dev/null 2>&1 || true
  else
    "${fetch[@]}" >/dev/null 2>&1 || true
  fi

  counts=$(git -C "$root" rev-list --left-right --count origin/main...HEAD 2>/dev/null) || return 0
  behind=${counts%%[[:space:]]*}
  ahead=${counts##*[[:space:]]}
  [ -n "$behind" ] && [ -n "$ahead" ] || return 0

  if [ "$behind" -eq 0 ]; then
    echo "Branch: $branch, current with origin/main ($ahead ahead)."
  elif [ "$ahead" -eq 0 ] && [ "$branch" != "main" ]; then
    echo "Branch: $branch is $behind behind origin/main with nothing of its own."
    echo "  Its work is merged or it never had any. Restart it from main before editing:"
    echo "  git checkout main && git pull && git checkout -B $branch origin/main"
  elif [ "$branch" = "main" ]; then
    echo "Branch: main is $behind behind origin/main. \`git pull\` before starting."
  else
    echo "Branch: $branch is $behind behind origin/main and $ahead ahead."
    echo "  Merge origin/main before your first edit, not at push time."
  fi
}

branch_state
