"""Who holds an item, read from the claims sessions record on their own branches.

`vcs` derives who is working on what from the shape of the work - which ids
lead the commit subjects, which paths a commit touched, how old a ref is - and
twenty items were each a new shape of work that some reader misread that way
(`PL-MB2W`). So the fact is recorded instead, by the only party that knows it:
a session takes an item by committing an empty `Claim:` trailer on its own
branch, and a reader asks `holdings` rather than inferring. Landing stays
derived; holding is recorded. `PL-MB2W` § "Design round, 2026-09-24" is the
specification, and what follows is the part of it this module decides.

**The carrier is a trailer in the last paragraph of a commit on the holder's
own branch**, and nothing is written into the store:

    Claim: <ID> <branch> [<session>] [over <ref>@<hash>]
    Yield: <ID> <branch>

So nothing conflicts, and a claim that squashes into the default branch is
inert there, because the base's own commits are never read for claims. The
last paragraph because that is the only place git reads a trailer from: a
`Claim:` line in an earlier paragraph, or as a subject, is prose.

**A claim counts only for the branch its token names.** It holds for ref R
when R's name, less its remote, equals `<branch>`. A branch that merged the
claiming one, a recovery that cherry-picked a claim commit and any other
bystander carrying the commit hold nothing by it, which is what `PL-2BZY` and
`PL-61MD` each recorded going wrong when a commit was credited to whichever ref
reached it. A local branch and its tracking ref name one branch, so they are
one holder, read as the union of their commits.

**It stays live under a lease** (`LEASE_TERM`) that the branch's non-merge
commits renew, dated by `%cI`: a claim lapses once a gap longer than the term
opens anywhere between it, the branch's later commits, and `now`. A lapse is
final for that claim; only a new `Claim:` revives the branch's hold, and it
stakes from its own date. The default branch's commits never renew it, since
the read starts at the base, and neither does a merge of it, since merges are
not read. A rebase does renew it: it rewrites every committer date.

**Order is `(%aI, hash)`**, which a rebase leaves alone, so two sessions order
themselves identically from one set of commits. It is an order and not a
fence: nothing stops a later claim being written, and `PL-J9S0`'s check is what
refuses one that orders behind another. A takeover - `over <ref>@<hash>` -
releases the claim it names and sorts immediately ahead of it, so a successor
inherits the dead claim's place rather than queueing behind claims made while
it stood.

**A claim ends in one of five ways**: a `Yield:` on its branch, the branch's
own copy of the item reaching a status in `RELEASING_STATUSES`, a takeover, a
lapse, or landing. Landing is derived, at two levels. A branch the base
contains, or whose content it holds, is never offered by
`vcs._unlanded_refs`. Within a branch still offered, a claim on an item the
base has closed is spent, and so is every claim the branch's *landed prefix*
takes in: some commit descending from the claim adds content, all of it
content the base has held, and the branch's own work through it is all on
the base. That is the shape a squash merge leaves on a branch that goes on
committing (`PL-8JQQ`), and continuing work there claims again. Descent, not
place in the walk, because a merge of the base brings in commits that sort
after a claim without descending from it.

**Three other kinds of hold ride the same read, and none is a claim.** A
*disposition* is a branch whose copy of an item has moved its `status:` away
from both the fork's copy and the base's - a grooming pass blocking or
dropping it, a triage pass readying it - which `docket next` must not offer
over. It needs the item at the fork and on the base, so a capture holds
nothing; it reads `status:` alone, so a pass rewriting another field of a
hundred items holds none of them (`PL-3W3P`); it runs on the branch's lease;
and it never orders against a claim or holds arming. A *cut* is a release's
notes file on the branch, `vcs.cuts_in_flight`'s read, and it always refuses a
release. A *name* is a branch named for its item, `claude/pl-k7qx-slug`, which
`flight` has always read as carrying it and which needs no history to read
(`PL-TZ3R`); it runs on the branch's lease and never orders
against a claim or holds arming. It holds only an item the base's copy of the
store or the branch's own holds (`named_id`), since the id grammar fits a word
too: `claude/fix-pl-html-export-abc123` named no item (`PL-WK57`). They are
kept apart from the claims (`Holdings.dispositions`, `Holdings.cuts`,
`Holdings.named`) so that a reader wanting claims cannot be handed one.

**Every commit is read by its trailers alone.** The old rule - a subject
leading with ids claimed them where the commit's diff was empty or reached
outside the queue - was kept for commits made before a session could write a
claim, and `PL-CH3Z` deleted it on 2026-09-26, once `flight` counted no ref
still holding by it. A commit from before the record carries no `Claim:`
trailer, so it claims nothing, and its leading ids are attribution.

**git 2.22 is the floor** (`GIT_FLOOR`), declared rather than worked around: a
git that cannot read one trailer key's values declines, and says so, rather
than having git's trailer rules re-implemented here.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .config import Config
from .model import CLOSED_STATUSES, parse_front_matter
from .release import NOTES_DIR
from .store import ID_PATTERN
from .vcs import (
    BRANCH_ID_RE,
    ITEM_FILE_RE,
    Branch,
    FlightReport,
    QueueEdit,
    Runner,
    SettledBranch,
    SettledReport,
    _cut_versions,
    _head_name,
    _item_paths_on,
    _landing_split,
    _notes_on,
    _remotes,
    _run_git,
    _Silences,
    _superseded,
    _unlanded_refs,
    _work_already_on_base,
    answered,
    changed_path_args,
    default_base,
    leading_ids,
    listed_paths,
)

#: How long a claim survives with no commit on its branch. Seven days clears the
#: longest owner absence measured on `main`, 92.1 h across 34 days, by 1.8 times,
#: because a session waiting on the owner cannot renew; the longest gap inside a
#: live session was 8.43 h over 300 pull requests. No margin is added for clock
#: skew, which is minutes against a term of days. `PL-MB2W` § "Lease" carries the
#: evidence, and the rule for revisiting it: shorten it if dead claims on open
#: items need more than three takeovers in thirty days, lengthen it after any
#: false lapse.
LEASE_TERM = timedelta(days=7)

#: The statuses whose appearance in the branch's own copy of an item releases the
#: branch's claim on it. `blocked` is here by the project owner's decision
#: (2026-09-24, ratified, over holding the claim until the item is `done` or
#: `dropped`, `PL-KWCY`'s rule): a session that blocks its own item has stopped
#: working it, and holding the claim strands a queue-only branch that never arms.
RELEASING_STATUSES = CLOSED_STATUSES + ("blocked",)

#: The first git whose `%(trailers:...)` placeholder takes `key=`, `valueonly` and
#: `separator=` (git 2.22.0 release notes), which is what reads one trailer key's
#: values without copying git's rules for finding a trailer block into Python.
GIT_FLOOR = (2, 22)

#: Where a remote session's own id is read from, to decide `Hold.mine`. `claim`
#: writes the same variable's value as a claim's `<session>` token.
SESSION_VARIABLE = "CLAUDE_CODE_REMOTE_SESSION_ID"

#: `Hold.kind`: a recorded claim, a status disposition, a release cut, or a branch
#: named for its item.
CLAIM = "claim"
DISPOSITION = "disposition"
CUT = "cut"
NAMED = "named"

#: The namespace every agent session's branch sits in: the web harness gives it
#: to each session it starts, and `CLAUDE.md` asks a session naming its own
#: branch to use it. The unclaimed-work question binds this namespace and no
#: other, because a contributor has no queue and no `bin/docket` to claim with
#: (`PL-8P6D`). Declared here since `flight`'s `unclaimed:` row asks it as well
#: as `tools/branch_id_check.py`, and the two must read one definition
#: (`PL-FFR0`).
AGENT_BRANCH_PREFIX = "claude/"

#: `Hold.state`: holding the item at `now`, out of lease, or ended.
LIVE = "live"
LAPSED = "lapsed"
RELEASED = "released"

#: `Hold.released_by`: which of the release routes ended a released claim.
BY_YIELD = "yield"
BY_STATUS = "status"
BY_OVER = "over"
#: Spent by the branch's landed prefix.
BY_LANDING = "landed"
#: Spent because the base records the item as closed.
BY_CLOSED = "closed"

# One line per non-merge commit in `base..R`: its hash, both dates, its parents,
# the values of its `Claim:` and `Yield:` trailers, and its subject. The unit
# separator delimits fields and the record separator the values of one key,
# because a subject can hold anything a keyboard can type; `unfold` joins a
# trailer value git has folded onto a continuation line. `%P` is empty for a
# commit whose parents this checkout lacks, which is how a walk that ran off a
# truncated history is told from one the base stopped. The subject comes last so
# a stray separator in it cannot shift the fields before it. `--raw` follows
# each line with the commit's changes, whose paths say which items and notes it
# touched and whose new blobs are what the landed prefix is judged on.
_LOG_FORMAT = (
    "--format=%H%x1f%aI%x1f%cI%x1f%P"
    "%x1f%(trailers:key=Claim,valueonly,unfold,separator=%x1e)"
    "%x1f%(trailers:key=Yield,valueonly,unfold,separator=%x1e)"
    "%x1f%s"
)
_FIELDS = 7

_ID = re.compile(ID_PATTERN, re.I)
_HASH = re.compile(r"[0-9a-f]{7,64}", re.I)
_VERSION = re.compile(r"(\d+)\.(\d+)")


@dataclass(frozen=True)
class Hold:
    """One branch's hold on one item, in the state it was in at the read's `now`.

    One per item and branch, standing for the branch's latest claim episode: a
    `Yield:` ends an episode, and a claim after it opens the next. Within an
    episode the hold is the earliest claim whose lease is unbroken, since later
    claims in the same unbroken chain are renewals; after a break it is the claim
    that revived the chain, and where nothing revived it, the last one made.

    `since` is that claim's author date and `commit` its hash, which together are
    its place in `Holdings.order` - except that a takeover sorts ahead of the
    claim it names, whatever its own date says. `renewed` is the newest commit
    date in its unbroken chain, so a lapsed hold lapsed at `renewed` plus the
    term.

    `ref` is the local branch where the checkout holds one, the name `flight`
    has always shown, and otherwise the tracking ref. `status` is the item's
    status in the branch's own copy, read from whichever of those two is newer;
    empty where that copy has no such item. `on_base` says whether the default
    branch has a copy of the item at all: a claim on an item the base lacks is
    still a claim, and only what a reader is told about it differs, as it does
    for `vcs.Branch`.

    A disposition fills the same fields from the commit that last touched the
    item's file, and is `live` or `lapsed` only; a cut's `key` is the version
    it cuts, without its `v`, and it is always `live`. A name's `since` and
    `commit` are the branch's first commit, and `renewed` its newest; a ref
    whose commits went unread has neither, so both dates are the read's `now`
    and `commit` is empty.
    """

    key: str
    ref: str
    kind: str
    state: str
    since: datetime
    renewed: datetime
    commit: str
    #: The claim's `<session>` token, which decides `mine` and is what
    #: `get_session` is asked about before a takeover. Empty for a claim written
    #: without one.
    session: str = ""
    status: str = ""
    #: Whether this checkout's session made the claim. Decided by the session
    #: token where the claim carries one, and otherwise by whether the checkout's
    #: `HEAD` is on the claiming branch - never by order.
    mine: bool = False
    on_base: bool = True
    #: `BY_YIELD`, `BY_STATUS`, `BY_OVER`, `BY_LANDING` or `BY_CLOSED` for a
    #: released hold, and empty otherwise.
    released_by: str = ""
    #: The `<ref>@<hash>` this claim took over, as written.
    over: str = ""
    #: The `resource:` the item names in the claiming branch's own copy - what
    #: `Holdings.holder` answers for, so a release item's claim holds the
    #: release train without a flag its session has to remember.
    resource: str = ""


@dataclass(frozen=True)
class Holdings:
    """Every hold the readable refs record, and what could not be read to find out.

    `holds` is the claims, sorted into the order that decides which branch
    continues: author date, then hash, with a takeover immediately ahead of the
    claim it names, and last the branch's name, which keeps the order the same
    in every checkout rather than leaving it to which refs this one lists
    first. One order across every item,
    so `order` is a filter of it and `holder` its first match. `dispositions`,
    `cuts` and `named` are the other three kinds, kept apart so that no reader
    wanting claims is handed one.

    **What went unread travels with the answer**, as it does on `FlightReport`.
    `unreadable` names refs whose history this checkout cannot compare with the
    base - no merge-base, or a walk that ran off a truncated history - and whose
    claims were therefore not believed. `malformed` names trailers the grammar
    could not parse, which would otherwise vanish silently for a session that
    hand-wrote one. `declined` says git failed to answer something, or is older
    than `GIT_FLOOR`: every hold here was then collected from an incomplete read,
    and a missing hold proves nothing.
    """

    holds: tuple[Hold, ...] = ()
    dispositions: tuple[Hold, ...] = ()
    cuts: tuple[Hold, ...] = ()
    #: One per branch whose name carries the id of an item some copy of the
    #: store holds (`named_id`), in the order refs were listed.
    named: tuple[Hold, ...] = ()
    unreadable: tuple[str, ...] = ()
    malformed: tuple[str, ...] = ()
    base: str = ""
    #: The one moment every lease in this read was judged at.
    now: datetime | None = None
    #: What `flight` reports beside the holds: refs that edited an item's file
    #: where nothing holds the item and the base has not superseded the edit,
    #: every such ref per item (`PL-1X2C`), and readable refs no subject, claim
    #: or name attributes to any item.
    editing: tuple[QueueEdit, ...] = ()
    unattributed: tuple[str, ...] = ()
    #: Per `Hold.ref`, when that branch's newest non-merge commit was made.
    last: Mapping[str, datetime] = field(default_factory=dict)
    declined: str = ""
    #: The `Hold.ref` of the branch `HEAD` is on, or `""` where it is detached or
    #: that branch is not read. A claim carrying a session token is `mine` by the
    #: token alone, so this is what says a claim is on this branch although
    #: another session made it - the case `claim` answers by branch.
    head: str = ""

    @property
    def ids(self) -> frozenset[str]:
        """The items some branch holds live, by a claim, a disposition or its name."""
        return frozenset(
            hold.key
            for hold in (*self.holds, *self.dispositions, *self.named)
            if hold.state == LIVE
        )

    def order(self, key: str) -> tuple[Hold, ...]:
        """The live claims on one item, the one that continues first."""
        wanted = key.upper()
        return tuple(hold for hold in self.holds if hold.key == wanted and hold.state == LIVE)

    def holder(self, resource: str) -> Hold | None:
        """The live claim holding a resource: the first, in claim order, whose item names it."""
        return next(
            (hold for hold in self.holds if hold.state == LIVE and hold.resource == resource), None
        )

    def lapsed_open(self) -> tuple[Hold, ...]:
        """Lapsed claims on items the base still holds open: dead claims worth taking over.

        An item the base has closed has spent every claim on it, and one the
        base has no copy of is no longer anybody's to start, so neither is
        worth a line.
        """
        return tuple(hold for hold in self.holds if hold.state == LAPSED and hold.on_base)

    def holding(self) -> dict[str, Hold]:
        """The one hold that puts each item in flight, by item.

        The claim that continues first, where nothing claims it the
        disposition, and where neither holds it the branch named for it
        (`PL-TZ3R`). `flight` is these as rows, and `flight`'s command reads
        them whole for the kind and state a row has no field for.
        """
        held: dict[str, Hold] = {}
        for hold in (*self.holds, *self.dispositions, *self.named):
            if hold.state == LIVE:
                held.setdefault(hold.key, hold)
        return held

    def flight(self) -> FlightReport:
        """The holds as a `vcs.FlightReport`, the shape every in-flight reader takes.

        One `Branch` per item held live, from `holding`.
        """
        held = self.holding()
        return FlightReport(
            branches=tuple(
                Branch(
                    name=hold.ref,
                    item_id=key,
                    last_commit=self.last.get(hold.ref),
                    on_base=hold.on_base,
                )
                for key, hold in sorted(held.items())
            ),
            unreadable=self.unreadable,
            unattributed=self.unattributed,
            editing=self.editing,
            base=self.base,
            declined=self.declined,
        )

    @property
    def known(self) -> bool:
        """Whether git answered every question this reading rests on."""
        return not self.declined


@dataclass(frozen=True)
class _Commit:
    """One non-merge commit on a branch, as the log reported it."""

    commit: str
    authored: datetime
    committed: datetime
    claims: tuple[str, ...]
    yields: tuple[str, ...]
    subject: str
    paths: tuple[str, ...]
    #: The blobs the commit wrote: the new side of each change but a deletion.
    added: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Claim:
    """One claim bound to its branch, and where it falls in that branch's history."""

    key: str
    branch: str
    commit: str
    authored: datetime
    committed: datetime
    #: Its commit's index in the branch's walk, oldest first, which orders it
    #: against the branch's yields.
    position: int
    session: str = ""
    over: str = ""

    @property
    def identity(self) -> tuple[str, str, str]:
        return (self.key, self.branch, self.commit)


