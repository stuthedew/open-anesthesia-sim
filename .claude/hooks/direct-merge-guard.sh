#!/usr/bin/env bash
# PreToolUse hook on every MCP tool: let a session's merge through only while
# GitHub itself holds it to its base branch's checks (`PL-NXRJ`).
#
# The rule is `direct_merge_guard.py` beside this file, whose docstring says
# which calls are merges, what it asks GitHub, and why. This script starts it
# with the payload on standard input (`PL-S3TF`, `PL-B5K1`), and decides only
# when Python does not: where python3 is missing or fails, it refuses a call
# whose text contains "merge" in any case. Every call the module takes for a
# merge contains it, so no merge gets through unjudged, and the other MCP
# calls, such as a Projects thread's posts, are not blocked with it.
set -uo pipefail

payload=$(cat)
printf '%s' "$payload" |
  python3 "$(dirname "${BASH_SOURCE[0]}")/direct_merge_guard.py" 2>/dev/null && exit 0

shopt -s nocasematch
if [[ $payload != *merge* ]]; then
    exit 0
fi
cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Refused: this hook could not judge whether this call merges a pull request, because its python3 step is missing or failed, and the call mentions a merge.\n\nA session merges by arming auto-merge (`enable_pr_auto_merge`) while a check is pending. Where GitHub will not arm a pull request because it is already in clean status, tell the owner it cannot be armed and that the Squash and merge is theirs, in the browser, and do not merge it another way (`docs/maintainer.md`; `PL-NXRJ`)."}}
JSON
