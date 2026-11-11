"""Fail where GitHub would let through an action that a session must never take (`PL-39Y1`).

A session can delete a branch, force another history onto one, or merge a
pull request, and none of those can be undone from the session. Four fixes
put a guard in the session, and each guard read what the session typed. A
hook can read nothing else, so each time another spelling of the same action
passed: `PL-61FT`, `PL-1ZZ0`, `PL-95BJ` and the guard leads in `PL-VZ57`.
`GUARD_ESCAPES` lists those spellings.

**The refusal belongs where the action lands.** A cloud session acts on GitHub
as the owner's account, an admin, through Anthropic's proxy. The proxy keeps
the credential, and the Claude GitHub App may not change a ruleset or a branch
protection rule, so a session cannot lift a rule the owner sets
(https://code.claude.com/docs/en/github-actions § "GitHub App permissions",
read 2026-11-11). GitHub then refuses the action whichever client sends it
and however the command is spelt. The session's hooks stay as early warnings.

**So this check reads GitHub's rules and fails where one is missing.**
`GITHUB_RULES` names each rule, the action it refuses and the setting that
restores it. The rules live in repository settings, where an edit leaves no
commit, and a guard that trusted them unread would keep passing after one was
switched off. `required_checks_check.py` reads the required status checks the
same way, and this runs beside it as a step of the `checks` job.

**What GitHub is asked**, each without a credential on a public repository
(measured 2026-11-11):

- `GET /repos/{repo}/branches/{branch}` for whether the default branch's
  required checks bind an admin (`enforcement_level: everyone`).
- `GET /repos/{repo}/rules/branches/{branch}` for the active rules on the
  default branch and on `PROBE`, a branch name no ruleset names. The rules on
  `PROBE` are the rules every other branch gets.
- `GET /repos/{repo}/rulesets?targets=tag` and each ruleset, for a rule on
  release tags, and each ruleset relied on above for its bypass list.

**What it cannot check, and says so.**

- Anthropic's proxy refuses a branch deletion and a tag sent by `git push`
  (https://code.claude.com/docs/en/cloud-environments § "GitHub proxy", read
  2026-11-11; `docs/worker.md` § "Ref operations a session cannot perform"
  measured the `HTTP 403`). No endpoint reports that, so an escape the proxy
  refuses names the proxy and is not checked here.
- A branch deleted by a direct request to GitHub's API is refused by nothing.
  The rule that would refuse it, "Restrict deletions" on every branch, also
  stops GitHub deleting a merged branch and stops `tools/branch_sweep.py`.
  `PL-39Y1` records why it was left out.
- GitHub shows a ruleset's bypass list only to a reader who may edit the
  ruleset. Where the list is not shown, the check says which list went unread
  and does not fail on it.

Run it by hand with `python3 tools/github_refusals_check.py`. It is not part
of `make check`, which runs offline.
"""

from __future__ import annotations

import argparse
import fnmatch
import sys
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "subprojects" / "docket" / "src"))

from docket.vcs import default_branch, github_token

# The reader of GitHub's settings that this check shares.
import required_checks_check
from open_pull_requests import GITHUB_API, repo_slug

#: A branch name that no ruleset names, so its rules are those of every branch.
PROBE = "claude/a-branch-no-ruleset-names"
#: A release tag as `tools/tag_release.py` names one.
RELEASE_TAG = "refs/tags/v0.0.0"
#: The bypass actors a session holds, because it acts as the owner's account.
ROLES = frozenset({"RepositoryRole", "OrganizationAdmin", "Team"})

RULESETS = "Settings > Rules > Rulesets"


@dataclass(frozen=True)
class Settings:
    """The rules GitHub holds, as far as they were read."""

    #: The types of the active rules on the default branch.
    default_rules: frozenset[str]
    #: Whom the default branch's required checks bind: `everyone` includes an admin.
    enforcement: str | None
    #: The types of the active rules on a branch no ruleset names.
    other_rules: frozenset[str]
    #: The types of the active rules on a release tag.
    tag_rules: frozenset[str]
    #: Each role on the bypass list of a ruleset relied on, as `ruleset: type id`.
    bypass: tuple[str, ...]
    #: What GitHub did not show.
    unread: tuple[str, ...]


@dataclass(frozen=True)
class Refusal:
    """One rule GitHub must hold: what it refuses, and the setting that restores it."""

    key: str
    #: What a session can do while the rule is missing.
    action: str
    holds: Callable[[Settings], bool]
    #: What the owner sets, and where.
    setting: str