@dataclass(frozen=True)
class _Yield:
    """One `Yield:` bound to its branch."""

    key: str
    branch: str
    committed: datetime
    position: int


def named_id(name: str, stored: Callable[[str], bool]) -> str:
    """The item a branch's name holds, or `""`: its first id, where a copy of the store holds it.

    Read by `search`, first match only, as every reader of a name has read one,
    and `stored` answers whether the base's copy of the store or the branch's
    own holds an id. The grammar alone is not enough, because it fits a word as
    well as an id - `HTML`, like `CTRL`, is in its alphabet - so
    `claude/fix-pl-html-export-abc123` held an item that does not exist
    (`PL-WK57`). `PL-SN2T` gave `tools/branch_id_check.py`'s attribution the
    same rule, which reads a name through this.
    """
    match = BRANCH_ID_RE.search(name)
    if match is None:
        return ""
    key = match.group(1).upper()
    return key if stored(key) else ""


def holdings(
    root: Path,
    *,
    now: datetime,
    items_dir: str = "docs/items",
    notes_dir: str = NOTES_DIR,
    include_remote: bool = True,
    include_head: bool = True,
    term: timedelta = LEASE_TERM,
    runner: Runner | None = None,
) -> Holdings:
    """Every hold the unlanded refs record, each judged at `now`.

    `now` is required and must carry its offset, because every lease is judged
    against it and a read that took the clock itself could not be replayed:
    one instant per call, converted to UTC, and never the wall clock.

    `include_remote` reads `refs/remotes` as well as the checkout's own
    branches, as it does for `vcs.orphaned`. `include_head=False`
    leaves the checkout's own branches out, so that only what has been pushed -
    what every other session can also read - decides the answer.

    Refs are read from what is already fetched, so the answer can be stale by
    one fetch, and it reports rather than blocks for that reason.
    """
    moment = _utc(now)
    run = _Silences(runner or _run_git)

    # Neither `version` nor `remote` is a subcommand `GitRunner` memoizes, and
    # either empties its memo; asked before anything memoizable, that costs this
    # read nothing.
    too_old = _below_floor(root, run)
    if too_old:
        return Holdings(now=moment, declined=too_old)
    remotes = _remotes(root, run)

    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    skipped: frozenset[str] = frozenset() if include_head else _local_branches(root, run)
    candidates = [name for name in refs.candidates if name not in skipped]
    unreadable = {name for name in candidates if name in refs.unreadable}
    unlanded = set(refs.unlanded)
    branches: dict[str, list[str]] = {}
    for name in candidates:
        if name in unlanded:
            branches.setdefault(_head_name(name, remotes), []).append(name)

    histories: dict[str, list[_Commit]] = {}
    for branch, names in branches.items():
        history = _history(names, base, root, run)
        if history is None:
            unreadable.update(names)
        else:
            histories[branch] = history

    claims, yields, malformed = _events(histories, branches, remotes)
    episodes = _episodes(claims, yields)
    successors = _takeovers(claims, remotes)
    superseded = set(successors.values())
    by_identity = {claim.identity: claim for claim in claims}

    def rank(claim: _Claim) -> tuple[datetime, str, int, datetime, str]:
        """Where a claim sorts: at its own stake, or just ahead of the one it took over."""
        anchor, depth, seen = claim, 0, {claim.identity}
        while (named := successors.get(anchor.identity)) is not None and named not in seen:
            seen.add(named)
            anchor, depth = by_identity[named], depth + 1
        return (anchor.authored, anchor.commit, -depth, claim.authored, claim.commit)

    session = os.environ.get(SESSION_VARIABLE, "")
    here = _checked_out(root, run, remotes)
    prefix = items_dir.strip("/") + "/"
    copies: dict[str, dict[str, str]] = {}
    renewals = {
        branch: sorted(entry.committed for entry in history)
        for branch, history in histories.items()
    }
    tips = {branch: _newest(branches[branch], root, run) for branch in histories}
    touched = {branch: _touched(history, prefix) for branch, history in histories.items()}

    def status(ref: str, key: str) -> str:
        return _fields_at(ref, key, items_dir, root, run, copies).get("status", "")

    copies[base] = _item_paths_on(base, items_dir, root, run)
    on_base = set(copies[base])

    def stored(ref: str) -> Callable[[str], bool]:
        """Whether the base's copy of the store or `ref`'s holds an id: whether it names an item."""
        return lambda key: key in on_base or key in _copy(ref, items_dir, root, run, copies)

    landed: dict[str, dict[int, bool]] = {}
    ranked: list[tuple[tuple[datetime, str, int, datetime, str], str, str, Hold]] = []
    for (key, branch), (episode, yielded) in episodes.items():
        standing = [claim for claim in episode if claim.identity not in superseded]
        fork = refs.fork.get(tips[branch], "")
        unspent = [
            claim
            for claim in standing
            if not _landed_through(
                claim,
                histories[branch],
                branches[branch],
                fork,
                refs.base_blobs,
                root,
                run,
                landed.setdefault(branch, {}),
            )
        ]
        end = moment if yielded is None else yielded
        # The earliest claim whose lease is unbroken holds; any later claim in
        # the same chain is a renewal of it. Where every chain broke, the last
        # claim made stands for the episode, lapsed.
        pool = unspent or standing or episode
        holder: _Claim | None = None
        unbroken, renewed = False, moment
        for claim in pool:
            unbroken, renewed = _chain(claim.committed, renewals[branch], end, term)
            if unbroken:
                holder = claim
                break
        if holder is None:
            holder = pool[-1]
            unbroken, renewed = _chain(holder.committed, renewals[branch], end, term)

        fields = _fields_at(tips[branch], key, items_dir, root, run, copies)
        current = fields.get("status", "")
        if not standing:
            state, released_by = RELEASED, BY_OVER
        elif yielded is not None:
            state, released_by = RELEASED, BY_YIELD
        elif current in RELEASING_STATUSES:
            state, released_by = RELEASED, BY_STATUS
        elif status(base, key) in CLOSED_STATUSES:
            state, released_by = RELEASED, BY_CLOSED
        elif not unspent:
            state, released_by = RELEASED, BY_LANDING
        else:
            state, released_by = (LIVE if unbroken else LAPSED), ""

        tokens = {claim.session for claim in episode[episode.index(holder) :] if claim.session}
        hold = Hold(
            key=key,
            ref=branches[branch][0],
            kind=CLAIM,
            state=state,
            since=holder.authored,
            renewed=renewed,
            commit=holder.commit,
            session=holder.session,
            status=current,
            mine=session in tokens if tokens else bool(here) and branch == here,
            on_base=key in on_base,
            released_by=released_by,
            over=holder.over,
            resource=fields.get("resource", ""),
        )
        ranked.append((rank(holder), key, branch, hold))
    ranked.sort(key=lambda entry: (entry[0], entry[1], entry[2]))

    # A disposition: the branch's copy has moved `status:` away from both the
    # fork's and the base's. Asked only of items a commit on the branch touched,
    # and in the order that stops soonest: most edits change no status.
    dispositions: list[Hold] = []
    for branch, found in touched.items():
        fork = refs.fork.get(tips[branch], "")
        for key, (position, _) in found.items():
            if not fork or key not in on_base:
                continue
            moved = status(tips[branch], key)
            there = status(base, key)
            if not moved or moved == there or there in CLOSED_STATUSES:
                continue
            forked = status(fork, key)
            if not forked or moved == forked:
                continue
            entry = histories[branch][position]
            unbroken, renewed = _chain(entry.committed, renewals[branch], moment, term)
            dispositions.append(
                Hold(
                    key=key,
                    ref=branches[branch][0],
                    kind=DISPOSITION,
                    state=LIVE if unbroken else LAPSED,
                    since=entry.authored,
                    renewed=renewed,
                    commit=entry.commit,
                    status=moved,
                    mine=bool(here) and branch == here,
                )
            )
    dispositions.sort(key=lambda hold: (hold.since, hold.commit, hold.key))

    # A branch named for its item holds it by the name, which needs no history,
    # so a ref whose commits went unread still proves its id and stays in
    # `unreadable` for whatever those commits might add (`PL-TZ3R`). Live while
    # the branch's newest commit is within the term; an unread ref is live,
    # since nothing dates it and dropping the id offers an item a live session
    # may be holding. An item the base has closed releases it, as it does a
    # claim. A branch that recorded a claim on the item, in any state, holds it
    # by that record and not by its name, so that its yield, takeover or
    # close-out ends the hold rather than leaving the name holding for a lease
    # more (`PL-N162`); a close-out in its own copy is a disposition, and stays
    # in flight as one. The id must name an item the base's copy or the
    # branch's own holds (`named_id`); an unread ref's own copy is its tip's,
    # which a listing reads without the history.
    named: dict[str, Hold] = {}
    by_name: set[str] = set()
    for name in candidates:
        if name not in unlanded and name not in unreadable:
            continue
        branch = _head_name(name, remotes)
        key = named_id(name, stored(tips.get(branch, name)))
        if not key:
            continue
        by_name.add(branch)
        if f"{key} {branch}" in named or (key, branch) in episodes:
            continue
        history = histories.get(branch, [])
        dates = renewals.get(branch, [])
        if status(base, key) in CLOSED_STATUSES:
            state, released_by = RELEASED, BY_CLOSED
        else:
            state = LIVE if not dates or moment - dates[-1] <= term else LAPSED
            released_by = ""
        named[f"{key} {branch}"] = Hold(
            key=key,
            ref=branches[branch][0] if branch in histories else name,
            kind=NAMED,
            state=state,
            since=history[0].authored if history else moment,
            renewed=dates[-1] if dates else moment,
            commit=history[0].commit if history else "",
            status=status(tips[branch], key) if branch in tips else "",
            mine=bool(here) and branch == here,
            on_base=key in on_base,
            released_by=released_by,
        )

    holds = tuple(hold for *_, hold in ranked)
    held = {hold.key for hold in (*holds, *dispositions, *named.values()) if hold.state == LIVE}
    last = {branches[branch][0]: dates[-1] for branch, dates in renewals.items() if dates}
    cuts = _cuts(histories, branches, tips, last, base, notes_dir, root, run, moment)
    editing = _editing(touched, branches, tips, last, held, base, root, run, copies)
    return Holdings(
        holds=holds,
        dispositions=tuple(dispositions),
        cuts=cuts,
        named=tuple(named.values()),
        unreadable=tuple(name for name in candidates if name in unreadable),
        malformed=malformed,
        base=base,
        now=moment,
        editing=editing,
        # A subject's leading id attributes the branch by the name's rule: only
        # where a copy of the store holds it (`PL-WK57`).
        unattributed=tuple(
            branches[branch][0]
            for branch, history in histories.items()
            if branch not in by_name
            and not any(
                entry.claims or any(map(stored(tips[branch]), leading_ids(entry.subject)))
                for entry in history
            )
        ),
        last=last,
        declined=run.reason,
        head=branches[here][0] if here in branches else "",
    )


