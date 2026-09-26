"""Write a claim or a yield: the only code that writes what `claims` reads.

`claims.holdings` answers who holds an item from `Claim:` and `Yield:` trailers
on each holder's own branch (`PL-MB2W` § "Design round, 2026-09-24"). A
trailer a session types by hand is one blank line away from being prose, so
the record is written here, by `bin/docket claim` and `bin/docket yield`, and a
session has two things to remember: `claim` at pickup and for every rider, and
`yield` when it stops without closing.

**A claim is one empty commit**, subject `<IDs>: start`, whose last paragraph
holds one `Claim: <ID> <branch> [<session>] [over <ref>@<hash>]` line per item
and the attribution lines the session's commits must end with - in the same
paragraph, because git reads trailers from the last paragraph alone, and an
attribution line added below the claim afterwards turns it into prose. Empty,
and made with `--only`, so nothing staged rides it.

**It checks before it writes, and reads back after.** It fetches, then refuses
with `HELD_ELSEWHERE` and writes nothing where a live claim on another branch
orders first - unless `--over` names that branch, or `HEAD` already contains
that branch's tip, which is a continuation and is written as a takeover
without being asked. It pushes only a branch the remote does not have, unless
`push` says auto-merge is disarmed, and asks the remote itself rather than the
tracking setting or the clone's tracking ref (`PL-WX87`): a branch the remote
has may have a pull request open and armed, and a push would merge the claim
away with the branch (`PL-QP9Z`). It asks once, listing every branch the remote
has, and the read of who holds what is filtered by that listing too, so a
tracking ref for a branch the remote has deleted holds nothing there
(`PL-MT3R`). An upstream naming the default branch is how
the web harness starts a session branch (`PL-KX73`), so it is not refused as
pushing to another branch, and the push gives the branch its own. After a push
it fetches again and re-reads, because a claim pushed in the same minute is
invisible until then; where that one orders first, the answer is
`HELD_ELSEWHERE` and the line to yield by. A claim that did not reach the
remote is `LOCAL_ONLY`, whether its push failed or the branch's copy on the
remote meant none was tried: no other session can fetch it, and a session
reports the exit status as evidence that its claim is visible, so `CLAIMED`
would say it was held when it is not (`PL-1X56`). So is one where the remote
could not be asked, since whether it has the branch is what the push waits on
(`PL-WX87`), and one git could not compare with the branch's copy there, a tip
another writer pushed after this clone last fetched: that is said as not known
rather than as local, and nothing is pushed (`PL-20DL`). The message says
which, and names the `claim` that publishes it.

**A claim never pushed yields to one already published** (`PL-ZLJ9`). Claims
order by author date and git records no push time, so a claim written first
and published last would order first, and take the item from a session told
it held it while this one was invisible. So before anything else, every live
claim of this branch's that orders first but is not on the remote's copy of
the branch, where a claim on another branch is on that branch's copy, is
withdrawn: a `Yield:` committed and not pushed, since it matters only once the
claim it ends is published, and rides the same push. Every one, not only those
asked for, because a push publishes them all. An item asked for that is
withdrawn refuses the call with `HELD_ELSEWHERE`. A claim published by a hand
or work push skips the check, which is why every message asking for a push of
a claim names `claim` rather than `git push`; the item records that residual.
Where the remote could not be asked the check waits for a run that can ask it,
since which of this branch's claims are on its copy is what went unanswered,
and nothing is pushed until then.

**Why writes go round the command's runner.** `vcs._run_git` reads exit 1 as
git answering "no", and a failed push or fetch exits 1 too, so a write read
through it would report success it never had. And `GitRunner` remembers
answers for the command's lifetime, so every read after a write here is put to
git afresh, through `_run_git`.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .claims import (
    BY_CLOSED,
    BY_YIELD,
    LAPSED,
    LIVE,
    RELEASED,
    RELEASING_STATUSES,
    SESSION_VARIABLE,
    Hold,
    Holdings,
    _parse_claim,
    _parse_yield,
    holdings,
)
from .model import CLOSED_STATUSES, parse_front_matter
from .store import ID_PATTERN
from .vcs import (
    RemoteHeads,
    Runner,
    _head_name,
    _item_paths_on,
    _remotes,
    _run_git,
    _unlanded_refs,
    base_copies,
    default_base,
    remote_heads,
)

#: Exit statuses. `USAGE` is argparse's own. `HELD_ELSEWHERE` and `LOCAL_ONLY`
#: are the two a session has to act on differently from a plain refusal: the
#: first means another session has the item, the second that the claim exists
#: only in this checkout - its push failed, or the branch's copy on the remote
#: meant none was tried - until the push the message names, or that the remote
#: could not be asked whether it does, or git could not compare its copy.
CLAIMED = 0
REFUSED = 1
USAGE = 2
HELD_ELSEWHERE = 3
LOCAL_ONLY = 4

#: The remote a claim is fetched from and pushed to, as `vcs.fetch_remote` has it.
REMOTE = "origin"

#: How long one write is given. A push through the harness proxy is seconds, but
#: this is a write whose failure is reported rather than retried, so it is given
#: far longer than the ten seconds `vcs._run_git` gives a read.
WRITE_TIMEOUT = 120.0

# What an attribution line must look like to stay a trailer: a token, a colon, a
# space, a value, on one line. Anything else in the last paragraph can make git
# read the whole paragraph as prose, and the claim with it.
_TRAILER = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*: \S.*")
_ID = re.compile(ID_PATTERN, re.I)


@dataclass(frozen=True)
class Written:
    """What `claim` or `yield_claims` did: its exit status, what to print, and the commit."""

    code: int
    lines: tuple[str, ...]
    #: The commit written, or `""` where nothing was.
    commit: str = ""


@dataclass(frozen=True)
class _Ran:
    code: int
    out: str
    err: str


@dataclass(frozen=True)
class _Branch:
    """The branch a claim or yield is written on, and what was learned checking it."""

    name: str
    remotes: frozenset[str]


@dataclass(frozen=True)
class _OnRemote:
    """What the remote itself holds of the branch, read by `_on_remote` from its listing."""

    #: The branch's tip there, or `""` where the remote has no such branch.
    tip: str
    #: Why the remote's branches could not be listed, and `tip` then says nothing.
    failed: str = ""


#: The read-back a write is judged by, given the checkout, the fresh read, the ids
#: written, the branch and the commit: the exit status, and what to add.
_Check = Callable[[Path, Holdings, list[str], _Branch, str], tuple[int, list[str]]]


def claim(
    root: Path,
    keys: Sequence[str],
    *,
    items_dir: str,
    now: datetime,
    over: str = "",
    reason: str = "",
    trailers: Sequence[str] = (),
    fetch: bool = True,
    push: bool = False,
    runner: Runner | None = None,
) -> Written:
    """Claim `keys` for the branch `HEAD` is on, in one empty commit.

    All or nothing: an item another branch holds first refuses the whole call,
    so no session ends up holding half of what it asked for. `over` names the
    branch a takeover is from, and `reason` - required with it - goes into the
    commit's body; the evidence a takeover needs (the owner's word, or
    `get_session` showing that session archived or failed) is the session's to
    have, since nothing here can ask for it. `push` pushes a branch the remote
    already has, which the caller says is safe: no pull request on it armed.

    An item this branch already holds first is left alone, so running `claim`
    twice writes one commit.
    """
    wanted, problem = _keys(keys)
    if problem:
        return Written(USAGE, (f"claim: {problem}",))
    bad = _bad_trailers(trailers)
    if bad:
        return Written(USAGE, (f"claim: {bad}",))
    if bool(over) != bool(reason.strip()):
        return Written(
            USAGE,
            ("claim: `--over` and `--reason` go together: a takeover records why it was sound",),
        )
    run = runner or _run_git
    branch, refused = _branch(root, run, items_dir, wanted, "claim")
    if refused:
        return Written(REFUSED, refused)
    if fetch:
        fetched = _git(["fetch", "--quiet", REMOTE], root)
        if fetched.code != 0:
            return Written(
                REFUSED,
                (
                    f"claim: `git fetch {REMOTE}` failed, so a claim another session pushed "
                    "cannot be ruled out; nothing was written",
                    *_indented(fetched.err),
                    "  Refresh the refs yourself and pass `--no-fetch`, or try again.",
                ),
            )
        run = _run_git
    # Listed once, since nothing before the push `_publish` decides on moves the
    # remote's copy of this branch, and read by both questions put to the remote
    # below: who holds each item, and whether this branch is there to push onto.
    heads = remote_heads(root)
    read = holdings(root, now=now, items_dir=items_dir, remote=heads, runner=run)
    if not read.known:
        return Written(
            REFUSED,
            (
                f"claim: declined to read who holds these items - {read.declined}; "
                "nothing was written",
            ),
        )
    notes = _unread(read)
    closed = _closed_on_base(root, read.base, wanted, items_dir, run)
    if closed:
        return Written(REFUSED, (*notes, *closed))
    remote = _on_remote(heads, branch.name)
    # Which of this branch's claims are on that copy is what `_displaced` asks;
    # where the remote could not say, nothing is pushed, so the check waits for
    # a run that can ask it rather than withdraw on a guess.
    displaced = {} if remote.failed else _displaced(root, read, branch, remote, heads)
    if displaced:
        withdrawn = _withdraw(root, branch, displaced, trailers=trailers, asked=wanted)
        if withdrawn.code != CLAIMED:
            return Written(withdrawn.code, (*notes, *withdrawn.lines), withdrawn.commit)
        notes.extend(withdrawn.lines)

    takeovers: dict[str, Hold] = {}
    reasons: list[str] = [" ".join(reason.split())] if reason.strip() else []
    blocked: list[str] = []
    #: Each item this branch already holds first, and the claim commit holding it.
    already: dict[str, str] = {}
    for key in wanted:
        live = read.order(key)
        mine = [hold for hold in live if _branch_of(hold, branch) == branch.name]
        others = [hold for hold in live if _branch_of(hold, branch) != branch.name]
        rival = others[0] if others else None
        if mine and (rival is None or live.index(mine[0]) < live.index(rival)):
            already[key] = mine[0].commit
            continue
        named = _named(read, key, over, branch) if over else None
        if over and named is None:
            notes.append(f"{key}: `--over {over}` names no claim on it, so none is taken over")
        if rival is None:
            if named is not None:
                takeovers[key] = named
            continue
        other = _branch_of(rival, branch)
        if named is not None and _branch_of(named, branch) == other:
            takeovers[key] = named
        elif _continues(root, branch, other):
            takeovers[key] = rival
            reasons.append(f"{key} continues {other}, whose tip this branch contains.")
        else:
            blocked.extend(_held_first(rival, key, written=False))
    if blocked:
        return Written(HELD_ELSEWHERE, (*notes, *blocked))
    for key in already:
        notes.append(f"{key}: {branch.name} already holds it first; nothing written for it")
    writing = [key for key in wanted if key not in already]
    if not writing:
        published = {key: _published(root, remote, made) for key, made in already.items()}
        unknown = [key for key, state in published.items() if state is None]
        if unknown:
            return Written(LOCAL_ONLY, (*notes, *_uncompared(unknown, "claim", branch, remote)))
        unpushed = [key for key, state in published.items() if not state]
        if not unpushed:
            return Written(CLAIMED, tuple(notes))
        # An earlier run wrote the claim and could not push it; this run is
        # its retry, and a claim no other session can see is not held.
        return _publish(
            root,
            branch,
            unpushed,
            _head(root),
            remote=remote,
            made_now=False,
            command="claim",
            push=push,
            now=now,
            items_dir=items_dir,
            said=notes,
            check=_claimed,
        )

    token = _session_token()
    lines = []
    for key in writing:
        taken = takeovers.get(key)
        tail = f" over {_branch_of(taken, branch)}@{taken.commit}" if taken is not None else ""
        lines.append(f"Claim: {key} {branch.name}{f' {token}' if token else ''}{tail}")
    return _write(
        root,
        branch,
        writing,
        verb="start",
        body=reasons,
        trailers=[*lines, *trailers],
        remote=remote,
        push=push,
        now=now,
        items_dir=items_dir,
        notes=notes,
        check=_claimed,
    )


def yield_claims(
    root: Path,
    keys: Sequence[str],
    *,
    items_dir: str,
    now: datetime,
    trailers: Sequence[str] = (),
    runner: Runner | None = None,
) -> Written:
    """End this branch's claim on `keys` without closing them, in one empty commit.

    For a session that stops working an item it has not finished: its branch
    goes on holding the item until the lease runs out otherwise, and every
    other session is told the item is taken. A lapsed claim can be yielded too,
    which stops it being offered as a dead claim worth taking over. An item
    whose claim has already ended is left alone; one this branch never claimed
    is refused, since the id is more likely mistyped than meant.

    **Run again, it is the retry of a yield an earlier run could not push**,
    as `claim` is of a claim (`PL-NNLM`). The claim reads as ended from the
    local branch, where that yield already stands, while every other session
    reads the remote's copy and still sees the item held; so an ended claim
    whose `Yield:` the remote's tip does not carry goes to `_publish` again,
    rather than reporting a success nobody else can see.
    """
    wanted, problem = _keys(keys)
    if problem:
        return Written(USAGE, (f"yield: {problem}",))
    bad = _bad_trailers(trailers)
    if bad:
        return Written(USAGE, (f"yield: {bad}",))
    run = runner or _run_git
    branch, refused = _branch(root, run, items_dir, (), "yield")
    if refused:
        return Written(REFUSED, refused)
    # One listing for every question this puts to the remote, as `claim` takes.
    heads = remote_heads(root)
    read = holdings(root, now=now, items_dir=items_dir, remote=heads, runner=run)
    if not read.known:
        return Written(
            REFUSED, (f"yield: declined to read what this branch holds - {read.declined}",)
        )
    notes: list[str] = []
    writing: list[str] = []
    unheld: list[str] = []
    #: Each item whose claim here a yield of this branch's has already ended.
    ended: list[str] = []
    for key in wanted:
        mine = [
            hold
            for hold in read.holds
            if hold.key == key and _branch_of(hold, branch) == branch.name
        ]
        if any(hold.state in (LIVE, LAPSED) for hold in mine):
            writing.append(key)
        elif mine:
            notes.append(f"{key}: {branch.name}'s claim on it has already ended; nothing written")
            if any(hold.released_by == BY_YIELD for hold in mine):
                ended.append(key)
        else:
            unheld.append(key)
    if unheld:
        return Written(
            REFUSED,
            tuple(
                f"yield: {branch.name} holds no claim on {key}, so there is nothing to yield"
                for key in unheld
            ),
        )
    if not writing:
        if not ended:
            return Written(CLAIMED, tuple(notes))
        remote = _on_remote(heads, branch.name)
        published: dict[str, bool | None] = {}
        for key in ended:
            made = _recorded(root, read.base, branch, key, trailer="Yield")
            if made:
                published[key] = _published(root, remote, made)
        unknown = [key for key, state in published.items() if state is None]
        if unknown:
            return Written(LOCAL_ONLY, (*notes, *_uncompared(unknown, "yield", branch, remote)))
        unpushed = [key for key, state in published.items() if not state]
        if not unpushed:
            return Written(CLAIMED, tuple(notes))
        # An earlier run wrote the yield and could not push it; this run is
        # its retry, and a yield no other session can see ends nothing for them.
        return _publish(
            root,
            branch,
            unpushed,
            _head(root),
            remote=remote,
            made_now=False,
            command="yield",
            now=now,
            items_dir=items_dir,
            said=notes,
            check=_yielded,
        )
    return _write(
        root,
        branch,
        writing,
        verb="yield",
        body=[],
        trailers=[*(f"Yield: {key} {branch.name}" for key in writing), *trailers],
        remote=_on_remote(heads, branch.name),
        now=now,
        items_dir=items_dir,
        notes=notes,
        check=_yielded,
    )


def _keys(keys: Sequence[str]) -> tuple[list[str], str]:
    """The ids asked for, upper-cased and once each, or why they cannot be."""
    wanted: list[str] = []
    for key in keys:
        if _ID.fullmatch(key) is None:
            return [], f"{key!r} is not an item id"
        if key.upper() not in wanted:
            wanted.append(key.upper())
    return wanted, ""


def _bad_trailers(trailers: Sequence[str]) -> str:
    """Why an attribution line would not stay a trailer, or `""` where each one would."""
    for line in trailers:
        if _TRAILER.fullmatch(line) is None:
            return (
                f"{line!r} is not a trailer - one line of `Key: value` - and in the claim's "
                "paragraph it could turn the claim into prose"
            )
        if line.split(":", 1)[0].lower() in {"claim", "yield"}:
            return f"{line!r} would be read as a claim record; `claim` and `yield` write those"
    return ""


def _branch(
    root: Path, run: Runner, items_dir: str, keys: Sequence[str], command: str
) -> tuple[_Branch, tuple[str, ...]]:
    """The branch `HEAD` is on, or why nothing may be written on it.

    Refused on a detached `HEAD`, on the default branch, whose own commits are
    never read for claims, and on a branch pushing to one of another name,
    since the claim names its branch and would bind to neither.

    A branch tracking the default branch is not pushing to one of another name.
    It has no upstream of its own yet - `git checkout -b <branch> --track
    origin/main` is how the web harness starts a session branch (`PL-KX73`) -
    so it is read as having none, and the remote's copy decides whether the
    claim is pushed.

    For `claim`, each id must be an item `HEAD` holds and at a status that does
    not release a claim the moment it is written.
    """
    remotes = _remotes(root, run)
    name = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    empty = _Branch(name="", remotes=remotes)
    if name in {"", "HEAD"}:
        return empty, (f"{command}: HEAD is detached; a claim names the branch it is on",)
    base = _head_name(default_base(root, runner=run), remotes)
    if name == base:
        return empty, (
            f"{command}: HEAD is on {name}, the default branch, whose commits are never read "
            "for claims; start a work branch first",
        )
    upstream = run(
        ["for-each-ref", "--format=%(upstream:short)", f"refs/heads/{name}"], root
    ).strip()
    if upstream and _head_name(upstream, remotes) == base:
        upstream = ""
    if upstream and _head_name(upstream, remotes) != name:
        return empty, (
            f"{command}: {name} pushes to {upstream}, and a claim names one branch; "
            "give them one name first",
        )
    branch = _Branch(name=name, remotes=remotes)
    problems: list[str] = []
    copies = _item_paths_on("HEAD", items_dir, root, run) if keys else {}
    for key in keys:
        path = copies.get(key, "")
        if not path:
            problems.append(
                f"{command}: HEAD holds no item {key}; commit a capture before claiming it"
            )
            continue
        fields, _ = parse_front_matter(run(["show", f"HEAD:{path}"], root))
        status = fields.get("status", "").strip()
        if status in RELEASING_STATUSES:
            problems.append(
                f"{command}: {key} is `{status}` in HEAD's copy, which releases a claim as soon "
                "as it is written; set its status first"
            )
    return branch, tuple(problems)


def _closed_on_base(
    root: Path, base: str, keys: Sequence[str], items_dir: str, run: Runner
) -> tuple[str, ...]:
    """Why each item asked for is refused because the default branch has closed it.

    `holdings` releases a claim on an item the base has closed whatever the
    branch's own copy says (`BY_CLOSED`), and `_branch` reads only `HEAD`'s
    copy. So a branch forked before another session's close-out landed wrote
    the claim, pushed it, and read it back dead - reported as a defect in
    docket (`PL-Y48N`). Read after the fetch, from the base the read-back
    uses, so the rule refusing a claim here is the rule that would have
    released it there.

    The base's copy is read whether or not the base changed it since the
    fork, because the release does not ask; which of the two it was only
    decides what the refusal tells the session to do, and where that could
    not be read the refusal says only what it knows.
    """
    newer = base_copies(root, base, items_dir=items_dir, keys=keys, runner=run)
    paths = _item_paths_on(base, items_dir, root, run)
    refused: list[str] = []
    for key in keys:
        copy = newer.of(key)
        if copy is not None:
            status = copy.status
        elif key in paths:
            status = parse_front_matter(run(["show", f"{base}:{paths[key]}"], root))[0].get(
                "status", ""
            )
        else:
            continue
        if status not in CLOSED_STATUSES:
            continue
        released = f"a claim on an item {base} has closed is released as soon as it is written"
        if copy is not None:
            refused.append(
                f"claim: {key} is `{status}` on {base}, which closed it after this branch forked, "
                f"and {released}; nothing was written. `bin/docket branch` says how to bring "
                f"{base} in, and another item is the one to pick"
            )
        elif newer.declined:
            refused.append(
                f"claim: {key} is `{status}` on {base}, and {released}; nothing was written"
                f" (whether {base} closed it after this branch forked could not be read -"
                f" {newer.declined})"
            )
        else:
            refused.append(
                f"claim: {key} is `{status}` on {base} and this branch's copy reopens it, and "
                f"{released}; nothing was written, and the reopening has to reach {base} first"
            )
    return tuple(refused)


def _branch_of(hold: Hold, branch: _Branch) -> str:
    """The branch a hold is on, by the name a claim token uses."""
    return _head_name(hold.ref, branch.remotes)


def _named(read: Holdings, key: str, over: str, branch: _Branch) -> Hold | None:
    """The claim on `key` that `--over` names: that branch's live or lapsed hold."""
    wanted = _head_name(over, branch.remotes)
    for hold in read.holds:
        if hold.key == key and hold.state != RELEASED and _branch_of(hold, branch) == wanted:
            return hold
    return None