GITHUB_RULES = (
    Refusal(
        "default-history",
        "a forced push can replace the history of `main`",
        lambda found: "non_fast_forward" in found.default_rules,
        f'{RULESETS}: a ruleset on the default branch with "Block force pushes".',
    ),
    Refusal(
        "default-deletion",
        "`main` can be deleted",
        lambda found: "deletion" in found.default_rules,
        f'{RULESETS}: a ruleset on the default branch with "Restrict deletions".',
    ),
    Refusal(
        "default-pull-request",
        "a push can land on `main` without a pull request",
        lambda found: "pull_request" in found.default_rules,
        f'{RULESETS}: a ruleset on the default branch with "Require a pull request before '
        'merging".',
    ),
    Refusal(
        "default-binds-admins",
        "a merge into `main` can skip its required checks, because they do not bind an admin "
        "and a session merges as the owner",
        lambda found: found.enforcement == "everyone",
        'Settings > Branches > the rule for `main`: tick "Do not allow bypassing the above '
        'settings".',
    ),
    Refusal(
        "branch-history",
        "a forced push can replace the history of a branch other than `main`",
        lambda found: "non_fast_forward" in found.other_rules,
        f"{RULESETS} > New ruleset > New branch ruleset: Enforcement status Active, an empty "
        'Bypass list, every branch as the target, "Block force pushes" ticked and "Restrict '
        'deletions" unticked.',
    ),
    Refusal(
        "tag-history",
        "a release tag can be deleted or moved to another commit",
        lambda found: {"deletion", "non_fast_forward"} <= found.tag_rules,
        f"{RULESETS} > New ruleset > New tag ruleset: Enforcement status Active, an empty "
        'Bypass list, the target pattern `v*`, and "Restrict deletions" and "Block force '
        'pushes" both ticked.',
    ),
    Refusal(
        "no-bypass",
        "a ruleset exempts a role, and a session holds the owner's roles",
        lambda found: not found.bypass,
        f"{RULESETS}: remove each role from the Bypass list of the ruleset named below.",
    ),
)

PROXY = (
    "Anthropic's proxy refuses a branch deletion sent by `git push` "
    "(https://code.claude.com/docs/en/cloud-environments, read 2026-11-11)"
)


@dataclass(frozen=True)
class Escape:
    """One spelling that passed a session guard, and what refuses the action now."""

    spelling: str
    #: The item that recorded it.
    item: str
    #: The keys of the `GITHUB_RULES` that refuse it at GitHub.
    rules: tuple[str, ...] = ()
    #: Why the proxy refuses it, where no rule is needed.
    proxy: str = ""
    #: Why nothing refuses it, where that is so.
    open: str = ""


MERGE_RULES = ("default-pull-request", "default-binds-admins")
GUARD_ESCAPES = (
    Escape("git push --no-verify origin --delete <branch>", "PL-95BJ", proxy=PROXY),
    Escape("git -c core.hooksPath=/dev/null push origin --delete <branch>", "PL-95BJ", proxy=PROXY),
    Escape("CLAUDECODE= git push origin --delete <branch>", "PL-39Y1", proxy=PROXY),
    Escape(
        "CLAUDECODE= git fetch --prune",
        "PL-39Y1",
        open="it deletes refs in the session's own checkout, which GitHub never sees; "
        "`.claude/hooks/git/reference-transaction` warns of it",
    ),
    Escape("bash -c 'gh pr merge <number> --squash'", "PL-VZ57", rules=MERGE_RULES),
    Escape("curl -X PUT .../pulls/<number>/merge", "PL-VZ57", rules=MERGE_RULES),
    Escape(
        "curl -X DELETE .../git/refs/heads/<branch>",
        "PL-39Y1",
        open='"Restrict deletions" on every branch would also stop GitHub deleting a merged '
        "branch and stop the branch sweep",
    ),
    Escape(
        "curl -X PATCH .../git/refs/heads/<branch> -d '{\"force\": true}'",
        "PL-39Y1",
        rules=("default-history", "branch-history"),
    ),
    Escape(
        "git push --force origin <branch>", "PL-VZ57", rules=("default-history", "branch-history")
    ),
    Escape(
        "curl -X POST .../git/refs with a release tag's name, after deleting it",
        "PL-39Y1",
        rules=("tag-history",),
    ),
    Escape(
        "enable_pr_auto_merge on a pull request that `bin/docket arm` holds",
        "PL-VZ57",
        open="the `merge-hold` check fails on such a pull request, and `main` does not "
        "require that check yet (`PL-KH7Y`)",
    ),
)


def _types(rules: object) -> frozenset[str]:
    """The `type` of each rule in a list GitHub returned."""
    if not isinstance(rules, list):
        return frozenset()
    return frozenset(
        rule["type"]
        for rule in rules
        if isinstance(rule, dict) and isinstance(rule.get("type"), str)
    )