def settled_branches(
    root: Path,
    read: Holdings,
    *,
    opened: Callable[[], Collection[str] | None] | None = None,
    runner: Runner | None = None,
) -> SettledReport:
    """The in-flight refs that have finished: every item closed, and nothing open.

    An age cannot tell a live session from a branch nobody will merge, and it
    fails in the costly direction on the case that matters most: finished work
    sitting on a branch with no pull request behind it, reported to every
    session as in flight. `PL-Q664` is the worked instance: two items at
    `status: done`, ten item files existing nowhere else, and three hours
    before anybody noticed.

    Two facts separate that case, and neither is the age. The ref holds nothing
    but its own close-outs, and no pull request is open on it. Either alone is
    ordinary: a branch mid-review has closed its items, and a branch with no
    pull request is usually a session still working.

    **The first fact is read from the holds, not from the rows `flight` shows**
    (`PL-N162`). Closing an item in the branch's own copy releases the branch's
    claim on it (`BY_STATUS`), and the same status move is a disposition, which
    keeps the item in flight. So a ref is settled where every claim it recorded
    is finished (`_finished_claim`), shadowed or not, and every live hold it
    has, a disposition or its name, records a status in `CLOSED_STATUSES` in
    its own copy. Not `RELEASING_STATUSES`: a blocked item releases its claim,
    but it is not finished work. A name counts by the same reasoning, because
    it holds only where the branch recorded no claim on the item - a capture
    closed on the branch that filed it holds by nothing else. A cut is not an
    item and is left out of the question. Only a ref with a row in
    `Holdings.flight` is asked about, and its ids are that ref's own rows, so a
    settled row always replaces live ones rather than adding a branch or an id
    the report never named under it. It costs no `git show`: `Hold.status` is
    the copy's status, read when the holds were.

    **It never changes what is in flight.** The ids stay excluded from `docket
    next`, because the work exists on a branch and offering it again would have
    a second session redo it. Only how a reader is told changes.

    **The forge is asked through `opened`, never reached from here.** This
    package answers from a bare checkout with no network; the caller supplies a
    way to ask which branch names have a pull request open, and `None` - no way
    to ask, no token, no network - is carried into the report as `asked=False`
    rather than read as "none is open". A callable, so it is asked only where
    the cheap half found a candidate.

    Every silence fails toward the live reading. A ref whose commits went
    unread never settles, an item whose copy the ref lacks has no status and
    leaves the ref live, and a read git declined any part of says so in
    `declined`, because a live session wrongly called finished is the expensive
    mistake.
    """
    run = _Silences(runner or _run_git)
    unread = set(read.unreadable)
    shown: dict[str, set[str]] = {}
    for row in read.flight().branches:
        if row.name not in unread:
            shown.setdefault(row.name, set()).add(row.item_id)
    # Every claim the ref recorded is asked, whether or not it won its item's
    # row: a claim shadowed by another branch's is still a session working.
    unfinished = {hold.ref for hold in read.holds if not _finished_claim(hold)}
    for hold in (*read.dispositions, *read.named):
        if hold.state == LIVE and hold.status not in CLOSED_STATUSES:
            unfinished.add(hold.ref)

    finished = sorted(
        (
            SettledBranch(name=name, item_ids=tuple(sorted(ids)), last_commit=read.last.get(name))
            for name, ids in shown.items()
            if name not in unfinished
        ),
        key=lambda entry: entry.name,
    )
    declined = read.declined
    if not finished:
        # Nothing to ask the forge about, so it is not asked - and the report
        # says the question was answered, because a set with no members in it
        # has no member whose pull request went unchecked.
        return SettledReport(declined=declined)
    answer = None if opened is None else opened()
    if answer is None:
        return SettledReport(branches=tuple(finished), asked=False, declined=declined)
    remotes = _remotes(root, run)
    heads = {head.strip() for head in answer if head.strip()}
    return SettledReport(
        branches=tuple(entry for entry in finished if _head_name(entry.name, remotes) not in heads),
        declined=declined or run.reason,
    )


