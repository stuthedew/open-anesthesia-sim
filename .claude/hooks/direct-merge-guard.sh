#!/usr/bin/env bash
# PreToolUse hook on the GitHub server's merge tool: refuse it, because a
# session never merges a pull request itself (`PL-S17R`).
#
# **The rule is `CLAUDE.md`'s, and the case it missed is `PL-V2X5`'s.** A
# session merges only by arming auto-merge: its GitHub calls are the owner's,
# and an admin's merge passes the up-to-date rule `main` holds everyone else
# to, so a merge landing between a session's read and its call puts a stale
# branch on `main` - the merge skew `PL-6MW8` made `main` refuse. GitHub will
# not arm a pull request that is already green and current, and its refusal
# says "you can merge directly". `PL-V2X5` answered that case (project owner,
# 2026-09-26, ratified): the session says so, and the Squash and merge is the
# owner's. On 2026-09-28 a session with the rule resident met that refusal,
# judged a clean head safe to merge, and merged `#1224` through the API;
# `docs/maintainer.md` held the answer, and nothing a session reads before
# merging did.
#
# **Why a hook and not a clause.** The rule has to fire at the call, which no
# read precedes, and it was resident prose when it failed. The refusal's reason
# is shown to the model (https://code.claude.com/docs/en/hooks, read
# 2026-09-30), so the exception arrives at the one moment it is needed, in a
# subagent as in the main session, and the resident set does not grow to carry
# it.
#
# **Every call is refused.** The rule has no case in which a session merges, so
# the hook decides nothing. Letting a session merge means reopening `PL-V2X5`
# and removing this hook with it.
#
# **The matcher is a whole-name regex**, `^mcp__.+__merge_pull_request$`, so the
# merge tool is matched whatever its server is called. A matcher of letters and
# underscores alone is compared as an exact name, so a bare `merge_pull_request`
# would match no tool and refuse nothing; `tests/unit/test_direct_merge_guard.py`
# pins the wiring against that.
#
# **Fails closed, unlike its siblings.** They read a command and fail open,
# because a false refusal there blocks correct work. Here the matcher has
# already chosen a merge call and there is no correct one to block, so only a
# payload naming another tool is let through - a hook wired to the wrong
# matcher then refuses nothing rather than everything - and an unreadable one
# is refused. The reply is fixed text, so it needs neither python3 nor the
# store.
#
# **Known gap**: a merge made another way - `gh pr merge`, or a REST call from
# Bash - meets no hook. Cloud sessions have no `gh` and no GitHub token outside
# the MCP server, and `CLAUDE.md`'s sentence still covers the rest.
set -uo pipefail

payload=$(cat)

# The tool's name, from the documented payload. A JSON string escapes its
# quotes, so a commit message quoting `"tool_name"` cannot supply one.
tool=$(printf '%s' "$payload" |
  sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' |
  head -n 1)
case "$tool" in
  "" | *__merge_pull_request) ;;
  *) exit 0 ;;
esac

cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Refused: a session never merges a pull request itself. It merges only by arming auto-merge (`enable_pr_auto_merge`), because its GitHub calls are the owner's and an admin's merge passes the up-to-date rule `main` holds everyone else to: a merge that lands between your read and this call puts a stale branch on `main` (`CLAUDE.md`, the bullet on bringing `origin/main` into an open pull request; `PL-6MW8`).\n\nIf GitHub refused to arm because the pull request is already in clean status, its \"you can merge directly\" is not addressed to a session. Tell the owner it cannot be armed because it can merge now, and that the Squash and merge is theirs, in the browser (`docs/maintainer.md` § \"Bring a stale base in when you merge, with Update branch\"; project owner, 2026-09-26, ratified, `PL-V2X5`). Do not merge it another way."}}
JSON
