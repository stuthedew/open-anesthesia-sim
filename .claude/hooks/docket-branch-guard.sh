#!/usr/bin/env bash
# PreToolUse hook on the first edit of a session: say so if the base has moved.
#
# `PL-1CYR` made the branch-vs-`main` question askable at any moment
# (`bin/docket branch`) instead of only at session start. This is what asks it,
# at the one moment worth asking: a session opened to discuss the next piece of
# work sits while another session merges, and the staleness would otherwise
# surface at push time as a merge conflict. The first edit is where a
# discussion becomes implementation, so it is where the answer is wanted.
#
# **Once per session, not once per edit.** The check fetches, and paying for a
# fetch before every edit would be a worse tax than the conflict it prevents.
# The marker is keyed on the session id the hook is handed.
#
# **It says nothing when the branch is current** (`--if-stale`). A hook that
# speaks unasked has to earn each line, and "your base has not moved" is not
# worth interrupting an edit for.
#
# **It adds context; it never grants permission.** `permissionDecision` is
# deliberately absent from the JSON below: sending `allow` would auto-approve
# the very edit this is attached to, which is a security property, not a
# convenience. The hook's whole job is to say something.
#
# Exits 0 in every case, including every failure - a checkout without python3,
# git, a remote or the store still edits normally.
set -uo pipefail

payload=$(cat)

command -v python3 >/dev/null 2>&1 || exit 0
root="${CLAUDE_PROJECT_DIR:-}"
[ -n "$root" ] || exit 0
[ -x "$root/bin/docket" ] || exit 0

# The id, reduced to what is safe in a filename. An unreadable payload leaves
# it empty and the check runs once for "unknown", which is the safe direction:
# at worst it is asked once more than it needed to be.
session=$(printf '%s' "$payload" |
  sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' |
  tr -cd 'A-Za-z0-9_-')
marker="${TMPDIR:-/tmp}/docket-branch-${session:-unknown}"
[ -e "$marker" ] && exit 0
: >"$marker" 2>/dev/null || exit 0

# `docket` resolves the store from the working directory, so a hook run from
# somewhere else would answer confidently about the wrong repository.
cd "$root" 2>/dev/null || exit 0
line=$("$root/bin/docket" branch --brief --if-stale 2>/dev/null) || exit 0
[ -n "$line" ] || exit 0

# Plain stdout from a `PreToolUse` hook reaches the debug log and nowhere the
# session can read, so the line has to travel as `additionalContext` in the
# documented JSON form. `json.dumps` does the escaping: the text carries
# backticks, quotes and newlines.
CONTEXT="$line" python3 -c 'import json, os, sys

sys.stdout.write(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": os.environ["CONTEXT"],
            }
        }
    )
)
' 2>/dev/null || exit 0