def _finished_claim(hold: Hold) -> bool:
    """Whether `hold`, a claim, says nothing is left to do on its item on its branch.

    Released by a yield, a takeover, the landed prefix or the base's close, the
    work is elsewhere or done. Released by the branch's own status move, it is
    done only where that status is closed: `blocked` releases the claim, and a
    blocked item with no disposition behind it - a capture the base never had,
    or one the base already shows as blocked - would otherwise settle the
    branch that holds its only copy. A live or lapsed claim is unfinished; a
    lapsed one holds nothing, but the branch may still carry its work. The
    branch's copy is read before the base's, so an item it blocked and the base
    later closed still reads as blocked, which errs toward the live reading.
    """
    if hold.state != RELEASED:
        return False
    return hold.released_by != BY_STATUS or hold.status in CLOSED_STATUSES


# A work branch that claims nothing: `PL-MB2W`'s third "Forgetful session"
# catch, asked by `tools/branch_id_check.py`, which refuses it in CI, and by
# `flight`'s `unclaimed:` row, which counts it. One definition in this module
# for both (`PL-FFR0`), because two spellings of one question are two answers
# waiting to disagree, and the pre-registered 1-in-20 threshold is counted from
# the row while CI refuses on the check.

#: The pull requests' body records. `tools/pr_body_check.py --record` writes
#: `<N>.md` here on every pull request's branch before its merge, since
#: `pr-title`'s required job fails without it (`PL-979D`), and `--recover`
#: writes one for a pull request already merged. `arming.RECORDS` spells the
#: same directory for what arms on green, in the one module the gate holds for
#: a read, and is kept there rather than imported from here, so that widening
#: what arms still takes an edit the gate holds; `test_claims` pins the two
#: equal (`PL-F6MM`). The path is this repository's layout, as
#: `arming.TOOLING`'s is.
RECORDS = "docs/pr-bodies/"


