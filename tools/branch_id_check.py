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
that matched ids more loosely than `claims.holdings` does would certify a
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

**Since `PL-J9S0` it reads the claim record as well, for two refusals more**
(`PL-MB2W` § "Design round, 2026-09-24"). Who holds an item is a `Claim:`
trailer a session commits on its own branch, and `claims.holdings` is the one
reader of it - so this asks that reader rather than parsing a trailer itself,
for the reason the ids above come from `docket`'s own parsers.

- *A work branch that claims nothing is refused.* Work is a non-merge commit
  changing a path outside the queue - the items, the roadmap, the working notes
  and the pull requests' body records, the records a queue workflow writes
  (`claims.queue_records`). The question is per branch, never per id: a
  capture or a triage pass, whose ids lead its subjects, is never pushed into
  claiming them (`PL-3CTW`). A claim counts in any state. A branch releases
  its claim by closing its item in its own copy, so "no live claim" would
  refuse every finished pull request, and the session this exists for is the
  one that never claimed. A branch named for its item holds it by the name
  (`PL-TZ3R`), and one whose work is already on the base owes nothing.
  The question is `claims.claims_nothing`, not a copy of it here: `flight`'s
  `unclaimed:` row asks the same function of every branch it walks, so the
  refusal and the count the design's 1-in-20 threshold reads cannot disagree
  (`PL-FFR0`).
- *A claim that orders behind another live claim is refused* - the fence the
  claim order needs, since nothing stops a later claim being written.

The fence reads every pushed head, and CI's checkout holds them all: checked
on 2026-09-24 against `quality` run 35969686133, whose fetch was
`+refs/heads/*:refs/remotes/origin/*` into a fresh clone. Where the reader
could not answer - git below its floor, this branch's history unreadable - both
refusals go unasked and the output says so, as the walk above does.

`--hint PATH` is the first-edit hook's half of the same question: the line to
add before an edit to PATH, where PATH is work outside the queue and the
branch claims nothing.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.claims import (  # noqa: E402
    AGENT_BRANCH_PREFIX,
    LIVE,
    Hold,
    Holdings,
    claims_bound,
    claims_nothing,
    holdings,
    in_queue,
    queue_records,
)
from docket.config import Config  # noqa: E402
from docket.config import load as load_config  # noqa: E402
from docket.vcs import (  # noqa: E402
    BRANCH_ID_RE,
    DEFAULT_BRANCHES,
    SILENT,
    _head_name,
    _remotes,
    answered,
    default_base,
    leading_ids,
    resolved,
)

#: What `make release` writes and `git tag -a vX.Y.Z` marks. Anchored, so a
#: subject that merely mentions a release is not one.
RELEASE_RE = re.compile(r"^Release\s+v\d+\.\d+\.\d+")

#: `%p` is empty only for a commit whose parents this checkout does not hold.
#: A walk that emits one ran off the end of a truncated history instead of
#: stopping against the base, so nothing it reported is proven - see
#: `_attribution` for what that means for the verdict.
COMMIT_FORMAT = "--format=%p\x1f%s"

#: The line the first-edit hook adds and the head of the refusal: one remedy,
#: so one spelling.
CLAIMS_NOTHING = "this branch claims nothing: `bin/docket claim <id>`"

#: `--hint`'s exit status where PATH is not work outside the queue - an item
#: file, or a file outside this checkout - so nothing was asked and the hook
#: asks again at the next edit. Not 1, which a Python failure also exits with:
#: a check that cannot run is asked once, not before every edit.
NOT_ASKED = 3


def _git(args: list[str]) -> str:
    """Run git, returning its answer, or `SILENT` where it gave none.

    The classification is `docket.vcs._run_git`'s, because `default_base` reads
    it: `rev-parse --verify` exits 1 to say a candidate is not there, which is
    an answer, and anything else that is not 0 is git saying nothing. The walk
    has no "no" to give - `git log` exits 128 on a revision it cannot read - so
    `_subjects` asks `answered` rather than taking the empty string for a
    branch with nothing on it.

    Every failure used to collapse to the empty string here, and a base that
    resolved followed by a walk that did not printed "nothing ahead of <base>;
    no id is owed" and exited 0. `--base no-such-ref` was enough (`PL-1PBV`).
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return SILENT
    if result.returncode == 0:
        return result.stdout
    return "" if result.returncode == 1 else SILENT


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


def _runner(argv: list[str], _root: Path) -> str:
    """`_git` in the shape `docket`'s readers take a runner in."""
    return _git(argv)