def _covers(ruleset: dict[str, object], ref: str) -> bool:
    """Whether an active ruleset's conditions take in `ref`."""
    if ruleset.get("enforcement") != "active":
        return False
    conditions = ruleset.get("conditions")
    names = conditions.get("ref_name") if isinstance(conditions, dict) else None
    if not isinstance(names, dict):
        return False

    def matches(patterns: object) -> bool:
        return isinstance(patterns, list) and any(
            pattern == "~ALL" or (isinstance(pattern, str) and fnmatch.fnmatchcase(ref, pattern))
            for pattern in patterns
        )

    return matches(names.get("include")) and not matches(names.get("exclude"))


def read(repo: str, branch: str, token: str | None) -> Settings:
    """The rules GitHub holds for `repo`, whose default branch is `branch`.

    Raises `RuntimeError` where GitHub could not be read.
    """
    base = f"{GITHUB_API}/repos/{repo}"

    def get(path: str) -> object:
        return required_checks_check._get(base + path, token)

    def rules_on(name: str) -> object:
        return get("/rules/branches/" + urllib.parse.quote(name, safe=""))

    branch_doc = get("/branches/" + urllib.parse.quote(branch, safe=""))
    protection = branch_doc.get("protection") if isinstance(branch_doc, dict) else None
    checks = protection.get("required_status_checks") if isinstance(protection, dict) else None
    enforcement = checks.get("enforcement_level") if isinstance(checks, dict) else None

    on_default, on_other = rules_on(branch), rules_on(PROBE)
    relied: dict[int, dict[str, object]] = {}
    for rules in (on_default, on_other):
        for rule in rules if isinstance(rules, list) else []:
            number = rule.get("ruleset_id") if isinstance(rule, dict) else None
            if isinstance(number, int) and number not in relied:
                found = get(f"/rulesets/{number}")
                relied[number] = found if isinstance(found, dict) else {}

    tag_rules: set[str] = set()
    listed = get("/rulesets?targets=tag")
    for entry in listed if isinstance(listed, list) else []:
        number = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(number, int) or entry.get("enforcement") != "active":
            continue
        ruleset = get(f"/rulesets/{number}")
        if isinstance(ruleset, dict) and _covers(ruleset, RELEASE_TAG):
            tag_rules |= _types(ruleset.get("rules"))
            relied[number] = ruleset

    bypass: list[str] = []
    unread: list[str] = []
    for number, ruleset in sorted(relied.items()):
        name = ruleset.get("name") or number
        actors = ruleset.get("bypass_actors")
        if not isinstance(actors, list):
            unread.append(f"the bypass list of the ruleset `{name}`")
            continue
        bypass.extend(
            f"{name}: {actor['actor_type']} {actor.get('actor_id')}"
            for actor in actors
            if isinstance(actor, dict) and actor.get("actor_type") in ROLES
        )
    return Settings(
        default_rules=_types(on_default),
        enforcement=enforcement if isinstance(enforcement, str) else None,
        other_rules=_types(on_other),
        tag_rules=frozenset(tag_rules),
        bypass=tuple(bypass),
        unread=tuple(unread),
    )


def missing(found: Settings) -> list[Refusal]:
    """Each rule in `GITHUB_RULES` that `found` does not hold."""
    return [refusal for refusal in GITHUB_RULES if not refusal.holds(found)]


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    required_checks_check.add_repo_argument(parser)
    parser.add_argument(
        "--branch", default=None, help="the default branch; read from the checkout where not given"
    )
    args = parser.parse_args(argv)
    repo = args.repo or repo_slug(root)
    if repo is None:
        print("github-refusals: no --repo given, and origin names no GitHub repository")
        return 1
    branch = args.branch or default_branch(root)

    try:
        found = read(repo, branch, github_token())
    except RuntimeError as exc:
        print(f"github-refusals: {exc}")
        print(
            "github-refusals: GitHub's rules could not be read, so nothing was checked. This "
            "is not a clean result - re-run it."
        )
        return 1

    print(f"github-refusals: {repo}, default branch {branch}")
    for what in found.unread:
        print(f"  not shown to this reader, so not checked: {what}")
    absent = missing(found)
    for refusal in absent:
        print(f"github-refusals: FAIL - {refusal.action}")
        print(f"  The owner's setting: {refusal.setting}")
        for role in found.bypass if refusal.key == "no-bypass" else ():
            print(f"  On a bypass list: {role}")
        for escape in GUARD_ESCAPES:
            if refusal.key in escape.rules:
                print(f"  Passed a session guard ({escape.item}): {escape.spelling}")
    for escape in GUARD_ESCAPES:
        if escape.open:
            print(f"  refused by nothing: {escape.spelling} - {escape.open}")
    if absent:
        print(
            "github-refusals: a session cannot change these settings, and no session guard "
            "stands in for them (`PL-39Y1`)."
        )
        return 1
    print(f"github-refusals: OK - GitHub holds all {len(GITHUB_RULES)} rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