def queue_records(config: Config) -> tuple[str, ...]:
    """The records a queue workflow writes, as `in_queue` counts them and a refusal names them.

    A name ending in `/` is a directory and holds every path under it; any
    other is one file. One list for the check and for what its refusal says it
    admits, so the two cannot drift apart: `PL-F6MM`'s body records were
    missing from both.
    """
    return tuple(
        name
        for name in (
            config.items_dir.strip("/") + "/",
            config.roadmap_file,
            config.notes_file,
            RECORDS,
        )
        if name
    )


def in_queue(path: str, config: Config) -> bool:
    """Whether a repository path is one of the records a queue workflow writes.

    The items, the roadmap, the working notes and the pull requests' body
    records (`queue_records`). A capture, a triage pass or a design round writes
    these and nothing else - triage puts an item on the debt gate's list in the
    roadmap, a design round keeps its thread in the notes, and every pull
    request records its body before its merge - and owes no claim, since the
    ids it leads with are never pushed into one (`PL-3CTW`). Read as the items
    directory alone, as the spec's "outside `items_dir`" says, it refused 12
    such passes merged in the week to 2026-09-24, and would have made each
    claim the ids it triaged. Without the body records it refused every such
    pass once recorded, so `pr-title` and `checks` could not both pass on it
    (`PL-F6MM`).

    The whole records directory counts, a `--recover` pass's bodies included,
    so CI no longer refuses such a pass that claims nothing, though
    `CLAUDE.md`'s housekeeping rule still files and claims one. Telling a
    branch's own record from a recovery takes more than the path, and would
    buy a refusal for a pass with almost nothing left to do: every pull
    request with a body has recorded it since `PL-979D`, so `--recover` has
    only the bodies lost before it - two on 2026-09-26 (`PL-F6MM`).

    It is not what arms. `arming.arms_on_green` asks whether a change may merge
    on green CI without the owner's read, and keeps to the store, the tooling
    and the body records, so a `ROADMAP.md`-only triage pass owes no claim here
    and still waits on a read there (project owner, 2026-09-26, ratified, over
    widening arming to the roadmap and the notes, `PL-0JGZ`). That answer is
    spelt in the module the gate holds for a read rather than in this one, for
    the reason `RECORDS` above gives.
    """
    return any(
        path.startswith(name) if name.endswith("/") else path == name
        for name in queue_records(config)
    )


def work_outside_queue(
    root: Path, base: str, head: str, config: Config, *, runner: Runner | None = None
) -> bool | None:
    """Whether `head` changes a path outside the queue in a non-merge commit of its own.

    `None` where git did not answer. A merge is how the base arrives rather than
    the branch's own work, and `holdings` reads none either. Every commit
    counts: `PL-CH3Z` deleted the old rule that read a commit made before the
    record by its subject and had this skip it. `changed_path_args` asks for
    `-z`, so a path is compared as written rather than in git's quoted form,
    which no queue path would match.
    """
    run = runner or _run_git
    log = run(
        changed_path_args(
            "log", "--no-merges", "--format=%x1e%H", "--name-only", f"{base}..{head}", "--"
        ),
        root,
    )
    if not answered(log):
        return None
    for record in log.split("\x1e"):
        # The hash, then the commit's paths, each ended by NUL; git opens the
        # paths with one `\n`, which belongs to none of them. Nothing at all, or
        # the queue alone, is a claim or a yield, which are empty, a capture or
        # a triage pass; anything else is work.
        paths = listed_paths(record.partition("\0")[2].removeprefix("\n"))
        if paths and not all(in_queue(path, config) for path in paths):
            return True
    return False


def claims_bound(read: Holdings, branch: str, remotes: frozenset[str]) -> tuple[Hold, ...]:
    """The claims `branch` wrote under the record, in whatever state each is in now.

    Any state, by the project owner's reading (2026-09-24): a branch releases
    its claim by closing its item in its own copy, so "no live claim" would call
    every finished branch forgetful, and the session this catches is the one
    that never claimed.
    """
    return tuple(
        hold
        for hold in read.holds
        if hold.kind == CLAIM and _head_name(hold.ref, remotes) == branch
    )


