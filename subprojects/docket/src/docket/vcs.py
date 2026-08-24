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
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
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


def in_flight_ids(root: Path, *, runner: Runner | None = None) -> set[str]:
    return {branch.item_id for branch in branches_in_flight(root, runner=runner)}
