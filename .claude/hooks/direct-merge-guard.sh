#!/usr/bin/env bash
# PreToolUse hook on the GitHub server's merge tool: let a session's merge
# through only while GitHub itself holds it to its base branch's checks
# (`PL-NXRJ`).
#
# **When a session merges at all.** A session merges by arming auto-merge, and
# GitHub will not arm a pull request that is already green and current: it
# answers "you can merge directly". That merge stayed the owner's (`PL-V2X5`,
# `PL-S17R`) while `main`'s protection exempted an admin, because a session's
# GitHub calls are the owner's, and a merge landing between its read and its
# call put a stale branch on `main` - the merge skew `PL-6MW8` made `main`
# refuse. On 2026-10-03 the owner turned on "Do not allow bypassing the above
# settings" for `main` (project owner, 2026-10-03, ratified, over keeping that
# merge the owner's Squash and merge), so GitHub refuses an admin's merge too
# unless the required checks pass on a head current with the base, which is
# what auto-merge waits for. A session now merges directly what it would have
# armed.
#
# **Read at each call, never assumed.** The owner can switch the setting off
# again, to merge past a red check, and a hook that remembered it would then
# let a stale merge through. So each call asks GitHub for the pull request's
# base and then that branch's record, without a token as a public repository
# allows, and lets the call through only where
# `protection.required_status_checks.enforcement_level` reads `everyone`. It
# read `non_admins` before the switch and `everyone` after it (measured
# 2026-10-03). A required check moved into a ruleset leaves that record without
# one, and the merge is refused: the safe direction, since a refusal costs the
# owner a click and a wrong pass costs a stale `main`.
# `DIRECT_MERGE_GUARD_API` replaces the API root for the tests and is set
# nowhere else.
#
# **The merge method is not checked**: the repository allows squash merges
# alone (`allow_merge_commit` and `allow_rebase_merge` false, read 2026-10-03),
# so GitHub refuses any other.
#
# **Why a hook and not a clause.** The rule has to fire at the call, which no
# read precedes, and it was resident prose when a session merged `#1224` past
# it on 2026-09-28, while admins were still exempt. The refusal's reason is
# shown to the model (https://code.claude.com/docs/en/hooks, read 2026-09-30),
# so the route arrives at the one moment it is needed, in a subagent as in the
# main session.
#
# **The matcher is a whole-name regex**, `^mcp__.+__merge_pull_request$`, so the
# merge tool is matched whatever its server is called. A matcher of letters and
# underscores alone is compared as an exact name, so a bare `merge_pull_request`
# would match no tool and refuse nothing; `tests/unit/test_direct_merge_guard.py`
# pins the wiring against that.
#
# **Fails closed, unlike its siblings.** They read a command and fail open,
# because a false refusal there blocks correct work. Here the matcher has
# already chosen a merge call, so only a payload naming another tool is let
# through unread - a hook wired to the wrong matcher then refuses nothing rather
# than everything - and an unreadable payload, a record GitHub does not answer,
# and a python3 that is missing or fails are each refused.
#
# **Known gap**: a merge made another way - `gh pr merge`, or a REST call from
# Bash - meets no hook. While the base binds admins GitHub holds it to the same
# checks, and `CLAUDE.md`'s merge bullet covers the rest.
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

# Exits 0 having printed a refusal, or having printed nothing to let the call
# through to the ordinary permission flow.
PAYLOAD="$payload" python3 -c '
import json, os, sys, urllib.parse, urllib.request

API = os.environ.get("DIRECT_MERGE_GUARD_API") or "https://api.github.com"
ROUTE = (
    "A session merges by arming auto-merge (`enable_pr_auto_merge`) while a check is pending. "
    "Where GitHub will not arm a pull request because it is already in clean status, tell the "
    "owner it cannot be armed and that the Squash and merge is theirs, in the browser, and do "
    "not merge it another way (`docs/maintainer.md` § \"Bring a stale base in when you merge, "
    "with Update branch\"; `PL-NXRJ`)."
)


def refuse(why):
    decision = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Refused: " + why + "\n\n" + ROUTE,
    }
    sys.stdout.write(json.dumps({"hookSpecificOutput": decision}))
    sys.exit(0)


def record(path):
    """One record from the GitHub API, read without a token."""
    request = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json"})
    # Two reads of 15 s each stay well inside the 60 s Claude Code allows a hook by default.
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


try:
    call = json.loads(os.environ["PAYLOAD"])["tool_input"]
    owner, repo, number = str(call["owner"]), str(call["repo"]), int(call["pullNumber"])
except (KeyError, TypeError, ValueError):
    refuse(
        "the call names no pull request this hook can read, so it cannot ask GitHub "
        "whether the base branch holds the merge to its required checks."
    )

repository = "/repos/" + urllib.parse.quote(owner, safe="") + "/" + urllib.parse.quote(repo, safe="")
named = "`" + owner + "/" + repo + "#" + str(number) + "`"
try:
    base = record(repository + "/pulls/" + str(number))["base"]["ref"]
    branch = record(repository + "/branches/" + urllib.parse.quote(base, safe=""))
    level = (branch["protection"].get("required_status_checks") or {}).get("enforcement_level")
except (OSError, LookupError, TypeError, ValueError, AttributeError) as error:
    refuse(
        "GitHub did not answer whether the base branch of " + named + " holds an admin to "
        "its required checks (" + str(error) + "), and a session merges as the owner, an admin."
    )
if level != "everyone":
    refuse(
        "the GitHub record for `" + base + "` reads `enforcement_level: " + str(level) + "`, "
        "not `everyone`, so its required checks and up-to-date rule do not bind an admin, and "
        "a session merges as the owner, an admin: a merge landing between a read and this call "
        "would put a stale branch on `" + base + "`, the merge skew `PL-6MW8` made `main` "
        "refuse. Turning on **Do not allow bypassing the above settings** in that branch "
        "protection rule is what lets a session merge it."
    )
' && exit 0

# python3 is missing or failed before deciding, so nothing was read: refuse.
cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Refused: this hook could not run its python3 step to ask GitHub whether the base branch holds the merge to its required checks.\n\nA session merges by arming auto-merge (`enable_pr_auto_merge`) while a check is pending. Where GitHub will not arm a pull request because it is already in clean status, tell the owner it cannot be armed and that the Squash and merge is theirs, in the browser, and do not merge it another way (`docs/maintainer.md`; `PL-NXRJ`)."}}
JSON
