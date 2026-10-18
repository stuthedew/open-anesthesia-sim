#!/usr/bin/env bash
# PreToolUse hook on an edit, and PostToolUse hook after a Bash call: say so if
# the base has moved, and, at the first edit that is work, if the branch claims
# nothing.
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
# a capture or a triage pass writes only the queue - its items, the roadmap,
# the notes and its body record - and owes no claim, and asking then would
# spend the session's one question where it had no answer.
# `tools/branch_id_check.py --hint` decides, from the reader CI's refusal uses,
# so the hook and the gate cannot disagree: its exit 3 says the path was not
# work outside the queue and nothing was asked, and anything else spends the
# question, a failure included, since asking a broken check before every edit
# would tax each one.
#
# **After a Bash call, it reads the tree rather than the command** (`PL-RXFK`).
# A session can edit through Bash, which the harness's auto mode recommends for
# small edits, and a Bash command names no path. So the hook also runs after
# each Bash call: as `PostToolUse`, or as `PostToolUseFailure` where the
# command failed, which is common when one command edits and then runs a check.
# A clean tree means the call edited nothing yet, and the hook stops there.
# Otherwise both questions are asked as they are at an edit, and the claim
# question goes to `tools/branch_id_check.py --hint-changed`, which asks it of
# every file the checkout has changed. A command that edits and commits in one
# call leaves a clean tree, so it is asked at the next call that leaves a
# change. Speaking just after the edit rather than just before it costs
# nothing, because the hook adds context and blocks nothing.
#
# **Only the run that creates a marker speaks.** The hooks for parallel tool
# calls run at the same time, so each marker is created with `set -C`, which
# refuses a file that already exists. Without it, two parallel calls could
# both fetch and both print. `GIT_OPTIONAL_LOCKS=0` keeps the hook's reads of
# the tree from refreshing the index as a side effect, so they never hold the
# index lock while a `git add` or `git commit` in a parallel call needs it.
#
# Exits 0 in every case, including every failure - a checkout without python3,
# git, a remote or the store still edits normally.
set -uo pipefail

payload=$(cat)

command -v python3 >/dev/null 2>&1 || exit 0
# The checkout, as every hook finds it (`hook_input.py`, `PL-FB77`).
root=$(python3 "$(dirname "${BASH_SOURCE[0]}")/hook_input.py") || exit 0
[ -x "$root/bin/docket" ] || exit 0

# The id and the event, read as JSON as the rest of the payload is, so an id
# laid out on the line after its key is still the id (`PL-CXK6`), and each
# reduced to what is safe in a filename. A payload that is not JSON or names no
# id leaves it empty, and every such session shares the markers kept for
# "unknown": the first is asked, and the rest are not. A payload naming no
# event is read as an edit's.
fields=$(printf '%s' "$payload" | python3 -c 'import json, re, sys

try:
    data = json.load(sys.stdin)
    values = [data.get("session_id"), data.get("hook_event_name")]
except (AttributeError, ValueError):
    values = []
for value in values:
    print(re.sub(r"[^A-Za-z0-9_-]", "", value) if isinstance(value, str) else "")
' 2>/dev/null)
session=$(printf '%s\n' "$fields" | sed -n 1p)
event=$(printf '%s\n' "$fields" | sed -n 2p)
case "$event" in
  PostToolUse | PostToolUseFailure) ;;
  *) event=PreToolUse ;;
esac
stale="${TMPDIR:-/tmp}/docket-branch-${session:-unknown}"
claim="${TMPDIR:-/tmp}/docket-claim-${session:-unknown}"
[ -e "$stale" ] && [ -e "$claim" ] && exit 0

# `docket` resolves the store from the working directory, so a hook run from
# somewhere else would answer confidently about the wrong repository.
cd "$root" 2>/dev/null || exit 0
export GIT_OPTIONAL_LOCKS=0

# After a Bash call, a clean tree means the call edited nothing yet.
if [ "$event" != PreToolUse ] &&
  [ -z "$(git status --porcelain 2>/dev/null | head -n 1)" ]; then
  exit 0
fi

context=""
if [ ! -e "$stale" ] && (set -C && : >"$stale") 2>/dev/null; then
  # Of its stderr, only the floor refusal is kept, as the digest hook keeps it,
  # so a session below docket's Python floor is told why it hears nothing.
  errors=$(mktemp 2>/dev/null) || errors=/dev/null
  context=$("$root/bin/docket" branch --brief --if-stale 2>"$errors") ||
    context=$(grep -m 1 '^docket needs Python' "$errors" 2>/dev/null)
  [ "$errors" = /dev/null ] || rm -f "$errors"
fi

check="$root/tools/branch_id_check.py"
if [ ! -e "$claim" ] && [ -f "$check" ]; then
  hint=""
  asked=3
  if [ "$event" != PreToolUse ]; then
    hint=$(python3 "$check" --hint-changed 2>/dev/null)
    asked=$?
  else
    # The path being edited, from the documented `tool_input` of the four
    # edit tools.
    target=$(printf '%s' "$payload" | python3 -c 'import json, sys

try:
    edit = json.load(sys.stdin).get("tool_input") or {}
    print(edit.get("file_path") or edit.get("notebook_path") or "")
except (AttributeError, ValueError):
    pass
' 2>/dev/null) || target=""
    if [ -n "$target" ]; then
      hint=$(python3 "$check" --hint "$target" 2>/dev/null)
      asked=$?
    fi
  fi
  if [ "$asked" -ne 3 ] && (set -C && : >"$claim") 2>/dev/null && [ -n "$hint" ]; then
    context="${context:+$context
}$hint"
  fi
fi
[ -n "$context" ] || exit 0

# Plain stdout from a `PreToolUse` hook reaches the debug log and nowhere the
# session can read, so the line has to travel as `additionalContext` in the
# documented JSON form, which names the event it answers. `json.dumps` does the
# escaping: the text carries backticks, quotes and newlines.
CONTEXT="$context" EVENT="$event" python3 -c 'import json, os, sys

sys.stdout.write(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": os.environ["EVENT"],
                "additionalContext": os.environ["CONTEXT"],
            }
        }
    )
)
' 2>/dev/null || exit 0
