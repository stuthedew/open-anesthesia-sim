#!/usr/bin/env bash
# PreToolUse hook on an edit: refuse a regular expression written without a
# reason beside it, and say what to try first (`PL-7JYV`).
#
# The project owner asked on 2026-11-03 that a session stop each time it
# reaches for a regular expression, consider whether a parser or a string
# method does the job better, look up the best practice for the task, and use
# the regular expression only where it is still the right tool.
#
# The rule is `screen` in `tools/regex_check.py`, which also runs over the
# whole tree in `make check` and CI. Its docstring says what the hook reads and
# what it lets through. This script is only the entry point, kept here so that
# what `.claude/settings.json` runs stays in the protected directory, as
# `docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)" explains.
#
# A failure lets the edit through and says so in a note the session reads,
# never silently (`PL-9KSJ`). The tool reports its own errors that way. The
# note below covers the one case it cannot: a Python that does not start.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if ! python3 "$root/tools/regex_check.py" --screen; then
  printf '%s\n' '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "This edit was not checked for a regular expression without a reason: the hook could not start. `make check` still checks the file."}}'
fi
exit 0
