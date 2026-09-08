"""Refuse a branch that carries work no item id names.

`docket flight`, `show`, `next`, `concurrent` and the session-start digest all
answer "is anybody already on this?" by matching a `PL-` id - in a branch name
or at the front of a commit subject. Work that was never filed has no id, so
every one of those returns a clean answer for it: correctly, and uselessly.

That is most of what actually collides. The duplicated work this project sees
is repository housekeeping rather than queue items - resolving a merge,
clearing a stale ref, a docs sweep, a lint fix, recovering a stranded item.
None of it is filed, all of it is obvious enough that two sessions recommend it
in the same hour, and it stays invisible to the guards even after both sessions
have pushed (`PL-CP74`).

The rule here is the narrow, exact half of that: **a branch ahead of the
default base must carry an item id somewhere a guard reads.** Not every commit
- one is enough to make the branch visible, and demanding more would put this
tool in the middle of a judgment it has no business making (below). The
remedy is two commands, and the failure prints them.

**It reads the ids with `docket`'s own parsers rather than its own.** A check
that matched ids more loosely than `branches_in_flight` does would certify a
branch as visible that `docket flight` still cannot see, which is worse than
no check at all: the guarantee would be void while the gate stayed green. So
`BRANCH_ID_RE` and `leading_ids` are imported from the module under protection,
and a change to either moves both together.

**Deliberately not decided here: how small is too small to file.** A rule
demanding an item for a one-line typo fix converts the queue into a log, which
is worse than the collisions it prevents - so the question this asks is not
"should this change have been an item" but "can any guard see this branch at
all", which is answerable from the tree and has one right answer. A branch
doing something too small to file passes the moment it is committed under any
id the session is already working, which is what such a change usually rides
along with anyway.

One exemption, and it is exact: a release commit. `Release v0.3.6: ...` is what
`make release` produces, it closes no item so `pr_title_check.py` owes it no id
either, and its provenance is the version table and the tag rather than an
entry in the queue.

**It binds the agent namespace and nothing else (`PL-8P6D`).** Everything above
is an argument about agent sessions: they are what `docket flight` serves, and
an id is what they have. A contributor has no queue, no id and no `bin/docket`,
so demanding one buys nothing and the remedy printed below asks them for a tool
they cannot run. This refused `#394` - the project owner's own two-line README
edit from the GitHub web UI, on branch `stuthedew-patch-1` - nine seconds into
the required job, which is what the first drive-by pull request would have met.

So a branch owes an id only when its name is in the namespace every session's
branch sits in: `claude/`, which the web harness gives every session it starts
and which `CLAUDE.md` asks a session naming its own branch to use. The rule
lives here rather than in an `if:` on the CI step so that `make check` and CI
answer identically, which is the same requirement `branch_name` reads
`GITHUB_HEAD_REF` to meet.

**What that gives up, stated rather than left to be discovered.** An agent
branch named outside the namespace is now unchecked, and one exists:
`origin/chore/docket-record-452` is `PL-CP74`'s unfiled-housekeeping shape
exactly. Its two siblings, `origin/chore/pl-vzl0-promote` and
`origin/chore/pl-483k-third-observation`, carry an id in the name and pass
either way. The trade is one demonstrated catch for a route a human can walk,
and the convention that closes it again is one `CLAUDE.md` already states. A
name that cannot be read at all stays in scope, because that direction
preserves the old verdict and no contributor reaches it: `GITHUB_HEAD_REF` is
set on every `pull_request` event, fork or not.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.vcs import BRANCH_ID_RE, default_base, leading_ids  # noqa: E402

#: What `make release` writes and `git tag -a vX.Y.Z` marks. Anchored, so a
#: subject that merely mentions a release is not one.
RELEASE_RE = re.compile(r"^Release\s+v\d+\.\d+\.\d+")

#: The namespace an agent session's branch sits in, and the whole of what this
#: check binds. Not `docket`'s to know - it matches ids, and has no concept of
#: who made a branch - so unlike `BRANCH_ID_RE` this is declared locally.
AGENT_BRANCH_PREFIX = "claude/"

#: `%p` is empty only for a commit whose parents this checkout does not hold.
#: A walk that emits one ran off the end of a truncated history instead of
#: stopping against the base, so nothing it reported is proven - see
#: `_attribution` for what that means for the verdict.
COMMIT_FORMAT = "--format=%p\x1f%s"


def _git(args: list[str]) -> str:
    """Run git, returning empty output rather than raising.

    Every failure mode collapses to "nothing known", which this tool reads as
    a checkout it cannot answer about rather than as a branch that failed.
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def branch_name() -> str:
    """The name a guard would read this branch under.

    `GITHUB_HEAD_REF` first, because on a `pull_request` event the checkout is
    a detached merge commit and `rev-parse` answers `HEAD` - so without it CI
    would fail a branch whose *name* carries the id, where `make check` on the
    same commits passed. The two must agree or the check reads as flaky.
    """
    head_ref = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if head_ref:
        return head_ref
    return _git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()


