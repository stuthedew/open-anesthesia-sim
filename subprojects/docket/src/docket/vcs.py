"""What git already knows about work in progress.

Whether an item is being worked on right now is a fact the repository
already holds: a branch is carrying its commits. Storing that in the item file
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

And for work that never arrived: an item committed on a branch that is closed
without merging exists only on that branch, invisible to every session that
reads the store in its own checkout. Git holds the branch, so git can be asked
what is on it that nowhere else has.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .model import parse_item
from .store import ID_PATTERN

# The default branch, in the order it is looked for: a branch whose tip that
# one already contains is finished rather than in flight. Trying several means
# a repository using a different name for it still gets the filtering, and a
# checkout with no remote falls back to its local branch.
DEFAULT_BRANCHES = ("origin/main", "origin/master", "main", "master")

Runner = Callable[[list[str], Path], str]


def _run_git(args: list[str], root: Path) -> str:
    """Run git, returning empty output rather than raising.

    A checkout without git, without a remote, or without network is a normal
    condition for this tool - the session-start digest must not fail because
    of it - so every failure mode collapses to "nothing known about branches".

    `git` is named rather than given an absolute path on purpose: the path
    differs across the environments this runs in, and resolving it through
    `PATH` is what lets the same code work in all of them. That is also why
    pinning one would not harden anything - a checkout that cannot run `git`
    is already a case this function answers with "nothing known".
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


BRANCH_ID_RE = re.compile(
    r"(?:^|[/_-])(pl-(?:\d{3}|[0-9bcdfghjklmnpqrstvwxyz]{4}))(?:$|[/_-])", re.I
)

# The ids at the *front* of a commit subject, and only there. `CLAUDE.md`
# requires the id of the work to lead every implementation subject, so an id
# that leads is the branch's own work while one mentioned further in is
# usually somebody else's: measured over 120 commits of this project's `main`,
# 79 subjects contained an id and 64 led with one, and all 15 of the
# difference were captures, close-outs or merges rather than implementation.
#
# So matching an id anywhere in a subject would report roughly 19% false
# positives, and a false positive here is worse than the blindness it would
# cure - it makes `docket next` skip an item that is startable, which is the
# opposite of the defect. `PL-F5HB Close it out; triage PL-4CW7 with the
# environment fix applied` is the case in miniature: the leading id is the
# work, the mentioned one had merely been triaged.
#
# A subject may lead with more than one id, because one branch may carry two
# items (`PL-N7R9, PL-J295: the pull request stops being a question`), so the
# whole leading run is read rather than only its first id.
LEADING_IDS_RE = re.compile(rf"^\s*{ID_PATTERN}(?:\s*(?:,|&|and)\s*{ID_PATTERN})*", re.I)
ANY_ID_RE = re.compile(ID_PATTERN, re.I)

# One line per commit: the ref that reached it, the day it was committed, the
# parents this checkout holds, and its subject. `%S` needs `--source`, and the
# unit separator is used as the delimiter because a subject can contain
# anything a keyboard can type. `%p` is empty for a commit whose parents this
# checkout does not have, which is how a walk that ran off the end of a
# truncated history is told from one the default branch stopped.
COMMIT_FORMAT = "--format=%S%x1f%cs%x1f%p%x1f%s"


@dataclass(frozen=True)
class Branch:
    """One ref that is carrying an item's work.

    `last_commit` is the day of the newest commit the ref holds that the
    default branch does not, or `None` when this checkout could read none of
    them - a branch created but not yet committed on, or one whose commits sit
    beyond a truncated clone's horizon.
    """

    name: str
    item_id: str
    last_commit: date | None = None


