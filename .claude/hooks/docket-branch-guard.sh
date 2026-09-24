#!/usr/bin/env bash
# PreToolUse hook on an edit: say so if the base has moved, and, at the first
# edit that is work, if the branch claims nothing.
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
# **The claim question waits for the first edit outside the queue** (`PL-J9S0`,
# `PL-MB2W` § "Forgetful session"). Who holds an item is a `Claim:` trailer the
# session commits, and a session that forgets to write one is invisible to
# every reader of that record until CI refuses its pull request. So before the
# first edit that is work, the hook adds "this branch claims nothing:
# `bin/docket claim <id>`" where that is so. Not at the first edit of any kind:
# a capture or a triage pass writes only item files and owes no claim, and
# asking then would spend the session's one question where it had no answer.
# `tools/branch_id_check.py --hint` decides, from the reader CI's refusal uses,
# so the hook and the gate cannot disagree: its exit 3 says the path was not
# work outside the queue and nothing was asked, and anything else spends the
# question, a failure included, since asking a broken check before every edit
# would tax each one.
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
stale="${TMPDIR:-/tmp}/docket-branch-${session:-unknown}"
claim="${TMPDIR:-/tmp}/docket-claim-${session:-unknown}"
[ -e "$stale" ] && [ -e "$claim" ] && exit 0

# `docket` resolves the store from the working directory, so a hook run from
# somewhere else would answer confidently about the wrong repository.
cd "$root" 2>/dev/null || exit 0

context=""
if [ ! -e "$stale" ] && : >"$stale" 2>/dev/null; then
  context=$("$root/bin/docket" branch --brief --if-stale 2>/dev/null) || context=""
fi

check="$root/tools/branch_id_check.py"
if [ ! -e "$claim" ] && [ -f "$check" ]; then
  # The path being edited, from the documented `tool_input` of the four tools
  # this hook is attached to.
  target=$(printf '%s' "$payload" | python3 -c 'import json, sys

try:
    edit = json.load(sys.stdin).get("tool_input") or {}
    print(edit.get("file_path") or edit.get("notebook_path") or "")
except (AttributeError, ValueError):
    pass
' 2>/dev/null) || target=""
  if [ -n "$target" ]; then
    hint=$(python3 "$check" --hint "$target" 2>/dev/null)
    if [ $? -ne 3 ] && : >"$claim" 2>/dev/null && [ -n "$hint" ]; then
      context="${context:+$context
}$hint"
    fi
  fi
fi
[ -n "$context" ] || exit 0

# Plain stdout from a `PreToolUse` hook reaches the debug log and nowhere the
# session can read, so the line has to travel as `additionalContext` in the
# documented JSON form. `json.dumps` does the escaping: the text carries
# backticks, quotes and newlines.
CONTEXT="$context" python3 -c 'import json, os, sys

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
