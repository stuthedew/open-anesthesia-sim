#!/usr/bin/env bash
# SessionStart hook: emit a short digest of docs/PUNCH_LIST.md into session
# context, so a session knows the queue exists, what is at the top of it, and
# whether a grooming pass is due - without reading the whole file. The digest
# is deliberately a few lines: this text is resent on every turn.
#
# Fails silently if python3 or the punch list is missing, so a checkout
# without either still starts cleanly.
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0

root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
tool="$root/tools/punch_list.py"
[ -r "$tool" ] || exit 0

# The branch name decides whether the digest also says where to put the item
# id. Absent outside a git checkout, in which case the digest simply omits it.
branch="$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"

python3 "$tool" digest ${branch:+--branch "$branch"} 2>/dev/null || exit 0
