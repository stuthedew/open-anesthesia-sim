#!/usr/bin/env bash
# PreToolUse hook on every MCP tool: let a session's merge through only while
# GitHub itself holds it to its base branch's checks (`PL-NXRJ`).
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
# **Only a merge into this repository is judged** (`PL-L08H`). The skew the
# hook prevents is a stale branch on this repository's `main`. A session also
# merges in other repositories, such as the private references corpus, which
# has no branch protection and no CI. Its merges have no checks to skip, and the
# hook refused them for nothing, leaving each one to the owner. So the hook
# reads which GitHub repository its own checkout is from
# `tools/open_pull_requests.repo_slug`, the one reading of that fact
# (`PL-LGDV`), and lets a merge naming any other repository through unread.
# Where `origin` names no GitHub repository, or the read fails, the hook cannot
# tell its own merges from others, so it judges every merge, as it did before.
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
# **Every MCP tool reaches it, and the script picks out the merges** (`PL-NZJG`).
# The GitHub server owns its tool names and changes them without notice. It has
# already folded its issue and review tools into `issue_write` and
# `pull_request_review_write`, each of which takes a `method`. A matcher naming
# `merge_pull_request` would stop this guard silently after such a change. So
# `.claude/settings.json` wires it on `^mcp__.*$`, whatever the server is
# called. The script treats a call as a merge when its tool's own name contains
# "merge", or when its `method` is `merge`. It names the two tools it skips,
# `enable_pr_auto_merge` and `disable_pr_auto_merge`, which arm and disarm
# auto-merge rather than merge. A renamed merge tool is still checked. A tool
# wrongly taken for a merge is asked about at GitHub like a merge, which lets it
# through while the base binds admins. What goes unchecked after a rename is a
# merge tool whose name lacks "merge" and whose call carries no `method` of
# `merge`. `.claude/rules/apparatus-standard.md` § "The floor" has the rule, in
# its paragraph on a guard keyed on names that another system owns.
#
# **Fails closed on a merge, unlike its siblings.** They read a command and fail
# open, because a false refusal there blocks correct work. Here a call taken for
# a merge is refused when it names no pull request or GitHub does not answer.
# Where the script cannot judge a call at all, because python3 is missing or
# fails or the payload names no tool, the call is refused only if its text
# contains "merge" in any case. Every call the script would take for a merge
# contains it, so no merge gets through unjudged, and the other MCP calls, such
# as a Projects thread's posts, are not blocked with it.
#
# **Known gap**: a merge sent from Bash meets this hook only through `gh`, whose
# writes `gh_write_guard.py` refuses outright, so every `gh` merge is turned
# back to the MCP call this hook reads (`PL-3986`). A REST call from another
# client that carries the token, such as `curl` with `$GH_TOKEN`, meets no
# hook. While the base binds admins GitHub holds it to the same checks.
set -uo pipefail

payload=$(cat)

# Exits 0 having printed a refusal, or having printed nothing to let the call
# through to the ordinary permission flow. Exits 3 where the payload names no
# tool, and the shell after it then decides.
PAYLOAD="$payload" HOOKS="$(dirname "${BASH_SOURCE[0]}")" python3 -c '
import json, os, sys, urllib.parse, urllib.request

sys.path.insert(0, os.environ["HOOKS"])
import hook_input

API = os.environ.get("DIRECT_MERGE_GUARD_API") or "https://api.github.com"
ROUTE = (
    "A session merges by arming auto-merge (`enable_pr_auto_merge`) while a check is pending. "
    "Where GitHub will not arm a pull request because it is already in clean status, tell the "
    "owner it cannot be armed and that the Squash and merge is theirs, in the browser, and do "
    "not merge it another way (`docs/maintainer.md` § \"Bring a stale base in when you merge, "
    "with Update branch\"; `PL-NXRJ`)."
)
# The tools whose names contain "merge" but which arm or disarm auto-merge
# rather than merge (`PL-NZJG`).
NOT_A_MERGE = frozenset({"enable_pr_auto_merge", "disable_pr_auto_merge"})


def refuse(rule, why):
    reason = "Refused: " + why + "\n\n" + ROUTE
    sys.stdout.write(hook_input.deny("direct-merge-guard", rule, reason, os.environ["PAYLOAD"]))
    sys.exit(0)


