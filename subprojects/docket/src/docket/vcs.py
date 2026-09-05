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
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from .model import parse_item
from .release import version_in
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

# One line per commit: the ref that reached it, when it was committed, the
# parents this checkout holds, its hash, and its subject. `%S` needs
# `--source`, and the unit separator is used as the delimiter because a subject
# can contain anything a keyboard can type. `%p` is empty for a commit whose
# parents this checkout does not have, which is how a walk that ran off the end
# of a truncated history is told from one the default branch stopped.
#
# The full timestamp rather than the day, and the hash rather than nothing,
# because `precedence` has to put two branches in a single order that both of
# their sessions compute identically. Two sessions start minutes apart, so a
# day cannot separate them, and two commits can share a second - which is what
# the hash is there to break. `flight` still wants only the day and takes it
# from the same read.
COMMIT_FORMAT = "--format=%S%x1f%cI%x1f%p%x1f%H%x1f%s"


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

    `unreadable` is why this is a type rather than a list. A ref whose commits
    this checkout cannot compare with the default branch contributes nothing
    from them, and silence about it would present a partial reading as a
    complete one - the same collapse `PullRequestHistory.declined` guards
    against, per ref rather than for the whole check, because one unreadable
    ref does not stop the others from being read.

    Two things put a ref there, and a truncated clone is behind both: no
    merge-base with the default branch that this checkout can resolve, and a
    commit walk that ran off the end of the history instead of stopping
    against the default branch. The second is not implied by the first -
    `_unmerged_commits` has the argument - so a ref answering the merge-base
    is not thereby answerable.

    **It names what went unread, not a ref that was skipped, so a ref can sit
    in both halves at once.** What the checkout could not read is the commits;
    a branch named `claude/pl-k7qx-short-slug` still names its item, and that
    read needs no history. Such a ref appears in `branches` for the id its name
    proves *and* in `unreadable` for the ids its commits might have added.

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


def leading_ids(subject: str) -> list[str]:
    """Every item id in the run of them a commit subject opens with."""
    match = LEADING_IDS_RE.match(subject)
    if match is None:
        return []
    return [found.group(0).upper() for found in ANY_ID_RE.finditer(match.group(0))]


@dataclass(frozen=True, order=True)
class Stake:
    """When a ref said it was carrying an item, and the commit that said so.

    Ordered, and ordered on the hash after the time, because that is the whole
    job: two branches carrying one item have to be put in an order both of
    their sessions compute identically, and two commits made in the same second
    would otherwise be a tie nobody can break. The hash is arbitrary as a
    ranking and total as an order, which is the property wanted here - an
    arbitrary answer both sessions reach is worth more than a principled one
    they reach differently.
    """

    when: datetime
    commit: str


# Sorts a carrier with no readable stake behind every carrier that has one,
# without ever being compared against a real one: the flag ahead of it in the
# sort key separates the two groups first. Aware, so that a comparison against
# one of these does not raise if a later change puts them side by side.
_UNDATED = Stake(when=datetime.min.replace(tzinfo=UTC), commit="")


@dataclass(frozen=True)
class _Walk:
    """What one pass over the unlanded refs produced.

    Four readings of the same commits. They are kept together because they come
    from one `git log`: separating them into functions of their own would mean
    walking the history once per question, and the questions are asked together
    every time.
    """

    last: dict[str, date]
    ids: dict[str, str]
    staked: dict[tuple[str, str], Stake]
    opened: dict[str, Stake]
    unbounded: set[str]


def _annotates_only(paths: list[str], prefix: str) -> bool:
    """Whether a commit's whole diff sits inside the queue directory.

    **The rule that separates recording an item from working on it**, and it
    is deliberately about where the commit wrote rather than about what it
    wrote there. `CLAUDE.md` requires a finding to be captured before a session
    ends, requires the leading id on every commit subject, and requires a
    behavior change to land in the session that asks for it - so a capture, a
    triage pass, a `docket record` write and a note added to a brief all lead
    with an id they are not implementing. Reading their subjects alone marked
    the item as work somebody held, and `docket next` withheld it from every
    session until the branch merged, which for a branch nobody merges is
    forever (`PL-X3WZ`).

    Measured over the eight false marks that item recorded: every one is a
    commit whose entire diff is inside the queue directory, and the one branch
    genuinely implementing an item is not. Nothing finer was needed - no
    frontmatter-versus-body parse, which would in any case have failed on the
    capture and triage commits, since both write frontmatter.

    **It fails toward keeping the mark, and both of its silences do.** A commit
    with no paths at all is a merge - `--name-only` prints none for one - or a
    read that went wrong, and neither is evidence of annotation, so an empty
    list is not annotation. A path git quoted, which it does for one carrying
    non-ASCII bytes, fails the prefix test and lands the same way. That is the
    cheaper error of the two available: an item wrongly left marked is one a
    session picks around, while an item wrongly unmarked is two sessions on one
    piece of work (`PL-PRHN`).

    The residual case it cannot see is a session that *starts* an item by
    pushing only a `touches` fill or a `verify:` command, which is annotation
    by this rule and a claim in fact. A branch the session names for the item
    still carries the claim in its own name, which is read whatever the diff
    says; a branch the harness named does not, and goes unmarked until its
    first commit outside the queue. `.claude/skills/docket/SKILL.md` says so
    where it asks for that first push.
    """
    return bool(paths) and all(path.startswith(prefix) for path in paths)


def _unmerged_commits(
    refs: list[str], base: str, root: Path, run: Runner, *, items_dir: str = "docs/items"
) -> _Walk:
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

    **`staked` and `opened` keep the *earliest* commit where the rest keeps the
    newest**, and the difference is which question each answers. How long a
    branch has been sitting is a question about its last commit; when a branch
    began carrying an item - the only fact two sessions can order themselves by
    - is a question about its first. `staked` dates the claim a commit subject
    makes, per ref and per id, so a branch that picked up a rider is dated from
    the rider rather than from its own first commit; `opened` dates the branch
    itself, which is the claim a branch *name* makes from the moment there is
    anything on it.

    **`ids` and `staked` read the commit's diff as well as its subject**, and
    `opened` does not. A leading id says which item a commit concerns, never
    that the commit implements it, so `_annotates_only` withholds the ones
    whose whole diff sits in the queue directory - a capture, a triage pass, a
    recovered item, a note written into a brief. `opened` is the claim a branch
    *name* makes, which no diff qualifies.
    """
    if not refs:
        return _Walk({}, {}, {}, {}, set())
    # `--name-only` rather than a `git show --stat` per commit, and that is the
    # whole reason the diff can be read at all here. This walk is on the hot
    # path of `next`, `list`, `triage`, `status` and the session-start digest,
    # so a subprocess per commit would have put the read out of reach; asking
    # the walk that is already running to also name the paths costs one pass
    # over the same trees. Measured on this repository: 4.6 ms to 8.8 ms over
    # 50 commits, 9.5 ms to 25.1 ms over 200 - against roughly 4 ms of process
    # spawn *each* for the per-commit form.
    #
    # The trailing `--` is what keeps a branch sharing a name with a file from
    # being read as a path, which git refuses to guess at and answers with an
    # error - and every error here collapses to "nothing known".
    output = run(["log", "--source", COMMIT_FORMAT, "--name-only", f"^{base}", *refs, "--"], root)
    prefix = items_dir.strip("/") + "/"
    last: dict[str, date] = {}
    ids: dict[str, str] = {}
    staked: dict[tuple[str, str], Stake] = {}
    opened: dict[str, Stake] = {}
    unbounded: set[str] = set()

    # A commit's paths follow its formatted line, so the claim it makes cannot
    # be judged until the next commit begins or the output ends. Only the id
    # half is held back: the dates and the parentless-commit guard are
    # properties of the commit itself and are read where they are parsed.
    pending: tuple[str, Stake | None, str] | None = None
    paths: list[str] = []

    def credit_claims() -> None:
        """Credit the held commit's leading ids, unless its diff only annotates."""
        if pending is None:
            return
        ref, stake, subject = pending
        if _annotates_only(paths, prefix):
            return
        for identifier in leading_ids(subject):
            ids.setdefault(identifier, ref)
            if stake is not None:
                held = staked.get((ref, identifier))
                if held is None or stake < held:
                    staked[(ref, identifier)] = stake

    for line in output.splitlines():
        parts = line.split("\x1f", 4)
        if len(parts) != 5:
            # Everything that is not a commit line is one of that commit's
            # paths, or the blank line git writes between the two. A path can
            # no more carry four unit separators than a subject can, so the
            # field count keeps the two apart without a second delimiter.
            if line.strip():
                paths.append(line.strip())
            continue
        credit_claims()
        pending, paths = None, []
        ref, committed, parents, commit, subject = parts
        if not parents.strip():
            unbounded.add(ref)
        try:
            when: datetime | None = datetime.fromisoformat(committed)
        except ValueError:
            # A date this checkout's git wrote in some other shape. The commit
            # still names whatever it names, so the ids are read from it as
            # before and only the ordering loses a data point - the direction
            # that reports less rather than the one that reports wrongly.
            when = None
        stake = None if when is None else Stake(when=when, commit=commit)
        if when is not None and when.date() > last.get(ref, date.min):
            last[ref] = when.date()
        if stake is not None:
            first = opened.get(ref)
            if first is None or stake < first:
                opened[ref] = stake
        pending = (ref, stake, subject)
    credit_claims()
    return _Walk(last=last, ids=ids, staked=staked, opened=opened, unbounded=unbounded)