def claims_nothing(
    read: Holdings,
    branch: str,
    *,
    base: str,
    head: str,
    root: Path,
    config: Config,
    remotes: frozenset[str],
    runner: Runner | None = None,
) -> bool | None:
    """Whether `branch` is a work branch that claims nothing, or `None` where git did not answer.

    A `claude/` branch with a non-merge commit that changes a path outside the
    queue (`work_outside_queue`, walking `base..head`), no claim of its own in
    any state (`claims_bound`), and no hold by its name in `read`, which a
    branch named for an item holds it by (`PL-TZ3R`). Asked of `read` rather
    than of the name, so a name `flight` reads as naming no item exempts
    nothing (`PL-WK57`). The question is per branch, never per id, so a
    capture or a triage pass is never pushed into claiming the ids it leads
    with. A branch `read` did not walk has nothing the base has not taken, and
    owes nothing.
    """
    if (
        claims_bound(read, branch, remotes)
        or not branch.lower().startswith(AGENT_BRANCH_PREFIX)
        or any(_head_name(hold.ref, remotes) == branch for hold in read.named)
    ):
        return False
    if not any(_head_name(ref, remotes) == branch for ref in read.last):
        return False
    return work_outside_queue(root, base, head, config, runner=runner)


@dataclass(frozen=True)
class Unclaimed:
    """The work branches that claim nothing, and those git did not answer about.

    `branches` are `Hold.ref` names, as `flight` shows every other row.
    `unasked` is not "claims something": a branch there may be either.
    """

    branches: tuple[str, ...] = ()
    unasked: tuple[str, ...] = ()


def unclaimed(
    root: Path, read: Holdings, config: Config, *, runner: Runner | None = None
) -> Unclaimed:
    """Every branch `read` walked that `claims_nothing`, for `flight`'s `unclaimed:` rows.

    Asked of `read`'s own base and of each ref it walked, so a row and the
    holds beside it are one reading. Nothing is asked where `read` declined:
    its `last` and `holds` are then incomplete, and a branch missing a claim
    from a partial read would be named as forgetful.
    """
    if not read.known:
        return Unclaimed()
    run = runner or _run_git
    remotes = _remotes(root, run)
    found: list[str] = []
    unasked: list[str] = []
    for ref in sorted(read.last):
        answer = claims_nothing(
            read,
            _head_name(ref, remotes),
            base=read.base,
            head=ref,
            root=root,
            config=config,
            remotes=remotes,
            runner=run,
        )
        if answer is None:
            unasked.append(ref)
        elif answer:
            found.append(ref)
    return Unclaimed(branches=tuple(found), unasked=tuple(unasked))


def _utc(now: datetime) -> datetime:
    """`now` in UTC, refusing a naive one rather than guessing its zone."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError(
            "holdings() needs an aware `now`: a naive one would be read in this machine's "
            "own zone, and a lease judged against it could be hours out"
        )
    return now.astimezone(UTC)


def _below_floor(root: Path, run: Runner) -> str:
    """Why this git cannot read claims, or `""` where it is 2.22 or later."""
    text = run(["version"], root)
    if not answered(text):
        return "git did not say which version it is, and reading a claim needs git 2.22 or later"
    match = _VERSION.search(text)
    if match is None:
        return f"git's version could not be read from {text.strip()!r}; reading a claim needs 2.22"
    if (int(match.group(1)), int(match.group(2))) < GIT_FLOOR:
        return (
            f"git {match.group(0)} is older than 2.22, the first that reads one trailer key's "
            "values, so no claim was read"
        )
    return ""


def _local_branches(root: Path, run: Runner) -> frozenset[str]:
    """The checkout's own branches, by the short name `_unlanded_refs` lists them under."""
    listing = run(["for-each-ref", "--format=%(refname:short)", "refs/heads"], root)
    return frozenset(name.strip() for name in listing.splitlines() if name.strip())


def _checked_out(root: Path, run: Runner, remotes: frozenset[str]) -> str:
    """The branch `HEAD` is on, by the name a claim token uses, or `""` when detached."""
    name = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    return "" if name in {"", "HEAD"} else _head_name(name, remotes)


def _history(names: list[str], base: str, root: Path, run: Runner) -> list[_Commit] | None:
    """One branch's non-merge commits since the base, oldest first, or `None` where unproven.

    Every ref naming the branch is walked at once, so a local branch ahead of
    its tracking ref contributes its unpushed commits and neither is read
    twice. `--author-date-order`, reversed, puts every parent before its
    children and orders the rest by author date, which is what places a
    `Yield:` after the claim it ends even where a rebase has rewritten one copy
    of the branch and not the other.

    **A walk must stop because the base accounted for what came next, never
    because the checkout ran out of history.** `^base` excludes only the
    commits this checkout can reach from the base, and in a truncated clone
    the base's own history ends at a grafted commit, so everything below the
    graft goes unexcluded. A branch reaching round it - a merge of the base is
    enough - would have the base's own commits, and the claims they carry,
    read as its own. A merge-base that resolves does not rule this out: it
    proves the two share *a* commit this checkout can see, never that the walk
    can see the rest. So a commit with no parents here means the walk ran off
    a grafted history and nothing it produced is proven, and the whole branch
    is unread. The repository's true root reads the same way and is answered
    the same way, since it sits on the base. Reading the commits settles it
    rather than `is_shallow`, so a git too old to say whether the checkout is
    truncated is guarded too. A date git wrote in a shape this cannot parse is
    treated the same way, because a claim that cannot be dated can be neither
    leased nor ordered.

    **The converse does not hold, and the limit is accepted** (`PL-W1LN`,
    decided with the project owner 2026-09-13). Where the base reaches the root
    down one path and is grafted on another, a single `--depth` truncates
    unevenly, and a branch forked below the graft descends through commits
    `^base` cannot exclude before ending against the fork point the short path
    still reaches. Every commit it emits has a parent, so the test above stays
    silent and the base's own commits come back in the walk. `_landed_through`
    is what keeps them from holding anything: they wrote only content the base
    holds, so a claim they carry is spent (`PL-N162`). No sound test exists
    inside a truncated checkout - naming a branch unread whenever the base is
    grafted would silence this read in every agent container, and deepening
    the clone breaks the rule that these commands need no network.
    `test_cli.py::test_flight_reads_below_an_uneven_horizon_by_the_landed_prefix`
    pins it end to end.
    """
    output = run(
        changed_path_args(
            "log",
            "--no-merges",
            "--author-date-order",
            "--reverse",
            "--raw",
            "--no-abbrev",
            _LOG_FORMAT,
            f"^{base}",
            *names,
            "--",
        ),
        root,
    )
    entries: list[tuple[list[str], list[str], list[str]]] = []
    # Split on the NUL `-z` ends every field with, never `splitlines()`: that
    # also breaks at `\x1e`, the separator between one key's values, and read
    # that way a commit claiming two items lost both claims and itself. Git
    # opens a commit's changes with one `\n`, which belongs to no field.
    words = iter(output.split("\0"))
    for word in words:
        word = word.removeprefix("\n")
        if word.startswith(":"):
            # `:<mode> <mode> <blob> <blob> <status>`, then the path as a field
            # of its own, written as it is whatever it holds (`PL-PQ0R`).
            path = next(words, "")
            parts = word.split()
            if entries:
                entries[-1][1].append(path)
                if len(parts) == 5 and set(parts[3]) != {"0"}:
                    entries[-1][2].append(parts[3])
            continue
        fields = word.split("\x1f", _FIELDS - 1)
        if len(fields) == _FIELDS:
            entries.append((fields, [], []))
    history: list[_Commit] = []
    for fields, paths, added in entries:
        commit, authored, committed, parents, claims, yields, subject = fields
        if not parents.strip():
            return None
        try:
            when_authored = datetime.fromisoformat(authored)
            when_committed = datetime.fromisoformat(committed)
        except ValueError:
            return None
        history.append(
            _Commit(
                commit=commit,
                authored=when_authored,
                committed=when_committed,
                claims=_values(claims),
                yields=_values(yields),
                subject=subject,
                paths=tuple(paths),
                added=tuple(added),
            )
        )
    return history


