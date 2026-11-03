#!/usr/bin/env bash
# PreToolUse hook on Bash: before a `git push` sends this repository's tree,
# run the checks that most often turn a pull request red, and deny the push
# while any fails.
#
# The rule is `push_check_guard.py` beside this file, whose docstring says
# which checks run, on which tree, and why. This script only starts it, so that
# what `.claude/settings.json` runs stays a shell entry point in the protected
# directory, as `docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)" explains.
# The payload reaches Python on standard input (`PL-S3TF`, `PL-B5K1`).
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0
python3 "$(dirname "${BASH_SOURCE[0]}")/push_check_guard.py" 2>/dev/null || exit 0
