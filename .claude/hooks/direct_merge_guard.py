"""Let a session's merge through only while GitHub holds it to its base branch's checks.

A `PreToolUse` hook on every MCP tool (`PL-NXRJ`).
GitHub itself holds it to its base branch's checks (`PL-NXRJ`).

**When a session merges at all.** A session merges by arming auto-merge, and
GitHub will not arm a pull request that is already green and current: it
answers "you can merge directly". That merge stayed the owner's (`PL-V2X5`,
`PL-S17R`) while `main`'s protection exempted an admin, because a session's
GitHub calls are the owner's, and a merge landing between its read and its
call put a stale branch on `main` - the merge skew `PL-6MW8` made `main`
refuse. On 2026-10-03 the owner turned on "Do not allow bypassing the above
settings" for `main` (project owner, 2026-10-03, ratified, over keeping that
merge the owner's Squash and merge), so GitHub refuses an admin's merge too
unless the required checks pass on a head current with the base, which is
what auto-merge waits for. A session now merges directly what it would have
armed.

**Read at each call, never assumed.** The owner can switch the setting off
again, to merge past a red check, and a hook that remembered it would then
let a stale merge through. So each call asks GitHub for the pull request's
base and then that branch's record, without a token as a public repository
allows, and lets the call through only where
`protection.required_status_checks.enforcement_level` reads `everyone`. It
read `non_admins` before the switch and `everyone` after it (measured
2026-10-03). A required check moved into a ruleset leaves that record without
one, and the merge is refused: the safe direction, since a refusal costs the
owner a click and a wrong pass costs a stale `main`.
`DIRECT_MERGE_GUARD_API` replaces the API root for the tests and is set
nowhere else.

**Only a merge into this repository is judged** (`PL-L08H`). The skew the
hook prevents is a stale branch on this repository's `main`. A session also
merges in other repositories, such as the private references corpus, which
has no branch protection and no CI. Its merges have no checks to skip, and the
hook refused them for nothing, leaving each one to the owner. So the hook
reads which GitHub repository its own checkout is from
`tools/open_pull_requests.repo_slug`, the one reading of that fact
(`PL-LGDV`), and lets a merge naming any other repository through unread.
Where `origin` names no GitHub repository, or the read fails, the hook cannot
tell its own merges from others, so it judges every merge, as it did before.

**The merge method is not checked**: the repository allows squash merges
alone (`allow_merge_commit` and `allow_rebase_merge` false, read 2026-10-03),
so GitHub refuses any other.

**Why a hook and not a clause.** The rule has to fire at the call, which no
read precedes, and it was resident prose when a session merged `#1224` past
it on 2026-09-28, while admins were still exempt. The refusal's reason is
shown to the model (https://code.claude.com/docs/en/hooks, read 2026-09-30),
so the route arrives at the one moment it is needed, in a subagent as in the
main session.

**Every MCP tool reaches it, and the script picks out the merges** (`PL-NZJG`).
The GitHub server owns its tool names and changes them without notice. It has
already folded its issue and review tools into `issue_write` and
`pull_request_review_write`, each of which takes a `method`. A matcher naming
`merge_pull_request` would stop this guard silently after such a change. So
`.claude/settings.json` wires it on `^mcp__.*$`, whatever the server is
called. The script treats a call as a merge when its tool's own name contains
"merge", or when its `method` is `merge`. It names the two tools it skips,
`enable_pr_auto_merge` and `disable_pr_auto_merge`, which arm and disarm
auto-merge rather than merge. A renamed merge tool is still checked. A tool
wrongly taken for a merge is asked about at GitHub like a merge, which lets it
through while the base binds admins. What goes unchecked after a rename is a
merge tool whose name lacks "merge" and whose call carries no `method` of
`merge`. `.claude/rules/apparatus-standard.md` § "The floor" has the rule, in
its paragraph on a guard keyed on names that another system owns.

**Fails closed on a merge, unlike its siblings.** They read a command and fail
open, because a false refusal there blocks correct work. Here a call taken for
a merge is refused when it names no pull request or GitHub does not answer.
Where the script cannot judge a call at all, because python3 is missing or
fails or the payload names no tool, the call is refused only if its text
contains "merge" in any case. Every call the script would take for a merge
contains it, so no merge gets through unjudged, and the other MCP calls, such
as a Projects thread's posts, are not blocked with it.

**Known gap**: a merge sent from Bash meets this guard only through `gh`,
whose writes `gh_write_guard.py` refuses outright, so every `gh` merge is
turned back to the MCP call this guard reads (`PL-3986`). A REST call from
another client that carries the token, such as `curl` with `$GH_TOKEN`, meets
no hook. While the base binds admins GitHub holds it to the same checks.
"""

