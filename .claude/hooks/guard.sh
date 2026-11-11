#!/usr/bin/env bash
# The command `.claude/settings.json` runs for each tool call a guard watches
# (`PL-9KSJ`). It starts `guard.py` beside it, with the call on standard input
# and the group named by its first argument, and prints what `guard.py`
# decides. `guard.py`'s docstring says what a guard is and how a guard that
# fails is reported.
#
# This script reports what Python cannot report itself: a `python3` that is
# missing, or one that exits non-zero before `guard.py` has decided, as it
# does when the standard library will not load. The call then goes through,
# with a note saying it was not checked. Nothing is refused here: GitHub
# refuses a merge past `main`'s checks wherever it is sent from, and
# `tools/github_refusals_check.py` fails CI where that rule is off (`PL-39Y1`).
#
# It uses bash's own commands for everything but `python3` and the scratch
# file for Python's errors, so that it still reports on a machine missing
# the rest. Keep it short and free of any rule, so that a merge rarely
# touches it. A line bash cannot parse here makes bash exit 2, which Claude
# Code takes for a refusal of every call this script is wired on.
set -uo pipefail

IFS= read -r -d '' payload || true
errors=$(mktemp 2>/dev/null) || errors=/dev/null
if command -v python3 >/dev/null 2>&1; then
  output=$(printf '%s' "$payload" | python3 "${BASH_SOURCE[0]%/*}/guard.py" "${1:-}" 2>"$errors")
  status=$?
  why="python3 exited with status $status"
else
  output=""
  status=127
  why="python3 is not on the PATH"
fi
last=""
while IFS= read -r line || [ -n "$line" ]; do
  [ -n "$line" ] && last=$line
done <"$errors"
[ "$errors" = /dev/null ] || rm -f "$errors" 2>/dev/null
if [ "$status" -eq 0 ]; then
  printf '%s' "$output"
  exit 0
fi

# Print `$1` as a JSON string, quotes included. Control characters are
# dropped, since JSON refuses them unescaped.
json_string() {
  local text=$1
  text=${text//\\/\\\\}
  text=${text//\"/\\\"}
  text=${text//[$'\001'-$'\037']/}
  printf '"%s"' "$text"
}

why="$why${last:+ ($last)}"
event=PreToolUse
if [[ $payload =~ \"hook_event_name\"[[:space:]]*:[[:space:]]*\"([A-Za-z]+)\" ]]; then
  event=${BASH_REMATCH[1]}
fi
note="No guard checked this call (${1:-none named}), so it went through unchecked: $why."
printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": %s}}\n' \
  "$event" "$(json_string "$note")"
exit 0
