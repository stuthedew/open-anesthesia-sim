"""Proving that delegated work stayed inside the commission it was given.

A passing check proves the check passed. It does not prove the work is
correct, because a check can be satisfied by the wrong route: weakening an
assertion, adding a suppression, editing the gate itself, or doing the item
correctly and changing three unrelated files on the way past. Every one of
those produces a green build.

So this module verifies two things that together are worth more than either
alone - that the item's own command passes, and that the diff which produced
it stayed inside the paths the item declared. The second is the half that
makes review cheap: without it, accepting delegated work means reading the
diff, which is the cost delegation exists to avoid.

What it deliberately does not do is decide whether the work is *right*. A new
test can exercise the intended line and assert the wrong value, and no check
here can tell. The report says so in as many words rather than presenting a
clean result as a guarantee, because a tool that implied otherwise would be
worse than no tool.

Commands are shelled out, never imported. This package is standard-library
only and runs without a virtualenv; the commands it runs belong to the
project, and that separation is what keeps a bare checkout able to use it.
"""

from __future__ import annotations

import os
import subprocess
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from . import vcs
from .config import Config
from .model import Item, parse_front_matter

# Suppressions matched as text. `noqa` is deliberately absent: a project whose
# ruff configuration does not enable a rule carries `noqa` directives that
# suppress nothing, so flagging the text would fire on inert directives and
# still miss one written against a rule that *is* enabled. Whether a `noqa`
# matters is a question for the linter's own `RUF100`, not for a substring
# search, and answering it here would be guessing at the judgment half.
SUPPRESSIONS = ("# type: ignore", "typing.no_type_check", "xfail", "pytest.skip", "@skip")

RESIDUAL = (
    "Not proven: whether a new test asserts the value the model should produce "
    "or merely the value it currently produces. A test can exercise the right "
    "line and assert the wrong thing. Read the new test bodies."
)


@dataclass(frozen=True)
class Check:
    """One thing that was looked at, and what was found."""

    name: str
    passed: bool
    detail: str = ""
    lines: tuple[str, ...] = ()

    def describe(self) -> str:
        head = f"  {'PASS' if self.passed else 'FAIL'}  {self.name}"
        if self.detail:
            head += f" - {self.detail}"
        return "\n".join([head, *(f"          {line}" for line in self.lines)])


@dataclass
class Verification:
    """Every check run against one item, and whether it may be accepted."""

    item: Item
    base: str
    #: What is wrong with the base itself, when something is. A scope check is
    #: only as good as the ref it subtracts, and a stale one produces a report
    #: that is wrong in the direction of looking alarming - other branches'
    #: files, named as this item's overreach.
    base_note: str = ""
    checks: list[Check] = field(default_factory=list)
    #: Whether the per-item checks stopped before they had all run. An item
    #: with no command, or with nothing between its base and `HEAD`, has
    #: nothing further to look at, and the project-wide check says nothing
    #: about it either way.
    stopped_early: bool = False

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def describe(self) -> str:
        lines = [f"{self.item.identifier} {self.item.title}", f"  against {self.base}"]
        if self.base_note:
            lines.append(f"  {self.base_note}")
        lines.append("")
        lines.extend(check.describe() for check in self.checks)
        lines.append("")
        lines.append("  ACCEPT" if self.passed else "  REJECT")
        lines.append(f"  {RESIDUAL}")
        return "\n".join(lines)