def _continues(root: Path, branch: _Branch, other: str) -> bool:
    """Whether `HEAD` contains every tip this checkout has for the branch `other`.

    Every one rather than any, so that work the other session pushed after
    this branch took its copy is not taken over as though it had been.
    """
    patterns = [
        f"refs/heads/{other}",
        *(f"refs/remotes/{remote}/{other}" for remote in branch.remotes),
    ]
    listing = _git(["for-each-ref", "--format=%(objectname)", *patterns], root)
    tips = [line.strip() for line in listing.out.splitlines() if line.strip()]
    if listing.code != 0 or not tips:
        return False
    return all(_git(["merge-base", "--is-ancestor", tip, "HEAD"], root).code == 0 for tip in tips)


def _held_first(hold: Hold, key: str, *, written: bool) -> tuple[str, ...]:
    """What to say where another branch holds `key` first."""
    who = _holds(hold, first=True)
    if written:
        return (
            f"claim: {key}: {who}, and this branch's claim, just written, orders behind it.",
            f"  Yield it with `bin/docket yield {key}`, and hand the work over as start mode says.",
        )
    return (f"claim: {key}: {who}; nothing was written.", *_take_another(hold, key))


def _holds(hold: Hold, *, first: bool) -> str:
    """Who holds an item, and since when."""
    who = f"{hold.ref} holds it{' first' if first else ''} (claimed {_when(hold.since)}"
    return who + (f", session {hold.session})" if hold.session else ")")


