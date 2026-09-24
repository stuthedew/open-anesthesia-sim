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
lapse, or landing. The first four are decided here. Landing is split: the
ref-level half - the branch is contained in the base, or its content is -
arrives with `vcs._unlanded_refs`, which never offers a landed ref, and the
per-claim half (the landed prefix, an item closed on the base) belongs to
`PL-NST2`, with disposition holds, cut holds, the `resource:` field and
`Holdings.flight()`.

**A commit made before claims were recorded is read by the old rules**
(`CUTOVER_MARKER`): a subject leading with ids claims them where the commit's
diff is empty or reaches outside the queue - `vcs._annotates_only`'s rule -
under the same lease, and with none of `vcs`'s promotions. `PL-CH3Z` deletes
that reading once no ref carries such a commit.

**git 2.22 is the floor** (`GIT_FLOOR`), declared rather than worked around: a
git that cannot read one trailer key's values declines, and says so, rather
than having git's trailer rules re-implemented here.
"""

from __future__ import annotations

import os
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .model import CLOSED_STATUSES, parse_front_matter
from .store import ID_PATTERN
from .vcs import (
    Runner,
    _annotates_only,
    _closed_on_base,
    _head_name,
    _item_paths_on,
    _remotes,
    _run_git,
    _Silences,
    _unlanded_refs,
    answered,
    default_base,
    leading_ids,
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

#: The file whose presence in a commit's own tree says the commit was made after
#: claims were recorded: this module, which reached the default branch with the
#: reader. A commit whose tree lacks it predates the record and is read by the
#: old rules. The test needs no clock and survives the branch merging `main`
#: later - the merge gives the branch the file and leaves the commits before it
#: as they were. The path is this repository's layout, and it goes when
#: `PL-CH3Z` removes the old reading.
CUTOVER_MARKER = "subprojects/docket/src/docket/claims.py"

#: Where a remote session's own id is read from, to decide `Hold.mine`. `claim`
#: writes the same variable's value as a claim's `<session>` token.
SESSION_VARIABLE = "CLAUDE_CODE_REMOTE_SESSION_ID"

#: `Hold.kind` for a recorded claim. `PL-NST2` adds the disposition and cut kinds.
CLAIM = "claim"

#: `Hold.state`: holding the item at `now`, out of lease, or ended.
LIVE = "live"
LAPSED = "lapsed"
RELEASED = "released"

#: `Hold.released_by`: which of the release routes ended a released claim.
BY_YIELD = "yield"
BY_STATUS = "status"
BY_OVER = "over"

# One line per non-merge commit in `base..R`: its hash, both dates, its parents,
# the values of its `Claim:` and `Yield:` trailers, and its subject. The unit
# separator delimits fields and the record separator the values of one key,
# because a subject can hold anything a keyboard can type; `unfold` joins a
# trailer value git has folded onto a continuation line. `%P` is empty for a
# commit whose parents this checkout lacks, which is how a walk that ran off a
# truncated history is told from one the base stopped. The subject comes last so
# a stray separator in it cannot shift the fields before it.
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
    #: without one and for every claim read by the old rules.
    session: str = ""
    status: str = ""
    #: Whether this checkout's session made the claim. Decided by the session
    #: token where the claim carries one, and otherwise by whether the checkout's
    #: `HEAD` is on the claiming branch - never by order.
    mine: bool = False
    on_base: bool = True
    #: Read by the old rules, from a commit made before claims were recorded.
    legacy: bool = False
    #: `BY_YIELD`, `BY_STATUS` or `BY_OVER` for a released hold, and empty
    #: otherwise.
    released_by: str = ""
    #: The `<ref>@<hash>` this claim took over, as written.
    over: str = ""


@dataclass(frozen=True)
class Holdings:
    """Every hold the readable refs record, and what could not be read to find out.

    `holds` is sorted by item and, within one item, into the order that decides
    which branch continues: author date, then hash, with a takeover immediately
    ahead of the claim it names. `order` and `ids` read only the live ones.

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
    unreadable: tuple[str, ...] = ()
    malformed: tuple[str, ...] = ()
    base: str = ""
    #: The one moment every lease in this read was judged at.
    now: datetime | None = None
    #: The held items whose copy on the base is closed, which `lapsed_open`
    #: leaves out.
    closed_on_base: frozenset[str] = frozenset()
    declined: str = ""

    @property
    def ids(self) -> frozenset[str]:
        """The items some branch holds live."""
        return frozenset(hold.key for hold in self.holds if hold.state == LIVE)

    def order(self, key: str) -> tuple[Hold, ...]:
        """The live holds on one item, the one that continues first."""
        wanted = key.upper()
        return tuple(hold for hold in self.holds if hold.key == wanted and hold.state == LIVE)

    def lapsed_open(self) -> tuple[Hold, ...]:
        """Lapsed holds on items the base still holds open: dead claims worth taking over.

        An item the base has closed, or has no copy of, is no longer anybody's
        to start, so a dead claim on it is not worth a line.
        """
        return tuple(
            hold
            for hold in self.holds
            if hold.state == LAPSED and hold.on_base and hold.key not in self.closed_on_base
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
    legacy: bool = False

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


def holdings(
    root: Path,
    *,
    now: datetime,
    items_dir: str = "docs/items",
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
    branches, as it does for `vcs.branches_in_flight`. `include_head=False`
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

    claims, yields, malformed = _events(histories, branches, items_dir, remotes, root, run)
    episodes = _episodes(claims, yields)
    if not episodes:
        return Holdings(
            unreadable=tuple(name for name in candidates if name in unreadable),
            malformed=malformed,
            base=base,
            now=moment,
            declined=run.reason,
        )
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
    on_base = set(_item_paths_on(base, items_dir, root, run))
    renewals = {
        branch: sorted(entry.committed for entry in history)
        for branch, history in histories.items()
    }
    tips: dict[str, str] = {}
    copies: dict[str, dict[str, str]] = {}

    ranked: list[tuple[str, tuple[datetime, str, int, datetime, str], Hold]] = []
    for (key, branch), (episode, yielded) in episodes.items():
        standing = [claim for claim in episode if claim.identity not in superseded]
        end = moment if yielded is None else yielded
        # The earliest claim whose lease is unbroken holds; any later claim in
        # the same chain is a renewal of it. Where every chain broke, the last
        # claim made stands for the episode, lapsed.
        holder: _Claim | None = None
        unbroken, renewed = False, moment
        for claim in standing:
            unbroken, renewed = _chain(claim.committed, renewals[branch], end, term)
            if unbroken:
                holder = claim
                break
        if holder is None:
            holder = (standing or episode)[-1]
            unbroken, renewed = _chain(holder.committed, renewals[branch], end, term)

        names = branches[branch]
        if branch not in tips:
            tips[branch] = _newest(names, root, run)
        status = _status_at(tips[branch], key, items_dir, root, run, copies)
        if not standing:
            state, released_by = RELEASED, BY_OVER
        elif yielded is not None:
            state, released_by = RELEASED, BY_YIELD
        elif status in RELEASING_STATUSES:
            state, released_by = RELEASED, BY_STATUS
        else:
            state, released_by = (LIVE if unbroken else LAPSED), ""

        tokens = {claim.session for claim in episode[episode.index(holder) :] if claim.session}
        hold = Hold(
            key=key,
            ref=names[0],
            kind=CLAIM,
            state=state,
            since=holder.authored,
            renewed=renewed,
            commit=holder.commit,
            session=holder.session,
            status=status,
            mine=session in tokens if tokens else bool(here) and branch == here,
            on_base=key in on_base,
            legacy=holder.legacy,
            released_by=released_by,
            over=holder.over,
        )
        ranked.append((key, rank(holder), hold))

    ranked.sort(key=lambda entry: (entry[0], entry[1]))
    held = {key for key, _, _ in ranked}
    return Holdings(
        holds=tuple(hold for _, _, hold in ranked),
        unreadable=tuple(name for name in candidates if name in unreadable),
        malformed=malformed,
        base=base,
        now=moment,
        closed_on_base=_closed_on_base(held, items_dir, base, root, run),
        declined=run.reason,
    )


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
    because the checkout ran out of history** - `vcs._unmerged_commits` has the
    argument. A commit with no parents here means the walk ran off a grafted
    history and nothing it produced is proven, so the whole branch is unread.
    A date git wrote in a shape this cannot parse is treated the same way,
    because a claim that cannot be dated can be neither leased nor ordered.
    """
    output = run(
        [
            "log",
            "--no-merges",
            "--author-date-order",
            "--reverse",
            "--name-only",
            _LOG_FORMAT,
            f"^{base}",
            *names,
            "--",
        ],
        root,
    )
    entries: list[tuple[list[str], list[str]]] = []
    for line in output.splitlines():
        fields = line.split("\x1f", _FIELDS - 1)
        if len(fields) == _FIELDS:
            entries.append((fields, []))
        elif line.strip() and entries:
            # Everything else is one of that commit's paths, or the blank line
            # git writes between a commit and its paths.
            entries[-1][1].append(line.strip())
    history: list[_Commit] = []
    for fields, paths in entries:
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
            )
        )
    return history


def _values(field: str) -> tuple[str, ...]:
    """One trailer key's values, as the log joined them."""
    return tuple(value.strip() for value in field.split("\x1e") if value.strip())


def _events(
    histories: dict[str, list[_Commit]],
    branches: dict[str, list[str]],
    items_dir: str,
    remotes: frozenset[str],
    root: Path,
    run: Runner,
) -> tuple[list[_Claim], list[_Yield], tuple[str, ...]]:
    """Every claim and yield bound to the branch it was read on, and each unparsed trailer.

    A commit made after claims were recorded speaks only through its trailers,
    and each binds to a branch only where its token names that branch; its
    leading ids are attribution and claim nothing. A commit made before is read
    by the old rule and nothing else. Which of the two a commit is is asked only
    of commits that could say something under either reading, and once each.
    """
    prefix = items_dir.strip("/") + "/"
    recorded: dict[str, bool] = {}
    claims: dict[tuple[str, str, str], _Claim] = {}
    yields: list[_Yield] = []
    malformed: dict[tuple[str, str], str] = {}
    for branch, history in histories.items():
        for position, entry in enumerate(history):
            ids = leading_ids(entry.subject)
            old_rule = bool(ids) and not _annotates_only(list(entry.paths), prefix)
            if not (entry.claims or entry.yields or old_rule):
                continue
            if entry.commit not in recorded:
                marker = run(["show", f"{entry.commit}:{CUTOVER_MARKER}"], root)
                recorded[entry.commit] = bool(marker.strip())
            if not recorded[entry.commit]:
                # Made before claims were recorded: any trailer it carries is
                # not read, and the old rule is the whole of what it says.
                if old_rule:
                    for key in ids:
                        claim = _Claim(
                            key=key,
                            branch=branch,
                            commit=entry.commit,
                            authored=entry.authored,
                            committed=entry.committed,
                            position=position,
                            legacy=True,
                        )
                        claims.setdefault(claim.identity, claim)
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
        mine = run(["rev-parse", "--verify", "--quiet", newest], root).strip()
        theirs = run(["rev-parse", "--verify", "--quiet", other], root).strip()
        if mine and theirs and mine != theirs:
            if run(["merge-base", newest, other], root).strip() == mine:
                newest = other
    return newest


def _status_at(
    ref: str, key: str, items_dir: str, root: Path, run: Runner, copies: dict[str, dict[str, str]]
) -> str:
    """The item's status in one ref's copy, found by its id, or `""` where it has none.

    Found by the id at the head of the file name rather than by a path, so a
    branch that renamed the file is still read.
    """
    if ref not in copies:
        copies[ref] = _item_paths_on(ref, items_dir, root, run)
    path = copies[ref].get(key, "")
    if not path:
        return ""
    fields, _ = parse_front_matter(run(["show", f"{ref}:{path}"], root))
    return fields.get("status", "").strip()