def _run(
    args: list[str],
    root: Path,
    *,
    shell: bool = False,
    timeout: float = 1800,
    env: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Run a command, returning its exit status and combined output.

    Two kinds of command come through here, and both are meant to. Most
    callers read history with `git`, named rather than given an absolute
    path for the same reason as `vcs._run_git`: the path differs by
    environment. The other two run a command recorded in the store - an
    item's `verify:` field, and the configured check command - as written
    and through a shell, because running the recorded command verbatim is
    the entire job. Both were trusted enough to be committed to the
    repository, so there is no untrusted input to guard against here; the
    guard that matters is review of what gets committed.
    """
    try:
        result = subprocess.run(
            " ".join(args) if shell else args,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=shell,
            env=env,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return 1, str(error)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def item_commits(root: Path, base: str, identifier: str) -> tuple[str, ...]:
    """Commits on this branch whose subject carries the item's id.

    One commit per item is what `docs/worker.md` asks of a worker, and this is
    what that rule buys. A batch branch carries several items' work, so
    checking one item against the branch's whole diff would fail every time
    and say nothing. Scoped to its own commits, each item is judged on what it
    actually changed - which is also what lets a reviewer take four items and
    reject the fifth.
    """
    _, output = _run(["git", "log", "--format=%H", f"--grep={identifier}", f"{base}..HEAD"], root)
    return tuple(line.strip() for line in output.splitlines() if line.strip())


def changed_paths(root: Path, base: str, commits: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Every path the work has touched, committed or not.

    The working tree is included because a worker that has not committed
    everything has still changed it, and a scope check that only saw commits
    would pass a branch with an uncommitted edit to the scientific core
    sitting in it. Uncommitted work belongs to no item in particular, so it is
    attributed to whichever item is being verified rather than excused.
    """
    if commits:
        _, committed = _run(["git", "show", "--name-only", "--format=", *commits], root)
    else:
        _, committed = _run(["git", "diff", "--name-only", f"{base}...HEAD"], root)
    _, working = _run(["git", "status", "--porcelain"], root)
    paths = {line.strip() for line in committed.splitlines() if line.strip()}
    for line in working.splitlines():
        entry = line[3:].strip() if len(line) > 3 else ""
        if " -> " in entry:  # a rename touches both names
            before, _, after = entry.partition(" -> ")
            paths.update({before.strip(), after.strip()})
        elif entry:
            paths.add(entry)
    return tuple(sorted(paths))


def _within(path: str, allowed: tuple[str, ...]) -> bool:
    candidate = path.strip().strip("/")
    for entry in allowed:
        target = entry.strip().strip("/")
        if target and (candidate == target or candidate.startswith(target + "/")):
            return True
    return False


def _diff_text(root: Path, base: str, commits: tuple[str, ...]) -> str:
    if commits:
        _, diff = _run(["git", "show", "--format=", *commits], root)
        return diff
    _, diff = _run(["git", "diff", f"{base}...HEAD"], root)
    return diff


def _added_lines(root: Path, base: str, commits: tuple[str, ...] = ()) -> list[str]:
    diff = _diff_text(root, base, commits)
    return [line[1:] for line in diff.splitlines() if line.startswith("+") and line[1:2] != "+"]


def _removed_lines(root: Path, base: str, commits: tuple[str, ...] = ()) -> list[str]:
    diff = _diff_text(root, base, commits)
    return [line[1:] for line in diff.splitlines() if line.startswith("-") and line[1:2] != "-"]


def _front_matter_changed(root: Path, base: str, item: Item) -> tuple[str, ...]:
    """Front-matter keys whose value the branch changed.

    A worker adds a `**Worked.**` or `**Blocked.**` note to an item's body and
    changes nothing above the fence. Marking work done, re-scoping `touches`,
    or rewriting the `verify:` command it was measured against are the
    reviewer's, and a branch that did any of them is reporting on a commission
    other than the one it was given.
    """
    if not item.path:
        return ()
    status, before = _run(["git", "show", f"{base}:{item.path}"], root)
    if status != 0:
        return ()  # a new item file has no previous front matter to differ from
    try:
        after = (root / item.path).read_text(encoding="utf-8")
    except OSError:
        return ()
    old, _ = parse_front_matter(before)
    new, _ = parse_front_matter(after)
    return tuple(sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k)))


def base_warning(root: Path, base: str) -> str:
    """What to say when the ref being compared against is not what it looks like.

    Empty when the base is current, which is the common case and says nothing.
    """
    behind = vcs.behind_remote(root, base)
    if not behind:
        return ""
    return (
        f"WARNING: {base} is {behind} commit(s) behind origin/{base}, so paths "
        "reported outside `touches` may be other branches' merged work rather "
        f"than this item's. Re-run with --base origin/{base}."
    )


