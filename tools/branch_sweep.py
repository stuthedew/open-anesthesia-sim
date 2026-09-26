"""Archive, then delete, every `claude/` branch whose work is finished.

**The failure** (`PL-X8SV`). GitHub deletes a head branch only when that
branch's own pull request merges, and a session cannot delete one at all
(`docs/worker.md` § "Ref operations a session cannot perform"). So a branch
whose pull request never merges stays for good: a session that handed its work
to another, one that ended before opening a pull request, one whose pull
request closed unmerged, and a push after a merge. Fourteen had built up by
2026-09-26, each re-read by `flight`, `stranded` and the session-start digest,
and the only remedy was the project owner deleting them by hand.

**The rule is the existing detectors', not a new one.** A branch is kept while
any of these holds, and swept only when none does:

- a pull request is open from it, or onto it;
- `docket` reads unfinished work on it (`claims.unfinished_work`, the test
  `flight` settles a branch by), or a release cut;
- it holds the only copy of an item, or an edit to an item the default branch
  holds open (`vcs.stranded`);
- a merged pull request left commits on it (`vcs.orphaned`, and
  `left_behind_check`, which asks GitHub);
- its last commit is under `GRACE` old, which covers a session's first pushes,
  before it has claimed anything.

So sweeping a branch never hides what the digest or `bin/docket stranded` would
report for recovery. The one listing it removes is an edit to an item the
default branch has closed: nothing is left for that edit to inform, and its
lines go into the archive with the branch.

**A wrong call costs a restore, not work.** One atomic push copies the tip to
`refs/archive/<branch>/<tip>` and deletes the branch, leased on the tip the rule
judged, so a branch pushed to since is left alone. An archive ref is in neither
`refs/heads` nor `refs/tags`, so no default fetch reads it and no branch list
shows it, but it keeps the commits reachable. Each swept branch is printed with
the command that restores it.

**It declines rather than guesses.** Where any reading fails - no token, no
network, a shallow checkout - it pushes nothing, says which reading failed, and
exits 1, since a sweep that quietly stopped would let the branches build up
again unseen.

Lists by default; `--apply` pushes. `.github/workflows/branch-sweep.yml` runs it
daily with a token that may delete branches. It reads the refs already fetched
and fetches nothing itself. Standard library only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.claims import holdings, unfinished_work  # noqa: E402
from docket.model import CLOSED_STATUSES  # noqa: E402
from docket.store import read_items  # noqa: E402
from docket.vcs import orphaned, stranded  # noqa: E402

import left_behind_check  # noqa: E402
from open_pull_requests import open_pull_requests, repo_slug  # noqa: E402

#: The branches read. The harness names every session's branch under it, so the
#: default branch and any branch the project owner makes are never touched.
PREFIX = "claude/"

#: Where a swept branch's tip is kept, as `<ARCHIVE>/<branch>/<tip>`. The tip in
#: the name means a branch swept twice keeps both.
ARCHIVE = "refs/archive"

#: How long after its last commit a branch is kept whatever else holds.
GRACE = timedelta(hours=72)

REMOTE = "origin"
ITEMS = "docs/items"


class Declined(Exception):
    """A reading could not be taken, so nothing is swept."""


@dataclass(frozen=True)
class Branch:
    """One fetched `claude/` branch: its name, its tip, and when the tip was committed."""

    name: str
    tip: str
    committed: datetime


@dataclass
class Readings:
    """Why each branch stays, and what goes into the archive with one that does not.

    Keyed by branch name without the remote, whichever spelling a detector
    used: `docket` names a tracking ref `origin/claude/x`, GitHub names the
    branch `claude/x`, and a reason filed under the other spelling would be a
    reason never read.
    """

    kept: dict[str, list[str]] = field(default_factory=dict)
    notes: dict[str, list[str]] = field(default_factory=dict)

    def keep(self, ref: str, why: str) -> None:
        self.kept.setdefault(ref.removeprefix(f"{REMOTE}/"), []).append(why)

    def note(self, ref: str, what: str) -> None:
        self.notes.setdefault(ref.removeprefix(f"{REMOTE}/"), []).append(what)


@dataclass(frozen=True)
class Verdict:
    """One branch's answer: swept where `kept` is empty."""

    branch: Branch
    kept: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, timeout=120, check=False
    )


