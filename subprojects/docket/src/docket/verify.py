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
import re
import subprocess
import tempfile
import time
from collections import Counter
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median

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

# Pytest's own exit codes, which are what make "ran and matched nothing"
# separable from "ran and something failed": 0 passed, 1 tests failed, 5 no
# tests were collected. Only 5 is needed here, and only pytest promises it.
NO_TESTS_COLLECTED = 5

# A status no process can return, so a caller can tell a command killed at the
# timeout from one that ran and failed. A shell reports an exit status in
# 0-255 and a signal death as a small negative number, so a value outside both
# collides with neither.
#
# It needs a status of its own because 1 is what a failing test returns.
# Without one, a command killed part-way through is indistinguishable from one
# that ran its assertions and correctly failed, and `already_passing` reports
# that reading to a reader as fact - the "could not look" rendered as "looked,
# found nothing" that the rest of this module exists to refuse (`PL-T940`).
TIMED_OUT = 1000

# Matched as text because the command is a shell line, not a parsed argv:
# `pytest`, `uv run pytest`, `python -m pytest` and a compound command whose
# last clause is one of those all reach here as a string. Word-bounded so that
# a file named `test_pytest_helpers.py` in the arguments is not mistaken for
# the runner - `_` is a word character, so no boundary falls before that
# `pytest`.
PYTEST_RE = re.compile(r"\bpytest\b")


def selects_no_test(command: str, status: int) -> bool:
    """Whether a command ran and matched no test, rather than failing.

    The two are the same shell exit as far as anything reading a status is
    concerned - non-zero - and they mean opposite things. A command that fails
    ran an assertion and the assertion did not hold, which is what an unstarted
    item's command is supposed to do. A command that selects no test asserted
    nothing at all: `-k` matched no name, pytest deselected the file and
    exited 5, and the same 5 comes back after the work as before it unless a
    test name happens to match. Nothing distinguishes such an item from a
    finished one, and nothing ever will on its own.

    The claim is made only about a command that names pytest, because pytest
    is what promises 5 means "collected nothing". A shell exit of 5 from
    anything else means whatever that program decided it means, and reading it
    as an empty selection would be guessing - the error this check exists to
    stop, made by the check itself.

    False negatives are accepted and are silent, which is the state today: a
    suite invoked through a wrapper that does not spell `pytest`, or a
    compound command whose last clause masks the status, is not classified.
    A false positive would put a wrong sentence in front of a reader, so the
    test is deliberately the narrow one.
    """
    return status == NO_TESTS_COLLECTED and bool(PYTEST_RE.search(command))


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
    except subprocess.TimeoutExpired as error:
        # Ahead of the clause below rather than folded into it: `TimeoutExpired`
        # is a `SubprocessError`, so the ordering is the whole of what keeps a
        # killed command distinguishable from a failed one.
        return TIMED_OUT, str(error)
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
    lines = () if status == 0 else tuple(output.strip().splitlines()[-4:])
    # A rejection either way, and for opposite reasons, so the report says
    # which. "The command failed" sends a reviewer to look for the missing
    # work; "the command selected no test" sends them to the command, which is
    # where the fault is - the work may well be finished and unprovable.
    if selects_no_test(item.verify, status):
        lines = (
            "this command selects no test (pytest exit 5, nothing collected), so it "
            "proves neither that the work is done nor that it is missing",
        ) + lines
    report.checks.append(Check("`verify:` command passes", status == 0, item.verify, lines))
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
# cannot hang `make check`. Re-measured on 2026-09-02, since the figure here is
# the only record of the cost anyone reading this constant sees and the store
# had roughly doubled under the old one: 48 candidate commands, 34.9s in total
# run serially and 6.9s at worst. The timeout bounds a single command, so it is
# the worst case that has to fit rather than the total - and the total is now
# paid concurrently in any case.
LANDED_TIMEOUT = 120.0


def landed_workers() -> int:
    """How many candidate commands to run at once.

    Each is a subprocess that spends most of its life on interpreter startup
    and imports rather than on the CPU, so more of them than there are cores
    is the right shape. Measured against this store on 2026-09-02, 49
    candidates on a four-core box: 33.9 s serially, 10.8 s at four workers,
    10.1 s at eight. The knee is at the core count and the tail beyond it is
    the startup overlap, which is why this doubles rather than matching.

    Capped because the win is already spent by then and an uncapped pool on a
    large machine would put dozens of pytest processes on one working tree for
    no measured gain.
    """
    return min(8, (os.cpu_count() or 1) * 2)


# Statuses worth asking about. `done` and `dropped` are settled, and an
# untriaged capture has not promised to do anything yet.
LANDED_STATUSES = ("ready", "needs-decision")

