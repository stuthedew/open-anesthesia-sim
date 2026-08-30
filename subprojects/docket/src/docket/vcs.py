"""What git already knows about work in progress.

Whether an item is being worked on right now is a fact the repository
already holds: a branch named after it exists. Storing that in the item file
instead would mean a session has to remember to write it when it starts and
to clear it when it stops - and a session that crashes, or that is simply
abandoned, leaves the item marked in-progress forever with nobody able to
tell whether that is true.

So it is derived, never stored. A branch that is gone means work that is not
in flight, which is exactly right: branches are deleted when their pull
request merges.

The same holds for finished work: which pull requests have reached the
default branch is a fact the repository holds, so an item's recorded pull
request can be checked against it rather than trusted.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# Branches whose tip is already contained in one of these are finished, not in
# flight. Checked against whichever exists, so a repository using a different
# default branch name still gets the filtering.
DEFAULT_BRANCHES = ("origin/main", "origin/master", "main", "master")

BRANCH_ID_RE = re.compile(
    r"(?:^|[/_-])(pl-(?:\d{3}|[0-9bcdfghjklmnpqrstvwxyz]{4}))(?:$|[/_-])", re.I
)


@dataclass(frozen=True)
class Branch:
    """One ref that may be carrying an item's work."""

    name: str
    item_id: str


Runner = Callable[[list[str], Path], str]


def _run_git(args: list[str], root: Path) -> str:
    """Run git, returning empty output rather than raising.

    A checkout without git, without a remote, or without network is a normal
    condition for this tool - the session-start digest must not fail because
    of it - so every failure mode collapses to "nothing known about branches".
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def branches_in_flight(
    root: Path, *, include_remote: bool = True, runner: Runner | None = None
) -> list[Branch]:
    """Every branch whose name carries an item id and whose work is unfinished.

    Refs are read from what is already fetched, so the answer can be stale by
    exactly one fetch. That is an acceptable error for an advisory and an
    unacceptable one for a lock, which is why this reports rather than blocks.

    Merged branches are excluded, and that exclusion matters more than it
    looks: deleting a branch on the remote does not remove the local
    remote-tracking ref until someone prunes, so without this every item ever
    shipped goes on being reported as in-flight work and the signal becomes
    noise within a few releases.
    """
    run = runner or _run_git
    args = ["for-each-ref", "--format=%(refname:short)", "refs/heads"]
    if include_remote:
        args.append("refs/remotes")

    merged: set[str] = set()
    for base in DEFAULT_BRANCHES:
        output = run([*args, f"--merged={base}"], root)
        if output:
            merged |= {name.strip() for name in output.splitlines() if name.strip()}
            break

    found: dict[str, Branch] = {}
    for name in run(args, root).splitlines():
        name = name.strip()
        if not name or name in merged:
            continue
        match = BRANCH_ID_RE.search(name)
        if match is None:
            continue
        item_id = match.group(1).upper()
        # A local branch and its remote tracking ref are one piece of work.
        found.setdefault(item_id, Branch(name=name, item_id=item_id))
    return sorted(found.values(), key=lambda b: b.item_id)


def default_base(root: Path, *, runner: Runner | None = None) -> str:
    """The ref a branch should be compared against, preferring the remote's.

    `main` names the *local* branch, which in a fresh clone - the normal state
    for an agent session, which starts from one - can sit many commits behind
    what everyone else has pushed. A diff taken against it reports every file
    that landed in between as this branch's own work: verifying PL-VP7N that
    way named 20 paths outside the item's commission where the true answer was
    4, the other 16 being item files other sessions had merged. So the remote
    ref is preferred wherever it resolves, because that is what the branch
    actually forked from.

    Falls back to `main` when nothing resolves, which is a repository this
    tool cannot answer about either way; `verify` then reports finding no
    change rather than reporting a clean scope.
    """
    run = runner or _run_git
    for candidate in DEFAULT_BRANCHES:
        if run(["rev-parse", "--verify", "--quiet", candidate], root).strip():
            return candidate
    return "main"


def behind_remote(root: Path, base: str, *, runner: Runner | None = None) -> int | None:
    """How many commits `base` trails its own remote-tracking branch.

    `None` when the question does not arise - `base` is already a remote ref,
    has no counterpart on `origin`, or the count cannot be read - and `0` when
    it is current. The distinction is worth keeping after `default_base` moved
    the default to the remote ref, because `--base main` can still be passed
    by hand, and a stale answer that looks clean is the failure being guarded
    against rather than the flag that produced it.
    """
    run = runner or _run_git
    if "/" in base:
        return None
    remote = f"origin/{base}"
    if not run(["rev-parse", "--verify", "--quiet", remote], root).strip():
        return None
    counts = run(["rev-list", "--count", f"{base}..{remote}"], root).strip()
    return int(counts) if counts.isdigit() else None


def tags(root: Path, *, runner: Runner | None = None) -> frozenset[str]:
    """Every tag name the repository holds.

    Empty for a checkout with no tags, no git, or no repository at all - the
    same collapse every other read here makes. What that emptiness *means* is
    decided by the caller: `release.is_untagged` reads it as "this project does
    not tag" rather than as "every release is untagged", because a tool that
    started refusing releases in a project that never tagged would be teaching
    a practice rather than holding one.
    """
    run = runner or _run_git
    return frozenset(
        line.strip() for line in run(["tag", "--list"], root).splitlines() if line.strip()
    )


def in_flight_ids(root: Path, *, runner: Runner | None = None) -> set[str]:
    return {branch.item_id for branch in branches_in_flight(root, runner=runner)}


# A pull request number as it reaches the default branch. GitHub writes one of
# two subjects depending on how the merge was made: `Merge pull request #71
# from owner/branch` for a merge commit, and `Title (#71)` for a squash. Both
# are matched, because a repository that switches from one to the other keeps
# the history it already has.
PR_SUBJECT_RE = re.compile(r"^Merge pull request #(\d+)\b|\(#(\d+)\)\s*$")


def merged_pull_requests(root: Path, *, runner: Runner | None = None) -> frozenset[int] | None:
    """Every pull request number named by a commit on the default branch.

    `None` means the question could not be answered, and it is the reason this
    function exists rather than a bare `git log` at the call site. A shallow
    clone answers `git log` confidently and wrongly: the commits it is missing
    are exactly the old ones, so provenance recorded years ago reads as
    provenance that never landed. The container an agent session runs in is
    normally shallow, so that is the common case rather than the exotic one.

    So the only state that permits an answer is a repository that says outright
    it is not shallow. Anything else - a truncated clone, no git, no
    repository, a git too old to have `--is-shallow-repository` - collapses to
    `None`, and the caller reports nothing rather than reporting every item as
    broken.
    """
    run = runner or _run_git
    if run(["rev-parse", "--is-shallow-repository"], root).strip() != "false":
        return None
    subjects = run(["log", "--format=%s", default_base(root, runner=run)], root)
    if not subjects.strip():
        return None
    found: set[int] = set()
    for subject in subjects.splitlines():
        match = PR_SUBJECT_RE.search(subject.strip())
        if match is not None:
            found.add(int(match.group(1) or match.group(2)))
    return frozenset(found)
