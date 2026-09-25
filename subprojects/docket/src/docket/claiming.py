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
without being asked. It pushes only a branch with no upstream of its own and
no copy on the remote: a branch with either may have a pull request open and
armed, and a push would merge the claim away with the branch (`PL-QP9Z`). An
upstream naming the default branch is not the branch's own - it is how the web
harness starts a session branch (`PL-KX73`) - so the push goes ahead there,
and gives the branch one. After a push it fetches again and
re-reads, because a claim pushed in the same minute is invisible until then;
where that one orders first, the answer is `HELD_ELSEWHERE` and the line to
yield by. A push that fails is `LOCAL_ONLY`, and says the claim is local.

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
    BY_YIELD,
    CUTOVER_MARKER,
    LAPSED,
    LIVE,
    RELEASED,
    RELEASING_STATUSES,
    SESSION_VARIABLE,
    Hold,
    Holdings,
    _parse_claim,
    holdings,
)
from .model import parse_front_matter
from .store import ID_PATTERN
from .vcs import (
    Runner,
    _head_name,
    _item_paths_on,
    _remotes,
    _run_git,
    _unlanded_refs,
    default_base,
)

#: Exit statuses. `USAGE` is argparse's own. `HELD_ELSEWHERE` and `LOCAL_ONLY`
#: are the two a session has to act on differently from a plain refusal: the
#: first means another session has the item, the second that the claim exists
#: only in this checkout.
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
    upstream: str
    remotes: frozenset[str]


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
    runner: Runner | None = None,
) -> Written:
    """Claim `keys` for the branch `HEAD` is on, in one empty commit.

    All or nothing: an item another branch holds first refuses the whole call,
    so no session ends up holding half of what it asked for. `over` names the
    branch a takeover is from, and `reason` - required with it - goes into the
    commit's body; the evidence a takeover needs (the owner's word, or
    `get_session` showing that session archived or failed) is the session's to
    have, since nothing here can ask for it.

    An item this branch already holds first by a recorded claim is left alone,
    so running `claim` twice writes one commit. One held only by the old rules
    is claimed again, which records it.
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
    read = holdings(root, now=now, items_dir=items_dir, runner=run)
    if not read.known:
        return Written(
            REFUSED,
            (
                f"claim: declined to read who holds these items - {read.declined}; "
                "nothing was written",
            ),
        )
    notes = _unread(read)

    takeovers: dict[str, Hold] = {}
    reasons: list[str] = [" ".join(reason.split())] if reason.strip() else []
    blocked: list[str] = []
    #: Each item this branch already holds first by a recorded claim, and that claim.
    already: dict[str, str] = {}
    for key in wanted:
        live = read.order(key)
        mine = [hold for hold in live if _branch_of(hold, branch) == branch.name]
        others = [hold for hold in live if _branch_of(hold, branch) != branch.name]
        rival = others[0] if others else None
        # A hold read by the old rules counts for every branch reaching its
        # commit, so a branch that merged the holder's can tie with it on that
        # one commit; a tie is not a lead, and goes the takeover's way.
        if mine and (
            rival is None
            or (live.index(mine[0]) < live.index(rival) and rival.commit != mine[0].commit)
        ):
            recorded = _recorded(root, read.base, branch, key) if mine[0].legacy else mine[0].commit
            if recorded:
                already[key] = recorded
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
        unpushed = [key for key, made in already.items() if not _published(root, branch, made)]
        if not unpushed:
            return Written(CLAIMED, tuple(notes))
        # An earlier run wrote the claim and could not push it; this run is
        # its retry, and a claim no other session can see is not held.
        return _publish(
            root,
            branch,
            unpushed,
            _head(root),
            made_now=False,
            command="claim",
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
    read = holdings(root, now=now, items_dir=items_dir, runner=run)
    if not read.known:
        return Written(
            REFUSED, (f"yield: declined to read what this branch holds - {read.declined}",)
        )
    notes: list[str] = []
    writing: list[str] = []
    unheld: list[str] = []
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
        return Written(CLAIMED, tuple(notes))
    return _write(
        root,
        branch,
        writing,
        verb="yield",
        body=[],
        trailers=[*(f"Yield: {key} {branch.name}" for key in writing), *trailers],
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
    since the claim names its branch and would bind to neither. Refused too
    where `HEAD`'s tree predates the claim record - a commit made there is read
    by the old rules, which read no trailer at all.

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
    empty = _Branch(name="", upstream="", remotes=remotes)
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
    if not run(["show", f"HEAD:{CUTOVER_MARKER}"], root).strip():
        return empty, (
            f"{command}: HEAD's tree has no {CUTOVER_MARKER}, so a claim record written here "
            "would be read by the old rules and its trailers ignored; merge the default "
            "branch first",
        )
    branch = _Branch(name=name, upstream=upstream, remotes=remotes)
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
    who = f"{hold.ref} holds it first (claimed {_when(hold.since)}"
    who += f", session {hold.session})" if hold.session else ")"
    if written:
        return (
            f"claim: {key}: {who}, and this branch's claim, just written, orders behind it.",
            f"  Yield it with `bin/docket yield {key}`, and hand the work over as start mode says.",
        )
    return (
        f"claim: {key}: {who}; nothing was written.",
        "  Take another item. Where that session is gone - `get_session` shows it ARCHIVED or "
        "failed - or the owner says so:",
        f'  bin/docket claim {key} --over {hold.ref} --reason "..."',
    )


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
    now: datetime,
    items_dir: str,
    notes: list[str],
    check: _Check,
) -> Written:
    """Commit, push where there is no upstream, and read the result back."""
    command = "claim" if verb == "start" else "yield"
    paragraphs = [
        f"{', '.join(keys)}: {verb}",
        *([" ".join(body)] if body else []),
        "\n".join(trailers),
    ]
    made = _git(
        ["commit", "--quiet", "--allow-empty", "--only", "-m", "\n\n".join(paragraphs)], root
    )
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
        made_now=True,
        command=command,
        now=now,
        items_dir=items_dir,
        said=notes,
        check=check,
    )


def _publish(
    root: Path,
    branch: _Branch,
    keys: list[str],
    commit: str,
    *,
    made_now: bool,
    command: str,
    now: datetime,
    items_dir: str,
    said: list[str],
    check: _Check,
) -> Written:
    """Push where the remote has no copy of the branch, then read the result back.

    **The remote's copy decides, not the tracking setting.** A branch pushed
    without `-u`, or checked out in a fresh container without tracking or
    tracking the default branch, has no upstream of its own and can still carry
    an open, armed pull request, which is the case the refusal to push exists
    for (`PL-QP9Z`).
    """
    said = list(said)
    short = commit[:12]
    what = f"{', '.join(keys)}: {command} " + (
        f"written on {branch.name} as {short}" if made_now else f"{short} on {branch.name}"
    )
    upstream = branch.upstream or _remote_copy(root, branch.name)
    if upstream:
        # Named in full because a bare `git push` fails on a branch with no
        # upstream of its own, and one still tracking the default branch sends
        # it there, or is refused, depending on `push.default`.
        said.append(
            f"{what}, and not pushed: the branch is on the remote as {upstream}, so a pull "
            "request may be open on it and armed, and a push could merge it away. Disarm "
            f"auto-merge if it is armed, then push it with `git push --set-upstream {REMOTE} "
            f"{branch.name}`."
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
                    f"  Push it with `git push --set-upstream {REMOTE} {branch.name}`, or run "
                    "this again.",
                ),
                commit,
            )
        said.append(f"{what}, and pushed")
        if _git(["fetch", "--quiet", REMOTE], root).code != 0:
            said.append(
                f"note: `git fetch {REMOTE}` after the push failed, so a claim pushed in the same "
                "minute cannot be ruled out; `bin/docket show` each id once it answers"
            )
    reread = holdings(root, now=now, items_dir=items_dir, runner=_run_git)
    code, lines = check(root, reread, keys, branch, commit)
    return Written(code, (*said, *lines), commit)


def _head(root: Path) -> str:
    return _git(["rev-parse", "HEAD"], root).out.strip()


def _remote_copy(root: Path, name: str) -> str:
    """`origin/<name>` where the remote has the branch, as of the last fetch, else `""`."""
    found = _git(["rev-parse", "--verify", "--quiet", f"refs/remotes/{REMOTE}/{name}"], root)
    return f"{REMOTE}/{name}" if found.code == 0 else ""


def _published(root: Path, branch: _Branch, commit: str) -> bool:
    """Whether the remote's copy of the branch already carries `commit`."""
    remote = f"refs/remotes/{REMOTE}/{branch.name}"
    return _git(["merge-base", "--is-ancestor", commit, remote], root).code == 0


def _recorded(root: Path, base: str, branch: _Branch, key: str) -> str:
    """The newest recorded claim on `key` this branch made, or `""` where it made none.

    Asked where the branch's hold is read by the old rules: a recorded claim
    made after that one renews it rather than taking its place, so the hold
    still reads as old-rule, and without this every run would write another.
    """
    fmt = "--format=%H%x1f%(trailers:key=Claim,valueonly,unfold,separator=%x1e)"
    log = _git(["log", "--no-merges", fmt, f"^{base}", "HEAD", "--"], root)
    for line in log.out.split("\n"):
        commit, _, values = line.partition("\x1f")
        for text in values.split("\x1e"):
            parsed = _parse_claim(text.strip()) if text.strip() else None
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
                f"{branch.name}; {_unread_because(root, read, branch)}"
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


def _unread_because(root: Path, read: Holdings, branch: _Branch) -> str:
    """Why a claim just written reads as holding nothing."""
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