def _base_blobs(base: str, root: Path, run: Runner) -> frozenset[str]:
    """Every blob the default branch's history holds, read in one walk.

    The question each caller actually asks is per blob - has the default
    branch ever held this content - and `git log --find-object` answers it
    one blob at a time, walking the whole history for each. Listing the
    objects reachable from the base answers it for all of them at once, and
    the two agree by construction: a blob some commit on the base introduced
    is a blob some tree on the base holds.

    Measured on this repository at 425 commits: 17 `--find-object` walks cost
    0.62 s and this costs 0.033 s, so the *complete* split below is cheaper
    than the short-circuited all-or-nothing test it replaced.

    A truncated clone reaches fewer commits and so returns fewer blobs, which
    reads as "not landed" - the same safe direction `_landing_split` documents
    and the same one `--find-object` gave.
    """
    found: set[str] = set()
    for line in run(["rev-list", "--objects", base], root).splitlines():
        oid, _, path = line.partition(" ")
        # Only entries carrying a path are blobs or trees; a bare oid is a
        # commit. Trees cost a membership test that can never match, since
        # nothing compared against this set is a tree.
        if path.strip():
            found.add(oid.strip())
    return frozenset(found)


def _landing_split(
    ref: str, fork_point: str, base_blobs: frozenset[str], root: Path, run: Runner
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The paths a ref introduces, split into what the base holds and what it does not.

    Containment answers "has this branch landed" for a merge commit and never
    for a squash: the squash writes one new commit carrying the branch's
    *content* and none of its commits, so `--merged` calls the branch unmerged
    for as long as its ref survives, and every id leading one of its subjects
    reports in flight forever. GitHub deleting the head branch on merge is what
    usually hides that; a long-lived checkout that does not prune is where it
    bites.

    So the question asked here is about content rather than ancestry: of the
    blobs the ref adds to the tree it forked from, has the default branch held
    each one at some point? That is `stranded`'s rule - compare what the trees
    hold, never how the commits got there - pointed the other way, and it
    answers a rebase or a cherry-pick the same way it answers a squash.

    **The default branch's history, not its tip.** Comparing against the base
    tree alone would call a squash-merged branch unlanded again the moment
    anyone edited a file it had touched - which in this store is what the next
    triage pass does to every item a branch captured, so the branch would be
    back to reporting in flight one merge later. Asking whether the blob was
    ever on the default branch does not decay.

    **Both sides are returned, because two readers need opposite halves.**
    `_work_already_on_base` needs to know the outstanding side is empty;
    `orphaned` needs to know neither side is, which is what a branch looks like
    when its pull request took part of its work and something pushed the rest
    afterwards. Computing them separately would be two spellings of one
    question, and two spellings are two answers waiting to disagree.

    Two silences read as "not landed", which is the safe direction. A ref that
    adds no blob at all - one with no commits yet, one that only deletes, or
    one git could not read - and a blob whose landing sits below a truncated
    clone's horizon: both keep the ref in the report. Reporting a merged branch
    as in flight is the noise this removes; reporting a live session's branch
    as merged would hand its item to a second session, which is the collision
    the whole read exists to prevent.
    """
    landed: list[str] = []
    outstanding: list[str] = []
    for line in run(
        ["diff", "--raw", "--no-renames", "--no-abbrev", fork_point, ref, "--"], root
    ).splitlines():
        # `:<src mode> <dst mode> <src blob> <dst blob> <status>\t<path>`. The
        # fields end at the first tab, and everything after it is the path -
        # which can itself contain a tab, so it is taken whole rather than
        # split. git quotes a path it cannot print literally, and such a path
        # is reported the way git wrote it.
        head, _, path = line.partition("\t")
        fields = head.split()
        if len(fields) == 5 and set(fields[3]) != {"0"}:
            (landed if fields[3] in base_blobs else outstanding).append(path or fields[3])
    return tuple(landed), tuple(outstanding)


def _work_already_on_base(split: tuple[tuple[str, ...], tuple[str, ...]]) -> bool:
    """Whether everything a ref adds is content the default branch has held.

    `_landing_split` carries the reasoning; this is the all-or-nothing reading
    of it, kept as a named rule rather than spelled at the one call site so
    that `orphaned`'s reading of the same split sits beside it and the two can
    be compared. A ref introducing nothing has an empty landed side and reads
    as not landed, which is what keeps a branch with no commits yet in the
    report.
    """
    landed, outstanding = split
    return bool(landed) and not outstanding


@dataclass(frozen=True)
class _Refs:
    """Every ref this checkout holds, split by what can be believed about it.

    `candidates` keeps the order refs were listed in, because that order
    decides which of two refs holding one piece of work - a local branch and
    its own tracking ref - is the one reported for it.
    """

    #: How many refs the listing returned before the merged ones were removed.
    #: The count rather than the names, because the only caller needs to tell
    #: "git listed nothing" - no git, no repository - from "every ref it listed
    #: has landed", and those are opposite answers that an empty `candidates`
    #: reports identically.
    listed: int
    candidates: list[str]
    unlanded: list[str]
    unreadable: set[str]
    #: Per unlanded ref, the paths it introduces that the base already holds
    #: and the paths it does not. Kept because deciding a ref is unlanded
    #: computes it, and `orphaned` would otherwise ask git the same question a
    #: second time to find out *which* half was which.
    landing: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]


def _unlanded_refs(base: str, root: Path, run: Runner, *, include_remote: bool) -> _Refs:
    """Which refs still carry work the default branch has not taken.

    Split out because two reads need exactly this and would otherwise each
    spell the four git questions it asks - listing the refs, subtracting the
    merged ones, resolving each fork point, and asking after the content a
    squash merge keeps - and two spellings of one question are two answers
    waiting to disagree.
    """
    args = ["for-each-ref", "--format=%(refname:short)", "refs/heads"]
    if include_remote:
        args.append("refs/remotes")
    merged = {
        name.strip() for name in run([*args, f"--merged={base}"], root).splitlines() if name.strip()
    }
    listing = [name.strip() for name in run(args, root).splitlines() if name.strip()]
    candidates = [name for name in listing if name not in merged]

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
    landing: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    # One walk of the base's objects, before the loop rather than inside it:
    # the question is per blob and the answer is the same set for every ref.
    base_blobs = _base_blobs(base, root, run)
    for name in candidates:
        fork_point = run(["merge-base", base, name], root).strip()
        if not fork_point:
            unreadable.add(name)
            continue
        split = _landing_split(name, fork_point, base_blobs, root, run)
        if not _work_already_on_base(split):
            unlanded.append(name)
            landing[name] = split
    return _Refs(
        listed=len(listing),
        candidates=candidates,
        unlanded=unlanded,
        unreadable=unreadable,
        landing=landing,
    )


def branches_in_flight(
    root: Path,
    *,
    include_remote: bool = True,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
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
    Both reads of a ref's *commits* against the default branch need history the
    checkout may not hold, so each has a guard and neither guard covers the
    other: a merge-base that will not resolve, and a commit walk that ran off
    the end of a grafted history rather than stopping against the default
    branch. Either one names the ref as unread - and naming it so stops its
    commits being believed, not its name being read, because the id a branch
    name carries needs no history at all.

    What remains is qualified rather than filtered. An unmerged branch may be a
    live session or work nobody will ever merge, and only the date of its last
    commit separates the two - so that is carried into the report and left to
    the reader, the way `stranded` reports rather than decides.

    **A subject's leading id is a claim only where the commit did more than
    write to the queue.** Capturing a finding, triaging an item, recovering a
    stranded one and recording a merged pull request number all lead with ids
    under rules `CLAUDE.md` makes mandatory, and none of them is work in
    progress; read as claims they withheld startable items from every session
    until the branch merged. `_annotates_only` carries that reading and the
    error it prefers.
    """
    run = runner or _run_git

    # One base for the whole read: what counts as merged, what a ref is
    # compared against, and what the commit walk excludes have to agree, or the
    # answer is assembled from two different questions.
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    candidates, unlanded, unreadable = refs.candidates, refs.unlanded, set(refs.unreadable)

    # A resolvable merge-base answers only half of it. The walk that reads the
    # ids has to be able to exclude the default branch's own commits, and in a
    # truncated clone it cannot always reach them - so a ref whose walk ran off
    # the end of the history joins the ones the merge-base could not answer
    # rather than contributing what it appeared to say. The direction matters:
    # an id wrongly reported here is removed from `docket next` under the words
    # "do not start these again", so an unread ref is the cheaper error.
    walk = _unmerged_commits(unlanded, base, root, run, items_dir=items_dir)
    last_commit, subject_ids = walk.last, walk.ids
    if walk.unbounded:
        unreadable |= walk.unbounded
        unlanded = [name for name in unlanded if name not in walk.unbounded]
        subject_ids = {
            identifier: name
            for identifier, name in subject_ids.items()
            if name not in walk.unbounded
        }
    unlanded_set = set(unlanded)

    # **A ref whose name carries an id contributes it whether or not its
    # commits could be read.** The two reads need different evidence and only
    # one of them needs history: `^base` can exclude the default branch's own
    # work only where the checkout holds it, while `claude/pl-k7qx-short-slug`
    # names its item in a checkout holding nothing at all. Sending an unread
    # ref past this loop discarded the answer that was certain along with the
    # ones that were not.
    #
    # It cuts against the direction the two guards above take, and the
    # difference is what is being believed. There an id was *inferred* from a
    # walk the history could not support, and a wrong one withholds a startable
    # item under "do not start these again". Here the id is proven and only the
    # branch's landedness is open - which is the cheaper uncertainty, because
    # an item whose work landed is closed and never a candidate for `docket
    # next` anyway, while dropping the id offers an item a live session is
    # holding. That is the collision this whole read exists to prevent.
    #
    # A local branch and its remote tracking ref are one piece of work, and so
    # are a branch named for an item and its own commits: the first ref that
    # accounts for an id is the one reported for it. Candidate order decides
    # that, which prefers a local branch to its tracking ref and a ref that was
    # read to one that was not.
    named = [name for name in candidates if name in unlanded_set or name in unreadable]
    in_flight: dict[str, Branch] = {}
    for name in named:
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


@dataclass(frozen=True)
class Carrier:
    """One piece of work carrying an item, and the commit where it said so.

    Identified by that commit rather than by the ref that reached it, because a
    local branch and its own tracking ref are one session's work seen twice and
    telling a session to yield to itself is the one answer this must never
    give. `ref` is therefore a label - whichever ref git credited the commit to
    - and never the thing being compared.

    `mine` follows from the same identity: this checkout is carrying the work
    when its `HEAD` *contains* the staking commit, which is true of the local
    branch, its tracking ref, and a branch pushed under some third name alike.
    Matching branch names would answer only the first of those, and would
    answer it wrongly the moment `--source` credited the shared commit to the
    tracking ref - which is what it does whenever the local branch is ahead by
    so much as a merge.

    `staked` is `None` for a ref whose name carries the id and whose commits
    this checkout could not read. That is a claim it cannot date rather than
    one made at the beginning of time, so it sorts *behind* every dated claim:
    an unread ref put first would make every session that can read its own
    commits yield to it, which in a truncated clone is every session.
    """

    ref: str
    item_id: str
    staked: Stake | None = None
    last_commit: date | None = None
    mine: bool = False


@dataclass(frozen=True)
class Precedence:
    """Which branch carrying an item continues, and which yield to it.

    **The point is that two sessions compute this identically, so it is a total
    order rather than a judgment.** Everything else this module does about
    parallel sessions detects a collision; nothing said which of the two
    discovering it was the one to stop, and two sessions reasoning in prose
    from the same evidence can reach the same answer as each other or the
    opposite one, with no way to tell which happened until the merge. The
    failure that costs the most is not both continuing - that is merely today -
    but both standing down, after which the work is unstarted and each session
    believes the other has it.

    So the order is over commits: the earliest commit naming the item holds it,
    a tie breaks on that commit's hash. Both properties are load-bearing. It is
    the *earliest* commit rather than the newest, so a session that pushes
    after a break does not overtake one that started before it; and it is a
    commit rather than a push time, because git records no push time and
    because a commit's date is the same fact in both checkouts.

    Two sessions can still both continue, when one has pushed nothing the other
    can see. That is the state of the world before this existed, so it is not a
    regression, and it is what `PL-SK88`'s "push the first commit as soon as
    there is one" shrinks. What cannot happen is both yielding: yielding needs
    a carrier strictly ahead of your own in one order, and two carriers cannot
    each be ahead of the other.
    """

    item_id: str
    carriers: tuple[Carrier, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""
    branch: str = ""

    @property
    def holder(self) -> Carrier | None:
        """The carrier that continues, or `None` where nothing carries the item."""
        return self.carriers[0] if self.carriers else None

    @property
    def mine(self) -> Carrier | None:
        """This checkout's own claim, or `None` where it has staked none."""
        return next((carrier for carrier in self.carriers if carrier.mine), None)

    @property
    def yields(self) -> bool:
        """Whether this checkout is carrying the item and is not the one that continues.

        False where this checkout carries nothing, which is the ordinary state
        of a session that has not started: there is no work to hand over and
        nothing to yield. That case is what `branches_in_flight` already
        reports, and reporting it here as a yield would turn the first guard a
        session meets into an instruction to stop before it began.
        """
        mine = self.mine
        return mine is not None and mine is not self.holder


def _head_carries(stake: Stake | None, root: Path, run: Runner) -> bool:
    """Whether this checkout's `HEAD` holds the commit that staked a claim.

    Asked by containment rather than by comparing branch names, because a
    session's own work reaches it under several names - the local branch, its
    tracking ref, a branch pushed under a third one - and the walk credits the
    commit to exactly one of them. A name comparison therefore reports "not
    yours" for a session's own branch as soon as it is ahead of its tracking
    ref by anything at all, including the merge that keeps it current, and a
    session told to yield to itself would stop for nobody.

    `merge-base` rather than `--is-ancestor`, whose answer is an exit code:
    every failure in this module collapses to the empty string, and an exit
    code that means "no" would be indistinguishable from git not running.
    """
    if stake is None:
        return False
    return run(["merge-base", stake.commit, "HEAD"], root).strip() == stake.commit


def precedence(
    root: Path,
    item_id: str,
    *,
    include_remote: bool = True,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> Precedence:
    """Every branch carrying one item, in the order that decides which continues.

    `branches_in_flight` reports one branch per item deliberately - it is
    answering "is this startable", and a second name adds nothing to that. Here
    the second name *is* the answer, so the same evidence is read again without
    that collapse, and with the timestamps a day-resolution report has no use
    for.

    **Only what is pushed can settle it, and this reads local refs anyway.** A
    claim nobody else can fetch cannot enter the other session's ordering, so
    two sessions reading only remote refs is the configuration in which they
    always agree. But a session's own unpushed branch is exactly what it needs
    to be told about - that its claim is invisible, and one push makes it real
    - and dropping local refs would hide the case rather than fix it. The
    asymmetry it leaves is the benign one: a session whose rival has pushed
    nothing sees no rival and continues, which is where the world already was.
    """
    run = runner or _run_git
    identifier = item_id.upper()
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    walk = _unmerged_commits(refs.unlanded, base, root, run, items_dir=items_dir)
    unreadable = refs.unreadable | walk.unbounded
    readable = {name for name in refs.unlanded if name not in walk.unbounded}

    # Candidate order, so that the ref a group is *named* by is chosen the same
    # way `branches_in_flight` chooses it: a local branch ahead of its own
    # tracking ref.
    staked: dict[str, Stake | None] = {}
    grouped: dict[str, list[str]] = {}
    moved: dict[str, date] = {}
    for name in refs.candidates:
        if name not in readable and name not in unreadable:
            continue
        match = BRANCH_ID_RE.search(name)
        by_name = match is not None and match.group(1).upper() == identifier
        claims: list[Stake] = []
        if name in readable:
            # A branch named for the item has been carrying it since its first
            # commit; a branch named for anything else has been carrying it
            # only since the commit that said so, which is what dates a rider
            # picked up mid-branch from the branch it rode in on.
            if by_name and (opened := walk.opened.get(name)) is not None:
                claims.append(opened)
            if (subject := walk.staked.get((name, identifier))) is not None:
                claims.append(subject)
        if not claims and not by_name:
            continue
        stake = min(claims) if claims else None

        # The commit is the identity of the claim, so one piece of work reached
        # by two refs groups under it whatever those refs are called. A claim
        # with no readable commit can only be grouped by its own name, which is
        # right: nothing proves it is the same work as anything else.
        key = stake.commit if stake is not None else f"\x00{name}"
        grouped.setdefault(key, []).append(name)
        staked[key] = stake
        if (day := walk.last.get(name)) is not None and day > moved.get(key, date.min):
            moved[key] = day

    branch = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    if branch == "HEAD":
        # A detached HEAD is not a branch, and nothing here needs it to be one:
        # the claims are matched against what HEAD *contains*.
        branch = ""
    carriers = sorted(
        (
            Carrier(
                ref=names[0],
                item_id=identifier,
                staked=staked[key],
                last_commit=moved.get(key),
                mine=_head_carries(staked[key], root, run),
            )
            for key, names in grouped.items()
        ),
        key=lambda carrier: (carrier.staked is None, carrier.staked or _UNDATED, carrier.ref),
    )

    # One session, one claim. A branch whose commits reach two of these is
    # carrying one piece of work that git happened to credit to two refs, and
    # the earliest of them is when this checkout began carrying it - so the
    # later ones are dropped rather than listed as rivals of the first.
    seen_mine = False
    collapsed: list[Carrier] = []
    for carrier in carriers:
        if carrier.mine:
            if seen_mine:
                continue
            seen_mine = True
        collapsed.append(carrier)

    return Precedence(
        item_id=identifier,
        carriers=tuple(collapsed),
        unreadable=tuple(name for name in refs.candidates if name in unreadable),
        base=base,
        branch=branch,
    )


@dataclass(frozen=True)
class BranchFiles:
    """What one in-flight ref has actually changed since the default branch.

    `item_ids` is every item `branches_in_flight` attributed to this ref, so a
    reader told their file is being edited can also be told by whom. It may be
    empty in principle and is not in practice: a ref reaches here only because
    an id was read from its name or its subjects.
    """

    branch: str
    item_ids: tuple[str, ...]
    paths: tuple[str, ...]


@dataclass(frozen=True)
class FlightFiles:
    """What the in-flight branches are changing, and which could not be read.

    This is the *observed* half of the contention question, against `touches`,
    which is the declared half. The two fail in opposite directions and that is
    why both are worth having. A `touches` list is a prediction written before
    the work, so it is complete about intent and silent about drift; a branch
    diff is a measurement taken during the work, so it is exact about what has
    happened so far and says nothing about what the branch will touch next.
    Neither certifies a pair as safe, and this one does not either: it names
    what has *already* collided.

    `unreadable` carries the same obligation it does on `FlightReport`, for the
    same reason. `_run_git` answers a failure with an empty string, so an
    unreadable diff and a branch that changed nothing arrive here identically -
    and reporting the first as the second would turn a gap in the evidence into
    a clean bill of health, which is the one thing this package refuses to do.
    """

    branches: tuple[BranchFiles, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""


def files_in_flight(
    root: Path, report: FlightReport, *, runner: Runner | None = None
) -> FlightFiles:
    """The files each in-flight branch has changed, read from the branch itself.

    Kept out of `branches_in_flight` deliberately. That read is on the hot path
    of `next`, `list`, `triage`, `status` and the session-start digest, and this
    one costs a `git diff` per unmerged ref - so it is paid by the two callers
    that ask the file question and by nobody else.

    A ref `branches_in_flight` could not read is not read here either. Its
    commits are the thing the checkout is missing, and a three-dot diff needs
    exactly the merge-base that already failed to resolve, so asking again
    would produce an empty answer indistinguishable from a branch that changed
    nothing.

    The diff is `base...ref` rather than `base..ref`: the two-dot form re-reports
    every file the default branch has changed since the fork as though the
    branch had changed it, which for a session started a day ago is most of the
    tree. The three-dot form is the branch's own work, which is the question.
    """
    run = runner or _run_git
    base = report.base
    if not base:
        return FlightFiles()

    ids: dict[str, list[str]] = {}
    for branch in report.branches:
        ids.setdefault(branch.name, []).append(branch.item_id)

    unread = set(report.unreadable)
    found: list[BranchFiles] = []
    for name, item_ids in ids.items():
        if name in unread:
            continue
        paths = tuple(
            sorted(
                {
                    line.strip()
                    for line in run(["diff", "--name-only", f"{base}...{name}"], root).splitlines()
                    if line.strip()
                }
            )
        )
        # An empty diff is either a branch whose commits cancel out or a git
        # that failed, and the two must not be conflated. A ref carrying
        # commits the base does not have owes a non-empty file list, so when it
        # does not, the read is named as unread rather than reported as clean.
        if not paths and _has_own_commits(name, base, root, run):
            unread.add(name)
            continue
        found.append(BranchFiles(branch=name, item_ids=tuple(sorted(item_ids)), paths=paths))

    return FlightFiles(
        branches=tuple(sorted(found, key=lambda entry: entry.branch)),
        unreadable=tuple(sorted(unread)),
        base=base,
    )


def _has_own_commits(name: str, base: str, root: Path, run: Runner) -> bool:
    """Whether the ref holds commits the default branch does not.

    Only asked to disambiguate an empty diff, so the cost is paid on the rare
    branch rather than on every one.
    """
    count = run(["rev-list", "--count", f"{base}..{name}"], root).strip()
    return count.isdigit() and int(count) > 0


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


# What a branch should do about where it stands, decided from the counts rather
# than from the words used to say it. `render` turns one of these into a
# sentence and a command; keeping the choice here is what lets a test assert
# the decision without matching prose, and what stops two callers wording the
# same state differently.
CURRENT = "current"
RESTART = "restart"
PULL = "pull"
MERGE = "merge"


@dataclass(frozen=True)
class BranchState:
    """Where the working branch stands against the default branch, and what moved.

    `declined` carries the meaning it does everywhere else here: the question
    could not be answered, and why. A checkout sharing no readable history with
    the default branch is the case that matters, because `git rev-list
    --left-right --count A...B` does not fail there - it prints the size of
    each side of an unrelated pair, which reads exactly like a real answer. A
    fabricated "98 ahead" tells a session it is carrying work it does not have,
    which argues against merging in the very case this exists to catch.

    `landed` is what makes it worth running twice. The counts say the base
    moved; the ids say *what* moved, which is what a session waiting on another
    session actually wants to know, and it costs one `git log` over a range
    already computed.

    `fetched` is not about git's answer but about how old the refs behind it
    are. This reads what the checkout holds and never fetches - the decision
    has to stay answerable from a bare checkout with no network - so a caller
    that did not refresh `origin/main` first gets an answer as stale as its
    last fetch, and saying so is the difference between a report and a guess.

    `absent` separates the two shapes of "no position" that the session-start
    hook has always distinguished by staying silent. A detached HEAD, a
    checkout with no base, and the default branch itself with no remote copy
    are cases where *no comparison exists*, and a digest resent on every turn
    should not carry a line saying so. A clone that shares no readable history
    is the other shape: the comparison exists and could not be made, which is
    the one that has to be said out loud.

    It records that the caller *attempted* a refresh, not that one arrived: a
    quiet `git fetch` prints nothing whether it succeeded or failed, and no
    read here can tell those apart. So it is reported only in the negative -
    nothing tried - which is the claim that can be made. A fetch that tried and
    failed leaves the answer stale by exactly one fetch, which is the error the
    session-start hook has always accepted.
    """

    branch: str = ""
    base: str = ""
    behind: int = 0
    ahead: int = 0
    landed: tuple[str, ...] = ()
    fetched: bool = False
    declined: str = ""
    absent: bool = False

    @property
    def disposition(self) -> str:
        """Which of the four states this is, or `""` when there is no answer."""
        if self.declined:
            return ""
        if self.behind == 0:
            return CURRENT
        if self.is_default:
            return PULL
        return RESTART if self.ahead == 0 else MERGE

    @property
    def is_default(self) -> bool:
        """Whether the working branch is the default branch itself."""
        return bool(self.branch) and self.base.rsplit("/", 1)[-1] == self.branch


def _landed_since(
    fork: str, base: str, root: Path, run: Runner, limit: int = 40
) -> tuple[str, ...]:
    """The ids leading the subjects the default branch gained since the fork.

    Only a leading id counts, for the reason `_unmerged_commits` gives: a
    subject mentioning an item further in is usually bookkeeping about somebody
    else's work. Bounded, because a branch forked long ago would otherwise
    print a release's worth of ids into a digest line - the newest are the ones
    a session waiting on something wants.
    """
    output = run(["log", f"-n{limit}", "--format=%s", f"{fork}..{base}", "--"], root)
    found: list[str] = []
    for line in output.splitlines():
        for identifier in leading_ids(line):
            if identifier not in found:
                found.append(identifier)
    return tuple(found)


def fetch_remote(root: Path, *, runner: Runner | None = None) -> None:
    """Refresh the remote-tracking refs, or fail quietly having tried.

    The one read in this module that goes to the network, kept apart from the
    rest for exactly that reason: a caller that must not touch it simply does
    not call this. Every branch tip rather than `main` alone, and deliberately
    not `--prune` - a branch deleted on the remote leaves a tracking ref that
    is the only surviving copy of anything committed on it, which is the case
    `stranded` exists to catch.
    """
    run = runner or _run_git
    run(["fetch", "--quiet", "origin"], root)


def branch_state(root: Path, *, runner: Runner | None = None, fetched: bool = False) -> BranchState:
    """Where the working branch stands against the default branch.

    This was fifty lines of bash in the session-start hook, which is the only
    place it could run: at session start, once, on a condition that develops
    *during* a session. A session opened to discuss the next piece of work
    while another session finishes something is told its base is current, talks
    for a while, and starts implementing against a base that moved - and the
    staleness surfaces at push time as a merge conflict, which is the rework
    cycle the check exists to prevent.

    So the decision lives here, where a command can ask it again at any moment
    and a test can hold it to an answer. The hook keeps only the fetch.

    **It never fetches.** The rule the rest of this module follows - a read
    that must work from a bare checkout with no network - applies to the
    decision, so refreshing `origin/main` is the caller's, and `fetched` says
    whether the caller did it. What is reported is therefore stale by exactly
    one fetch at worst, which is an acceptable error for a report and would be
    an unacceptable one for a claim.
    """
    run = runner or _run_git
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    if not branch or branch == "HEAD":
        return BranchState(
            fetched=fetched,
            absent=True,
            declined="no branch is checked out here, so there is nothing to compare",
        )

    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return BranchState(
            branch=branch,
            fetched=fetched,
            absent=True,
            declined=f"this checkout has no {base} to compare against",
        )

    # The default branch with no remote copy of it: `default_base` fell all the
    # way back to the local branch, which is the one already checked out, and
    # comparing a ref with itself answers nothing. Distinct from being current,
    # because there is no other side to have moved.
    if base == branch:
        return BranchState(
            branch=branch,
            base=base,
            fetched=fetched,
            absent=True,
            declined=f"{branch} is the default branch and has no remote copy to compare with",
        )

    # The fork point is asked for before the counts, and both guard and answer
    # come from the one read: `rev-list --left-right --count` on refs sharing
    # no history reports each side's whole length instead of failing, and a
    # count invented that way is worse than no count at all.
    fork = run(["merge-base", "HEAD", base], root).strip()
    if not fork:
        return BranchState(
            branch=branch,
            base=base,
            fetched=fetched,
            declined=(
                f"this clone shares no readable history with {base}, so its position "
                "cannot be counted - something ran a `--depth` fetch, and "
                "`git fetch --deepen=100 origin` restores the answer"
            ),
        )

    counts = run(["rev-list", "--left-right", "--count", f"{base}...HEAD"], root).split()
    if len(counts) != 2 or not all(part.isdigit() for part in counts):
        return BranchState(
            branch=branch,
            base=base,
            fetched=fetched,
            absent=True,
            declined="git would not count the two sides",
        )

    behind, ahead = int(counts[0]), int(counts[1])
    return BranchState(
        branch=branch,
        base=base,
        behind=behind,
        ahead=ahead,
        landed=_landed_since(fork, base, root, run) if behind else (),
        fetched=fetched,
    )


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


@dataclass(frozen=True)
class BaseRelease:
    """What the default branch already records as shipped, or that it is unread.

    `known` carries the obligation every read in this module carries.
    `_run_git` answers a failure with the empty string, so a base this
    checkout cannot read and a base that has never cut a release arrive here
    identically - and reporting the first as the second would let a duplicate
    release through under a check that appeared to have run, which is the one
    thing a guard must never do.

    The version file is what decides it. A project being cut releases for has
    one; a ref that cannot produce it is a ref this checkout has no answer
    about, whether because there is no remote, no network since the clone, or
    no such branch. An empty `notes` under `known` is the other case and a
    real answer: the base holds no notes for anything.

    Read from the ref as it stands in this checkout, so it is stale by
    whatever the last fetch left behind. That is a floor on what the answer
    can prove, not a flaw in it: what it reports present is present.
    """

    base: str = ""
    #: The version the base's own version file declares, unparsed of its `v`.
    version: str = ""
    #: Notes file names as they sit in `notes_dir` on the base - `v0.3.7.md`,
    #: not the path to it, because the directory is the caller's own constant.
    notes: frozenset[str] = frozenset()
    known: bool = False


def released_on_base(
    root: Path,
    *,
    version_file: str,
    notes_dir: str,
    base: str | None = None,
    runner: Runner | None = None,
) -> BaseRelease:
    """Which releases the default branch already holds, read from the ref itself.

    Two reads of one ref rather than of the working tree, and that is the
    whole point: the working tree is this session's own release in progress,
    which would answer "yes, already cut" to its own work. The base is what
    everyone else has, so it is the only place a second copy of a release can
    be seen from.

    Costs two `git` calls and no network, so a caller that has just fetched
    gets a current answer and one that cannot fetch still gets a sound one -
    older, and never wrong about what it names.
    """
    run = runner or _run_git
    ref = base or default_base(root, runner=run)

    declared = run(["show", f"{ref}:{version_file}"], root)
    if not declared.strip():
        return BaseRelease(base=ref)

    names = frozenset(
        line.strip().rsplit("/", 1)[-1]
        for line in run(["ls-tree", "--name-only", ref, f"{notes_dir}/"], root).splitlines()
        if line.strip()
    )
    return BaseRelease(base=ref, version=version_in(declared), notes=names, known=True)


@dataclass(frozen=True)
class BranchCut:
    """One ref carrying a release the default branch has not taken.

    `mine` is this checkout's own cut seen from outside - a local branch, its
    tracking ref, or a branch pushed under a third name - decided by whether
    `HEAD` contains the ref's tip rather than by comparing names, for the
    reason `Carrier.mine` gives: a session told to yield to itself would stop
    for nobody.

    `cut` dates the commit that wrote the notes, not the ref's tip, because
    the question a reader has is how old the *release* is. It separates a live
    session from a branch nobody will merge, and this reports it rather than
    deciding between them, the way `flight` and `stranded` do.
    """

    ref: str
    #: Versions without their `v`, so they compare against a version string.
    versions: tuple[str, ...]
    cut: date | None = None
    mine: bool = False


@dataclass(frozen=True)
class CutsInFlight:
    """Which refs are cutting a release nobody has merged, or which could not be read.

    **This is the guard no `PL-` id can carry.** A release cut carries none by
    design, so `branches_in_flight` and everything reading it are blind to the
    widest write in the repository, and two sessions cut v0.3.7 within an hour
    (`PL-66FP`). The evidence here is the notes file a ref introduces, which is
    the one artifact a cut cannot happen without.

    `unreadable` carries the obligation it carries everywhere else here: a ref
    whose history this checkout does not hold is named, never reported clean.
    """

    branches: tuple[BranchCut, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""


def cuts_in_flight(
    root: Path,
    *,
    notes_dir: str,
    on_base: frozenset[str] = frozenset(),
    include_remote: bool = True,
    runner: Runner | None = None,
) -> CutsInFlight:
    """Every release being cut on a ref the default branch has not taken.

    **`on_base` is what makes the answer usable, and leaving it out breaks
    this.** A squash merge keeps none of the branch's commits, so a merged
    release branch stays "unlanded" by `_work_already_on_base`'s test whenever
    it carries anything else the base did not take - measured 2026-09-04, the
    branch whose v0.3.9 release had merged twenty minutes earlier was still
    listed. A three-dot diff then reports its notes file forever, and a guard
    that fires on every release after the first is one nobody reads. So a
    version the base already holds is not in flight, by definition, and the
    caller passes what the base holds.

    Read from refs, so it is stale by exactly one fetch and blind to a session
    that has pushed nothing. Both are floors on what it can prove rather than
    flaws in it: what it names, it names on evidence a second checkout would
    read identically.
    """
    run = runner or _run_git
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)

    found: list[BranchCut] = []
    for name in refs.unlanded:
        versions = tuple(
            sorted(
                {
                    version
                    for line in run(
                        ["diff", "--name-only", f"{base}...{name}", "--", f"{notes_dir}/"], root
                    ).splitlines()
                    if (leaf := line.strip().rsplit("/", 1)[-1])
                    and leaf not in on_base
                    and (version := leaf.removesuffix(".md").lstrip("v"))
                }
            )
        )
        if not versions:
            continue
        tip = run(["rev-parse", name], root).strip()
        found.append(
            BranchCut(
                ref=name,
                versions=versions,
                cut=_cut_date(name, notes_dir, versions[0], root, run),
                mine=bool(tip) and run(["merge-base", tip, "HEAD"], root).strip() == tip,
            )
        )

    return CutsInFlight(
        branches=tuple(sorted(found, key=lambda entry: entry.ref)),
        unreadable=tuple(sorted(refs.unreadable)),
        base=base,
    )


def _cut_date(ref: str, notes_dir: str, version: str, root: Path, run: Runner) -> date | None:
    """When the notes for a version were written on a ref, or `None` if unreadable."""
    stamp = run(
        ["log", "-1", "--format=%cI", ref, "--", f"{notes_dir}/v{version}.md"], root
    ).strip()
    try:
        return datetime.fromisoformat(stamp).astimezone(UTC).date()
    except ValueError:
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


@dataclass(frozen=True)
class ClosureReport:
    """Which item closures already stand on the default base, or why that is unknown.

    Reading *whether* a closure landed is deliberately not gated on
    `is_shallow`, unlike `merged_pull_requests`. That reader needs history,
    which a shallow clone answers confidently and wrongly; this one needs a
    single tree read, which `git show <ref>:<path>` answers correctly however
    truncated the history behind the ref is. The distinction earns its own
    type: a shallow clone is the normal state of an agent session, so a reader
    that declined there would decline in exactly the case this exists to cover.

    Reading *which pull request* landed it is the other kind of question, and
    `shallow` is what keeps the two apart. A derived number is trustworthy at
    any depth - the commit was found, and finding it is proof enough. Its
    absence is not: at `fetch-depth: 1` there is one commit to search, so
    every closure but the newest yields nothing, and a caller that read that
    as "no commit names a number" would call correct provenance lost. It did:
    `main` was red on 97573ae and 3b37a75 for a `pr` recoverable from a commit
    the clone no longer held (`PL-99Y4`). So the emptiness is reported with
    the depth that produced it, and the caller decides - the rule `PL-J295`
    already set for `tags`, applied to the question beside it.
    """

    base: str = ""
    landed: frozenset[str] = frozenset()
    #: The pull request each landed closure's own merge commit names, where
    #: the base still holds that commit. Pairs rather than a mapping to keep
    #: the type hashable like everything else here; `numbers` unpacks it.
    derived: tuple[tuple[str, int], ...] = ()
    #: Whether the history behind `base` is truncated, or `None` where git
    #: will not say - straight from `is_shallow`, and read only to qualify
    #: what a *missing* `derived` entry is allowed to mean. Defaults to `None`
    #: so that a report built without it claims nothing.
    shallow: bool | None = None
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def numbers(self) -> dict[str, int]:
        return dict(self.derived)


def closures_on_base(
    root: Path,
    closures: Mapping[str, str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> ClosureReport:
    """Which of `closures` already read `status: done` on the default base.

    `closures` maps an item id to the file name that holds it, and is expected
    to carry only the items whose closure is in question: each one costs a
    `git show`, and the caller is the one that knows which those are.

    An item absent from the base is a closure that has not landed, which is
    the whole point rather than a failure to read it. So is one whose file is
    there under another name, because retitling an item renames its file and
    the old path stops resolving. Both are accepted rather than reported, which
    is the safe direction: this rule's failure mode is blocking a closure that
    is already correct.

    Each landed closure is also asked which pull request its own merge commit
    names, which is the question that decides whether a missing `pr` is a gap
    or a transcription still owed. It costs one history read for the whole
    set, made only when something landed, and it reuses the two parsers that
    already exist: the subject a squash merge writes carries the item ids it
    opens with and the number in trailing parentheses.

    Deriving nothing is a normal answer, not a failure, and `shallow` is
    recorded alongside so the caller can tell which kind of nothing it is. A
    complete history that names no number means none exists; a truncated one
    means the commit may simply be outside it, which at `fetch-depth: 1` is
    true of every closure but the newest.
    """
    run = runner or _run_git
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return ClosureReport(declined="no default branch this checkout can read")
    landed: set[str] = set()
    for identifier, name in closures.items():
        text = run(["show", f"{base}:{items_dir}/{name}"], root)
        if text and parse_item(text, name).status == "done":
            landed.add(identifier)
    return ClosureReport(
        base=base,
        landed=frozenset(landed),
        derived=_merges_naming(landed, closures, items_dir, base, root, run),
        shallow=is_shallow(root, runner=run),
    )


def _merges_naming(
    identifiers: set[str],
    closures: Mapping[str, str],
    items_dir: str,
    base: str,
    root: Path,
    run: Runner,
) -> tuple[tuple[str, int], ...]:
    """The pull request number each id's closure on `base` can be traced to.

    Two readings, tried in that order. The subject scan is first because it is
    one history read for the whole set: one commit can close two items - a
    subject may open with a run of ids - so a single merge answers for several,
    and each is recorded against the same number. Only the newest such commit
    counts: an id that led an earlier subject too, most often the capture that
    filed it, was not the merge that landed its work.

    **Recency is not enough, and the scan's answer is confirmed before it is
    believed.** Leading a subject proves the commit is *about* the item, never
    that it *closed* it, and several kinds of commit are about a closed item:
    the bookkeeping merge that writes its `pr` back, a follow-up fix, a triage
    that filed it. Measured 2026-09-04 over the 122 closed items on `main` that
    a leading-id subject names, the unconfirmed scan answered 21 of them with a
    number that is not their closure - `PL-1TF4` and `PL-J49T` with `250`, whose
    subject reads "record #249"; `PL-B0YN` and `PL-G1MF` with `188` from "record
    their pull request" against a true `186`; `PL-YLZQ` with `159`, the commit
    that triaged it, against a true `204` (`PL-GW37`). The rider closure this
    was raised for is one shape of that, not the whole of it.

    So each answer is put to the test `_number_closing` already uses on the
    file: the commit must read `status: done` in its own tree and not in its
    parent's. That is what distinguishes the closure from every other commit
    naming the item, it costs two `git show` for each id the scan answered, and
    it is asked only of items whose `pr` is missing - a handful, not the store.
    Over the same 122 it agreed with the file reading in every case where both
    could answer, and disagreed in none.

    Whatever the subjects do not answer - or answer unconfirmably - falls back
    to the item's own file, per `PL-2XTF`. A squash merge takes its subject from
    the pull request title, which is written by whoever opened it and need not
    lead with any id - `#220` was created from the Claude Code UI, closed three
    items, and left `main` red with an error no recovery could clear, because
    the one subject that landed named none of them. The file always knows: the
    commit that wrote `status: done` into it *is* the closure, and it carries
    `(#N)` like every other squash. That is strictly more evidence than the
    subject scan, not less, and it costs a read only for the ids the cheap pass
    missed.

    That fallback has a defect of its own, recorded as `PL-S5LB` rather than
    fixed here: it walks `git log -- <path>` without rename detection, so for an
    item whose file was renamed after it closed, the oldest commit the walk can
    see is the rename, whose parent does not hold the path at all. This change
    does not introduce it and reduces the wrong answers overall, but it does
    route more ids into it.
    """
    if not identifiers:
        return ()
    found: dict[str, int] = {}
    candidates: dict[str, tuple[str, int]] = {}
    for line in run(["log", "--format=%H%x1f%s", base], root).splitlines():
        revision, _, subject = line.partition("\x1f")
        subject = subject.strip()
        match = PR_SUBJECT_RE.search(subject)
        if match is None:
            continue
        number = int(match.group(1) or match.group(2))
        for identifier in leading_ids(subject):
            if identifier in identifiers:
                candidates.setdefault(identifier, (revision.strip(), number))
    for identifier, (revision, number) in candidates.items():
        name = closures[identifier]
        path = f"{items_dir}/{name}"
        if _done_at(revision, path, name, root, run) and not _done_at(
            f"{revision}^", path, name, root, run
        ):
            found[identifier] = number
    for identifier in sorted(identifiers - set(found)):
        recovered = _number_closing(closures[identifier], items_dir, base, root, run)
        if recovered is not None:
            found[identifier] = recovered
    return tuple(sorted(found.items()))


def _number_closing(name: str, items_dir: str, base: str, root: Path, run: Runner) -> int | None:
    """The number on the commit that wrote `status: done` into one item's file.

    Walks the commits on `base` that touched the file, newest first, and takes
    the first one that closed it - `done` in that commit's tree and not in its
    parent's. The parent comparison is what keeps a *later* edit from being
    read as the closure: backfilling a `pr` field, or correcting a brief, both
    touch the file long after the work landed and both carry their own `(#N)`.
    Answering with one of those would record a false provenance, which is worse
    than the missing one this exists to supply.

    A commit whose parent this checkout does not hold reads as "not done
    there", because `_run_git` answers a failed `show` with empty output. That
    is the safe direction on a truncated clone: it can only make the walk
    accept an older commit it should have skipped, never invent a number for an
    item that has none, and `ClosureReport.shallow` already tells the caller
    the history was not whole.
    """
    path = f"{items_dir}/{name}"
    for line in run(["log", "--format=%H%x1f%s", base, "--", path], root).splitlines():
        revision, _, subject = line.partition("\x1f")
        match = PR_SUBJECT_RE.search(subject.strip())
        if match is None:
            continue
        if _done_at(revision, path, name, root, run) and not _done_at(
            f"{revision}^", path, name, root, run
        ):
            return int(match.group(1) or match.group(2))
    return None


def _done_at(revision: str, path: str, name: str, root: Path, run: Runner) -> bool:
    """Whether the item at `path` reads `status: done` in that revision's tree."""
    text = run(["show", f"{revision}:{path}"], root)
    return bool(text) and parse_item(text, name).status == "done"


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


@dataclass(frozen=True)
class BaseRecord:
    """What the default base's copy of one closed item records as its proof."""

    identifier: str
    verify: str


@dataclass(frozen=True)
class RecordReport:
    """What the base recorded as the `verify:` of the closed items changed here.

    A closed item's command is a record of an experiment that was performed:
    this command was run, it failed before the work and passed after. It is a
    fact about a tree that no longer exists, not a claim about `main` today,
    and it stops resolving as a matter of course - measured over this store,
    14 of the 179 closed items carrying one no longer resolve, and every one
    of the 14 is a later change correctly consuming the state the earlier item
    established. Four are `grep '^blocked-by: PL-...'` commands whose blocker
    was resolved, which is to say commands written to stop resolving.

    So the reading this supports is not "has the command rotted" - it has, and
    that is the system working - but "is this branch about to rewrite one".
    Re-pointing a closed command at whatever covers the ground now replaces the
    command that proved the work with one that never ran it, which is a false
    provenance where there was a true one.

    `declined` carries the same meaning it does everywhere else here: a check
    that could not run, reported as such rather than as a clean result.
    """

    base: str = ""
    #: One entry per closed item this checkout changed that the base also reads
    #: `done`. An id absent from the base, open on it, or untouched here is
    #: absent from this, so a missing entry is "nothing to compare" rather than
    #: "compared and matched".
    records: tuple[BaseRecord, ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def commands(self) -> dict[str, str]:
        return {record.identifier: record.verify for record in self.records}


def _changed_items(root: Path, base: str, items_dir: str, run: Runner) -> set[str]:
    """The item ids this checkout has changed, committed on the branch or not.

    Two diffs, because `make check` runs at two moments and each is blind to
    the other's case. `<base>...HEAD` is what the branch's commits changed,
    which is what CI sees on a pull request; `HEAD` is what the working tree
    holds and has not committed, which is what a session sees running `make
    check` before committing - the moment an edit can still be undone cheaply.

    Neither is `<base>` against the working tree, which would have been one
    call for both. That form also lists the files *the base* changed and this
    branch did not, so a branch merely behind `main` would be asked to answer
    for somebody else's edit. A check that accuses the wrong branch is one
    every session learns to route around, which is the failure `CLAUDE.md`
    reserves its retirement rule for.

    A `...` with no merge base to resolve returns nothing, because `_run_git`
    answers a failed command with empty output. That is the safe direction: the
    caller then under-reports, which leaves the tree exactly as it is today,
    rather than reporting a rewrite that did not happen.
    """
    changed: set[str] = set()
    for revision in (f"{base}...HEAD", "HEAD"):
        for line in run(["diff", "--name-only", revision, "--", items_dir], root).splitlines():
            path = line.strip()
            match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1]) if path else None
            if match is not None:
                changed.add(match.group(1))
    return changed


def records_on_base(
    root: Path,
    closed: Mapping[str, str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> RecordReport:
    """What the default base records as the `verify:` of each closed item changed here.

    `closed` maps an item id to the file name holding it, for every item that
    reads `done` in the working tree. Narrowing that to the ones this checkout
    actually changed happens here rather than in the caller, because it is a
    question about git rather than about the store: the store cannot tell
    which of two hundred closed items this branch has an opinion about, and
    asking after all of them would be a `git show` each on every `make check`.

    Resolution is by id, never by path. Retitling an item renames its file, so
    the working tree's path need not exist on the base at all and a comparison
    by path would read the rename as an item the base does not hold - the gap
    `closures_on_base` accepts, closed here because one `ls-tree` answers it
    for the whole store and is read only when something changed.

    Needs no history behind the base: one tree listing and one `git show` per
    changed closed item, which is what lets it answer in the shallow clone an
    agent session starts from.
    """
    run = runner or _run_git
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return RecordReport(declined="no default branch this checkout can read")
    changed = _changed_items(root, base, items_dir, run) & set(closed)
    if not changed:
        return RecordReport(base=base)
    at_base = _items_at(base, root, items_dir, run)
    records: list[BaseRecord] = []
    for identifier in sorted(changed):
        path = at_base.get(identifier)
        if path is None:  # closed here, and the base has never held the item
            continue
        text = run(["show", f"{base}:{path}"], root)
        if not text:
            continue
        recorded = parse_item(text, path.rsplit("/", 1)[-1])
        if recorded.status == "done":
            records.append(BaseRecord(identifier=identifier, verify=recorded.verify))
    return RecordReport(base=base, records=tuple(records))


@dataclass(frozen=True)
class ClosedByReport:
    """Which items one commit closed, or why that could not be read.

    The counterpart to `ClosureReport`, asked from the other end. That one
    starts from a set of closures and walks history backwards looking for the
    merge that landed each; this starts from one merge and reads what it
    closed. A caller that already knows the number - the merge-time job, which
    is handed it by the event that fired it - needs only this one, and needs no
    subject parsing at all.
    """

    revision: str = ""
    #: Item id to the path holding it in that commit's tree. Pairs rather than
    #: a mapping, to stay hashable like every other report in this module;
    #: `paths` unpacks it.
    closed: tuple[tuple[str, str], ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def paths(self) -> dict[str, str]:
        return dict(self.closed)


def closed_by(
    revision: str, root: Path, *, items_dir: str = "docs/items", runner: Runner | None = None
) -> ClosedByReport:
    """The items whose closure `revision` itself landed, as id to path.

    Closed *here* means `status: done` in this commit's tree and not in its
    parent's. That is the question a merge-time caller is asking, and the
    stricter half of it is the parent: a pull request records its number on
    what it closed, never on what was already closed when it branched.
    `_number_closing` asks the same question of one file, walking backwards
    until it finds the commit that closed it; this asks it of one commit,
    forwards, and needs no subject to parse because the caller already has the
    number.

    The comparison is by id rather than by path. A title edit renames an item's
    file, so a path missing from the parent tree proves nothing about whether
    the item was already done - it may have been done under its old name.
    Reading the parent's ids costs one `ls-tree` and removes the whole class.

    `git diff` against the first parent rather than `diff-tree`, because a true
    merge commit shows an empty `diff-tree` by default and would read as
    closing nothing. Only the files the commit touched are examined, which is
    what keeps this at a handful of tree reads instead of one per item: a file
    the commit did not touch cannot have been closed by it.

    A revision whose parent this checkout does not hold declines rather than
    answering. At `fetch-depth: 1` there is nothing to compare against, and
    "no parent" would otherwise read as "everything done here was closed here"
    - the confident wrong answer this module refuses to give, and here it would
    stamp one pull request number across the whole store.
    """
    run = runner or _run_git
    if not run(["rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}"], root).strip():
        return ClosedByReport(declined=f"what `{revision}` closed: it names no commit here")
    if not run(["rev-parse", "--verify", "--quiet", f"{revision}^^{{commit}}"], root).strip():
        return ClosedByReport(
            declined=(
                f"what `{revision}` closed: its parent is outside this checkout, so its tree "
                f"has nothing to be compared against"
            )
        )

    touched: dict[str, str] = {}
    listing = run(["diff", "--name-only", f"{revision}^", revision, "--", items_dir], root)
    for line in listing.splitlines():
        path = line.strip()
        name = path.rsplit("/", 1)[-1]
        match = ITEM_FILE_RE.match(name) if path else None
        if match is not None and _done_at(revision, path, name, root, run):
            touched[match.group(1)] = path
    if not touched:
        return ClosedByReport(revision=revision)

    before = _items_at(f"{revision}^", root, items_dir, run)
    closed = {
        identifier: path
        for identifier, path in touched.items()
        if not _done_before(before.get(identifier), revision, root, run)
    }
    return ClosedByReport(revision=revision, closed=tuple(sorted(closed.items())))


def _done_before(path: str | None, revision: str, root: Path, run: Runner) -> bool:
    """Whether the item held at `path` already read `done` in `revision`'s parent.

    An id absent from the parent tree is new in this commit, which cannot have
    been done before it.
    """
    if path is None:
        return False
    return _done_at(f"{revision}^", path, path.rsplit("/", 1)[-1], root, run)


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


@dataclass(frozen=True)
class LostItem:
    """An item file this ref's history held, and its tree no longer does.

    `blob` rather than the commit that held it, for two reasons. It is what
    recovers the content - `git cat-file -p <blob>` works for as long as any
    checkout holds the object, and keeps working after the branch is deleted,
    which a `git show <commit>:<path>` recovery does not. And finding the
    commit would cost a `--find-object` history walk per blob, which is the
    expense `PL-01CK` measures against exactly this kind of read.
    """

    identifier: str
    path: str
    blob: str


@dataclass(frozen=True)
class LostReport:
    """Items removed from the tree without any commit deleting them.

    `truncated` carries the same honesty `StrandedReport.refs_read` does: a
    clean answer from a clone holding twenty commits and a clean answer from
    one holding the whole history are different claims, and only one of them
    means the store is sound.

    `declined` means the check could not run, reported as such rather than as
    a clean result.
    """

    items: tuple[LostItem, ...] = ()
    ref: str = ""
    truncated: bool = False
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def lost(
    root: Path, *, ref: str = "HEAD", items_dir: str = "docs/items", runner: Runner | None = None
) -> LostReport:
    """Item ids this ref's history holds a file for, and its tree does not.

    **Why the object walk rather than a diff.** A conflict resolution deletes
    the file in the *merge's own tree*, and a merge is not diffed against
    either parent by default, so `git log --diff-filter=D -- docs/items/`
    returns nothing for the case this exists to catch. Reproduced 2026-09-02
    against a scratch repository: the deletion is invisible to the diff walk
    and plainly visible in the object walk, which lists every blob reachable
    from the ref with the path it was stored under.

    **Why it must be asked of a branch, not of the default branch.** After a
    squash merge the branch's commits are not ancestors of anything, so its
    objects stop being reachable and the evidence is gone. Measured on this
    repository: `PL-Q8QX` was captured on the v0.3.0 release branch, dropped
    by a merge resolution, and is reachable from no commit `main` holds - a
    check run on `main` reports it clean and is wrong to. So this runs on the
    branch, in CI, on the pull request, before the squash collapses the
    history. It still catches an ordinary merge on the default branch; it
    cannot catch a squashed one, and nothing run there can.

    **Comparison is by id, never by path.** An item file is renamed whenever
    its title changes, which adds one path and removes another. By path that
    reads as a loss; by id it reads as what it is.
    """
    run = runner or _run_git
    present = _items_at(ref, root, items_dir, run)
    if not present:
        # The same guard `stranded` keeps: an unreadable store makes every id
        # in the history look lost, which is the one output worse than none.
        return LostReport(
            ref=ref, declined=f"no items found on {ref}, so its whole history would read as lost"
        )

    prefix = items_dir.rstrip("/") + "/"
    ever: dict[str, tuple[str, str]] = {}
    for line in run(["rev-list", "--objects", ref], root).splitlines():
        blob, _, path = line.partition(" ")
        path = path.strip()
        if not path.startswith(prefix):
            continue
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
        if match is not None:
            # `rev-list` walks newest commit first, so the first blob seen for
            # an id is the last content it had. That is the version worth
            # handing back for recovery.
            ever.setdefault(match.group(1), (blob.strip(), path))

    gone = tuple(
        LostItem(identifier=identifier, path=path, blob=blob)
        for identifier, (blob, path) in sorted(ever.items())
        if identifier not in present
    )
    return LostReport(items=gone, ref=ref, truncated=is_shallow(root, runner=run) is not False)


@dataclass(frozen=True)
class OrphanedCommit:
    """A commit on a branch carrying content the default branch does not hold."""

    commit: str
    subject: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class OrphanedBranch:
    """A branch the default branch took part of and not the rest.

    `landed` is what makes this different from an ordinary branch in flight,
    and it is the whole of the evidence. A branch nobody has merged has landed
    nothing; a branch merged whole is not reported here at all, because
    `_unlanded_refs` already excluded it. Both sides non-empty means the base
    holds some of what this branch introduced and not the rest - which is what
    a branch looks like after its pull request merged and something pushed to
    it afterwards.
    """

    ref: str
    landed: tuple[str, ...]
    outstanding: tuple[str, ...]
    commits: tuple[OrphanedCommit, ...]


@dataclass(frozen=True)
class OrphanedReport:
    """Work that exists only on a branch whose pull request has already merged.

    The counterpart to `StrandedReport`, asked of the tree instead of the
    store. That one finds an *item* nobody merged, by comparing ids across
    trees; this finds any *content* nobody merged, and the asymmetry it closes
    is the finding in `PL-3D2M`: the queue had a stranded-work detector and the
    rest of the repository had none, so a dropped commit that touched
    `docs/items/` surfaced in the next session and one that touched a skill, a
    rule or `src/` did not.

    `refs_read` and `unreadable` carry the same meaning they do for
    `StrandedReport` and `FlightReport`: what was compared, and which refs the
    checkout could not compare, so a clean answer from a container holding two
    refs is not mistaken for one from a checkout holding twenty.
    """

    branches: tuple[OrphanedBranch, ...] = ()
    refs_read: int = 0
    unreadable: tuple[str, ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def _commits_touching(
    ref: str, base: str, paths: frozenset[str], root: Path, run: Runner
) -> tuple[OrphanedCommit, ...]:
    """The ref's commits *none* of whose work reached the base, newest first.

    **Wholly, not partly, and that is the whole of the rule.** A commit whose
    changes are partly on the base is a commit the merge *took*: the squash
    landed it and merged it with whatever the base had changed underneath, so
    the files they both touched differ from the branch's copies while the work
    itself is there. A commit none of whose changes reached the base is one
    nothing took. Only the second is work left behind.

    That distinction was learned from this check's own first live firing
    (`PL-JHJ3`). `origin/claude/snapshot-run-history-copy-dw6djz` carried the
    v0.3.8 release commit, which `#312` squash-merged while `#311` was landing
    edits to the same `ROADMAP.md` prose; the merge wrote the combined text, so
    three of that commit's ten paths read as never landed and the branch was
    reported as carrying lost work. `main` was *ahead* of it, not missing
    anything. Ten paths touched and seven landed is the signature of a merge
    that happened, and no content comparison of the outstanding three can see
    that - only counting them against the rest of the same commit can.

    A merge commit lists no paths of its own under `--name-only`, which is the
    wanted behaviour: merging the default branch into a branch introduces no
    work to leave behind, and such a commit is neither reported nor counted.

    The cost is recall, in one narrow shape: a commit pushed after the merge
    that happens to leave one file in a state the base has held reads as partly
    landed and goes unreported. Silence is this check's expensive direction
    everywhere else, and the trade is taken here only because the alternative
    was an advisory firing in every session's digest - which `CLAUDE.md` calls
    a defect in the check rather than coverage.

    `\\x1e` opens each record so a subject containing a newline cannot be read
    as the start of another commit.
    """
    output = run(["log", "--format=%x1e%H%x1f%s", "--name-only", f"^{base}", ref, "--"], root)
    found: list[OrphanedCommit] = []
    for record in output.split("\x1e"):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        commit, _, subject = header.partition("\x1f")
        touched = tuple(line.strip() for line in body.splitlines() if line.strip())
        if touched and all(path in paths for path in touched):
            found.append(
                OrphanedCommit(commit=commit.strip(), subject=subject.strip(), paths=touched)
            )
    return tuple(found)


def orphaned(
    root: Path, *, include_remote: bool = True, runner: Runner | None = None
) -> OrphanedReport:
    """Branches carrying work the default branch took only part of.

    **The failure it detects.** A pull request merges; the session pushes one
    more commit to the same branch afterwards. Nothing merges a merged pull
    request a second time, so that commit lands nowhere - and it is silent in
    every direction that would normally catch a mistake. There is no conflict,
    no red check and no advisory; the branch reads as merged, the pull request
    reads as merged, and the next session starts from a default branch missing
    work everyone believes landed. Observed 2026-09-04 on `#284`, whose
    follow-up `#286` says it outright: "That pull request merged at its first
    commit, so the behavior change pushed to the same branch afterwards never
    landed."

    **Why the branch ref is the evidence and the pull request is not.** GitHub
    freezes `refs/pull/<n>/head` when the pull request closes, so the commit
    pushed after the merge appears in no pull-request ref and no merge-time
    check could see it. Measured against this repository: all 311 pull refs
    survive branch deletion, and comparing each merged head against the commit
    that landed it found no discrepancy in any of the 204 then merged - the loss
    is not visible from that side at all. What does survive is the branch,
    precisely because the post-merge push recreates or keeps it.

    That 204 is a sample and not a proof, and saying so is the point: the very
    next merge produced a shape it did not contain - a release branch whose
    prose the base had edited under it - and the check fired falsely on it. The
    population a measurement covered is part of what it measured.

    **The rule, in two parts, and the second was learned the hard way.** A
    branch whose introduced content is partly on the base and partly not, *and*
    which carries a commit none of whose paths reached the base at all. The
    content split alone selects candidates - a branch nobody merged has landed
    nothing and is ordinary work in flight; a branch merged whole never reaches
    here - but it cannot tell a commit nothing took from a commit the merge took
    and *merged*, which is what a squash against a base that moved underneath
    produces. `_commits_touching` carries that half and the branch that taught
    it (`PL-JHJ3`).

    **What it can get wrong.** Two sessions running `bin/docket record` write
    the same tool-dictated line, so one branch can hold a blob identical to one
    the other landed and read as partly landed - which now costs nothing unless
    a whole commit is also unaccounted for. In the other direction, a commit
    pushed after the merge that happens to leave one file in a state the base
    has held is not reported. Silence is the expensive direction here and the
    trade is taken deliberately; `_commits_touching` says why. The reader
    decides, the way they do for `flight` and `stranded`.
    """
    run = runner or _run_git
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    if not refs.listed:
        # No git, no repository, or a listing git could not answer. An empty
        # result would otherwise read as "every branch is accounted for",
        # which is the confident wrong answer this module refuses to give.
        return OrphanedReport(declined="no branch refs this checkout can read")
    branches: list[OrphanedBranch] = []
    for name in refs.unlanded:
        landed, outstanding = refs.landing.get(name, ((), ()))
        if not (landed and outstanding):
            continue
        left = _commits_touching(name, base, frozenset(outstanding), root, run)
        # A split alone is not enough, and the branch that taught this is named
        # in `_commits_touching`. The split says some of the branch's content is
        # not on the base, which a squash merged against a moving base produces
        # on its own; a commit *wholly* absent says nothing took it. Without a
        # commit to name there is also nothing to hand a reader, which is the
        # same fact from the other side.
        if left:
            # The branch's outstanding side is narrowed to the paths of the
            # commits actually reported. The wider set includes files a merged
            # commit touched that the base then merged differently, which are
            # not missing from anywhere and must not be offered for recovery.
            carried = tuple(sorted({path for commit in left for path in commit.paths}))
            branches.append(
                OrphanedBranch(ref=name, landed=landed, outstanding=carried, commits=left)
            )
    return OrphanedReport(
        branches=tuple(branches),
        refs_read=len(refs.candidates),
        unreadable=tuple(sorted(refs.unreadable)),
    )