def branches(root: Path) -> list[Branch]:
    """Every fetched `claude/` branch, oldest last commit first."""
    listed = _git(
        root,
        "for-each-ref",
        "--sort=committerdate",
        "--format=%(refname:strip=3)%09%(objectname)%09%(committerdate:unix)",
        f"refs/remotes/{REMOTE}/{PREFIX}",
    )
    if listed.returncode != 0:
        raise Declined(f"git could not list the fetched branches: {listed.stderr.strip()}")
    found = []
    for line in listed.stdout.splitlines():
        name, tip, stamp = line.split("\t")
        found.append(Branch(name, tip, datetime.fromtimestamp(int(stamp), UTC)))
    return found


def read_pull_requests(root: Path, now: datetime, readings: Readings) -> None:
    slug = repo_slug()
    found = None if slug is None else open_pull_requests(slug)
    if found is None:
        raise Declined(
            "GitHub's open pull requests could not be listed, which needs a token in "
            "GH_TOKEN or GITHUB_TOKEN and the network"
        )
    for pull in found:
        if not pull.base:
            raise Declined(f"pull request #{pull.number} came back without its base branch")
        readings.keep(pull.head, f"pull request #{pull.number} is open from it")
        readings.keep(pull.base, f"pull request #{pull.number} is open onto it")


def read_docket(root: Path, now: datetime, readings: Readings) -> None:
    read = holdings(root, now=now, items_dir=ITEMS, include_head=False)
    if read.declined:
        raise Declined(f"docket could not read the claims: {read.declined}")
    for ref in read.unreadable:
        readings.keep(ref, "docket could not read its commits")
    for ref, keys in unfinished_work(read).items():
        readings.keep(ref, f"unfinished work on {', '.join(keys)}")
    for cut in read.cuts:
        readings.keep(cut.ref, f"the release cut of v{cut.key}")


def read_stranded(root: Path, now: datetime, readings: Readings) -> None:
    items = read_items(root / ITEMS)
    held_open = {item.identifier for item in items if item.status not in CLOSED_STATUSES}
    report = stranded(root, {item.identifier for item in items}, items_dir=ITEMS)
    if report.declined:
        raise Declined(f"`stranded` could not read the branches: {report.declined}")
    for lost in report.items:
        for ref in lost.branches:
            readings.keep(ref, f"the only copy of {lost.identifier}")
    for edit in report.edits:
        for ref in edit.branches:
            if edit.identifier in held_open:
                readings.keep(ref, f"an edit to {edit.identifier}, open on main, that main lacks")
            else:
                readings.note(ref, f"an edit to {edit.identifier}, which main has closed")


def read_orphaned(root: Path, now: datetime, readings: Readings) -> None:
    report = orphaned(root, items_dir=ITEMS)
    if not report.known:
        raise Declined(f"`vcs.orphaned` could not read the branches: {report.declined}")
    for branch in report.branches:
        readings.keep(branch.ref, "commits a merged pull request left behind")
    for ref in report.rewritten:
        readings.keep(ref, "rewritten history it may hold the only copy of")
    for ref in report.unreadable:
        readings.keep(ref, "`vcs.orphaned` could not compare it with main")


def read_left_behind(root: Path, now: datetime, readings: Readings) -> None:
    report = left_behind_check.check(root)
    if report.declined:
        raise Declined(f"`left_behind_check` could not read the branches: {report.declined}")
    for verdict in report.verdicts:
        if verdict.left:
            readings.keep(
                verdict.branch,
                f"{len(verdict.left)} commit(s) past the head #{verdict.number} merged",
            )
        elif verdict.declined:
            readings.keep(
                verdict.branch, f"`left_behind_check` could not read it: {verdict.declined}"
            )