def _subjects(base: str) -> tuple[list[str], bool]:
    """The subjects this branch adds to `base`, and whether the walk was sound.

    A walk must stop because `base` accounted for what came next, never because
    the checkout ran out of history. In a truncated clone `base`'s own history
    ends at a grafted commit, so everything below it goes unexcluded and the
    default branch's commits are reported as this branch's work - which would
    pass this check on ids that belong to somebody else's merged items.
    """
    sound = True
    subjects: list[str] = []
    for line in _git(["log", COMMIT_FORMAT, f"{base}..HEAD", "--"]).splitlines():
        parents, _, subject = line.partition("\x1f")
        if not parents.strip():
            sound = False
        subjects.append(subject)
    return subjects, sound


def in_agent_namespace(name: str) -> bool:
    """Whether this branch is one of the agent sessions this rule binds.

    A name that could not be read answers True: it is the direction that keeps
    the old verdict, and no contributor's pull request lands here, because
    `branch_name` reads `GITHUB_HEAD_REF` and CI sets it on every
    `pull_request` event. Compared lowercased, which can only ever widen the
    scope - git branch names are case-sensitive, so `Claude/x` is a distinct
    name that no harness produces and no contributor would choose.
    """
    if not name or name == "HEAD":
        return True
    return name.lower().startswith(AGENT_BRANCH_PREFIX)


def attribution(name: str, subjects: list[str]) -> list[str]:
    """What names this branch's work, in the forms a guard actually reads."""
    found: list[str] = []
    match = BRANCH_ID_RE.search(name)
    if match is not None:
        found.append(f"branch name carries {match.group(1).upper()}")
    for subject in subjects:
        ids = leading_ids(subject)
        if ids:
            found.append(f"a commit subject leads with {', '.join(ids)}")
            break
    for subject in subjects:
        if RELEASE_RE.match(subject):
            found.append("a release commit, which owes no id")
            break
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=None, help="ref to compare against")
    args = parser.parse_args()

    base = args.base or default_base(ROOT, runner=lambda argv, _root: _git(argv))
    subjects, sound = _subjects(base)
    if not subjects:
        print(f"branch-id: nothing ahead of {base}; no id is owed")
        return 0
    if not sound:
        print(
            f"branch-id: this checkout cannot walk {base}..HEAD to its end; not checked. "
            f"`git fetch --unshallow origin` makes it answerable."
        )
        return 0

    name = branch_name()
    found = attribution(name, subjects)
    if found:
        print(f"branch-id: visible in flight - {found[0]}")
        return 0
    if not in_agent_namespace(name):
        print(f"branch-id: {name} is outside `{AGENT_BRANCH_PREFIX}`; no id is owed")
        return 0

    print(
        f"branch-id: {len(subjects)} commit(s) ahead of {base}, and no item id names any of "
        f"them.\n"
        f"  branch: {name or '(detached)'}\n"
        f"  Only a branch in the `{AGENT_BRANCH_PREFIX}` namespace owes one; a contributor's "
        f"does not.\n"
        f"  Every in-flight guard - `docket flight`, `show`, `next`, `concurrent`, the "
        f"session-start digest - matches an id in a branch name or at the front of a commit "
        f"subject, so this work is invisible to all of them and to the next session that "
        f"asks.\n"
        f"  File it, then put the id at the front of a commit subject:\n"
        f"    bin/docket new '<what this work is>'\n"
        f"    git commit --amend -m '<PL-XXXX>: <what this commit does>'",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
