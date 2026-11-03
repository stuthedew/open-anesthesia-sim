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
# `docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)" explains. A failure of
# the tool lets the edit through, and the check over the tree still applies.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "$root/tools/regex_check.py" --screen || true
exit 0
