#!/usr/bin/env bash
# SessionStart hook: emit a short digest of the docket into session context, so
# a session knows the queue exists, what is at the top of it, what is already
# in flight on a branch, and whether anything is waiting to be triaged - all
# without reading the store. The digest is deliberately a few lines: this text
# is resent on every turn of the session.
#
# Fails silently if python3 or the store is missing, so a checkout without
# either still starts cleanly.
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0

root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
package="$root/subprojects/docket/src"
[ -d "$package" ] || exit 0
[ -d "$root/docs/items" ] || exit 0

PYTHONPATH="$package" python3 -m docket digest 2>/dev/null || exit 0