from __future__ import annotations

import json
import os
import urllib.parse

import hook_input

ROUTE = (
    "A session merges by arming auto-merge (`enable_pr_auto_merge`) while a check is pending. "
    "Where GitHub will not arm a pull request because it is already in clean status, tell the "
    "owner it cannot be armed and that the Squash and merge is theirs, in the browser, and do "
    'not merge it another way (`docs/maintainer.md` § "Bring a stale base in when you merge, '
    'with Update branch"; `PL-NXRJ`).'
)
#: The refusal of a call this guard could not read as a tool call, where its text mentions a merge.
NO_TOOL_REFUSAL = (
    "Refused: this hook could not judge whether this call merges a pull request, because the "
    "call names no tool, and the call mentions a merge.\n\n" + ROUTE
)
# The tools whose names contain "merge" but which arm or disarm auto-merge
# rather than merge (`PL-NZJG`).
NOT_A_MERGE = frozenset({"enable_pr_auto_merge", "disable_pr_auto_merge"})


class Refused(Exception):
    """A merge this guard refuses: the rule that refused it, and why."""

    def __init__(self, rule: str, why: str) -> None:
        super().__init__(why)
        self.rule = rule
        self.why = why


#: Seconds the guard waits for each of its two reads of GitHub. Both reads
#: together must finish inside the deadline `guard.py` gives this guard, which
#: the entry point's test checks (`PL-KJN6`, `PL-9KSJ`).
MERGE_READ_TIMEOUT_S = 15


def record(path: str) -> object:
    """One record from the GitHub API, read without a token.

    The request is the one `open_pull_requests.api_request` builds for every
    tool that asks GitHub (`PL-LGDV`). `DIRECT_MERGE_GUARD_API` replaces the
    API root for the tests and is set nowhere else.
    """
    import urllib.request

    # `open_pull_requests`, the repository's one GitHub client, is imported only
    # once a call is taken for a merge, because it loads docket's git reader,
    # and this guard runs before every MCP call. `guard.py` puts `tools/` on
    # the path.
    import open_pull_requests

    root = os.environ.get("DIRECT_MERGE_GUARD_API") or open_pull_requests.GITHUB_API
    request = open_pull_requests.api_request(root + path, agent="direct-merge-guard")
    with urllib.request.urlopen(request, timeout=MERGE_READ_TIMEOUT_S) as response:
        answer: object = json.load(response)
    return answer


def member(value: object, key: str) -> object:
    """`value[key]`, where `value` is a JSON object, or `TypeError` where it is not one."""
    if not isinstance(value, dict):
        raise TypeError(f"GitHub's answer holds no object where {key!r} was looked for")
    return value[key]


def own_repository() -> str | None:
    """`owner/name` of the GitHub repository this hook is checked into, or None.

    It is read by `open_pull_requests.repo_slug`, from the `origin` of the
    checkout that holds this hook (`PL-L08H`). None means the hook cannot tell
    which merges are its own: `origin` names no GitHub repository, or the read
    failed. The caller then judges every merge.
    """
    try:
        import open_pull_requests

        return open_pull_requests.repo_slug()
    except Exception:
        return None


