#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a bare `python3` aimed at the 3.14 trees.
#
# The rule is `floor_interpreter_guard.py` beside this file, whose docstring
# says what it refuses and why. This script only starts it, so that what
# `.claude/settings.json` runs stays a shell entry point in the protected
# directory, as `docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)" explains.
# The payload reaches Python on standard input (`PL-S3TF`, `PL-B5K1`).
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0
python3 "$(dirname "${BASH_SOURCE[0]}")/floor_interpreter_guard.py" 2>/dev/null || exit 0