# How far above the typical command one has to be before it is worth naming.
#
# Measured against this store on 2026-09-02, 46 commands at the configured pool
# width on four cores: a healthy store's slowest command was 8.95 s against a
# 0.65 s median, **14x**, and adding one full-suite `pytest --cov` put a 59.3 s
# command in the same pool at **88x**. So 14x is what a store already looks
# like when nothing is wrong, and this sits between the two with roughly twice
# the margin above that - about 20 s on today's median, which is where one
# command doubles a 9.5 s check rather than merely sitting at its floor. Move
# it knowing those two numbers; they are why it is 30 and not 10 or 100.
#
# A ratio against the median rather than an absolute number of seconds,
# because the general cost level rises as the suite grows and an absolute
# threshold would then fire on everything. The median is the right denominator
# specifically because it cannot collapse: every command here pays interpreter
# and `uv run` startup, so the typical one has a floor - it measured 0.65 s and
# 0.67 s across the two runs above, the second with a 59 s command in it.
SLOW_COMMAND_RATIO = 30.0

# And a floor under the ratio, because a ratio against a near-zero median is
# meaningless. Where every command is trivial the median falls to a few
# milliseconds, ordinary process-startup jitter is then tens of times it, and
# the rule above would name a command that took 100 ms as the thing the check
# waits for. That is the false positive this whole advisory exists to avoid
# becoming: a sentence nobody can act on, printed with the same weight as one
# they can.
#
# A second is the bar for "long enough that a person waited", and on a real
# store it decides nothing - the median there is 0.65 s, so the ratio gate
# stands at ~20 s and is what actually fires. It only bites where the pool is
# small and fast, which is every test in this suite and no real run.
SLOW_COMMAND_FLOOR = 1.0


@dataclass(frozen=True)
class SlowCommand:
    """One item's `verify:` command, and what it cost the run that executed it."""

    identifier: str
    seconds: float