def _values(field: str) -> tuple[str, ...]:
    """One trailer key's values, as the log joined them."""
    return tuple(value.strip() for value in field.split("\x1e") if value.strip())


def _events(
    histories: dict[str, list[_Commit]], branches: dict[str, list[str]], remotes: frozenset[str]
) -> tuple[list[_Claim], list[_Yield], tuple[str, ...]]:
    """Every claim and yield bound to the branch it was read on, and each unparsed trailer.

    A commit speaks only through its trailers, and each binds to a branch only
    where its token names that branch; its leading ids are attribution and
    claim nothing. So a claim commit two branches reach through a merge is one
    claim, on the branch its token names, and a commit made before the record,
    which carries no trailer, claims nothing at all (`PL-CH3Z`).
    """
    claims: dict[tuple[str, str, str], _Claim] = {}
    yields: list[_Yield] = []
    malformed: dict[tuple[str, str], str] = {}
    for branch, history in histories.items():
        for position, entry in enumerate(history):
            if not (entry.claims or entry.yields):
                continue
            for text in entry.yields:
                parsed_yield = _parse_yield(text)
                if parsed_yield is None:
                    where = f"{entry.commit[:12]} on {branches[branch][0]}"
                    malformed.setdefault((entry.commit, text), f"{where}: Yield: {text}")
                elif _head_name(parsed_yield[1], remotes) == branch:
                    yields.append(
                        _Yield(
                            key=parsed_yield[0],
                            branch=branch,
                            committed=entry.committed,
                            position=position,
                        )
                    )
            for text in entry.claims:
                parsed = _parse_claim(text)
                if parsed is None:
                    where = f"{entry.commit[:12]} on {branches[branch][0]}"
                    malformed.setdefault((entry.commit, text), f"{where}: Claim: {text}")
                    continue
                key, token, session, over = parsed
                if _head_name(token, remotes) != branch:
                    continue
                claim = _Claim(
                    key=key,
                    branch=branch,
                    commit=entry.commit,
                    authored=entry.authored,
                    committed=entry.committed,
                    position=position,
                    session=session,
                    over=over,
                )
                claims.setdefault(claim.identity, claim)
    return list(claims.values()), yields, tuple(malformed.values())


def _parse_claim(text: str) -> tuple[str, str, str, str] | None:
    """`<ID> <branch> [<session>] [over <ref>@<hash>]`, or `None` where it does not parse."""
    tokens = text.split()
    if len(tokens) < 2 or _ID.fullmatch(tokens[0]) is None:
        return None
    key, branch, rest = tokens[0].upper(), tokens[1], tokens[2:]
    session = ""
    if rest and rest[0] != "over":
        session, rest = rest[0], rest[1:]
    if not rest:
        return key, branch, session, ""
    if len(rest) != 2 or rest[0] != "over":
        return None
    ref, _, digest = rest[1].rpartition("@")
    if not ref or _HASH.fullmatch(digest) is None:
        return None
    return key, branch, session, rest[1]


def _parse_yield(text: str) -> tuple[str, str] | None:
    """`<ID> <branch>`, or `None` where it does not parse."""
    tokens = text.split()
    if len(tokens) != 2 or _ID.fullmatch(tokens[0]) is None:
        return None
    return tokens[0].upper(), tokens[1]


def _takeovers(
    claims: list[_Claim], remotes: frozenset[str]
) -> dict[tuple[str, str, str], tuple[str, str, str]]:
    """Each takeover mapped to the claim it names.

    `over <ref>@<hash>` names the claim on the same item, on the branch `<ref>`
    names, whose commit `<hash>` abbreviates. A takeover naming nothing this
    read holds - the branch is gone, or the hash matches no claim or more than
    one - takes nothing over, and orders on its own date like any other claim.
    """
    named: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    for claim in claims:
        if not claim.over:
            continue
        ref, _, digest = claim.over.rpartition("@")
        branch, prefix = _head_name(ref, remotes), digest.lower()
        matches = [
            other
            for other in claims
            if other is not claim
            and other.key == claim.key
            and other.branch == branch
            and other.commit.startswith(prefix)
        ]
        if len(matches) == 1:
            named[claim.identity] = matches[0].identity
    return named


def _episodes(
    claims: list[_Claim], yields: list[_Yield]
) -> dict[tuple[str, str], tuple[list[_Claim], datetime | None]]:
    """Per item and branch, the claims of the latest episode and when a yield ended it.

    A yield ends the episode open when it is read, and a claim after it opens
    the next; a yield with no episode open ends nothing. Within one commit a
    yield is read before a claim, so a commit carrying both leaves the branch
    holding the item - the reading that errs toward a hold. Earlier episodes all
    ended in a yield, and nothing about who holds the item now depends on them.
    """
    events: dict[tuple[str, str], list[tuple[int, int, _Claim | _Yield]]] = {}
    for ended in yields:
        events.setdefault((ended.key, ended.branch), []).append((ended.position, 0, ended))
    for claim in claims:
        events.setdefault((claim.key, claim.branch), []).append((claim.position, 1, claim))
    episodes: dict[tuple[str, str], tuple[list[_Claim], datetime | None]] = {}
    for held, found in events.items():
        episode: list[_Claim] = []
        yielded: _Yield | None = None
        for _, _, event in sorted(found, key=lambda entry: (entry[0], entry[1])):
            if isinstance(event, _Yield):
                if episode and yielded is None:
                    yielded = event
            else:
                if yielded is not None:
                    episode, yielded = [], None
                episode.append(event)
        if episode:
            episodes[held] = (episode, None if yielded is None else yielded.committed)
    return episodes


def _chain(
    start: datetime, renewals: Sequence[datetime], end: datetime, term: timedelta
) -> tuple[bool, datetime]:
    """Whether a lease begun at `start` is unbroken at `end`, and its newest renewal.

    `renewals` is every commit date on the branch, sorted. The chain runs from
    the claim through each later one to `end`, and breaks at the first gap
    longer than the term, however much is committed after it: a broken chain is
    revived by a new claim, never by a later commit. A gap of exactly the term
    holds. A commit dated after `end` renews too - that is clock skew, and
    reading it as a renewal errs toward the hold.
    """
    renewed = start
    for when in renewals:
        if when <= renewed:
            continue
        if when - renewed > term:
            return False, renewed
        renewed = when
    return end - renewed <= term, renewed


def _newest(names: list[str], root: Path, run: Runner) -> str:
    """Of the refs naming one branch, the one whose tip contains the others'.

    A local branch is this checkout's own work and usually the newer copy, but
    one checked out once and never pulled trails its tracking ref, and reading
    its copy of an item would report a status the branch left long ago. Where
    neither contains the other - a rebase not yet pushed - the local branch,
    which is listed first, is kept.
    """
    newest = names[0]
    for other in names[1:]:
        kept = run(["rev-parse", "--verify", "--quiet", newest], root).strip()
        offered = run(["rev-parse", "--verify", "--quiet", other], root).strip()
        if kept and offered and kept != offered:
            if run(["merge-base", newest, other], root).strip() == kept:
                newest = other
    return newest