def verify_item(
    root: Path, item: Item, config: Config, base: str, base_note: str = ""
) -> Verification:
    """Run the checks that are about this item, and no others.

    Split from `verify` for the one reason that matters when several items are
    reviewed together: everything here is genuinely per-item - the item's own
    command, its declared scope, its commits - while the project's own check
    proves a property of the tree and proves it identically however many items
    are being looked at. Running it once per item made a six-item batch take
    over two minutes, five of those runs re-proving a proved thing, and a
    reviewer who waits that long stops running the command at all.
    """
    report = Verification(item=item, base=base, base_note=base_note)
    commits = item_commits(root, base, item.identifier)
    paths = changed_paths(root, base, commits)

    if not item.verify:
        report.checks.append(Check("has a `verify:` command", False, "none recorded"))
        report.stopped_early = True
        return report

    # An empty diff is not verified work. Every path check below would pass on
    # nothing at all, and the report would read ACCEPT for a branch carrying no
    # change - which a mistyped or stale base makes easy to reach, and which is
    # exactly where a confident green does the most harm.
    if not paths:
        report.checks.append(
            Check(
                "there is something to verify",
                False,
                f"nothing to verify: no change between {base} and HEAD"
                + (f", and no commit naming {item.identifier}" if not commits else ""),
            )
        )
        report.stopped_early = True
        return report

    # The item's own file is always in scope: a worker is asked to append a
    # `**Worked.**` note to it, and `path` is a bare filename rather than a
    # repository path, so it is matched by basename.
    own_file = Path(item.path).name if item.path else ""
    outside = [p for p in paths if not _within(p, item.touches) and Path(p).name != own_file]
    report.checks.append(
        Check(
            "diff stayed inside `touches`",
            not outside,
            f"{len(outside)} path(s) outside"
            if outside
            else f"{len(paths)} path(s) in {len(commits) or 1} commit(s), all declared",
            tuple(outside),
        )
    )

    protected = [p for p in paths if _within(p, config.protected_paths)]
    report.checks.append(
        Check(
            "no protected path modified",
            not protected,
            ", ".join(protected) if protected else "none touched",
        )
    )

    gates = [p for p in paths if _within(p, config.gate_paths)]
    report.checks.append(
        Check(
            "the checks themselves are unedited",
            not gates,
            ", ".join(gates) if gates else "none touched",
        )
    )

    added = _added_lines(root, base, commits)
    suppressed = [line.strip() for line in added if any(s in line for s in SUPPRESSIONS)]
    report.checks.append(
        Check(
            "no suppression added",
            not suppressed,
            f"{len(suppressed)} line(s)" if suppressed else "none",
            tuple(suppressed[:5]),
        )
    )

    dropped = [line.strip() for line in _removed_lines(root, base, commits) if "assert" in line]
    report.checks.append(
        Check(
            "no existing assertion removed",
            not dropped,
            f"{len(dropped)} line(s)" if dropped else "none",
            tuple(dropped[:5]),
        )
    )

    fields = _front_matter_changed(root, base, item)
    report.checks.append(
        Check(
            "item front matter unchanged", not fields, ", ".join(fields) if fields else "unchanged"
        )
    )

    status, output = _run([item.verify], root, shell=True)
    report.checks.append(
        Check(
            "`verify:` command passes",
            status == 0,
            item.verify,
            () if status == 0 else tuple(output.strip().splitlines()[-4:]),
        )
    )
    return report


def project_check(root: Path, config: Config) -> Check:
    """Run the project's own full check once, whoever is asking.

    Shared evidence rather than per-item evidence: it says the tree is sound,
    which is a property of the tree. Every report a batch produces carries the
    same result because it is the same result.
    """
    status, output = _run([config.check_command], root, shell=True)
    return Check(
        "the project's own checks pass",
        status == 0,
        config.check_command,
        () if status == 0 else tuple(output.strip().splitlines()[-4:]),
    )


def verify(root: Path, item: Item, config: Config, base: str) -> Verification:
    """Run every check against one item's branch, project-wide check included."""
    report = verify_item(root, item, config, base, base_warning(root, base))
    if not report.stopped_early:
        report.checks.append(project_check(root, config))
    return report


def verify_batch(
    root: Path, items: Sequence[Item], config: Config, base: str
) -> list[Verification]:
    """Verify several items, running the project's own check exactly once.

    The item's own command still runs per item, because that is what makes
    each one individually acceptable or rejectable - a batch that could only
    be taken or refused whole would hand the reviewer back the all-or-nothing
    choice that one-commit-per-item exists to remove.
    """
    note = base_warning(root, base)
    reports = [verify_item(root, item, config, base, note) for item in items]
    outstanding = [report for report in reports if not report.stopped_early]
    if outstanding:
        shared = project_check(root, config)
        for report in outstanding:
            report.checks.append(shared)
    return reports