def _take_another(hold: Hold, key: str) -> tuple[str, ...]:
    """What to do where another branch holds `key`: leave it, or take it over."""
    return (
        "  Take another item. Where that session is gone - `get_session` shows it ARCHIVED or "
        "failed - or the owner says so:",
        f'  bin/docket claim {key} --over {hold.ref} --reason "..."',
    )


def _displaced(
    root: Path, read: Holdings, branch: _Branch, remote: _OnRemote, heads: RemoteHeads
) -> dict[str, tuple[Hold, Hold]]:
    """This branch's claims that publishing would put over one already published, by item.

    Each is a live claim of the branch's that orders first and is not on the
    remote's copy of the branch, as the remote itself answered (`PL-WX87`),
    paired with the first live claim behind it that is on its own branch's copy
    there, as the same listing answered (`PL-C3MN`): the one every other
    session reads as holding the item, and whose session was told it does
    (`PL-ZLJ9`).

    A claim git cannot compare with the branch's copy is withdrawn for
    nothing, as where the remote could not be asked: read as unpublished, a
    claim every clone reads as holding first was withdrawn for a later one
    (`PL-20DL`). The run that has the copy's tip decides.
    """
    found: dict[str, tuple[Hold, Hold]] = {}
    for hold in read.holds:
        if hold.state != LIVE or _branch_of(hold, branch) != branch.name:
            continue
        live = read.order(hold.key)
        if live[0] is not hold or _published(root, remote, hold.commit) is not False:
            continue
        for rival in live[1:]:
            name = _branch_of(rival, branch)
            if name != branch.name and _on_copy(root, heads, name, rival.commit):
                found[hold.key] = (hold, rival)
                break
    return found