def is_merge(tool: str, arguments: object) -> bool:
    """Whether a call of `tool` with `arguments` merges, by its name or its `method` (`PL-NZJG`)."""
    name = tool.rsplit("__", 1)[-1]
    method = arguments.get("method") if isinstance(arguments, dict) else None
    return name not in NOT_A_MERGE and (
        "merge" in name.lower() or (isinstance(method, str) and method.lower() == "merge")
    )


def judge(arguments: object) -> None:
    """Raise `Refused` unless the merge `arguments` name may go through."""
    try:
        owner, repo = str(member(arguments, "owner")), str(member(arguments, "repo"))
        pull_number = member(arguments, "pullNumber")
        if not isinstance(pull_number, int | float | str):
            raise TypeError("the call's pullNumber is not a number")
        number = int(pull_number)
    except (KeyError, TypeError, ValueError) as error:
        raise Refused(
            "unreadable-call",
            "the call names no pull request this hook can read, so it cannot ask GitHub "
            "whether the base branch holds the merge to its required checks.",
        ) from error

    # A merge in another repository cannot leave a stale branch on the `main` of
    # this one. GitHub treats owner and repository names without regard to case.
    own = own_repository()
    if own is not None and (owner + "/" + repo).lower() != own.lower():
        return

    repository = (
        "/repos/" + urllib.parse.quote(owner, safe="") + "/" + urllib.parse.quote(repo, safe="")
    )
    named = "`" + owner + "/" + repo + "#" + str(number) + "`"
    try:
        base = member(member(record(repository + "/pulls/" + str(number)), "base"), "ref")
        if not isinstance(base, str):
            raise TypeError("GitHub's answer names no base branch")
        branch = record(repository + "/branches/" + urllib.parse.quote(base, safe=""))
        protection = member(branch, "protection")
        if not isinstance(protection, dict):
            raise TypeError("GitHub's answer holds no branch protection")
        checks = protection.get("required_status_checks") or {}
        if not isinstance(checks, dict):
            raise TypeError("GitHub's answer holds no required checks")
        level = checks.get("enforcement_level")
    except (OSError, LookupError, TypeError, ValueError, AttributeError) as error:
        raise Refused(
            "no-answer",
            "GitHub did not answer whether the base branch of " + named + " holds an admin to "
            "its required checks (" + str(error) + "), and a session merges as the owner, an "
            "admin.",
        ) from error
    if level != "everyone":
        raise Refused(
            "admins-unbound",
            "the GitHub record for `"
            + base
            + "` reads `enforcement_level: "
            + str(level)
            + "`, not `everyone`, so its required checks and up-to-date rule do not bind an "
            "admin, and a session merges as the owner, an admin: a merge landing between a read "
            "and this call would put a stale branch on `" + base + "`, the merge skew "
            "`PL-6MW8` made `main` refuse. Turning on **Do not allow bypassing the above "
            "settings** in that branch protection rule is what lets a session merge it.",
        )


def decide(payload: str) -> str:
    """The refusal of the merge in `payload` that GitHub would not hold to its checks, or ""."""
    try:
        data = json.loads(payload)
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    # The name of the tool, from the documented payload read as JSON: a commit
    # message quoting `"tool_name"` cannot supply one, and a name laid out on the
    # line after its key is still the name, where a sed run a line at a time read
    # none and refused the call of another tool (`PL-CXK6`).
    tool = data.get("tool_name")
    if not isinstance(tool, str) or not tool:
        # No tool to judge. Every call taken for a merge contains "merge", so
        # refuse only a call whose text contains it, in any case.
        if "merge" in payload.lower():
            return hook_input.deny("direct-merge-guard", "no-tool", NO_TOOL_REFUSAL, payload)
        return ""
    arguments = data.get("tool_input")
    if not is_merge(tool, arguments):
        return ""
    try:
        judge(arguments)
    except Refused as refusal:
        reason = "Refused: " + refusal.why + "\n\n" + ROUTE
        return hook_input.deny("direct-merge-guard", refusal.rule, reason, payload)
    return ""
