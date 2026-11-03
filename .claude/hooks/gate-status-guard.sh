#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a gate command whose exit status the command
# then throws away, and `bin/docket arm` piped into another command.
#
# The rule is `gate_status_guard.py` beside this file, whose docstring says
# which commands are gates, how a status is lost or kept, and why. This script
# only starts it, so that what `.claude/settings.json` runs stays a shell entry
# point in the protected directory, as `docs/apparatus.md` § "Wired hooks
# (`.claude/hooks/`)" explains. The payload reaches Python on standard input
# (`PL-S3TF`, `PL-B5K1`).
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0
python3 "$(dirname "${BASH_SOURCE[0]}")/gate_status_guard.py" 2>/dev/null || exit 0