@dataclass(frozen=True)
class FlightReport:
    """Which items are in flight, and which refs could not be read to find out.

    `unreadable` is why this is a type rather than a list. A ref this checkout
    cannot compare with the default branch contributes nothing to the answer,
    and silence about it would present a partial reading as a complete one -
    the same collapse `PullRequestHistory.declined` guards against, per ref
    rather than for the whole check, because one unreadable ref does not stop
    the others from being read.

    Two things put a ref there, and a truncated clone is behind both: no
    merge-base with the default branch that this checkout can resolve, and a
    commit walk that ran off the end of the history instead of stopping
    against the default branch. The second is not implied by the first -
    `_unmerged_commits` has the argument - so a ref answering the merge-base
    is not thereby answerable.

    **Every caller takes the ids from here rather than from a function that
    returns them alone.** A `set[str]` is the natural shape for ranking and
    marking, and it is exactly the shape that cannot say "and one ref went
    unread" - so a caller handed one presents a partial reading as a complete
    one, which is the collapse this type exists to prevent. `ids` is a
    property of the report for that reason: the gap travels with the answer,
    and a caller that wants to ignore it has to do so in writing.
    """

    branches: tuple[Branch, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""

    @property
    def ids(self) -> frozenset[str]:
        """The items this checkout proved are in flight, for ranking and marking."""
        return frozenset(branch.item_id for branch in self.branches)


def _leading_ids(subject: str) -> list[str]:
    """Every item id in the run of them a commit subject opens with."""
    match = LEADING_IDS_RE.match(subject)
    if match is None:
        return []
    return [found.group(0).upper() for found in ANY_ID_RE.finditer(match.group(0))]


def _unmerged_commits(
    refs: list[str], base: str, root: Path, run: Runner
) -> tuple[dict[str, date], dict[str, str], set[str]]:
    """The newest commit day per ref, the ref leading with each id, and what went unread.

    One `git log` covers every ref at once: `--source` reports which ref on the
    command line reached each commit, so the walk that finds the ids also dates
    the branches. Refs are passed in the order they will be reported in, so a
    commit two refs share - a local branch and its own tracking ref - is
    attributed to the one that will be named.

    **A walk must stop because the default branch accounted for what came next,
    never because the checkout ran out of history.** `^base` excludes only the
    commits this checkout can reach *from* `base`, and in a truncated clone
    `base`'s own history ends at a grafted commit - so everything below that
    graft goes unexcluded. A ref reaching round it, which a merge of the
    default branch into a branch is enough to do, then has the default
    branch's own commits reported as its work and the ids leading their
    subjects reported as items somebody is implementing. A merge-base that
    resolves does not rule this out: it proves the two share *a* commit this
    checkout can see, never that the walk can see the rest.

    The signature is a commit with no parents in this checkout. A walk that
    ends soundly ends against a commit `base` excluded; one that emits a
    parentless commit ran off the end of a grafted history instead, so nothing
    it produced is proven and the ref it belongs to is returned as unread. The
    repository's true root reads the same way and is answered the same way -
    it sits on the default branch, so a walk reaching it is one `base` failed
    to exclude. Reading the commits is what settles this rather than
    `is_shallow`, so a git too old to say whether the checkout is truncated is
    guarded too.
    """
    if not refs:
        return {}, {}, set()
    # The trailing `--` is what keeps a branch sharing a name with a file from
    # being read as a path, which git refuses to guess at and answers with an
    # error - and every error here collapses to "nothing known".
    output = run(["log", "--source", COMMIT_FORMAT, f"^{base}", *refs, "--"], root)
    last: dict[str, date] = {}
    ids: dict[str, str] = {}
    unbounded: set[str] = set()
    for line in output.splitlines():
        parts = line.split("\x1f", 3)
        if len(parts) != 4:
            continue
        ref, committed, parents, subject = parts
        if not parents.strip():
            unbounded.add(ref)
        try:
            day = date.fromisoformat(committed)
        except ValueError:
            day = None
        if day is not None and day > last.get(ref, date.min):
            last[ref] = day
        for identifier in _leading_ids(subject):
            ids.setdefault(identifier, ref)
    return last, ids, unbounded


def _work_already_on_base(ref: str, fork_point: str, base: str, root: Path, run: Runner) -> bool:
    """Whether everything the ref adds is content the default branch has held.

    Containment answers this for a merge commit and never for a squash: the
    squash writes one new commit carrying the branch's *content* and none of
    its commits, so `--merged` calls the branch unmerged for as long as its ref
    survives, and every id leading one of its subjects reports in flight
    forever. GitHub deleting the head branch on merge is what usually hides
    that; a long-lived checkout that does not prune is where it bites.

    So the question asked here is about content rather than ancestry: of the
    blobs the ref adds to the tree it forked from, has the default branch held
    each one at some point? That is `stranded`'s rule - compare what the trees
    hold, never how the commits got there - pointed the other way, and it
    answers a rebase or a cherry-pick the same way it answers a squash.

    **The default branch's history, not its tip.** Comparing against `base`
    itself would call a squash-merged branch unlanded again the moment anyone
    edited a file it had touched - which in this store is what the next triage
    pass does to every item a branch captured, so the branch would be back to
    reporting in flight forever one merge later. `git log --find-object` asks
    instead whether the blob was ever on the default branch, and that does not
    decay.

    Two silences read as "not landed", which is the safe direction. A ref that
    adds no blob at all - one with no commits yet, one that only deletes, or
    one git could not read - and a blob whose landing sits below a truncated
    clone's horizon: both keep the ref in the report. Reporting a merged branch
    as in flight is the noise this removes; reporting a live session's branch
    as merged would hand its item to a second session, which is the collision
    the whole read exists to prevent.
    """
    introduced: list[str] = []
    for line in run(
        ["diff", "--raw", "--no-renames", "--no-abbrev", fork_point, ref, "--"], root
    ).splitlines():
        # `:<src mode> <dst mode> <src blob> <dst blob> <status>\t<path>`. The
        # path is dropped rather than parsed - a blob is what is asked about,
        # and a path can contain anything including the tab that precedes it.
        fields = line.split("\t", 1)[0].split()
        if len(fields) == 5 and set(fields[3]) != {"0"}:
            introduced.append(fields[3])
    if not introduced:
        return False
    return all(
        run(["log", "-1", "--format=%H", f"--find-object={blob}", base], root).strip()
        for blob in introduced
    )


def branches_in_flight(
    root: Path, *, include_remote: bool = True, runner: Runner | None = None
) -> FlightReport:
    """Every item whose work sits on a branch the default branch has not taken.

    **The id is read from the commit subjects as well as from the branch
    name**, and that is the whole point of the read. A branch a session names
    for itself carries the id (`claude/pl-k7qx-short-slug`); a branch the web
    harness names is built from the opening prompt
    (`claude/roadmap-release-write-failure-nhsjwo`) and carries nothing, and
    cannot be renamed afterwards. Reading names alone therefore went blind in
    exactly the case this exists for, and `docket next` would hand a session an
    item another session was already implementing.

    Refs are read from what is already fetched, so the answer can be stale by
    exactly one fetch. That is an acceptable error for an advisory and an
    unacceptable one for a lock, which is why this reports rather than blocks.

    Branches whose work has landed are excluded, and that exclusion matters
    more than it looks: deleting a branch on the remote does not remove the
    local remote-tracking ref until someone prunes, so without this every item
    ever shipped goes on being reported as in-flight work and the signal
    becomes noise within a few releases. It is asked twice, because one test
    cannot answer it. `--merged` is exact and cheap for a branch the default
    branch contains; a squash merge keeps none of the branch's commits, so
    `_work_already_on_base` asks after the content instead.

    What that leaves is read, and only what the checkout can prove is reported.
    Both reads of a ref against the default branch need history the checkout
    may not hold, so each has a guard and neither guard covers the other: a
    merge-base that will not resolve, and a commit walk that ran off the end of
    a grafted history rather than stopping against the default branch. Either
    one names the ref as unread.

    What remains is qualified rather than filtered. An unmerged branch may be a
    live session or work nobody will ever merge, and only the date of its last
    commit separates the two - so that is carried into the report and left to
    the reader, the way `stranded` reports rather than decides.
    """
    run = runner or _run_git
    args = ["for-each-ref", "--format=%(refname:short)", "refs/heads"]
    if include_remote:
        args.append("refs/remotes")

    # One base for the whole read: what counts as merged, what a ref is
    # compared against, and what the commit walk excludes have to agree, or the
    # answer is assembled from two different questions.
    base = default_base(root, runner=run)
    merged = {
        name.strip() for name in run([*args, f"--merged={base}"], root).splitlines() if name.strip()
    }
    candidates = [
        name.strip()
        for name in run(args, root).splitlines()
        if name.strip() and name.strip() not in merged
    ]

    # A truncated clone is the normal state of an agent session's container,
    # and a ref with no readable merge-base is one whose commits this checkout
    # simply does not have. Excluding `^base` from a walk that cannot reach
    # `base` would report the ref's whole visible history as its own work, so
    # it is named as unread instead of answered wrongly. This is the first of
    # two guards and not the sufficient one: a merge-base that resolves says
    # the two share a commit this checkout can see, not that the walk below it
    # is complete, which is what the second guard tests.
    #
    # The merge-base is the fork point the content test compares against, so
    # the read that decides whether a ref can be answered at all is the same
    # one that answers it - two calls asking git the same question could
    # disagree about which commit the branch left from.
    unlanded: list[str] = []
    unreadable: set[str] = set()
    for name in candidates:
        fork_point = run(["merge-base", base, name], root).strip()
        if not fork_point:
            unreadable.add(name)
        elif not _work_already_on_base(name, fork_point, base, root, run):
            unlanded.append(name)

    # A resolvable merge-base answers only half of it. The walk that reads the
    # ids has to be able to exclude the default branch's own commits, and in a
    # truncated clone it cannot always reach them - so a ref whose walk ran off
    # the end of the history joins the ones the merge-base could not answer
    # rather than contributing what it appeared to say. The direction matters:
    # an id wrongly reported here is removed from `docket next` under the words
    # "do not start these again", so an unread ref is the cheaper error.
    last_commit, subject_ids, unbounded = _unmerged_commits(unlanded, base, root, run)
    if unbounded:
        unreadable |= unbounded
        unlanded = [name for name in unlanded if name not in unbounded]
        subject_ids = {
            identifier: name for identifier, name in subject_ids.items() if name not in unbounded
        }

    # A local branch and its remote tracking ref are one piece of work, and so
    # are a branch named for an item and its own commits: the first ref that
    # accounts for an id is the one reported for it.
    in_flight: dict[str, Branch] = {}
    for name in unlanded:
        match = BRANCH_ID_RE.search(name)
        if match is None:
            continue
        identifier = match.group(1).upper()
        in_flight.setdefault(
            identifier, Branch(name=name, item_id=identifier, last_commit=last_commit.get(name))
        )
    for identifier, name in subject_ids.items():
        in_flight.setdefault(
            identifier, Branch(name=name, item_id=identifier, last_commit=last_commit.get(name))
        )

    return FlightReport(
        branches=tuple(sorted(in_flight.values(), key=lambda branch: branch.item_id)),
        unreadable=tuple(name for name in candidates if name in unreadable),
        base=base,
    )


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


def is_shallow(root: Path, *, runner: Runner | None = None) -> bool | None:
    """Whether this checkout is truncated, or `None` when git will not say.

    Three answers rather than two, because the callers need the difference. A
    shallow clone is missing history and tags it can name; a git too old for
    `--is-shallow-repository`, a directory that is not a repository, or no git
    at all leaves the question open. Both forbid inferring anything from
    something's absence, and only the first can explain why.
    """
    run = runner or _run_git
    answer = run(["rev-parse", "--is-shallow-repository"], root).strip()
    if answer == "true":
        return True
    if answer == "false":
        return False
    return None


def tags(root: Path, *, runner: Runner | None = None) -> frozenset[str]:
    """Every tag name the repository holds.

    Empty for a checkout with no tags, no git, or no repository at all - the
    same collapse every other read here makes. **A truncated clone does not
    collapse to empty**: it returns the tags reachable within its depth and
    silently omits the rest, so a caller reasoning from a tag's absence must
    ask `is_shallow` first (`PL-J295`). What that emptiness *means* is
    decided by the caller: `release.is_untagged` reads it as "this project does
    not tag" rather than as "every release is untagged", because a tool that
    started refusing releases in a project that never tagged would be teaching
    a practice rather than holding one.
    """
    run = runner or _run_git
    return frozenset(
        line.strip() for line in run(["tag", "--list"], root).splitlines() if line.strip()
    )


# A pull request number as it reaches the default branch. GitHub writes one of
# two subjects depending on how the merge was made: `Merge pull request #71
# from owner/branch` for a merge commit, and `Title (#71)` for a squash. Both
# are matched, because a repository that switches from one to the other keeps
# the history it already has.
PR_SUBJECT_RE = re.compile(r"^Merge pull request #(\d+)\b|\(#(\d+)\)\s*$")


@dataclass(frozen=True)
class PullRequestHistory:
    """Which pull requests the default branch names, or why that is not known.

    `declined` is the whole reason this is a type rather than a set. A caller
    handed an empty set cannot tell "this project does not use pull requests"
    from "this checkout cannot see them", and the two demand opposite
    behaviour: the first is a clean answer, the second must be reported as a
    check that did not run. Collapsing them is the failure this guards.
    """

    numbers: frozenset[int] = frozenset()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def merged_pull_requests(root: Path, *, runner: Runner | None = None) -> PullRequestHistory:
    """Every pull request number named by a commit on the default branch.

    A shallow clone is a worse condition than a bare one, and the difference is
    why this declines rather than returning what it found. In a bare checkout
    git cannot answer and every read here already collapses to silence; in a
    shallow clone git answers confidently and wrongly. The commits it is
    missing are exactly the oldest, so the provenance that has been settled
    longest is what would be reported as never having landed - and the
    container an agent session runs in is normally shallow, so that is the
    common case rather than the exotic one.

    So the only state that permits an answer is a repository that says outright
    it is not shallow. Truncation, no git, no repository, or a git too old to
    have `--is-shallow-repository` all decline, each with the reason, so the
    caller can report a check that did not run instead of one that passed.

    Deliberately no fetch. `docket check` runs from a bare tree with no
    network, and deepening the history here would trade that away to answer a
    question the caller is perfectly able to skip.
    """
    run = runner or _run_git
    shallow = is_shallow(root, runner=run)
    if shallow is True:
        return PullRequestHistory(
            declined="the checkout is a shallow clone, so the commits it is missing are "
            "the oldest ones and the longest-settled provenance would read as broken"
        )
    if shallow is None:
        return PullRequestHistory(declined="git cannot say whether this checkout is complete")
    subjects = run(["log", "--format=%s", default_base(root, runner=run)], root)
    if not subjects.strip():
        return PullRequestHistory(declined="no default branch this checkout can read")
    found: set[int] = set()
    for subject in subjects.splitlines():
        match = PR_SUBJECT_RE.search(subject.strip())
        if match is not None:
            found.add(int(match.group(1) or match.group(2)))
    return PullRequestHistory(numbers=frozenset(found))


# An item file is named `<id>-<slug>.md`, so the id can be read from a tree
# listing without opening anything. The id grammar comes from `store` rather
# than being spelled again here: two spellings of it would drift, and the one
# that drifted would silently stop recognising items.
ITEM_FILE_RE = re.compile(rf"^({ID_PATTERN})-")


@dataclass(frozen=True)
class StrandedItem:
    """An item that exists on a branch and nowhere the store can see."""

    identifier: str
    title: str
    path: str
    branches: tuple[str, ...]


@dataclass(frozen=True)
class StrandedReport:
    """What is only on a branch, and how much of the repository was read.

    `refs_read` is part of the answer rather than diagnostics. The check can
    only see refs this checkout holds, and a container that cloned one branch
    holds two - so "nothing stranded" from a checkout that read two refs and
    the same words from one that read twenty are different claims, and the
    count is what tells them apart.

    `declined` carries the same meaning it does for `PullRequestHistory`: a
    check that could not run, reported as such rather than as a clean result.
    """

    items: tuple[StrandedItem, ...] = ()
    refs_read: int = 0
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def _items_at(ref: str, root: Path, items_dir: str, run: Runner) -> dict[str, str]:
    """Every item id the ref's tree holds, mapped to the file that holds it.

    `ls-tree` reads one tree and needs no history behind it, which is what
    makes this work in the shallow clone an agent session starts from. Every
    commit-graph answer - is this branch merged, how far ahead is it - is
    unreliable there, because the commits that would prove containment are
    exactly the ones a shallow clone is missing.
    """
    found: dict[str, str] = {}
    for line in run(["ls-tree", "-r", "--name-only", ref, "--", items_dir], root).splitlines():
        path = line.strip()
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1]) if path else None
        if match is not None:
            found.setdefault(match.group(1), path)
    return found