# `docket check` runs the commands below, and open items carry `verify:`
# commands ending in `bin/docket check`. Without a guard the outer run would
# re-enter itself once per such candidate, and each re-entry would do it
# again. The child is told not to ask, which is the whole fix: it still
# validates the store, it just does not recurse into this one question.
LANDED_GUARD = "DOCKET_SKIP_LANDED"

# Long enough for a project's own suite, short enough that one wedged command
# cannot hang `make check`. Measured against this store on 2026-09-01, the 29
# candidate commands took 18s in total and 5.1s at worst.
LANDED_TIMEOUT = 120.0

# Statuses worth asking about. `done` and `dropped` are settled, and an
# untriaged capture has not promised to do anything yet.
LANDED_STATUSES = ("ready", "needs-decision")


@dataclass(frozen=True)
class LandedReport:
    """Open items whose own `verify:` command already passes, or why that is unknown.

    The question `verify` asks of a branch, asked of the store instead: not
    "did this worker do what the item commissioned" but "does the item's own
    evidence of doneness already hold, while the item is still open".

    Passing proves less than it looks like it proves, and the type is shaped
    around saying so. It is consistent with two different findings - the work
    landed and nobody set `status: done`, or the command does not discriminate
    and would have passed before the work too - and no reading of an exit
    status can separate them. So this reports candidates and never a verdict,
    which is why nothing here sets a status or raises an error.

    `shared` is the part that *is* decidable. A command recorded against more
    than one open item cannot be proving any single one of them done, whatever
    it returns, so those candidates are the second reading with certainty
    rather than a maybe - and their fix is to give each item a command of its
    own, not to close anything.

    `declined` carries the meaning it does everywhere else here: the check did
    not run, and a caller must not read the empty `passing` as a clean result.
    """

    passing: tuple[str, ...] = ()
    shared: tuple[str, ...] = ()
    considered: int = 0
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def already_passing(
    root: Path,
    items: Sequence[Item],
    *,
    statuses: tuple[str, ...] = LANDED_STATUSES,
    timeout: float = LANDED_TIMEOUT,
) -> LandedReport:
    """Run every open item's `verify:` command and report the ones that pass.

    An item is closed by hand, so work that merges without its `status` being
    set leaves the item `ready` forever: it keeps its place in `next`, it is
    counted open by `wave` and `gate`, and the next session re-derives work
    that is already on `main`. Four instances are known, and in all four the
    item's own command passed on the merged tree while the file still read
    `ready`.

    Running the commands is the signal rather than reading commit subjects,
    which was measured and rejected: of the thirteen open items whose id led a
    commit subject on `main`, eleven were capture or triage commits, and an
    advisory wrong five times in six is one every session learns to skim.

    Two conditions decline rather than answer, both for the reason
    `merged_pull_requests` declines on a shallow clone - an empty result that
    means "could not look" must never render as "looked, found nothing":

    - the guard is set, so this is a nested run and the outer one is asking;
    - nothing could be executed at all, which is what a bare checkout with no
      virtualenv looks like from here. Every command returning "not found" is
      indistinguishable from a clean store unless it is reported as a refusal.
    """
    if os.environ.get(LANDED_GUARD):
        return LandedReport(
            declined="a `verify:` command re-entered `docket check`, which cannot "
            "ask this question about itself"
        )
    candidates = [item for item in items if item.status in statuses and item.verify]
    if not candidates:
        return LandedReport()

    child = {**os.environ, LANDED_GUARD: "1"}
    passing: list[str] = []
    unavailable = 0
    for item in candidates:
        status, _ = _run([item.verify], root, shell=True, timeout=timeout, env=child)
        if status == 0:
            passing.append(item.identifier)
        elif status == 127:  # the shell could not find the command at all
            unavailable += 1
    if unavailable == len(candidates):
        return LandedReport(
            declined="no `verify:` command could be run here, so finding none passing "
            "would say only that the toolchain is missing"
        )

    counts = Counter(item.verify for item in candidates)
    named = set(passing)
    shared = tuple(
        item.identifier
        for item in candidates
        if item.identifier in named and counts[item.verify] > 1
    )
    return LandedReport(passing=tuple(passing), shared=shared, considered=len(candidates))