def _subjects(base: str) -> tuple[list[str], bool] | None:
    """The subjects this branch adds to `base`, and whether the walk was sound.

    `None` where git did not answer the walk at all, which is not a branch
    with nothing ahead of `base`.

    A walk must stop because `base` accounted for what came next, never because
    the checkout ran out of history. In a truncated clone `base`'s own history
    ends at a grafted commit, so everything below it goes unexcluded and the
    default branch's commits are reported as this branch's work - which would
    pass this check on ids that belong to somebody else's merged items.
    """
    log = _git(["log", COMMIT_FORMAT, f"{base}..HEAD", "--"])
    if not answered(log):
        return None
    sound = True
    subjects: list[str] = []
    for line in log.splitlines():
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


def ahead_of(hold: Hold, report: Holdings) -> Hold | None:
    """The live claim ordering first on `hold`'s item, where that is another branch's."""
    if hold.state != LIVE:
        return None
    first = next(iter(report.order(hold.key)), None)
    return None if first is None or first.ref == hold.ref else first


def _when(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _behind(hold: Hold, first: Hold, name: str, remotes: frozenset[str]) -> str:
    holder = _head_name(first.ref, remotes)
    session = f", session {first.session}" if first.session else ""
    return (
        f"branch-id: {hold.key} is claimed first on {holder}, and this branch's claim orders "
        f"behind it.\n"
        f"  first: {holder}, claimed {_when(first.since)}{session}\n"
        f"  here:  {name}, claimed {_when(hold.since)}\n"
        f"  Whichever live claim orders first holds the item, and `bin/docket show {hold.key}` "
        f"prints the order (`PL-MB2W`). Yield it - commit what you have, then "
        f"`bin/docket yield {hold.key}` and push, opening no pull request - or, only on the "
        f"project owner's word or with `get_session` showing that session ARCHIVED or failed, "
        f"take it over:\n"
        f"    bin/docket claim {hold.key} --over {holder} --reason '<why>'"
    )


def _queue_named(config: Config) -> str:
    return ", ".join(queue_records(config))


def _claims_nothing(name: str, config: Config) -> str:
    return (
        f"branch-id: {CLAIMS_NOTHING}, naming the item this work is for.\n"
        f"  branch: {name}\n"
        f"  It changes files outside the queue ({_queue_named(config)}) in commits made under "
        f"the claim record, and no `Claim:` trailer on it names it. Who holds an item is that "
        f"record (`PL-MB2W`), so this work holds nothing, and another session can start the "
        f"same item unwarned.\n"
        f"  A capture, a triage pass or a design round owes no claim: a branch changing only "
        f"the queue is not asked."
    )


def check_claims(
    base: str, name: str, now: datetime, head: str = "HEAD"
) -> tuple[list[str], list[str]]:
    """What the claim record refuses on this branch, and what it could not decide.

    Returns the refusals and the notes. The fence applies to any branch that
    has claimed; the unclaimed-work refusal binds the agent namespace alone,
    for the reason the id rule does.
    """
    config = load_config(ROOT)
    report = holdings(ROOT, now=now, items_dir=config.items_dir)
    if not report.known:
        return [], [f"branch-id: claims not checked - {report.declined}"]
    if not name or name == "HEAD":
        return [], [
            "branch-id: claims not checked - a claim names its branch, and this one's "
            "name could not be read"
        ]
    remotes = _remotes(ROOT, _runner)
    if any(_head_name(ref, remotes) == name for ref in report.unreadable):
        return [], [
            f"branch-id: claims not checked - {name}'s history cannot be compared with "
            f"{report.base} here"
        ]

    mine = claims_bound(report, name, remotes)
    refusals = [
        _behind(hold, first, name, remotes)
        for hold in mine
        if (first := ahead_of(hold, report)) is not None
    ]
    notes: list[str] = []
    if mine and report.unreadable:
        notes.append(
            f"branch-id: {', '.join(report.unreadable)} could not be read, so a claim ordering "
            f"ahead of this branch's there is not ruled out"
        )
    # `flight`'s `unclaimed:` row asks the same function of every branch it
    # walked, so the refusal here and the count there cannot disagree (`PL-FFR0`).
    work = claims_nothing(
        report,
        name,
        base=base,
        head=head,
        root=ROOT,
        config=config,
        remotes=remotes,
        runner=_runner,
    )
    if work is None:
        notes.append(
            "branch-id: claims not checked - git did not answer which commits here are work"
        )
    elif work:
        refusals.append(_claims_nothing(name, config))
    return refusals, notes


def hint(path: str, now: datetime) -> int:
    """`--hint PATH`: the line the first-edit hook adds before an edit to PATH.

    Prints `CLAIMS_NOTHING` where PATH is in this checkout and outside the queue
    and the branch claims nothing, from the same reader the refusal uses. Exits
    `NOT_ASKED` where PATH is not work outside the queue, so the hook asks again
    at the next edit. Silent wherever the answer is not a clear "nothing": a
    hint that is wrong trains a session to skip the one that is right.
    """
    config = load_config(ROOT)
    target = Path(path)
    try:
        relative = (target if target.is_absolute() else Path.cwd() / target).resolve()
        inside = relative.relative_to(ROOT).as_posix()
    except (OSError, ValueError):
        return NOT_ASKED
    if in_queue(inside, config):
        return NOT_ASKED
    name = branch_name()
    if (
        not name
        or name == "HEAD"
        or not in_agent_namespace(name)
        or BRANCH_ID_RE.search(name) is not None
    ):
        return 0
    report = holdings(ROOT, now=now, items_dir=config.items_dir)
    remotes = _remotes(ROOT, _runner)
    if not report.known or any(_head_name(ref, remotes) == name for ref in report.unreadable):
        return 0
    if not claims_bound(report, name, remotes):
        print(
            f"{CLAIMS_NOTHING}, naming the item this work is for. Who holds an item is that "
            f"record (`PL-MB2W`); a capture, a triage pass or a design round, which changes "
            f"only the queue ({_queue_named(config)}), owes none."
        )
    return 0


def _instant(text: str) -> datetime:
    """`--now`: an ISO 8601 instant with its offset, since every lease is judged against it."""
    try:
        moment = datetime.fromisoformat(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"not an ISO 8601 instant: {text!r}") from error
    if moment.tzinfo is None:
        raise argparse.ArgumentTypeError(f"{text!r} carries no UTC offset")
    return moment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=None, help="ref to compare against")
    parser.add_argument(
        "--now",
        default=None,
        type=_instant,
        help="the instant every claim's lease is judged at, ISO 8601 with its UTC offset",
    )
    parser.add_argument(
        "--hint",
        default=None,
        metavar="PATH",
        help="print the first-edit hook's line for an edit to PATH, if it has one",
    )
    args = parser.parse_args()

    now = args.now or datetime.now(UTC)
    if args.hint is not None:
        return hint(args.hint, now)

    base = args.base or default_base(ROOT, runner=_runner)
    if not resolved(base):
        # A guessed base is not walked. Where nothing resolved, the walk against
        # it used to fail into "no id is owed" - the gate passing every branch
        # in a checkout it could not read (`PL-73P0`); where a later candidate
        # resolved past an unanswered one, it would walk the wrong ref. Say
        # what happened instead of certifying.
        print(
            f"branch-id: no candidate default branch resolved here "
            f"(tried {', '.join(DEFAULT_BRANCHES)}), so there is nothing to walk from; "
            f"not checked. `git fetch origin`, or pass --base <ref>."
        )
        return 0
    walk = _subjects(base)
    if walk is None:
        # The same route, reached past a base that did resolve, or was named:
        # `--base` with no such ref, a ref deleted between the probe and the
        # walk, or the walk timing out (`PL-1PBV`).
        print(
            f"branch-id: git did not answer the walk of {base}..HEAD, so what this branch "
            f"adds is unknown; not checked. Name a base git can resolve, or `git fetch origin`."
        )
        return 0
    subjects, sound = walk
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
    refusals, notes = check_claims(base, name, now)
    for note in notes:
        print(note)
    for refusal in refusals:
        print(refusal, file=sys.stderr)
    if found:
        print(f"branch-id: visible in flight - {found[0]}")
        return 1 if refusals else 0
    if not in_agent_namespace(name):
        print(f"branch-id: {name} is outside `{AGENT_BRANCH_PREFIX}`; no id is owed")
        return 1 if refusals else 0

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