def _title_at(ref: str, path: str, root: Path, run: Runner) -> str:
    """The title an item file carries on a branch, or empty if it cannot be read."""
    text = run(["show", f"{ref}:{path}"], root)
    return parse_item(text, path).title if text else ""


def stranded(
    root: Path, known_ids: set[str], *, items_dir: str = "docs/items", runner: Runner | None = None
) -> StrandedReport:
    """Items that exist on some branch and in neither the store nor the default branch.

    An item is committed on whatever branch the capturing session was on. If
    that branch is never merged the item exists only there, and since every
    other session reads `docs/items/` in its own checkout, nothing will ever
    mention it again. This is the read that finds those.

    Comparison is by **id and content, never by commit counts**, and that is
    the whole design. A squash-merged branch is never contained in the default
    branch, so a containment test calls it unmerged forever and reports every
    item it carries as lost; a renamed item file was added twice and deleted
    once, so a test over added paths reports the old name as lost. Both are
    answered by looking at what the trees actually hold: an id present on the
    default branch is not stranded, however its commits got there.

    `known_ids` is what the calling session can already see - the store in its
    own working tree - so an item captured on this branch a moment ago is not
    reported back to the session that captured it. The default branch's own
    ids are added to that, because a branch forked before an item landed has a
    working tree missing it and would otherwise report it as stranded.
    """
    run = runner or _run_git
    refs = [
        line.strip()
        for line in run(
            ["for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"], root
        ).splitlines()
        if line.strip()
    ]
    if not refs:
        return StrandedReport(declined="no branch refs this checkout can read")

    base = default_base(root, runner=run)
    on_base = _items_at(base, root, items_dir, run)
    if not on_base:
        # Either the read failed or the store does not live where it was said
        # to. Both would make every item on every branch look stranded, which
        # is the one output worse than none: it is long, alarming and wrong.
        return StrandedReport(
            declined=f"no items found on {base}, so every branch would read as stranding its own"
        )

    known = {identifier.upper() for identifier in known_ids} | set(on_base)
    elsewhere: dict[str, tuple[str, list[str]]] = {}
    for ref in refs:
        if ref == base:
            continue
        for identifier, path in _items_at(ref, root, items_dir, run).items():
            if identifier in known:
                continue
            # Every branch holding it is recorded, not just the first. A branch
            # missing from the report strands nothing and is safe to delete on
            # that count; naming only one copy would make the branch holding the
            # other look clean.
            elsewhere.setdefault(identifier, (path, []))[1].append(ref)

    found = [
        StrandedItem(
            identifier=identifier,
            title=_title_at(branches[0], path, root, run),
            path=path,
            branches=tuple(branches),
        )
        for identifier, (path, branches) in sorted(elsewhere.items())
    ]
    return StrandedReport(items=tuple(found), refs_read=len(refs))
