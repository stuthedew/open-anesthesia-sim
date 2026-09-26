"""Whether a pull request may be armed for auto-merge: `bin/docket arm`'s answer for `HEAD`.

`CLAUDE.md` arms a pull request whose branch carries only item files, so a
capture reaches the default branch even when its session ends before any work
does (project owner, 2026-09-23, ratified, over "a branch carrying only
captured items is not a pull request", `PL-WNCT`). Which pushes could be armed
was a catalog of claim shapes each session applied by judgment - the empty
start commit, a queue-only commit start mode read as one - and every shape it
missed merged a claim away with its branch while the work went on (`PL-QP9Z`,
`PL-1MCK`, `PL-KWCY`). A claim is a recorded fact now (`claims`), so the
question is decided here, from the tree, and asked before arming and before
every later push while a pull request is open.

**Four answers, and an exit status for each.**

- `arm` (0): the net change a squash would land - `base...HEAD` - lies under
  the store, the queue's own tooling, `subprojects/docket/`, or the pull
  requests' body records, `docs/pr-bodies/`, and leaves this module alone; no
  claim bound to this branch is unreleased; and the branch contains the base's
  tip.
- `hold` (1), naming what holds it. A claim holds the pull request unarmed and
  a draft, whichever push carried it, until the branch's own copy closes or
  blocks the item or the branch yields it: merged, the branch and its claim go
  together while the work goes on. A lapsed claim is unreleased too - it is
  work nobody finished or handed back. A path outside the store, the tooling
  and the records holds it unarmed, and so does a change to this module,
  because that work waits on a read rather than merging on green CI.
- `behind N` (1): nothing holds it, but the base has `N` commits the branch
  lacks, and `main` merges only an up-to-date branch while auto-merge never
  brings the base in (`PL-S5MF`). So the base is brought in first.
- `unknown` (2): something the answer rests on could not be read - no branch,
  no established base, a history git would not walk, a claim trailer that
  does not parse, a fetch that failed. Never `arm` from a partial read.

**`hold` outranks `unknown`.** A claim or a path that waits on a read is
reason enough whatever else went unread, so it is said, with what went unread beside
it, rather than withheld.

**The decisions the rule rests on**, moved here from `CLAUDE.md` with it:

- a claim holds whichever push carried it (project owner, 2026-09-23,
  ratified, over arming whatever rode the push, `PL-QP9Z`, and over reading
  only a start claim on that push, `PL-1MCK`);
- it holds until the item closes in the branch's own copy and not past it
  (same date, ratified, over holding it past the item's closing, `PL-KWCY`),
  and a block releases it too (2026-09-24, ratified, over holding it until
  closed, `PL-3FYK`) - `claims.RELEASING_STATUSES`;
- a pull request a claim rides is a draft (2026-09-24, ratified, over opening
  none while a claim rides or titling it as the capture, because `#978` was
  merged by hand while its claim was open, `PL-H14W`);
- the tooling arms on green beside the store, and everything else waits on a
  read, this module included (2026-09-25, ratified, over holding every path
  outside the store, `PL-SQTR`, built by `PL-K6B2`): the hold fired on every
  docket change and was clicked through, so it guarded nothing, the simulator
  included. This module stays held so that the gate cannot loosen itself;
- a body record arms on green beside them (2026-09-25, ratified with the
  record's form, over every pull request holding on the record it writes
  before its merge, `PL-979D`): the record is a copy of the body, never a
  change to read.

Status dispositions and release cuts never hold arming (`PL-MB2W` § "Other
holds"): a triage pass moving statuses is the queue-only work auto-merge
exists for, and a cut's notes file lies outside the store and the tooling,
so the paths hold it already.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .claiming import REMOTE, _git
from .claims import LAPSED, RELEASED, Hold, holdings
from .vcs import (
    Runner,
    _head_name,
    _remotes,
    _run_git,
    _Silences,
    answered,
    changed_path_args,
    default_base,
    listed_paths,
    resolved,
)

#: The four answers, each the first word of what `arm` prints.
ARM = "arm"
HOLD = "hold"
BEHIND = "behind"
UNKNOWN = "unknown"

#: The exit status of each answer. `behind` shares `hold`'s: both say "not
#: now", and the line printed says which.
EXIT = {ARM: 0, HOLD: 1, BEHIND: 1, UNKNOWN: 2}

#: How many paths outside the store, the tooling and the records a `hold`
#: names before counting the rest.
SHOWN = 5

#: The queue's own tooling, which arms on green beside the store. The path is
#: this repository's layout.
TOOLING = "subprojects/docket/"

#: The pull requests' body records, which arm on green beside the store and the
#: tooling: `tools/pr_body_check.py --record` writes one on each pull request's
#: branch before its merge, and a copy of a body is never a change to read
#: (`PL-979D`). `verify` sanctions the same write as `record`. The path is this
#: repository's layout, as `TOOLING`'s is.
RECORDS = "docs/pr-bodies/"

#: The one file under `TOOLING` that still waits on a read: this module, which
#: decides the answer, so a change to it could loosen the rule it states.
#: `test_cli` pins it to the module's own path, so a move cannot leave it
#: naming a file nothing reads.
GATE = TOOLING + "src/docket/arming.py"


@dataclass(frozen=True)
class Verdict:
    """`arm`'s answer for `HEAD`, and what it rests on.

    `claims` are the unreleased claims bound to this branch, `outside` the
    paths a merge would land outside the store, the tooling and the records,
    `gate` whether it would change this module, and `behind` how many of the
    base's commits the branch lacks. `unread` is why the answer is `unknown`,
    or what went unread beside a `hold`.
    """

    answer: str
    branch: str = ""
    base: str = ""
    items_dir: str = ""
    claims: tuple[Hold, ...] = ()
    outside: tuple[str, ...] = ()
    gate: bool = False
    behind: int = 0
    unread: tuple[str, ...] = ()

    @property
    def code(self) -> int:
        return EXIT[self.answer]

    @property
    def lines(self) -> tuple[str, ...]:
        """What `bin/docket arm` prints: the answer first, then what to do."""
        notes = tuple(f"  note: {reason}" for reason in self.unread)
        if self.answer == UNKNOWN:
            first, *rest = self.unread or ("nothing the answer rests on could be read",)
            return (f"unknown - {first}", *(f"  {reason}" for reason in rest))
        if self.answer == BEHIND:
            commits = "commit" if self.behind == 1 else "commits"
            return (
                f"behind {self.behind} - {self.base} has {self.behind} {commits} {self.branch} "
                "lacks, and main merges only an up-to-date branch",
                f"  Bring it in once - `update_pull_request_branch`, or merge {self.base} and "
                "push - then ask again.",
            )
        if self.answer == ARM:
            return (
                f"arm - {self.branch} changes nothing outside {self._arming}, leaves "
                f"{GATE.rpartition('/')[2]} alone, holds no open claim, and contains "
                f"{self.base}'s tip: mark its pull request ready and arm it",
            )
        read = ", so its pull request waits on a read" if self.outside or self.gate else ""
        said = [f"hold - {self.branch}: " + " and ".join(self._holding()) + read]
        for hold in self.claims:
            said.append(f"  {_described(hold)}")
        if self.outside:
            shown = ", ".join(self.outside[:SHOWN])
            more = len(self.outside) - SHOWN
            said.append(f"  {shown}{f', and {more} more' if more > 0 else ''}")
        said.append(
            "  Leave auto-merge off, disarming it before the push that brings this if it is "
            "armed"
            + (
                ", and keep the pull request a draft while a claim holds it."
                if self.claims
                else "."
            )
        )
        return (*said, *notes)

    @property
    def _arming(self) -> str:
        """The directories a change arms on green under, as `arm` and `hold` both name them."""
        return f"{self.items_dir}, {TOOLING.rstrip('/')} and {RECORDS.rstrip('/')}"

    def _holding(self) -> list[str]:
        """The one-clause reasons a `hold` names: claims, then paths, then the gate."""
        reasons = []
        if self.claims:
            keys = ", ".join(hold.key for hold in self.claims)
            reasons.append(f"a merge would erase its open claim on {keys}")
        if self.outside:
            count = len(self.outside)
            noun = "path" if count == 1 else "paths"
            reasons.append(f"it changes {count} {noun} outside {self._arming}")
        if self.gate:
            reasons.append(f"it changes {GATE}, the gate itself")
        return reasons


def arm(
    root: Path, *, items_dir: str, now: datetime, fetch: bool = True, runner: Runner | None = None
) -> Verdict:
    """Whether the pull request `HEAD`'s branch would open, or has open, may be armed.

    Fetches first unless `fetch` is false, because `behind` read from a stale
    base is a confident wrong answer; a fetch that fails leaves every answer
    but `hold` unknown. `now` judges the claims' leases, as it does for
    `claims.holdings`, and must carry its offset.
    """
    unread: list[str] = []
    ran = runner or _run_git
    if fetch:
        fetched = _git(["fetch", "--quiet", REMOTE], root)
        if fetched.code == 0:
            # The refs just moved, and a runner that remembers answers would
            # give the ones from before the fetch.
            ran = _run_git
        else:
            said = " ".join(fetched.err.split()) or f"exit {fetched.code}"
            unread.append(
                f"`git fetch {REMOTE}` failed ({said}), so whether the base has moved past this "
                "branch is not known; refresh the refs and pass --no-fetch, or ask again"
            )
    run = _Silences(ran)
    remotes = _remotes(root, run)
    name = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    # A git that answered nothing is said as that, not as the "no branch" or
    # "no base" it would otherwise read as (`vcs.branch_state` has the case).
    if run.reason or name in {"", "HEAD"}:
        reason = run.reason or "HEAD is on no branch, so there is no pull request to answer for"
        return Verdict(UNKNOWN, unread=(reason, *unread))
    base = default_base(root, runner=run)
    if not resolved(base):
        reason = run.reason or f"no default branch could be established to compare {name} with"
        return Verdict(UNKNOWN, branch=name, unread=(reason, *unread))
    branch = _head_name(name, remotes)
    if branch == _head_name(base, remotes):
        reason = f"HEAD is on {name}, the default branch, which opens no pull request of its own"
        return Verdict(UNKNOWN, branch=name, base=base, unread=(reason,))

    prefix = items_dir.strip("/") + "/"
    # Both sides of a rename, so a file moved into the store shows the deletion
    # it made outside it, which a rename would print as one path under the store.
    changed = run(changed_path_args("diff", "--name-only", f"{base}...HEAD", "--"), root)
    outside: tuple[str, ...] = ()
    gate = False
    if answered(changed):
        paths = set(listed_paths(changed))
        outside = tuple(
            sorted(path for path in paths if not path.startswith((prefix, TOOLING, RECORDS)))
        )
        gate = GATE in paths
    else:
        unread.append(f"git would not diff {name} against {base}, so what a merge lands is unknown")

    read = holdings(root, now=now, items_dir=items_dir, runner=ran)
    if not read.known:
        unread.append(f"who holds what could not be read - {read.declined}")
    claims = tuple(
        hold
        for hold in read.holds
        if hold.state != RELEASED and _head_name(hold.ref, remotes) == branch
    )
    for ref in read.unreadable:
        if _head_name(ref, remotes) == branch:
            unread.append(f"{ref} could not be compared with {base}, so a claim on it was not read")
    for line in read.malformed:
        # `<hash> on <ref>: Claim: <text>`, as `claims` writes it; a ref name
        # can hold neither a space nor a colon.
        where, _, _ = line.partition(": ")
        if _head_name(where.partition(" on ")[2], remotes) == branch:
            unread.append(f"a trailer on {name} is not a claim record, so it was not read: {line}")

    counted = run(["rev-list", "--count", f"HEAD..{base}"], root).strip()
    behind = int(counted) if counted.isdigit() else 0
    if not counted.isdigit():
        unread.append(f"git would not count {base}'s commits that {name} lacks")
    if run.reason:
        unread.append(run.reason)

    found = Verdict(
        HOLD,
        branch=name,
        base=base,
        items_dir=prefix.rstrip("/"),
        claims=claims,
        outside=outside,
        gate=gate,
        behind=behind,
        unread=tuple(unread),
    )
    if claims or outside or gate:
        return found
    if unread:
        return Verdict(UNKNOWN, branch=name, base=base, unread=tuple(unread))
    if behind:
        return Verdict(BEHIND, branch=name, base=base, items_dir=found.items_dir, behind=behind)
    return Verdict(ARM, branch=name, base=base, items_dir=found.items_dir)


def _described(hold: Hold) -> str:
    """One claim holding the branch: which item, since when, and how it ends."""
    when = hold.since.strftime("%Y-%m-%d %H:%M %z")
    line = f"{hold.key}: claimed in {hold.commit[:12]} on {when}"
    if hold.state == LAPSED:
        return (
            f"{line}, lapsed with no commit since {hold.renewed.strftime('%Y-%m-%d')}; "
            f"`bin/docket yield {hold.key}` ends it, `bin/docket claim {hold.key}` renews it"
        )
    return (
        f"{line}; released when this branch's copy closes or blocks it, "
        f"or by `bin/docket yield {hold.key}`"
    )