def _fields_at(
    ref: str, key: str, items_dir: str, root: Path, run: Runner, copies: dict[str, dict[str, str]]
) -> dict[str, str]:
    """The front matter of the item's copy on one ref, found by its id, or `{}` where it has none.

    Found by the id at the head of the file name rather than by a path, so a
    branch that renamed the file is still read.
    """
    path = _copy(ref, items_dir, root, run, copies).get(key, "")
    if not path:
        return {}
    fields, _ = parse_front_matter(run(["show", f"{ref}:{path}"], root))
    return {name: value.strip() for name, value in fields.items()}


def _copy(
    ref: str, items_dir: str, root: Path, run: Runner, copies: dict[str, dict[str, str]]
) -> dict[str, str]:
    """Each item id `ref`'s copy of the store holds, mapped to its path, listed once per read."""
    if ref not in copies:
        copies[ref] = _item_paths_on(ref, items_dir, root, run)
    return copies[ref]


def _touched(history: list[_Commit], prefix: str) -> dict[str, tuple[int, str]]:
    """Each item whose file the branch changed, with the newest such commit's place and path."""
    found: dict[str, tuple[int, str]] = {}
    for position, entry in enumerate(history):
        for path in entry.paths:
            if not path.startswith(prefix):
                continue
            match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
            if match is not None:
                found[match.group(1).upper()] = (position, path)
    return found


def _landed_through(
    claim: _Claim,
    history: list[_Commit],
    names: list[str],
    fork: str,
    base_blobs: frozenset[str],
    root: Path,
    run: Runner,
    landed: dict[int, bool],
) -> bool:
    """Whether the branch's landed prefix takes in the claim: whether the claim is spent.

    A landed commit wrote content, all of it content the base has held, and
    the branch's own work through it - the branch as of that commit, against
    its fork - is all on the base. That is where a squash merge took the
    branch, and a claim the commit descends from, or that is the commit, has
    been spent.

    **Descends from, not sorts after.** The walk is in author-date order, and
    a merge of the base brings in commits no claim is an ancestor of. Where the
    clone is grafted unevenly, the walk reaches them below the graft, and each
    writes only content the base holds. One authored after the claim sorts
    after it, and read by place it spent a live claim (`PL-N162`'s review of its
    slice 2). So the landed commit is sought among the claim's descendants,
    newest first. Taking the newest landed commit overall and then asking about
    ancestry would leave the claim live when a squash really had taken it.

    **Both tests, because either alone releases a live claim.** The commit's
    own blobs are true of an empty commit - the claim commit itself - and of
    one reverting a file to a version the base once held; the branch-level
    test is what a squash actually proves. The first is a necessary condition
    of the second, since a blob the commit writes is either in the branch's
    net change or is the fork's own copy, so it picks the candidates from the
    walk already made and only a candidate costs a diff; `landed` keeps each
    diff's answer by place, for the branch's other claims. A branch the squash
    cannot be proven against - a file the base resolved against its own later
    edits (`PL-LKFP`) - keeps its claims until a yield or the lease, and so does
    one git would not list descendants for.
    """
    if not fork:
        return False
    after = set(run(["rev-list", "--ancestry-path", f"^{claim.commit}", *names], root).split())
    after.add(claim.commit)
    # A descendant sorts after its ancestors in the walk, so nothing before the
    # claim can be one.
    for position in range(len(history) - 1, claim.position - 1, -1):
        entry = history[position]
        if entry.commit not in after:
            continue
        if not entry.added or not all(blob in base_blobs for blob in entry.added):
            continue
        if position not in landed:
            split = _landing_split(entry.commit, fork, base_blobs, root, run)
            landed[position] = _work_already_on_base(split)
        if landed[position]:
            return True
    return False


def _cuts(
    histories: dict[str, list[_Commit]],
    branches: dict[str, list[str]],
    tips: dict[str, str],
    last: dict[str, datetime],
    base: str,
    notes_dir: str,
    root: Path,
    run: Runner,
    moment: datetime,
) -> tuple[Hold, ...]:
    """One live hold per release a branch is cutting, `vcs.cuts_in_flight`'s read.

    Asked only of a branch a commit of which touched `notes_dir`, which no
    branch but a release's does. `mine` is today's rule: `HEAD` contains the
    branch's tip, so a session's own cut pushed under another name is its own.
    """
    prefix = notes_dir.strip("/") + "/"
    cutting = [
        branch
        for branch, history in histories.items()
        if any(path.startswith(prefix) for entry in history for path in entry.paths)
    ]
    if not cutting:
        return ()
    released = _notes_on(base, notes_dir, root, run)
    found: list[Hold] = []
    for branch in cutting:
        tip = tips[branch]
        name = branches[branch][0]
        head = run(["rev-parse", tip], root).strip()
        mine = bool(head) and run(["merge-base", head, "HEAD"], root).strip() == head
        for version in _cut_versions(tip, base, notes_dir, released, root, run):
            written = run(
                ["log", "-1", "--format=%H%x1f%aI", tip, "--", f"{prefix}v{version}.md"], root
            )
            commit, _, stamp = written.strip().partition("\x1f")
            try:
                since = datetime.fromisoformat(stamp)
            except ValueError:
                since = last.get(name, moment)
            found.append(
                Hold(
                    key=version,
                    ref=name,
                    kind=CUT,
                    state=LIVE,
                    since=since,
                    renewed=last.get(name, since),
                    commit=commit,
                    mine=mine,
                    on_base=False,
                )
            )
    return tuple(sorted(found, key=lambda hold: (hold.ref, hold.key)))


def _editing(
    touched: dict[str, dict[str, tuple[int, str]]],
    branches: dict[str, list[str]],
    tips: dict[str, str],
    last: dict[str, datetime],
    held: set[str],
    base: str,
    root: Path,
    run: Runner,
    copies: dict[str, dict[str, str]],
) -> tuple[QueueEdit, ...]:
    """Refs that edited an item's file where nothing holds the item: `FlightReport.editing`.

    The weaker mark (`PL-N1JK`): a second edit to the file collides at merge
    whatever either was for. An edit the base's tip already accounts for is not
    one (`PL-8MJ3`), which `vcs._superseded` asks once per branch.

    **Every branch whose edit survives is reported, in the order refs were
    listed** (`PL-1X2C`). Keeping only the first per item left out the one that
    would actually collide: run on the second of two branches that had promoted
    `PL-B8MK`, `show` named the reader's own and said nothing of the other. The
    checked-out branch is reported with the rest, because this is a measurement
    of the refs; a command that answers a reader leaves its own branch out, by
    `Holdings.head`, since the reader already knows what it wrote.
    """
    edited: dict[str, list[QueueEdit]] = {}
    for branch, found in touched.items():
        wanted = {key: path for key, (_, path) in found.items() if key not in held}
        if not wanted:
            continue
        tip = tips[branch]
        at_tip = copies.get(tip, {})
        paths = {key: at_tip.get(key, path) for key, path in wanted.items()}
        spent = _superseded(tip, base, tuple(sorted(set(paths.values()))), root, run)
        name = branches[branch][0]
        for key, path in paths.items():
            if path not in spent:
                edited.setdefault(key, []).append(
                    QueueEdit(name=name, item_id=key, last_commit=last.get(name))
                )
    return tuple(edit for key in sorted(edited) for edit in edited[key])