def record(path):
    """One record from the GitHub API, read without a token."""
    request = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json"})
    # Two reads of 15 s each stay well inside the 60 s Claude Code allows a hook by default.
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def own_repository():
    """`owner/name` of the GitHub repository this hook is checked into, or None.

    It is read by `open_pull_requests.repo_slug`, from the `origin` of the
    checkout that holds this hook (`PL-L08H`). None means the hook cannot tell
    which merges are its own: `origin` names no GitHub repository, or the read
    failed. The caller then judges every merge.
    """
    try:
        sys.path.insert(0, os.path.join(os.environ["HOOKS"], os.pardir, os.pardir, "tools"))
        import open_pull_requests

        return open_pull_requests.repo_slug()
    except Exception:
        return None


try:
    payload = json.loads(os.environ["PAYLOAD"])
except ValueError:
    payload = None

# The name of the tool, from the documented payload read as JSON: a commit
# message quoting `"tool_name"` cannot supply one, and a name laid out on the
# line after its key is still the name, where a sed run a line at a time read
# none and refused the call of another tool (`PL-CXK6`).
tool = payload.get("tool_name") if isinstance(payload, dict) else None
if not isinstance(tool, str) or not tool:
    # No tool to judge. Exit non-zero, so the shell below decides from the text.
    sys.exit(3)
name = tool.rsplit("__", 1)[-1]
arguments = payload.get("tool_input")
method = arguments.get("method") if isinstance(arguments, dict) else None
merges = name not in NOT_A_MERGE and (
    "merge" in name.lower() or (isinstance(method, str) and method.lower() == "merge")
)
if not merges:
    sys.exit(0)

try:
    call = payload["tool_input"]
    owner, repo, number = str(call["owner"]), str(call["repo"]), int(call["pullNumber"])
except (KeyError, TypeError, ValueError):
    refuse(
        "unreadable-call",
        "the call names no pull request this hook can read, so it cannot ask GitHub "
        "whether the base branch holds the merge to its required checks."
    )

# A merge in another repository cannot leave a stale branch on the `main` of
# this one. GitHub treats owner and repository names without regard to case.
own = own_repository()
if own is not None and (owner + "/" + repo).lower() != own.lower():
    sys.exit(0)

repository = "/repos/" + urllib.parse.quote(owner, safe="") + "/" + urllib.parse.quote(repo, safe="")
named = "`" + owner + "/" + repo + "#" + str(number) + "`"
try:
    base = record(repository + "/pulls/" + str(number))["base"]["ref"]
    branch = record(repository + "/branches/" + urllib.parse.quote(base, safe=""))
    level = (branch["protection"].get("required_status_checks") or {}).get("enforcement_level")
except (OSError, LookupError, TypeError, ValueError, AttributeError) as error:
    refuse(
        "no-answer",
        "GitHub did not answer whether the base branch of " + named + " holds an admin to "
        "its required checks (" + str(error) + "), and a session merges as the owner, an admin."
    )
if level != "everyone":
    refuse(
        "admins-unbound",
        "the GitHub record for `" + base + "` reads `enforcement_level: " + str(level) + "`, "
        "not `everyone`, so its required checks and up-to-date rule do not bind an admin, and "
        "a session merges as the owner, an admin: a merge landing between a read and this call "
        "would put a stale branch on `" + base + "`, the merge skew `PL-6MW8` made `main` "
        "refuse. Turning on **Do not allow bypassing the above settings** in that branch "
        "protection rule is what lets a session merge it."
    )
' && exit 0

# Nothing judged the call: python3 is missing or failed, or the payload names no
# tool. Every call the script takes for a merge contains "merge", so refuse only
# a call whose text contains it.
shopt -s nocasematch
if [[ $payload != *merge* ]]; then
    exit 0
fi
cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Refused: this hook could not judge whether this call merges a pull request, because its python3 step is missing or failed or the call names no tool, and the call mentions a merge.\n\nA session merges by arming auto-merge (`enable_pr_auto_merge`) while a check is pending. Where GitHub will not arm a pull request because it is already in clean status, tell the owner it cannot be armed and that the Squash and merge is theirs, in the browser, and do not merge it another way (`docs/maintainer.md`; `PL-NXRJ`)."}}
JSON