READERS: tuple[Callable[[Path, datetime, Readings], None], ...] = (
    read_pull_requests,
    read_docket,
    read_stranded,
    read_orphaned,
    read_left_behind,
)


def decide(found: Sequence[Branch], readings: Readings, now: datetime) -> list[Verdict]:
    verdicts = []
    for branch in found:
        kept = list(readings.kept.get(branch.name, ()))
        age = now - branch.committed
        if age < GRACE:
            kept.append(f"last commit {_hours(age)} ago, inside the {_hours(GRACE)} grace period")
        verdicts.append(Verdict(branch, tuple(kept), tuple(readings.notes.get(branch.name, ()))))
    return verdicts


def archive_ref(branch: Branch) -> str:
    return f"{ARCHIVE}/{branch.name}/{branch.tip}"


def restore_command(branch: Branch) -> str:
    return (
        f"git fetch {REMOTE} {archive_ref(branch)} && "
        f"git push {REMOTE} FETCH_HEAD:refs/heads/{branch.name}"
    )


def sweep(branch: Branch, root: Path) -> str:
    """Copy `branch`'s tip to its archive ref and delete it, in one push.

    Returns "" where the push landed, and git's refusal where it did not.
    `--atomic` makes the two refs one transaction, so a failure leaves both as
    they were, and the lease deletes only the tip the rule judged.
    """
    head = f"refs/heads/{branch.name}"
    pushed = _git(
        root,
        "push",
        "--atomic",
        f"--force-with-lease={head}:{branch.tip}",
        REMOTE,
        f"{branch.tip}:{archive_ref(branch)}",
        f":{head}",
    )
    if pushed.returncode == 0:
        return ""
    said = [line.strip() for line in pushed.stderr.splitlines() if line.strip()]
    refused = [line for line in said if line.startswith(("!", "error:", "fatal:"))]
    return (refused or said or [f"git push exited {pushed.returncode}"])[0]


def _hours(span: timedelta) -> str:
    return f"{int(span.total_seconds() // 3600)}h"


def report(verdicts: Sequence[Verdict], failed: dict[str, str], *, applied: bool) -> list[str]:
    swept = [v for v in verdicts if not v.kept and v.branch.name not in failed]
    kept = [v for v in verdicts if v.kept]
    verb = "Swept" if applied else "Would sweep (a dry run; --apply pushes)"
    lines = [
        f"{verb} {len(swept)} of {len(verdicts)} {PREFIX} branches, each kept under {ARCHIVE}/:"
    ]
    for verdict in swept:
        branch = verdict.branch
        lines.append(f"  {branch.name}  {branch.tip[:10]}  last commit {branch.committed:%Y-%m-%d}")
        lines.append(f"    restore: {restore_command(branch)}")
        lines.extend(f"    archived with it: {note}" for note in verdict.notes)
    if failed:
        lines.append(
            f"Not swept, because the push was refused ({len(failed)}); nothing changed for these:"
        )
        lines.extend(f"  {name}  {why}" for name, why in failed.items())
    lines.append(f"Kept {len(kept)}:")
    lines.extend(f"  {v.branch.name}  {'; '.join(v.kept)}" for v in kept)
    return lines


def main(argv: Sequence[str] | None = None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(
        description="Archive, then delete, every finished claude/ branch on origin."
    )
    parser.add_argument(
        "--apply", action="store_true", help="push; without it, list what would be swept"
    )
    args = parser.parse_args(argv)
    now = datetime.now(UTC)
    readings = Readings()
    try:
        found = branches(root)
        for read in READERS:
            read(root, now, readings)
    except Declined as declined:
        print(f"Nothing swept: {declined}.")
        return 1
    verdicts = decide(found, readings, now)
    failed: dict[str, str] = {}
    if args.apply:
        for verdict in verdicts:
            if not verdict.kept and (why := sweep(verdict.branch, root)):
                failed[verdict.branch.name] = why
    print("\n".join(report(verdicts, failed, applied=args.apply)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