def _withdraw(
    root: Path,
    branch: _Branch,
    displaced: dict[str, tuple[Hold, Hold]],
    *,
    trailers: Sequence[str],
    asked: Sequence[str],
) -> Written:
    """Yield each claim `_displaced` found, in one empty commit left unpushed.

    Unpushed because the yield matters only once the claim it ends is
    published, and the push that publishes that claim carries the yield with
    it. `CLAIMED` where the call can go on to what was asked, and
    `HELD_ELSEWHERE` where an item asked for was withdrawn, since a claim is
    all or nothing.
    """
    keys = list(displaced)
    made = _commit(
        root,
        keys,
        verb="yield",
        body=[
            f"{rival.ref} published a claim on {key} while this branch's was unpublished."
            for key, (_, rival) in displaced.items()
        ],
        trailers=[*(f"Yield: {key} {branch.name}" for key in keys), *trailers],
    )
    if made.code != 0:
        return Written(
            REFUSED,
            (
                f"claim: {', '.join(keys)}: this branch's claim was never pushed and another "
                "branch's is on the remote, but `git commit` failed writing the yield that "
                "withdraws it; nothing was written",
                *_indented(made.err),
                f"  Push nothing from {branch.name} until `bin/docket yield {' '.join(keys)}` "
                "has run.",
            ),
        )
    commit = _head(root)
    lines = [
        f"claim: {key}: {_holds(rival, first=False)}, published while this branch's claim, "
        f"{mine.commit[:12]}, was not, so publishing this one would take the item from a "
        "session told it holds it."
        for key, (mine, rival) in displaced.items()
    ]
    lines.append(
        f"  Withdrawn by {commit[:12]}, a yield on {branch.name} left unpushed: it rides the "
        "push that publishes the claim."
    )
    refused = [key for key in keys if key in asked]
    for key in refused:
        lines.extend(_take_another(displaced[key][1], key))
    if refused:
        lines.append("claim: no claim was written; a claim is all or nothing")
    return Written(HELD_ELSEWHERE if refused else CLAIMED, tuple(lines), commit)