@dataclass(frozen=True)
class LandedReport:
    """What running every open item's own `verify:` command found, or why nothing did.

    The question `verify` asks of a branch, asked of the store instead: not
    "did this worker do what the item commissioned" but "does the item's own
    evidence of doneness already hold, while the item is still open".

    One run, two findings, because both are about a command that specifies
    nothing and both are free once the commands have been executed. `passing`
    is the command that already holds. `vacuous` is the command that never
    ran an assertion at all - `-k` matched no test name, so pytest collected
    nothing and exited 5. The second is invisible without asking, which is
    the whole reason it is asked: 5 is not 0, so a command that selects
    nothing reads to `passing` as one that correctly fails, and stays that
    way for as long as the item is open.

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
    not run, and a caller must not read the empty `passing` - or the empty
    `vacuous` - as a clean result.

    `timed_out` and `unavailable` are the same refusal made per item rather
    than for the whole run. A command killed at the limit, or one the shell
    could not find, produced no evidence about its item, so it appears in
    neither finding above and is left out of `considered` - which is rendered
    to a reader as "checked", and would otherwise count a command that was
    not. They are reported rather than merely subtracted: an item that
    silently left the count would be the same failure in a quieter form.
    """

    passing: tuple[str, ...] = ()
    shared: tuple[str, ...] = ()
    #: Open items whose command matched no test, so it asserted nothing. Unlike
    #: `passing` this is a verdict rather than a candidate: `selects_no_test`
    #: only says so where pytest's own exit code says so.
    vacuous: tuple[str, ...] = ()
    #: Open items whose command was killed at `limit` before it could answer.
    timed_out: tuple[str, ...] = ()
    #: Open items whose command the shell could not find, where others could be
    #: run. Where none could, the whole run declines instead.
    unavailable: tuple[str, ...] = ()
    #: Candidates whose command ran to completion - not how many were offered.
    considered: int = 0
    #: The per-command limit these results were produced under, so a report can
    #: name the number a reader would have to change.
    limit: float = LANDED_TIMEOUT
    #: Commands far enough above the typical one to set this check's floor, and
    #: what each cost. A pool cannot finish before its slowest member, so these
    #: are what every `make check` waits through.
    slow: tuple[SlowCommand, ...] = ()
    #: The median command's cost, and the pool's own wall clock. Carried so a
    #: report can say what normal looks like and what the run came to, rather
    #: than a bare number nobody can scale.
    typical: float = 0.0
    elapsed: float = 0.0
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
    workers: int | None = None,
) -> LandedReport:
    """Run every open item's `verify:` command, and report what running it showed.

    Two findings from the one run: the commands that already pass, and the
    commands that selected no test and so asserted nothing. Both are ways an
    item can be open while its own evidence of doneness proves nothing, and
    neither is visible without executing the command.

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

    The commands run concurrently, because `make check` pays this and the bill
    grows with the queue: every item triaged to `ready` adds its command's
    runtime permanently, so the serial cost rises as the store gets healthier.
    Nothing about the answer changes - each command still runs, in the working
    tree, against the current state - so this is wall clock only, which is why
    it was preferred to caching a result or asking fewer items (`PL-LXR3`).

    Two conditions decline rather than answer, both for the reason
    `merged_pull_requests` declines on a shallow clone - an empty result that
    means "could not look" must never render as "looked, found nothing":

    - the guard is set, so this is a nested run and the outer one is asking;
    - nothing ran to completion, which is what a bare checkout with no
      virtualenv looks like from here, and what a box too loaded to finish a
      command inside the limit looks like too. Every command returning "not
      found", or every one killed at the limit, is indistinguishable from a
      clean store unless it is reported as a refusal.

    Where only some commands could not answer the run still reports, and names
    them in `timed_out` and `unavailable` rather than counting them checked.

    `slow` is the third finding, and the only one about cost rather than
    correctness. The pool cannot finish before its slowest member, so a single
    heavy `verify:` sets the floor for every `make check` from the moment it is
    written - measured at 10 s to 59 s for one full-suite `pytest --cov`
    (`PL-VG7G`). The session that writes such a command is the only one placed
    to reconsider it and was the one session told nothing, so a command far
    enough above the typical one is named with what it cost.
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

    with tempfile.TemporaryDirectory(prefix="docket-landed-") as scratch:

        def probe(item: Item) -> tuple[int, float]:
            # Coverage keeps its data in one file per run and reads it back to
            # decide `--cov-fail-under`, so two `--cov` commands sharing the
            # tree's default `.coverage` would race and one could fail on data
            # the other truncated - a wrong answer introduced by running them
            # at once rather than found by it. A path per child removes that by
            # construction, and stops these probe runs overwriting the coverage
            # data the tree's own suite wrote. Pytest's cache is left shared:
            # it is only read by selectors no recorded command uses, so a lost
            # entry cannot change an exit status.
            env = {**child, "COVERAGE_FILE": str(Path(scratch) / f"coverage.{item.identifier}")}
            started = time.monotonic()
            status, _ = _run([item.verify], root, shell=True, timeout=timeout, env=env)
            # Wall clock rather than CPU: what a session waits through is the
            # question, and it is measured under the pool's own contention
            # rather than standalone for the same reason. `dominant` reads the
            # ratio between these rather than any one of them, which is what
            # makes contention cancel instead of having to be corrected for.
            return status, time.monotonic() - started

        # `map` yields in the order it was given, which the findings below rely
        # on: they are reported as lists of ids, and an order that varied run to
        # run would make a stable store look like a changing one.
        started = time.monotonic()
        with ThreadPoolExecutor(max_workers=workers or landed_workers()) as pool:
            results = list(pool.map(probe, candidates))
        elapsed = time.monotonic() - started

    passing: list[str] = []
    vacuous: list[str] = []
    timed_out: list[str] = []
    unavailable: list[str] = []
    for item, (status, _) in zip(candidates, results, strict=True):
        # The two statuses that mean "no answer" are taken first, because both
        # are otherwise read as one: 127 is not 0 and neither is `TIMED_OUT`,
        # so either would fall through to `selects_no_test` and then out of
        # every finding, leaving the item counted as checked and nothing said.
        if status == TIMED_OUT:
            timed_out.append(item.identifier)
        elif status == 127:  # the shell could not find the command at all
            unavailable.append(item.identifier)
        elif status == 0:
            passing.append(item.identifier)
        elif selects_no_test(item.verify, status):
            vacuous.append(item.identifier)

    checked = len(candidates) - len(timed_out) - len(unavailable)
    if not checked:
        # Nothing ran to completion, so an empty `passing` is a fact about this
        # machine rather than about the store - a bare checkout with no
        # virtualenv, or a box too loaded to finish anything inside the limit.
        # Both are the refusal the class docstring describes, and the counts go
        # in the sentence because the two want different repairs.
        why = [f"{len(unavailable)} not found by the shell"] if unavailable else []
        if timed_out:
            why.append(f"{len(timed_out)} killed at the {timeout:g}s limit")
        return LandedReport(
            declined="no `verify:` command ran to completion here "
            f"({', '.join(why)}), so finding none passing would say only that the "
            "toolchain is missing or the limit too low"
        )

    # Only the commands that ran to completion. A killed one did not take its
    # duration - it was stopped at the limit - and one the shell could not find
    # returns instantly, so either would move the median without having cost
    # what it appears to.
    answered = [
        (item, seconds)
        for (item, (_, seconds)) in zip(candidates, results, strict=True)
        if item.identifier not in timed_out and item.identifier not in unavailable
    ]
    typical = median(seconds for _, seconds in answered) if answered else 0.0
    slow = (
        tuple(
            SlowCommand(item.identifier, seconds)
            for item, seconds in sorted(answered, key=lambda pair: -pair[1])
            if seconds >= max(typical * SLOW_COMMAND_RATIO, SLOW_COMMAND_FLOOR)
        )
        # A median of zero admits no ratio, and a pool of one or two commands
        # cannot contain an outlier by this test in any case: with two values
        # the larger is under twice their median by construction.
        if typical > 0
        else ()
    )

    counts = Counter(item.verify for item in candidates)
    named = set(passing)
    shared = tuple(
        item.identifier
        for item in candidates
        if item.identifier in named and counts[item.verify] > 1
    )
    return LandedReport(
        passing=tuple(passing),
        shared=shared,
        vacuous=tuple(vacuous),
        timed_out=tuple(timed_out),
        unavailable=tuple(unavailable),
        considered=checked,
        limit=timeout,
        slow=slow,
        typical=typical,
        elapsed=elapsed,
    )