def _when(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M %z")


def _session_token() -> str:
    """This session's id for the claim's `<session>` token, or `""` where it cannot be one."""
    token = os.environ.get(SESSION_VARIABLE, "").strip()
    if not token or len(token.split()) != 1 or token == "over":
        return ""
    return token


def _unread(read: Holdings) -> list[str]:
    """What the read could not see, said before anything is decided on it."""
    notes = [
        f"note: {name} could not be compared with the base, so a claim on it was not seen"
        for name in read.unreadable
    ]
    notes.extend(f"note: not a claim record, so not read: {line}" for line in read.malformed)
    return notes


def _write(
    root: Path,
    branch: _Branch,
    keys: list[str],
    *,
    verb: str,
    body: list[str],
    trailers: list[str],
    remote: _OnRemote,
    push: bool = False,
    now: datetime,
    items_dir: str,
    notes: list[str],
    check: _Check,
) -> Written:
    """Commit, push where the remote has no copy of the branch, and read the result back."""
    command = "claim" if verb == "start" else "yield"
    made = _commit(root, keys, verb=verb, body=body, trailers=trailers)
    if made.code != 0:
        return Written(
            REFUSED,
            (*notes, f"{command}: `git commit` failed; nothing was written", *_indented(made.err)),
        )
    return _publish(
        root,
        branch,
        keys,
        _head(root),
        remote=remote,
        made_now=True,
        command=command,
        push=push,
        now=now,
        items_dir=items_dir,
        said=notes,
        check=check,
    )


def _commit(
    root: Path, keys: list[str], *, verb: str, body: list[str], trailers: list[str]
) -> _Ran:
    """One empty commit, `<IDs>: <verb>`, with the record in its last paragraph."""
    paragraphs = [
        f"{', '.join(keys)}: {verb}",
        *([" ".join(body)] if body else []),
        "\n".join(trailers),
    ]
    return _git(
        ["commit", "--quiet", "--allow-empty", "--only", "-m", "\n\n".join(paragraphs)], root
    )


def _publish(
    root: Path,
    branch: _Branch,
    keys: list[str],
    commit: str,
    *,
    remote: _OnRemote,
    made_now: bool,
    command: str,
    push: bool = False,
    now: datetime,
    items_dir: str,
    said: list[str],
    check: _Check,
) -> Written:
    """Push where the remote has no copy of the branch, or `push` says to, then read back.

    **The remote's copy decides, not the tracking setting.** A branch pushed
    without `-u`, or checked out in a fresh container without tracking or
    tracking the default branch, has no upstream of its own and can still carry
    an open, armed pull request, which is the case the refusal to push exists
    for (`PL-QP9Z`). `push` is the caller saying none is armed. Nor does the
    clone's tracking ref decide, since it is not the remote's copy either:
    `remote` is what the remote said when asked, and where it could not be
    asked nothing is pushed, `push` or not, and the answer is `LOCAL_ONLY`.

    **Not pushed is `LOCAL_ONLY` whichever way it happened.** The read-back
    answers from this clone's refs, where a record just written is live, so
    without this a claim declined a push exited `CLAIMED` exactly as a pushed
    one did, while a second clone's `next` went on offering the item
    (`PL-1X56`). The read-back still runs, since a record that does not read
    back at all is a defect worth saying, but it promotes nothing to `CLAIMED`
    that nobody else can fetch.

    **A claim is published by `claim`, not by hand,** so the messages name it
    rather than `git push` (`PL-ZLJ9`): `claim` withdraws a claim of this
    branch's that another session's published since would be displaced by,
    and a hand push publishes it regardless. A yield displaces nobody, so a
    yield's messages name the push.
    """
    said = list(said)
    short = commit[:12]
    what = f"{', '.join(keys)}: {command} " + (
        f"written on {branch.name} as {short}" if made_now else f"{short} on {branch.name}"
    )
    # Named in full because a bare `git push` fails on a branch with no
    # upstream of its own, and one still tracking the default branch sends it
    # there, or is refused, depending on `push.default`.
    by_hand = f"git push --set-upstream {REMOTE} {branch.name}"
    again = f"bin/docket claim {' '.join(keys)}{' --push' if remote.tip else ''}"
    if remote.failed:
        # A commit made just now is certainly local; one an earlier run made
        # may already be on the remote, which is exactly what could not be asked.
        seen = (
            "It is local: no other session can see it."
            if made_now
            else "Whether an earlier run's push put it there is unknown too."
        )
        return Written(
            LOCAL_ONLY,
            (
                *said,
                f"{what}, and not pushed: `git ls-remote --heads {REMOTE}` failed, so whether the "
                "branch is on the remote, with a pull request a push could merge it away with, is "
                f"unknown. {seen}",
                *_indented(remote.failed),
                f"  Run `{again}` again once the remote answers, rather than pushing by hand, "
                "which skips the check for a claim published meanwhile."
                if command == "claim"
                else f"  Push it with `{by_hand}` once no pull request on the branch is armed.",
            ),
            commit,
        )
    held_back = bool(remote.tip) and not push
    if held_back:
        said.append(
            f"{what}, and not pushed, so only this checkout can see it: the branch is on the "
            f"remote as {REMOTE}/{branch.name}, so a pull request may be open on it and armed, "
            "and a push could merge it away. Disarm auto-merge if it is armed, then "
            + (
                f"publish it with `{again}`, not `git push`: a claim pushed by hand skips the "
                "check for one another session published meanwhile, and takes the item from it."
                if command == "claim"
                else f"push it with `{by_hand}`."
            )
        )
    else:
        pushed = _git(["push", "--quiet", "--set-upstream", REMOTE, branch.name], root)
        if pushed.code != 0:
            return Written(
                LOCAL_ONLY,
                (
                    *said,
                    f"{what}, but `git push` failed, so it is local: no other session can see it.",
                    *_indented(pushed.err),
                    # A yield displaces nobody, so its push is named rather than a
                    # rerun, though a rerun retries it as well (`PL-NNLM`).
                    f"  Run `{again}` again once what git says is dealt with, rather than "
                    "pushing by hand, which skips the check for a claim published meanwhile."
                    if command == "claim"
                    else f"  Push it with `{by_hand}`.",
                ),
                commit,
            )
        said.append(f"{what}, and pushed")
        if _git(["fetch", "--quiet", REMOTE], root).code != 0:
            said.append(
                f"note: `git fetch {REMOTE}` after the push failed, so a claim pushed in the same "
                "minute cannot be ruled out; `bin/docket show` each id once it answers"
            )
    # A listing of its own, not the one the claim was checked against: that one
    # predates the push, so it lacks a rival branch pushed in the same minute,
    # and filtering the re-fetched refs by it would drop exactly the claim this
    # read-back exists to catch (`PL-MT3R`).
    reread = holdings(
        root, now=now, items_dir=items_dir, remote=remote_heads(root), runner=_run_git
    )
    code, lines = check(root, reread, keys, branch, commit)
    if held_back and code == CLAIMED:
        code = LOCAL_ONLY
    return Written(code, (*said, *lines), commit)


def _head(root: Path) -> str:
    return _git(["rev-parse", "HEAD"], root).out.strip()


def _on_remote(heads: RemoteHeads, name: str) -> _OnRemote:
    """The branch as the remote answered for it, rather than the clone's copy of its last answer.

    `refs/remotes/origin/<name>` is what some fetch last saw, and a fetch that
    does not prune never deletes it - `claim`'s does not, deliberately, since
    such a ref can be the only surviving copy of a deleted branch's work
    (`vcs.fetch_remote`). The harness writes that ref at session start for a
    branch nobody has pushed, sometimes with the tracking setting too, so read
    as the remote's copy it kept every fresh session's claim unpushed and said
    the branch was on the remote (`PL-WX87`).

    It asked `git ls-remote` for this one branch until `PL-MT3R`, and now reads
    the command's one listing of every branch the remote has. The fix held for
    this reader alone, and each reader after it that needed the remote's copy
    picked a local stand-in of its own; with one listing per command, the read
    of who holds what and this answer come from the same moment of the remote,
    and a new reader has a record to consult rather than a copy to pick.
    """
    tip = heads.tip(name)
    if tip is None:
        return _OnRemote(tip="", failed=heads.failed or "the remote's branches were not listed")
    return _OnRemote(tip=tip)


def _published(root: Path, remote: _OnRemote, commit: str) -> bool | None:
    """Whether the branch's tip on the remote, as asked, already carries `commit`.

    `None` where git cannot say. `merge-base --is-ancestor` answers 0 for
    "carries it" and 1 for "does not"; anything else is git unable to answer,
    most often 128 for a tip the listing names that this clone has not
    fetched, which another writer's push leaves - GitHub's *Update branch*, a
    second session. Read as "does not", a claim every clone could fetch was
    reported as only in this checkout, with a `claim --push` git refuses, and
    a published claim was withdrawn for a later one (`PL-20DL`). So each
    caller says what it could not read instead, as `arming._unpulled` does of
    the same exit (`PL-21KN`).
    """
    if not remote.tip:
        return False
    carried = _git(["merge-base", "--is-ancestor", commit, remote.tip], root).code
    if carried in (0, 1):
        return carried == 0
    return None


def _uncompared(
    keys: list[str], command: str, branch: _Branch, remote: _OnRemote
) -> tuple[str, ...]:
    """What to say where `_published` could not tell whether the remote has a record.

    Neither "published" nor "only in this checkout", since either could be
    true, and nothing is pushed: a push is refused anyway until this clone
    has the tip. `claim` fetches before it reads, so running it again answers;
    `yield` does not, so the fetch is named.
    """
    listed = " ".join(keys)
    again = (
        f"Run `bin/docket claim {listed}` again, which fetches it first."
        if command == "claim"
        else f"Fetch it with `git fetch {REMOTE}`, then run `bin/docket yield {listed}` again."
    )
    return (
        f"{', '.join(keys)}: whether {REMOTE}'s copy of {branch.name} carries this branch's "
        f"{command} is not known: that copy is at {remote.tip[:12]}, a commit git could not "
        "compare with it - most often one another writer pushed after this clone last "
        "fetched - so nothing was pushed.",
        f"  {again}",
    )


def _on_copy(root: Path, heads: RemoteHeads, name: str, commit: str) -> bool:
    """Whether another branch's copy on the remote carries `commit`, as the listing has it.

    It read `refs/remotes/origin/<name>` until `PL-C3MN`, and no fetch here
    prunes, so a rival branch the remote had deleted still read as carrying
    its claim, and withdrew this branch's in favour of one no fresh clone can
    see. `holdings` drops such a ref since `PL-MT3R`, but not a local branch of
    the same name, so the listing decides here too: a branch it lacks carries
    nothing.

    The listing can name a tip the clone lacks - pushed since the fetch, or
    under `--no-fetch` - and git then cannot say what it carries. The tracking
    ref is the evidence left, read as it was before the listing, as it is
    where the listing failed: the remote still has the branch, so taking its
    claim as published withdraws this branch's in favour of one every clone
    can fetch, where the other answer would publish over a claim a session
    was told it holds (`PL-ZLJ9`).
    """
    if not commit:
        return False
    tip = heads.tip(name)
    if tip == "":
        return False
    if tip is not None:
        # 0 is "carries it" and 1 "does not"; anything else is git unable to say.
        carried = _git(["merge-base", "--is-ancestor", commit, tip], root).code
        if carried in (0, 1):
            return carried == 0
    ref = f"refs/remotes/{REMOTE}/{name}"
    return _git(["merge-base", "--is-ancestor", commit, ref], root).code == 0


def _recorded(root: Path, base: str, branch: _Branch, key: str, *, trailer: str = "Claim") -> str:
    """The newest `trailer` record on `key` this branch made, or `""` where it made none.

    Asked for a `Yield:` by a yield run again, which has nothing to push where
    the remote's tip already carries the one it finds. The `Claim:` reading
    once renewed a hold the old rule read from a subject; `PL-CH3Z` deleted
    that rule, and a recorded claim is its own commit.
    """
    parse = _parse_yield if trailer == "Yield" else _parse_claim
    fmt = f"--format=%H%x1f%(trailers:key={trailer},valueonly,unfold,separator=%x1e)"
    log = _git(["log", "--no-merges", fmt, f"^{base}", "HEAD", "--"], root)
    for line in log.out.split("\n"):
        commit, _, values = line.partition("\x1f")
        for text in values.split("\x1e"):
            parsed = parse(text.strip()) if text.strip() else None
            if parsed and parsed[0] == key and _head_name(parsed[1], branch.remotes) == branch.name:
                return commit
    return ""


def _claimed(
    root: Path, read: Holdings, keys: list[str], branch: _Branch, commit: str
) -> tuple[int, list[str]]:
    """Whether each claim just written holds first, read the way every other session reads it."""
    if not read.known:
        return REFUSED, [
            f"claim: written as {commit[:12]}, but the read back declined - {read.declined}"
        ]
    code, lines = CLAIMED, []
    for key in keys:
        live = read.order(key)
        mine = [hold for hold in live if _branch_of(hold, branch) == branch.name]
        if not mine:
            code = REFUSED if code == CLAIMED else code
            lines.append(
                f"claim: {key}: {commit[:12]} does not read back as a live claim by "
                f"{branch.name}; {_unread_because(root, read, branch, key)}"
            )
        elif live[0] is not mine[0]:
            code = HELD_ELSEWHERE
            lines.extend(_held_first(live[0], key, written=True))
    return code, lines


def _yielded(
    root: Path, read: Holdings, keys: list[str], branch: _Branch, commit: str
) -> tuple[int, list[str]]:
    """Whether each claim just yielded now reads as ended by the yield."""
    if not read.known:
        return REFUSED, [
            f"yield: written as {commit[:12]}, but the read back declined - {read.declined}"
        ]
    lines: list[str] = []
    for key in keys:
        mine = [
            hold
            for hold in read.holds
            if hold.key == key and _branch_of(hold, branch) == branch.name
        ]
        if not all(hold.state == RELEASED and hold.released_by == BY_YIELD for hold in mine):
            lines.append(
                f"yield: {key}: written as {commit[:12]}, but {branch.name} still reads as holding "
                "it; this is a defect in docket, and the commit is where to start"
            )
    return (REFUSED if lines else CLAIMED), lines


def _unread_because(root: Path, read: Holdings, branch: _Branch, key: str) -> str:
    """Why a claim just written reads as holding nothing.

    A closure on the base first: `_closed_on_base` refuses one it can see, so
    one found here landed between that read and the read-back, and it is a
    finished item rather than a defect in docket (`PL-Y48N`).
    """
    if any(
        hold.key == key
        and hold.released_by == BY_CLOSED
        and _branch_of(hold, branch) == branch.name
        for hold in read.holds
    ):
        return (
            f"{read.base} closed it after the read this claim was checked against, and a claim "
            f"on an item {read.base} has closed is released as soon as it is written. Another "
            "item is the one to pick"
        )
    refs = _unlanded_refs(read.base, root, _run_git, include_remote=True)
    if not any(_head_name(name, branch.remotes) == branch.name for name in refs.unlanded):
        return (
            "the branch reads as landed - what it carries is already on the default branch - "
            "and a landed branch holds nothing. Claim from a new branch off the default one"
        )
    return "this is a defect in docket, and the commit is where to start"


def _git(args: list[str], root: Path) -> _Ran:
    """Run one git command whose exit status is the answer, and keep all of what it said."""
    try:
        done = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=WRITE_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return _Ran(code=-1, out="", err=str(error))
    return _Ran(code=done.returncode, out=done.stdout, err=done.stderr)


def _indented(text: str) -> tuple[str, ...]:
    """git's own words, indented under the line that explains them."""
    return tuple(f"  {line}" for line in text.strip().splitlines()[-6:] if line.strip())
