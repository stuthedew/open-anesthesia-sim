"""The command line.

Each command answers one question a session or a maintainer actually asks,
and answers it in as few lines as the answer allows. Nothing here reads the
whole store into a person's attention when a summary would do.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass
from dataclasses import replace as with_fields
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any

from . import arming, claiming, instructions, notes, render
from .checks import Report, SettingsSource, analyze, brief_contradictions
from .concurrency import (
    ORDERING,
    SAME_AREA,
    SAME_FILE,
    Conflict,
    conflicts_for,
    observed_conflicts,
    parallel_batch,
    sequenceable,
    shared_by_path,
)
from .config import CONFIG_NAME, Config
from .config import load as load_config
from .duplicates import anchor, near_duplicates
from .model import (
    CLOSED_STATUSES,
    EFFORTS,
    LANE_CROSSING,
    LIST_FIELDS,
    MIN_RECURRENCES,
    PRIORITIES,
    SELECTABLE_LANES,
    STATUSES,
    WITHDRAWN_MARKER,
    Item,
    generator_defect_faults,
    generator_faults,
    generators_explaining,
    is_under,
    live_recurrences,
    misread_faults,
    ranks_as_generator,
    ranks_as_generator_defect,
    recurrence_count,
    recurrences_of,
)
from .plan import (
    OfferedReport,
    UnrankedGenerator,
    clusters,
    features,
    gate,
    generator_blockers,
    generator_defects,
    is_new_work,
    longest_waiting,
    overlaps,
    placement_clause,
    placement_line,
    promotable,
    recommend,
    recurring,
    set_aside,
    unranked_generators,
    unsound_generator_claims,
    waiting_since,
)
from .release import (
    NOTES_DIR,
    SEMVER_RE,
    Readiness,
    already_released,
    is_untagged,
    milestones,
    notes_by_version,
    notes_name,
    outstanding_roadmap_edits,
    prepare_bump,
    read_version,
    readiness,
    release_notes,
    restate_references,
    stamp,
    unrecorded_milestones,
    unreferenced_by_version,
)
from .roadmap import MilestoneStates, Scope, Wave, milestone_states, wave
from .store import (
    ID_PREFIX,
    find_item,
    insert_field,
    new_id,
    read_items,
    replace_field,
    rewrite_item,
    write_item,
)
from .trend import BY_DAY, BY_WEEK
from .trend import analyze as analyze_trend
from .vcs import (
    CURRENT,
    DEFAULT_BRANCHES,
    BranchCut,
    Churn,
    CutsInFlight,
    FilingReport,
    FlightReport,
    GitRunner,
    OrphanedReport,
    SinceFiled,
    StrandedReport,
    WrittenReport,
    branch_state,
    branches_in_flight,
    changed_items,
    churn,
    closed_by,
    closures_on_base,
    commands_written_here,
    cut_window,
    cuts_in_flight,
    default_base,
    fetch_remote,
    filed_with_work,
    files_in_flight,
    lost,
    merged_pull_requests,
    open_pull_requests,
    orphaned,
    precedence,
    records_on_base,
    ref_walk,
    released_on_base,
    resolved,
    settled_branches,
    since_filed,
    stranded,
    tags,
    working_paths,
)
from .verify import (
    GitUnanswered,
    LandedReport,
    already_passing,
    changed_paths,
    items_reading,
    verify_batch,
)

# The one thing that is true at capture, and nothing else. Empty headings for a
# session to write over were indistinguishable from headings a session had left
# empty, and a session holding the brief appended it below them rather than
# replacing them, which left a dead stub that `checks.py` then read in
# preference to the brief (queue item `PL-D188`). One line inverts that: a brief
# appended below it composes into a well-formed one, which is the operation
# sessions were performing anyway. The format itself is documented in the
# README, printed by `docket triage`, and required by `docket check` at `ready`
# - three statements of it, where the fourth was the one that misread.
CAPTURE_TEMPLATE = """**Problem.** {title}
"""


def find_root(start: Path | None = None) -> Path:
    """The repository root, or the working directory if there is no checkout."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def _root(items: Path | None) -> Path:
    """The repository root the store belongs to, walked up from the store itself.

    Not the parent of the store `--items` named, which is the root only where
    the store sits one level below it. That is the layout every test in
    `test_cli.py` happened to use and not the one this project ships: `--items
    docs/items` resolved the root to `docs/`, and everything downstream took
    its answer from there. Two readings broke and neither said so (`PL-P757`).

    The queue prefix handed to `branches_in_flight` became `items/` where `git
    log --name-only` prints `docs/items/...` from the repository root, so no
    path matched, `_annotates_only` read every commit as work and
    `_item_file_ids` read none as a file edit - the direction `PL-X3WZ`
    removed, with every item a branch had merely captured or triaged
    disappearing from `docket next`. And git was then *run* from `docs/`,
    where `ls-tree` prints paths relative to that directory while
    `<rev>:<path>` is always resolved from the repository root - so every
    `git show` this module makes found nothing, `stranded` printed each
    finding as `(title unreadable)`, and `vcs._standing`, handed empty texts,
    fell through to its report-it direction for every item on every branch.
    Exit zero throughout, which is what makes the derivation worth stating in
    one place rather than twenty.

    A store in no checkout at all keeps the old answer, its parent. There is
    no repository to walk up to, nothing git is asked can be answered, and the
    only reader left is `load_config`, whose file sits beside the store rather
    than inside it.
    """
    if items is None:
        return find_root()
    found = find_root(items)
    # `find_root` falls back to its own starting point, so a returned path with
    # no `.git` in it means the walk found no checkout rather than that the
    # store is one.
    return found if (found / ".git").exists() else items.resolve().parent


def _tracked(root: Path, directory: Path) -> str:
    """The queue directory beneath the repository root, as git spells it.

    Taken from the store the invocation resolved - `--items` wins over the
    setting, because a command pointed at one queue must not be answered about
    another. `branches_in_flight` decides whether a commit was recording an
    item or working on it by whether its whole diff sits in this directory, so
    the wrong directory here reads every commit as work. That is not
    hypothetical: it is what `--items docs/items` did, from a root taken as the
    store's parent, until `PL-P757`.

    A store git cannot address comes back as the empty prefix, which no path
    git prints can match, so every commit keeps its claim. Two cases take that
    one value: a store outside the repository, and the repository root itself,
    which `relative_to` answers with `.` - a prefix no path begins with, and
    one a membership test reads as the opposite of the empty prefix
    (`PL-3T2Q`). Keeping a claim is the direction the flight reading prefers:
    an item wrongly left marked is picked around, an item wrongly unmarked is
    two sessions on one piece of work. The readers that cannot ask git about
    such a store at all - `_stranded`, `_numbers_before_notes` and `record` -
    test this value rather than deriving their own.
    """
    try:
        prefix = directory.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return ""
    return "" if prefix == "." else prefix


def _settings_source(root: Path) -> SettingsSource:
    """Which `docket.toml` governed this run, named the way its reader would type it.

    The `root` is the caller's, so this follows `_root` wherever it goes
    rather than deriving the answer a second time - which is the property that
    matters, since the bug worth catching here is root resolution moving
    (`PL-P757`). What it adds is the half `load_config` cannot report:
    it returns a `Config` and not where it came from, and a `Config` holding
    library defaults is indistinguishable from a project that wrote those
    values down. `checks._note_settings` says what the answer is for.

    Made relative to the working directory where it can be, because the reader
    is being shown a path to go and look at and an absolute one from a
    temporary directory is noise. Absolute where the store is somewhere else
    entirely, which is the case that most needs saying.
    """
    path = root / CONFIG_NAME
    found = path.is_file()
    try:
        path = path.relative_to(Path.cwd())
    except ValueError:
        pass
    return SettingsSource(path=path, found=found)


#: What a branch-detection command prints under `--no-git`, and the whole of
#: its answer: nothing was asked, so there is nothing to report.
NO_GIT = "branch detection is off (`--no-git`), so nothing was read"


@dataclass(eq=False)
class Invocation:
    """What one command resolved once, and every read beneath it shares.

    Five facets of one question - which repository, which store, under which
    settings, as git spells the store, and through which runner if any - were
    each derived per call site until this existed, and each fix centralised
    one facet and left the next to drift: the root from the store's parent
    (`PL-P757`), the reads behind a count from the settings (`PL-T441`,
    `PL-WF3X`), a second runner losing the memo (`PL-M6FY`), `.` for the empty
    prefix (`PL-3T2Q`), and a `--no-git` that stopped some reads and not
    others (`PL-NGBM`). A call site takes the answer from here rather than
    deriving one, and `test_no_git_stops_every_git_read` and
    `test_every_git_read_in_the_cli_takes_the_invocations_runner` fail any
    that goes round it.

    **`--no-git` is `git` being `None`, and nothing else is.** A read site
    takes `git` and returns its declined or empty form where there is none, so
    the flag cannot hold at one site and lapse at the next. Every read in `vcs`
    takes a `runner` and builds a plain one where it is handed none, so the
    runner has to be threaded rather than trusted to arrive.

    Kept on the namespace, as `FlightReport` was before it (`PL-PMT7`):
    `argparse` builds a fresh one per parse, so the lifetime is the command's
    and nothing has to be remembered to reset. That lifetime is what makes the
    runner's memo safe - `cmd_branch` fetches in-process - and what lets
    `main` close its `cat-file` batch. `flight` is the one field written after
    construction, by `_flight`, once.

    The store itself is not held here: `_load` reads it on every call, because
    `set`, `new` and `withdraw` write between reads.
    """

    root: Path
    directory: Path
    config: Config
    tracked: str
    settings: SettingsSource
    git: GitRunner | None
    flight: FlightReport | None = None


#: Where the command's invocation is kept, for the lifetime `Invocation` gives.
_INVOCATION_ATTR = "_resolved_invocation"


def _invocation(args: argparse.Namespace) -> Invocation:
    """The command's one invocation, resolved on first use and shared after it."""
    cached: Invocation | None = getattr(args, _INVOCATION_ATTR, None)
    if cached is not None:
        return cached
    root = _root(args.items)
    config = load_config(root)
    directory = args.items or (root / config.items_dir)
    made = Invocation(
        root=root,
        directory=directory,
        config=config,
        tracked=_tracked(root, directory),
        settings=_settings_source(root),
        git=None if args.no_git else GitRunner(),
    )
    setattr(args, _INVOCATION_ATTR, made)
    return made


def _load(args: argparse.Namespace) -> tuple[Path, list[Item], Config]:
    """Resolve the store and the settings that govern it.

    Settings come from the root of the repository holding the store, not from
    wherever the command was run. Pointing `--items` at another project's
    queue and silently applying this project's policy to it would be wrong in
    exactly the way that is hard to notice - the answers look right and are
    governed by the wrong rules.

    `_root` is what finds that root, and until `PL-P757` this said "beside the
    store" and meant it: the root was the store's parent, so `--items
    docs/items` looked for `docket.toml` in `docs/` and, finding none, ran
    this project's own queue on the package defaults - no `known_classes`, no
    `workflow_paths`, no `protected_paths`, `top_band_limit` at 5 rather than
    12. The rule was always "the project that owns the store decides", and
    one level down is the only depth at which the store's parent says that.

    The store is read fresh on every call and everything else is the
    invocation's, resolved once.
    """
    inv = _invocation(args)
    return inv.directory, read_items(inv.directory), inv.config


def _flight(args: argparse.Namespace) -> FlightReport:
    """What is in flight, and which refs this checkout could not read to find out.

    The whole report rather than its ids, because every command below ranks or
    marks against the ids and none of them can see the refs that went unread.
    Handing them a set would present a partial reading as a complete one - a
    session told an item is startable when one unread ref might be carrying it
    - which is the collapse `FlightReport` exists to prevent.

    The root is resolved from the store, exactly as `_load` resolves it. Asking
    git about the repository this command happens to be *run* in, while
    answering about a queue somewhere else, is the same wrong-project error
    `_load` guards against and is harder to see: the branches come back looking
    perfectly plausible.

    **Computed once per invocation, and cached on it for that reason**
    (`PL-PMT7`). `cmd_next` and `cmd_digest` each asked twice - once through
    `_offered`, once directly - and every ask shells out to git per branch
    ref. Measured on a four-core container, `next` issued 26 git subprocesses
    where `flight` and `status` issued 13, and roughly 180 ms of its ~460 ms
    was the repeated work.

    Correctness is what keeps the cache on the invocation rather than in a
    module global or an `lru_cache`. One process must give one answer, and
    that answer must not outlive the command: a long-running caller ranking
    against a stale view of what is in flight would hand a session an item
    another session is holding, which is the collision this whole read exists
    to prevent. `FlightReport` is frozen, so a caller cannot edit what the
    next one reads.
    """
    inv = _invocation(args)
    if inv.flight is not None:
        return inv.flight
    report = (
        FlightReport()
        if inv.git is None
        else branches_in_flight(inv.root, items_dir=inv.tracked, runner=inv.git)
    )
    inv.flight = report
    return report


def _say_unread(flight: FlightReport) -> None:
    """Print the partial-answer line, for the commands that render their own output.

    `list`, `status`, `delegable` and the digest get it from the renderer that
    builds the rest of their answer; `next` and `concurrent` assemble theirs
    here, so they say it here. One sentence either way - it is `render` that
    owns the wording.
    """
    if line := render.format_unread(flight):
        print(line)


def _stranded(
    items: Sequence[Item], args: argparse.Namespace, *, fetched: bool = False
) -> StrandedReport | None:
    """What exists only on a branch, or `None` when the question cannot be asked.

    The store is passed in rather than re-read: what this session can already
    see is exactly what must not be reported back to it, and the caller has it.

    A store git cannot address - outside the repository, or the root itself,
    both the empty prefix (`_tracked`) - is `None` rather than an answer. Git
    can only be asked about paths it tracks, and searching the wrong path would
    find no items and report every branch as stranding all of its own.

    `fetched` is the caller's, because the two callers refresh differently and
    neither should refresh twice. `cmd_stranded` fetches for itself; the digest
    is run by a hook that has just fetched through `docket branch`, and a
    second fetch would cost every session start a network round trip for an
    answer it already has.
    """
    inv = _invocation(args)
    if inv.git is None or not inv.tracked:
        return None
    return stranded(
        inv.root,
        {item.identifier for item in items},
        items_dir=inv.tracked,
        fetched=fetched,
        runner=inv.git,
    )


def _orphaned(args: argparse.Namespace) -> OrphanedReport | None:
    """Work a branch carries that its own pull request left behind, or `None`.

    Unlike `_stranded` this needs no store *content*: the question is about
    the tree as a whole, which is the point of it. It does need to know where
    the queue sits, for the two readings that treat an item file differently
    from any other path - a landed commit that only annotates the queue is not
    evidence of a merge, and an item file whose copy here is behind the base's
    is not work left behind (`PL-MBTZ`). The invocation's `tracked` is what
    says where, so the two commands cannot disagree about it; a store git
    cannot address comes back as the empty prefix and leaves both readings at
    the default path, which is the answer for a queue git cannot be asked
    about at all. Only `--no-git` turns this off, for the same reason it turns
    the rest off - a caller that has said not to ask git must not be asked git.
    """
    inv = _invocation(args)
    if inv.git is None:
        return None
    if not inv.tracked:
        return orphaned(inv.root, runner=inv.git)
    return orphaned(inv.root, items_dir=inv.tracked, runner=inv.git)


def _complete_report(
    root: Path,
    items: list[Item],
    config: Config,
    args: argparse.Namespace,
    *,
    landed: LandedReport | None = None,
) -> Report:
    """The report behind a printed count, with every input asked for.

    Complete in what it *asks*, not in what comes back: a checkout that cannot
    answer still declines, and the decline travels in `report.declined` as it
    always did.

    **Why the gathering is one function and not three call sites.** `analyze`
    skips the check behind any input it was not handed, which is what lets
    `list` and `status` read the store without asking git anything. Three
    commands then print a *count* of what it found - `check`, `digest` and
    `next` - and a caller that asked less printed a smaller number with
    nothing on the line saying so. The digest asked least: it never supplied
    `closures`, so the `pr`-backfill advisories were structurally invisible to
    it and it reported 10 grooming advisories where `check` reported 19
    (`PL-VKGJ`; 3 against 5 re-measured on 2026-09-20). `next` omitted
    `milestones` as well, and under-counted the promotable-item advisory for a
    second reason.

    A count carries no qualification at the point it is read, so "the grooming
    debt is 10" and "the part of the grooming debt this caller asked about is
    10" are indistinguishable there - which is
    `.claude/rules/apparatus-standard.md`'s floor exactly: what the apparatus
    tells a session must be true, or must say what it could not read. Asking
    the same questions is the remedy rather than footnoting the answer,
    because the digest's number is what a session sizes its remaining debt
    against before it has read anything, and a footnote that fires on every
    session start is a line nobody reads.

    Gathering them here is what makes that structural rather than remembered.
    A new input added to `analyze` is added once, and every command that
    prints a count has it in the same commit; added at one call site, it
    silently reopens the gap. `landed` is the single deliberate exception and
    is the caller's argument for that reason: it replays every open item's own
    `verify:` command, 31 s of the 32 s `check --verify` takes, and only CI
    passes it. `make docket` - the command the digest's own line names - does
    not pass it either, so the digest still agrees with what its reader is
    being sent to.

    What the digest pays for it is one git read per input: measured over five
    runs of each on this repository, 2026-09-20, 279 ms added to a 947 ms
    command, of which `lost` is 119 ms, `closures_on_base` 74 ms and
    `merged_pull_requests` 45 ms, the rest under 10 ms apiece. `next` pays
    the same 274 ms on a 744 ms command. None of the reads touch the network,
    so a session start offline answers exactly as it did before, and the hook
    that prints the digest already spends 1.8 s on a fetch and a CI read.
    """
    # Where the store sits as git spells it, rather than what the settings call
    # it. Every read below resolves its paths from the repository root, and
    # `--items` may point at a store the loaded config does not name - the
    # config being read from beside the store, deliberately, so the project
    # that owns a queue is the one whose policy governs it. Handed
    # `config.items_dir`, each `git show` below then missed, no closure was
    # `landed`, no `pr` was owed, and the command reported a clean provenance
    # record for a store it never read: exit zero, a plausible count, and
    # nothing on the line saying the question went unasked (`PL-T441`). The
    # invocation answers it once for every reader, so asking it here is one
    # spelling of the question rather than a second.
    #
    # A store git cannot address comes back as the empty prefix, which git
    # rejects as a pathspec - so these reads decline and say so, which is the
    # honest answer for a queue git cannot be asked about at all.
    #
    # Under `--no-git` the five git reads below are not asked at all, and
    # `analyze` reads `None` as a caller that did not ask. `check`, `digest`
    # and `next` all gather here, so all three skip the same inputs and their
    # counts still agree (`PL-NGBM`).
    inv = _invocation(args)
    git = inv.git
    tracked = inv.tracked
    return analyze(
        items,
        args.today or date.today(),
        config,
        # Asked of what has merged rather than of the store, so it needs a
        # history to read. `None` comes back from a checkout too shallow to be
        # trusted, and the provenance check is skipped rather than run against
        # a truncated one.
        history=None if git is None else merged_pull_requests(root, runner=git),
        offered=_offered(root, items, config, args),
        milestones=_milestones(root, config),
        landed=landed,
        # Only the closures in question are asked about, because each costs a
        # `git show`: an item is judged for a missing `pr` once its closure
        # stands on the default base, and until then it is still in flight.
        closures=(
            None
            if git is None
            else closures_on_base(
                root,
                {i.identifier: i.path for i in items if i.status == "done" and not i.pr and i.path},
                items_dir=tracked,
                runner=git,
            )
        ),
        # The same `git show`, asked of the other half of a closure: not "has
        # this landed" but "does it still record the command that proved it".
        # Every closed item is offered and the reader narrows to the ones this
        # checkout changed, which is usually none - a diff rather than a read
        # per item, so it costs what the line above already costs.
        records=(
            None
            if git is None
            else records_on_base(
                root,
                {i.identifier: i.path for i in items if i.status == "done" and i.path},
                items_dir=tracked,
                runner=git,
            )
        ),
        # The same diff read for the open items: which commands this branch
        # wrote, so the admitted shapes reach a command written for an item
        # older than their cutover (`PL-1P5V`).
        written=(
            None
            if git is None or config.verify_allowlist_from is None
            else commands_written_here(
                root,
                {
                    i.identifier: i.verify
                    for i in items
                    if i.status not in CLOSED_STATUSES and i.verify
                },
                items_dir=tracked,
                runner=git,
            )
        ),
        # Asked of the branch rather than of the default branch, and that is
        # the whole point: a squash merge makes the branch's commits ancestors
        # of nothing, so the objects proving what it carried stop being
        # reachable. Run here, on a pull request, the evidence is still intact.
        lost=None if git is None else lost(root, items_dir=tracked, runner=git),
        # Read rather than asked of git: a stamped `milestone:` is judged
        # against the version the project is actually on, and an absent
        # version file leaves the question unasked rather than answered.
        version=read_version(root / config.version_file),
        # The other half of the same record. A release writes its items'
        # stamps and its notes in one run, so the two agreeing is a fact about
        # that run having finished - and nothing compared them until an
        # interrupted one made them disagree silently (`PL-1MKQ`). One
        # directory read of about 36 small files.
        notes=notes_by_version(root),
        # The third thing those two files can disagree about, and the one that
        # nothing compared until it had been filed four separate times: a
        # bullet naming an item and no pull request, while the item records
        # one. The same directory read as above (`PL-W7WL`).
        unreferenced=unreferenced_by_version(root),
        # The seam between those two halves. The notes are written at the cut
        # and the tag goes on the merge, so anything landing in between is
        # inside the tag's span and named in no notes - measured at 12 closing
        # pull requests across 11 of 47 tagged spans (`PL-028F`). Answerable
        # only while the cut is unmerged, which is where this runs: on the
        # release branch and on its pull request, where re-running the cut
        # still absorbs the newcomers.
        window=None if git is None else cut_window(root, runner=git),
        # The running cross-session log, split at its `##` headings - a
        # different file from the release notes two lines up. One read of one
        # file, and only where the project names one: a project configuring no
        # `notes_file` hands `None`, which leaves the stale-thread advisory
        # unraised rather than computed against an empty parse.
        threads=notes.read(root / config.notes_file) if config.notes_file else None,
        # The dated lines of the instruction set, for the staleness advisory.
        # A read of about twenty small markdown files, and only where the
        # project names them: `instruction_paths` empty hands `None`, which
        # leaves the advisory unraised rather than saying nothing has aged.
        #
        # Here rather than in `make check`'s `doc_check.py`, and the placement
        # is the decision: `docket check` is what `make docket` runs, where a
        # reader is already doing hygiene and has the judgment in hand. On an
        # edit-triggered check the same line would fire at a session nowhere
        # near an instruction file, every run, until it stopped being read.
        assertions=(
            instructions.read(root, config.instruction_paths) if config.instruction_paths else None
        ),
        # Not read from the store at all, unlike everything above: it is which
        # policy the store was read *under*, which only the caller that
        # resolved it knows.
        settings_source=inv.settings,
    )


def cmd_check(args: argparse.Namespace) -> int:
    # The repository root, not the store beneath it: `_load` returns the item
    # directory, and the roadmap `_offered` reads sits a level above it.
    _, items, config = _load(args)
    inv = _invocation(args)
    root = inv.root
    # The pull-request replay's scope, in two halves, computed here rather than
    # inside `already_passing` so the cost line can name which half an id came
    # from. The first is the items this branch edited; the second is the open
    # items whose `verify:` command reads a file this branch edited, which is
    # the half that catches a command a branch *invalidates* without ever
    # opening its item (`PL-XMNC`). Both read the diff against the same base,
    # and both under-report where that base cannot be resolved rather than
    # guessing - a scoped run then checks nothing and says so.
    #
    # Saying so is the half that was missing (`PL-ZPDM`). The read answered a
    # git that would not speak with an empty set, which is what a branch that
    # changed no item looks like - so the replay was scoped to nothing, ran
    # nothing, and the run reported a clean result. `unscoped` carries the
    # reason instead, and the replay below declines whole rather than claiming
    # a scope it could not read.
    changed: frozenset[str] = frozenset()
    reading: frozenset[str] = frozenset()
    unscoped = ""
    if args.verify and args.verify_base and inv.git is None:
        # A scope is a diff, and `--no-git` asks git nothing, so the scoped
        # replay declines whole and says why - the decline a base that will
        # not resolve gets, rather than a replay scoped to nothing reporting
        # clean. A bare `--verify` still replays: the commands it runs are the
        # project's own, not docket's reads.
        unscoped = (
            f"the replay is scoped to what this branch changed against "
            f"{args.verify_base}, and `--no-git` asks git nothing, so that was not read"
        )
    elif args.verify and args.verify_base:
        # The same resolution `_complete_report` makes, and for the same
        # reason: the diff behind the replay's scope is read from the
        # repository root, so a store the settings do not name scopes the
        # replay to nothing (`PL-T441`). An unreadable prefix leaves `known`
        # false, and `unscoped` below says so rather than reporting a clean
        # replay that never ran.
        edited = changed_items(root, args.verify_base, items_dir=inv.tracked, runner=inv.git)
        changed = edited.identifiers
        declined = edited.declined
        try:
            reading = items_reading(items, changed_paths(root, args.verify_base)) - changed
        except GitUnanswered as silence:
            # The other half of the scope, and the same answer. Until
            # `PL-9RFP` git's complaint came back as the changed paths, matched
            # no command, and left the half that catches a branch breaking
            # another item's `verify:` scoped to nothing.
            declined = declined or str(silence)
        if declined:
            unscoped = (
                f"the replay is scoped to what this branch changed against "
                f"{args.verify_base}, and that could not be read - {declined}"
            )
    report = _complete_report(
        root,
        items,
        config,
        args,
        # Runs every open item's own `verify:` command, which is the only
        # check here that executes the project rather than reading it - 83
        # subprocesses and 31 s of the 32 s this command took, measured
        # 2026-09-04, against 0.28 s for everything else here.
        #
        # Behind a flag rather than always, because it is the wrong question
        # for the caller that was paying it. `already_passing` finds work that
        # *merged* without its item's `status` being set - all four known
        # instances are that - so a pre-commit `make check` on a feature branch
        # spends half its runtime asking, once per commit, about a merged state
        # the commit under it cannot have changed. CI passes `--verify` and
        # keeps the answer on both the events it had it on before; `make check`
        # and `make docket` get the store validation alone (`PL-P3B6`).
        #
        # The cost also grew in the wrong direction. Every item triaged to
        # `ready` adds its command's runtime to every future run, so the
        # healthier the store got the more the gate cost - and narrowing the
        # heaviest commands does not recover it, because the floor is set by
        # the size of the queue: 1458 s of serial work over eight workers is a
        # 182 s floor against 204 s elapsed, measured 2026-09-19 (`PL-G6J5`).
        #
        # `None` rather than an empty report, which is the same path `list`,
        # `digest` and `next` take: `checks.py` reads it as "a caller that did
        # not ask" and says nothing, which is what a caller that was never the
        # right one to ask should produce. A line on every `make check` saying
        # the replay did not run would be an advisory nobody reads.
        #
        # `--verify-base` narrows it further, to the two sets computed above
        # (`PL-SDHR`, widened by `PL-XMNC`). The same argument one step on: if a
        # pre-commit gate cannot have changed whether another item's work
        # merged, neither can a pull request, and the sweep costs 87 s of the
        # quality job's 152 s on every push to every open pull request while
        # growing with the queue rather than with the change. CI scopes on
        # `pull_request` and sweeps on `push` to the default branch, which is
        # the one event where the answer is a fact about that branch.
        landed=(
            LandedReport(declined=unscoped)
            if unscoped
            else already_passing(
                root,
                items,
                scoped_to=changed | reading,
                reading=reading,
                scope_base=args.verify_base,
            )
            if args.verify and args.verify_base
            else already_passing(root, items)
            if args.verify
            else None
        ),
    )
    print(render.format_check(report))
    return 1 if report.errors else 0


def _offered(
    root: Path, items: Sequence[Item], config: Config, args: argparse.Namespace
) -> OfferedReport:
    """The ids `next` would suggest, as the grooming advisories read them.

    Deliberately the default offering - the same limit for every caller,
    ignoring `--effort` and `--limit` - because an advisory that changed with
    the flags of the command that happened to print it would report a
    different count in `check` than in `next`, and the count is the thing a
    session is being asked to act on.

    The flight report comes back whole and its unread refs travel with the
    ids, because the ranking is only as complete as the refs behind it. `check`
    was the seventh reader of that answer and the one left out of `PL-S1P1`,
    so its advisories named an item chosen from a partial reading with nothing
    saying so. The sentence is `render`'s, the same one the other six print.
    """
    plan = _plan(root, items, config)
    flight = _flight(args)
    picks = recommend(
        list(items),
        flight.ids,
        scope=plan.scope if plan is not None else None,
        generator_paths=config.generator_paths,
        protected_paths=config.protected_paths,
        gate_paths=config.gate_paths,
    )
    return OfferedReport(
        ids=frozenset(pick.item.identifier for pick in picks), declined=render.format_unread(flight)
    )


def cmd_list(args: argparse.Namespace) -> int:
    _, items, config = _load(args)
    root = _invocation(args).root
    report = analyze(
        items, args.today or date.today(), config, milestones=_milestones(root, config)
    )
    rendered = render.format_list(report, _flight(args), config.protected_paths, config.gate_paths)
    if rendered:
        print(rendered)
    return 0


def _plan(root: Path, items: Sequence[Item], config: Config) -> Wave | None:
    """Where the project stands on its own timeline, or `None` if that is unclear.

    The digest is emitted by a `SessionStart` hook, so this declines rather
    than raises: a project with no roadmap, or one whose roadmap has been
    edited into a shape the parser cannot read, still gets its queue. What it
    must not do is guess at a step, so an unreadable plan produces no plan
    line at all and `docket wave` is left to say what is wrong with it.
    """
    roadmap = root / config.roadmap_file
    if not roadmap.is_file():
        return None
    try:
        return wave(
            roadmap.read_text(encoding="utf-8"),
            read_version(root / config.version_file),
            frozenset(item.identifier for item in items if not item.is_open),
            frozenset(item.identifier for item in items),
            {item.identifier: item.blocked_by for item in items},
        )
    except (OSError, ValueError, KeyError):
        return None


def _milestones(root: Path, config: Config) -> MilestoneStates | None:
    """What the roadmap says about the milestones an item may be blocked on.

    Declines exactly as `_plan` does, and for the same reason: a bare checkout
    or an unreadable roadmap must still get its queue validated. `analyze`
    turns `None` into a declined line naming the items it could not judge,
    rather than into either a pass or a failure.
    """
    roadmap = root / config.roadmap_file
    if not roadmap.is_file():
        return None
    try:
        return milestone_states(roadmap.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError):
        return None


def cmd_digest(args: argparse.Namespace) -> int:
    _, items, config = _load(args)
    if not items:
        return 0
    root = _invocation(args).root
    # Through `_complete_report` rather than a narrower `analyze` of its own,
    # because the two count lines below - errors, and the grooming total - are
    # read as the store's whole answer by a session that has run nothing yet.
    report = _complete_report(root, items, config, args)
    ready = readiness(items, read_version(root / config.version_file), config.minor_classes)
    rendered = render.format_digest(
        report,
        _flight(args),
        ready,
        _plan(root, items, config),
        _stranded(items, args),
        config.workflow_paths,
        _orphaned(args),
        _cuts(root, config, args) if ready.is_worth_cutting else None,
        generator_paths=config.generator_paths,
        protected_paths=config.protected_paths,
        gate_paths=config.gate_paths,
        now=_now(args),
    )
    if rendered:
        print(rendered)
    if getattr(args, "profile", False):
        git = _invocation(args).git
        if git is None:
            print("git profile: nothing to profile - `--no-git` asked git nothing")
            return 0
        # The walk is asked with a plain runner, so the cost of measuring never
        # lands in what was measured; and it is asked after the digest, so the
        # digest's own output is identical whether or not `--profile` was given.
        with GitRunner(memoize=False, batch_blobs=False) as plain:
            walk = ref_walk(root, _invocation(args).tracked, runner=plain)
        print(render.format_git_profile(git.profile(walk)))
    return 0


def _cuts(root: Path, config: Config, args: argparse.Namespace) -> CutsInFlight | None:
    """Which refs are mid-release, read only where a release is being offered.

    Gated on the offer rather than run for every digest: it costs a walk of the
    unlanded refs (measured 103 ms on this repository), and a session not being
    offered a release has nothing to be warned off. It does not fetch - the
    digest's hook already did, and this must stay answerable in a checkout with
    no network.
    """
    run = _invocation(args).git
    if run is None:
        return None
    base = released_on_base(root, version_file=config.version_file, notes_dir=NOTES_DIR, runner=run)
    return cuts_in_flight(root, notes_dir=NOTES_DIR, on_base=base.notes, runner=run)


def cmd_triage(args: argparse.Namespace) -> int:
    """Everything untriaged, with what is unset on it and what the rules require.

    Prints; decides nothing. The digest already tells every session that items
    are waiting - what it could not do is put the rules in front of the
    session at the moment it applies them.

    The flight report is read for the same reason `show` reads one, and the
    case is stronger here: `show` is what a session runs having *chosen* an
    item, while triage is the first command a session runs after a digest that
    reports the untriaged count and nothing about who is holding those items.
    Two sessions answered `PL-B0YN` and `PL-LXR3` the same afternoon and the
    merge discarded most of one answer (queue item PL-PRHN).
    """
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    print(render.format_triage(report, config, _flight(args), _filed(args, report.untriaged)))
    return 0


def _filed(args: argparse.Namespace, untriaged: list[Item]) -> FilingReport:
    """Which of these items were filed by a commit that also changed code.

    Asked only here. The mark answers "was this worked when it was filed?",
    which is a question only a triage pass has, and the read is scoped to the
    items that pass is about to print rather than to the store (`PL-SWP3`).
    """
    inv = _invocation(args)
    if inv.git is None or not untriaged:
        return FilingReport()
    return filed_with_work(
        frozenset(item.identifier for item in untriaged),
        inv.root,
        prefix=inv.tracked,
        runner=inv.git,
    )


def cmd_new(args: argparse.Namespace) -> int:
    """Capture one or more ideas, with as little ceremony as it is possible to have.

    A title is the only required input. Everything else - the priority, the
    effort, the band it belongs in - is triage, and demanding it at the moment
    an idea occurs is how ideas stop being written down.

    Several titles are accepted in one call because that is how they arrive:
    an interruption rarely carries exactly one thought, and making each one a
    separate command turns a thirty-second capture into a conversation.
    """
    directory, items, _ = _load(args)
    # The `--touches` order that used to fail loudly now parses, so the one way
    # left to lose a path is to space-separate it and have it land in the title.
    # Refused rather than written, because the alternative is a silently captured
    # item called `controller.py` (`PL-YNCW`).
    strays = [title for title in args.title if _reads_as_a_path(title)]
    if args.touches and strays:
        print(
            f"'{strays[0]}' reads as a path rather than a title, so nothing was "
            "written. `--touches` takes one comma-separated value "
            "(`--touches a.py,b.py`) and may be repeated; a space-separated second "
            "path lands in the title instead."
        )
        return 1
    taken = {item.identifier for item in items}
    declared = _comma_separated(args.touches)
    # A fresh capture declares nothing, which is exactly when the search has
    # nothing to key on - and `PL-0KQP`, the fifth filing of the suppression
    # defect, is what fell through that hole. Read once for the whole call,
    # since every title in it was captured from the same working tree.
    inferred = () if declared else _inferred_paths(args)
    for title in args.title:
        # Searched before the write so that the capture cannot match itself, and
        # printed after it so that the id and path stay the first line: a session
        # that reads no further has still recorded its finding, which is the half
        # of this command that may not be made conditional on anything.
        found = near_duplicates(title, declared or inferred, items)
        identifier = _capture(directory, title, taken, args)
        taken.add(identifier)
        if found:
            print(render.format_near_duplicates(found, identifier, declared=bool(declared)))
            onto = anchor(found)
            if onto is not None:
                items = _record_recurrence(directory, items, onto.item, identifier, args)
    return 0


def _inferred_paths(args: argparse.Namespace) -> tuple[str, ...]:
    """What the working tree says this session is changing, as a stand-in for `touches`.

    A capture is made *while* working on the thing that produced it, so what
    the checkout is changing is the best available guess at what the capture is
    about - and the only one, since `bin/docket new` writes no `touches` and the
    capture rule forbids asking for any. `PL-0KQP` is the miss this closes: the
    session that filed it was on a branch whose commits touch
    `subprojects/docket/src/docket/verify.py`, the exact path all four items it
    duplicated declare, and nothing read it.

    **It may not prompt, refuse, or cost the session anything it can notice.**
    Capture is the one path in this project meant to be frictionless, so a
    reading git declines is simply an empty answer: the search then has no key,
    finds nothing, and the command behaves as it did before any of this existed.
    That is not a title-only fallback, and deliberately so - see
    `duplicates.near_duplicates`.
    """
    inv = _invocation(args)
    if inv.git is None:
        return ()
    return working_paths(inv.root, runner=inv.git).paths


def _record_recurrence(
    directory: Path, items: list[Item], matched: Item, identifier: str, args: argparse.Namespace
) -> list[Item]:
    """Write this filing onto the open item it matched, and say the count.

    The whole of `PL-X5JR`: a re-filing is evidence the defect fired again, and
    until this wrote it down the evidence had to be *asserted* by a session that
    happened to notice the cluster. `PL-STC4` documents its own duplication
    three times in its own prose, and nothing was ranked until a session read
    the five captures by hand.

    **Onto the top candidate alone, not onto everything printed.** The ranking
    is a similarity over prose and the lower candidates are there so a reader
    can check them, not because the tool believes in them; recording against
    all three would inflate every count in a cluster by the size of the cluster.
    Both ids and the date go in, so a reader who thinks the match was wrong can
    see exactly which filing was attributed and to what.

    **A file the rewrite could not keep faithful is left alone**, as `set`
    leaves one: a file spelling a key twice, or carrying a field this format
    does not know, would come back collapsed or shorn. Saying so and carrying on
    is the only acceptable outcome here, because the capture has already been
    written and must not be undone over a second item's formatting.
    """
    unsafe = matched.duplicate_fields + matched.unknown_fields + matched.block_list_fields
    if unsafe:
        print(
            f"    Not recorded on {matched.identifier}: its file spells "
            f"{', '.join(unsafe)} in a way a "
            "rewrite would silently change. `docket check` names the repair."
        )
        return items

    today = args.today or date.today()
    entry = f"{today.isoformat()} {identifier}"
    updated = with_fields(matched, recurrences=(*matched.recurrences, entry))
    try:
        insert_field(directory, matched, "recurrences", entry, append=bool(matched.recurrences))
    except ValueError as refusal:
        print(f"    Not recorded on {matched.identifier}: {refusal}.")
        return items

    count = recurrence_count(updated)
    # The condition is carried rather than resolved: `new` reads no refs, and
    # buying an accurate sentence with a git call would put that cost on the
    # capture path, which `CLAUDE.md` keeps cheap because it runs when usage is
    # nearly spent. Stating the floor is a fact about the count and always
    # true; the bare "`next` now names it" was a prediction about another
    # command, and `PL-CJ5R` made it false for an item already on a branch.
    reached = (
        " - the generator floor; `bin/docket next` offers it as a promotion "
        "candidate unless it is already in flight"
        if count == MIN_RECURRENCES
        else ""
    )
    plural = "filing" if count == 1 else "filings"
    print(f"    Recorded on {matched.identifier}: {count} {plural} matched to it{reached}.")
    return [updated if item is matched else item for item in items]


def cmd_withdraw(args: argparse.Namespace) -> int:
    """Disown a `recurrences:` entry whose match was wrong, without erasing it.

    `bin/docket new` writes that field and, until this, nothing read the other
    direction: a match made on a title similarity a reader disagreed with was
    permanent. The field is deliberately kept out of `docket set` - "the
    field's whole worth is that each entry was written by the tool at the
    moment it matched a filing", so a hand-written one is a claim about a
    filing that may never have happened (`PL-X5JR`). That argument is about
    *writing* an entry, and it does not carry across to withdrawing one: the
    hazard of an unwritable field is a fabricated filing, and the hazard of an
    unwithdrawable one is a false filing nobody can correct, which is the state
    `PL-34BG` found the store in.

    **It annotates rather than deletes**, which is what makes the correction as
    auditable as the write it undoes. A deleted entry leaves a file that reads
    as though the match was never made - a quieter record than the one that was
    there before, and the one edit in this mechanism's life that would leave no
    trace. The entry stays where it was, saying it was matched here on that
    date and disowned on this one.

    **`--because` names an item, not a sentence.** Why a match was wrong is a
    judgment - exactly the half this mechanism refuses to make - and a judgment
    belongs in a brief, where it can run to the length it needs and be read
    beside the two items it is about. The field then carries the pointer, which
    is the same shape as the write: an id a reader can open.

    Refuses on a doubled `recurrences:` key, where no single line is the one to
    change, and on nothing else about the file's formatting. An unrelated
    unknown key is no reason to leave a false entry standing: the write here
    replaces one line and cannot disturb another.
    """
    directory, items, _ = _load(args)
    matched = find_item(items, args.item)
    if matched is None:
        print(f"No item matches {args.item}, so nothing was withdrawn.")
        return 1
    brief = find_item(items, args.because)
    if brief is None:
        print(
            f"No item matches {args.because}, so nothing was withdrawn. `--because` names the "
            "item whose brief says why the match was wrong, and that pointer is the whole of "
            "what makes a withdrawal auditable."
        )
        return 1

    capture = _as_identifier(args.capture)
    entries = recurrences_of(matched)
    targets = [found for found in entries if found.identifier.upper() == capture]
    if not targets:
        recorded = ", ".join(found.identifier for found in entries if found.identifier)
        names = f"; it records {recorded}" if recorded else " - it records no filings at all"
        print(f"{matched.identifier} records no filing from {capture}{names}.")
        return 1

    standing = [found for found in targets if found.withdrawn is None]
    if not standing:
        already = targets[0]
        when = already.withdrawn.isoformat() if already.withdrawn else "an unreadable date"
        print(
            f"{capture} was already withdrawn from {matched.identifier} on {when}; "
            f"why, in {already.withdrawn_by}. Nothing changed."
        )
        return 0

    today = args.today or date.today()
    suffix = f" {WITHDRAWN_MARKER} {today.isoformat()} {brief.identifier}"
    value = ", ".join(
        found.raw + suffix
        if found.withdrawn is None and found.identifier.upper() == capture
        else found.raw
        for found in entries
    )
    try:
        replace_field(directory, matched, "recurrences", value)
    except ValueError as refusal:
        print(
            f"Nothing was withdrawn from {matched.identifier}: {refusal}. "
            "`docket check` names the repair."
        )
        return 1

    updated = with_fields(matched, recurrences=_comma_separated([value]))
    for found in standing:
        when = found.when.isoformat() if found.when else "an unreadable date"
        print(
            f"Withdrawn from {matched.identifier}: the {when} filing from {found.identifier}, "
            f"on {brief.identifier}'s reading. The entry stays, marked withdrawn."
        )
    count = recurrence_count(updated)
    print(f"    {matched.identifier} now counts {count} {'filing' if count == 1 else 'filings'}.")
    _say_undeclared_withdrawal(args, matched, brief)
    return 0


def _as_identifier(reference: str) -> str:
    """A typed reference as the store spells an id: upper case, prefix supplied.

    The same tolerance `find_item` extends, applied to a reference that names a
    *recorded entry* rather than an item - a withdrawn capture may be any id the
    field carries, so the comparison cannot go through the store.
    """
    wanted = reference.strip().upper()
    return wanted if wanted.startswith(ID_PREFIX) else ID_PREFIX + wanted


def _say_undeclared_withdrawal(args: argparse.Namespace, matched: Item, brief: Item) -> None:
    """Warn where the withdrawing item has not declared the file it just changed.

    A withdrawal is not exempt from the close-out audit, deliberately: unlike
    the append `docket new` makes, it is a deliberate act with something to
    gain, so it declares the file it touches like any other work. That is a
    `REJECT` at the end of a branch for a path the session could have declared
    in one command, and this is the only moment anything knows to say so.

    Silent where the path is already declared, which is the state it is asking
    for - an advisory that fires on every run is one nobody reads (`PL-ZBJ0`).
    """
    if not matched.path:
        return
    prefix = _invocation(args).tracked
    declared = f"{prefix}/{matched.path}" if prefix else matched.path
    if is_under(declared, brief.touches):
        return
    print(
        f"    {brief.identifier} does not declare {declared}, so `docket verify` reads this "
        f"edit as outside its commission - a withdrawal is not exempt the way the write is. "
        f"Add the path to {brief.identifier}'s `touches` before the close-out."
    )


def _comma_separated(values: list[str] | None) -> tuple[str, ...]:
    """A list flag as the item file spells it: comma-separated, in order, no blanks.

    One value per flag and the flag repeatable, for `new --touches` and for
    every list field `set` writes.
    """
    paths: list[str] = []
    for value in values or ():
        paths.extend(part.strip() for part in value.split(",") if part.strip())
    return tuple(paths)


def _reads_as_a_path(title: str) -> bool:
    """Whether a title is really a `--touches` value that landed in the wrong place.

    Narrow deliberately: one token with no whitespace, and either a directory
    separator or a short lowercase extension. A title anybody meant to write has
    a space in it, so the rule cannot refuse one that was intended.
    """
    if not title or any(character.isspace() for character in title):
        return False
    if "/" in title:
        return True
    stem, dot, suffix = title.rpartition(".")
    return bool(stem and dot and suffix.isalpha() and suffix.islower() and len(suffix) <= 4)


def _capture(directory: Path, title: str, taken: set[str], args: argparse.Namespace) -> str:
    identifier = new_id(taken)
    item = Item(
        identifier=identifier,
        title=title,
        priority="",
        effort="",
        status="untriaged",
        classes=(),
        touches=_comma_separated(args.touches),
        blocked_by=(),
        feature=args.feature or "",
        milestone="",
        added=args.today or date.today(),
        closed=None,
        commit="",
        reason="",
        body=CAPTURE_TEMPLATE.format(title=title),
    )
    path = write_item(directory, item)
    print(f"{identifier}  {path}")
    return identifier


#: The fields `set` writes, as the file spells them, paired with the `Item`
#: attribute each lands on - which is also the flag's `dest`, so one table
#: serves the parser, the conflict check and the write. Every field triage
#: answers is here and nothing else is: `id`, `title` and `added` are the
#: capture's, `pr` is `record`'s, `milestone` is `release`'s, `recurrences` is
#: `new`'s, and `commit` is retired. A flag outside this table is an unknown
#: field, and argparse refuses it before the store is read.
#:
#: `recurrences` is left out for the reason `pr` is, and the reason is stronger:
#: the field's whole worth is that each entry was written by the tool at the
#: moment it matched a filing, so a hand-written one is a claim about a filing
#: that may never have happened. `docket check` holds the entries to naming real
#: items, which is as far as a check can go (`PL-X5JR`).
SET_FIELDS: tuple[tuple[str, str], ...] = (
    ("priority", "priority"),
    ("effort", "effort"),
    ("status", "status"),
    ("classes", "classes"),
    ("feature", "feature"),
    ("touches", "touches"),
    ("blocked-by", "blocked_by"),
    ("deferred-from", "deferred_from"),
    ("closed", "closed"),
    ("reason", "reason"),
    ("payoff", "payoff"),
    ("verify", "verify"),
    ("not-delegable", "not_delegable"),
    ("falsifies", "falsifies"),
    ("root-cause-of", "root_cause_of"),
    ("generator", "generator"),
    ("misread", "misread"),
    ("impairs-generators", "impairs_generators"),
)


def cmd_set(args: argparse.Namespace) -> int:
    """Write triage's answers onto one item, in the order the store spells them.

    The judgment stays with the session - what an item is worth, how big it
    is, what it belongs with. What moves into code is the decidable half:
    which fields exist, the order they go in, and every rule `docket check`
    would apply a moment later, applied at the moment of writing instead so
    the answer is refused now rather than found by the checker one step on.
    A triage pass that wrote a 25-line helper for this and threw it away is
    the measurement behind it (`PL-L4YG`).

    Three refusals, and none is a rule of its own:

    - a flag the parser does not know is an unknown field, refused by argparse
      before the store is read. A misspelled field is silently ignored by
      every reader of it, so it is never written.
    - a field the item already records with a *different* value is refused
      without `--overwrite`. Replacing a value nobody looked at is the
      duplicate-key hazard arriving through the front door (`PL-BR4G`).
      `status` is exempt, because moving it is what the command is for: a
      status is a position in a lifecycle rather than a recorded fact, and
      the checker holds each one to what it requires.
    - a write that would add an error to `docket check`'s answer is refused
      with that error, and nothing is written. Measured as the difference
      between the store's errors with and without the write, so an error the
      store already carries elsewhere blocks nothing and no rule is restated
      here - the vocabulary, the safety pin, what `ready` and `dropped` owe,
      all arrive from `checks.py` in its own words.

    A file the rewrite could not keep faithful is refused too: one spelling a
    key twice would be collapsed to the parser's pick, one carrying a field
    the format does not know would lose it, and one holding a line no field
    reads would lose that line - usually the tail of a wrapped value
    (`PL-JD4L`). All are what `check` already reports, and a writer repairing
    them on its way past would be choosing a value on nobody's behalf.

    The file keeps its name. A rename arriving as a side effect of a field
    write is `PL-LBR6`, and bringing a drifted name back is `PL-YTDN`'s pass.
    An empty value removes a field, since the renderer omits what is empty.
    """
    directory, items, config = _load(args)
    item = find_item(items, args.item)
    if item is None:
        print(f"no item matching '{args.item}'")
        return 1
    unsafe = (
        *item.duplicate_fields,
        *item.unknown_fields,
        *item.block_list_fields,
        *(repr(line) for line in item.unread_lines),
    )
    if unsafe:
        print(
            f"{item.identifier}: its file spells "
            f"{', '.join(unsafe)} in a way a "
            "rewrite would silently change, so nothing was written; `docket check` "
            "names the repair"
        )
        return 1

    requested = _requested(args)
    if not requested:
        print("set: nothing to write; name at least one field (`docket set --help` lists them)")
        return 2

    refused: list[str] = []
    changes: dict[str, Any] = {}
    for key, attribute, value in requested:
        current = _spelled(getattr(item, attribute))
        wanted = _spelled(value)
        if current == wanted:
            print(f"{item.identifier}: `{key}` already records `{current}`; nothing to write")
            continue
        if current and key != "status" and not args.overwrite:
            refused.append(
                f"{item.identifier}: `{key}` already records `{current}`; pass "
                f"--overwrite to replace it with `{wanted}`"
            )
        changes[attribute] = value
    if refused:
        print(*refused, sep="\n")
        print(f"{item.identifier}: nothing was written")
        return 1
    if not changes:
        return 0

    updated = with_fields(item, **changes)
    after = [updated if i is item else i for i in items]
    today = args.today or date.today()
    # A command written here is written now, whatever the item's age, which is
    # the one fact `check` has to ask git for (`PL-1P5V`).
    written = (
        WrittenReport(identifiers=frozenset({item.identifier})) if "verify" in changes else None
    )
    introduced = analyze(after, today, config, written=written).errors
    if introduced:
        # Only what this write adds counts against it. An error the store
        # already carries is somebody else's, and blocking every write until
        # the whole store is clean would refuse the command on exactly the
        # days it is needed.
        already = set(analyze(items, today, config).errors)
        introduced = [error for error in introduced if error not in already]
    if introduced:
        print(f"{item.identifier}: nothing was written; `docket check` would then report:")
        for error in introduced:
            print(f"  {error}")
        return 1

    path = rewrite_item(directory, updated)
    for key, attribute, value in requested:
        if attribute in changes:
            print(f"{item.identifier}: {key}: {_spelled(value) or '(removed)'}")
    print(f"  {path}")
    _say_unblocked(item, updated, changes, items, after)
    _say_contradicted(changes, items, after, today)
    return 0


def _say_contradicted(
    changes: dict[str, Any], before: list[Item], after: list[Item], today: date
) -> None:
    """Name the passages this write left telling a reader the state it replaced.

    `docket set --status ready` is a one-line diff that never shows the
    paragraph 180 lines below it saying "Left at `needs-decision`", and closing
    an item never shows the briefs still saying they wait on it - which is how
    nine such passages stood unreported on 2026-09-22 (`PL-8YXJ`). `docket
    check` reports them to whoever runs it next; this reports them to the
    session holding the context, in the commit that made them.

    Only what this write created or changed, as `_say_unblocked` prints only
    what it released: `brief_contradictions` before and after, compared as
    messages, so a passage the store already contradicted stays `check`'s to
    report unless this write moved the status it contradicts.
    """
    if "status" not in changes and "blocked_by" not in changes:
        return
    already = set(brief_contradictions(before))
    added = [found for found in brief_contradictions(after) if found not in already]
    if not added:
        return
    print(
        f"{len(added)} passage(s) now say what this write changed; repair them in this "
        f"commit - reword each, or open its passage with `[superseded {today.isoformat()}]`:"
    )
    for found in added:
        print(f"  {found}")


def _say_unblocked(
    item: Item, updated: Item, changes: dict[str, Any], before: list[Item], after: list[Item]
) -> None:
    """Name the items this closure just took the last recorded blocker off.

    The reverse of `blocked-by` is derived rather than stored - a `blocking:`
    field was considered and refused, because it duplicates an edge the store
    already computes and adds a second place for it to be written wrong
    (project owner, 2026-09-20, ratified, over adding the field). What was
    missing was never the data. `plan.promotable` has derived this set all
    along and `docket check` has printed it all along, but nothing said it at
    the moment a blocker closes, so the reading reached only a session running
    a deliberate grooming pass - `PL-JFQ3` ran one over nine items, and
    `PL-8G48` and `PL-CHQY` ran two more over the same four four days later,
    two sessions filing for one batch on one day.

    **Newly promotable, never the whole set.** `cli._say_promotable` prints
    every stale-blocked item to a session choosing work, which is the standing
    backlog; this prints only what *this* write released, which is the half no
    other command can attribute to a cause. Printing the standing set here too
    would put the same ids in front of the one reader who did not cause them.

    Fires on a status moving into `CLOSED_STATUSES` and on nothing else.
    `dropped` closes an item as `done` does, and `promotable` resolves against
    both, so dropping a blocker releases what it held. A `blocked-by` write can
    also make an item promotable the instant it lands, which is a different
    event with a different reader and is deliberately left silent.

    Named, never promoted. Of 13 items reached this way across the two passes
    above, 6 were genuinely startable; the rest were already done inside
    another item, held by a condition nobody had declared, or carrying a
    user-facing question written in since triage. `PL-6T44` carries why a
    recomputed status must not override what an item declares - it would have
    put `PL-WZVZ`, unbuildable, into `P1` and onto the debt gate.
    """
    if "status" not in changes or updated.status not in CLOSED_STATUSES:
        return
    held = {candidate.identifier for candidate in promotable(before)}
    freed = [c for c in promotable(after) if c.identifier not in held]
    if not freed:
        return
    print(f"Closing {item.identifier} clears the last recorded blocker on {len(freed)} item(s):")
    for candidate in freed:
        print(f"  {candidate.identifier}  {candidate.title}")
    print(
        "  Not promoted for you - a closed blocker is not evidence that nothing else "
        "holds an item, and 7 of 13 measured this way were held by something the field "
        "could not see. Read each against the tree, then `docket set <id> --status ready` "
        "or write what is really holding it into `blocked-by`."
    )


def _requested(args: argparse.Namespace) -> list[tuple[str, str, object]]:
    """The fields the command line named, as (file key, attribute, value).

    An absent flag is `None` and is no request; an empty value is one, and
    asks for the field to be removed.
    """
    requested: list[tuple[str, str, object]] = []
    for key, attribute in SET_FIELDS:
        given = getattr(args, attribute)
        if given is None:
            continue
        value: object = given
        if key in LIST_FIELDS:
            value = _comma_separated(given)
        elif key == "closed":
            value = given or None
        requested.append((key, attribute, value))
    return requested


def _spelled(value: object) -> str:
    """A field's value as the item file writes it, so two spellings compare as text."""
    if isinstance(value, tuple):
        return ", ".join(value)
    if isinstance(value, date):
        return value.isoformat()
    return "" if value is None else str(value)


def _closing_date(text: str) -> date | str:
    """`--closed` as a date. The empty value passes through: it asks for the field's removal."""
    return date.fromisoformat(text) if text else text


def cmd_show(args: argparse.Namespace) -> int:
    """One item in full, and whether anybody else is already doing it.

    The in-flight exclusion lives in `plan.recommend`, so until now it reached
    a session only through `next`. Naming an item - the documented way to start
    one, and the form the `docket` skill's fresh-session line recommends -
    skipped it, and so did `triage`, `check` and this command. The one guard
    against two sessions doing the same work was applied only on the path where
    a person had *not* chosen the work, which is backwards (queue item PL-5KR2).

    So the mark is here, where a session reading an item it was handed will
    meet it. `format_unread` comes with it rather than as a nicety: the answer
    is bounded by the refs this checkout could read, and every other command
    that marks against in-flight ids says so. A mark without that line presents
    a partial reading as a complete one, which is the collapse `FlightReport`
    exists to prevent.

    **A second and weaker mark prints where the first is silent.** A branch
    that has only edited the item's file - a capture, a triage pass, a note -
    is not working the item and must not be reported as if it were, but it is
    a merge conflict waiting in that one file, which is what a session about to
    edit it needs. The wording carries the difference, per `format_queue_edit`
    (`PL-N1JK`).

    **The mark then had to say *whose* branch it was.** "Do not start this
    again" is the right answer to another session's work and a false alarm
    about your own, and re-reading the item you are implementing is the
    commonest reason to run this twice. `precedence` separates the two, and
    where more than one branch is carrying the item it also says which of them
    continues - the one question every other guard in this package leaves
    open (queue item PL-YHD3).

    **A fourth thing a session cannot learn from the item's own file: that
    something above it explains it.** `root-cause-of:` is written on the head,
    so a member carries no trace of the generator that names it and this
    command printed none. It is the same failure as the marks above - the item
    read alone looks startable - and it prints in the same place, under the
    plan line rather than beside the branch marks, because it is a fact about
    where the item sits in the queue rather than about who is working it
    (`PL-C97K`).
    """
    _, items, config = _load(args)
    item = find_item(items, args.item)
    if item is None:
        print(f"no item matching '{args.item}'")
        return 1
    flight = _flight(args)
    print(f"{item.identifier} {item.title}")
    print(f"  {item.priority or '-'} · {item.effort or '-'} · {item.status}")
    # Directly under the band, above the mechanics. `show` is how an item
    # named by the project owner is read, and it is the one path that skips
    # `next` entirely - so without this the surface they reach most carries
    # the ranking facts and nothing saying what the work is for.
    if item.payoff:
        print(f"  payoff: {item.payoff}")
    if item.touches:
        print(f"  touches: {', '.join(item.touches)}")
    if item.milestone:
        print(f"  milestone: {item.milestone}")
    root = _invocation(args).root
    plan = _plan(root, items, config)
    # Whether this item is on the generator tier, by either entrance, so the
    # plan line does not tell a session it "ranks on its band alone" about an
    # item that ranked above every band. `recommend` refuses that sentence
    # already; `show` asserted it, and `show` is the path a named item arrives
    # on.
    known_ids = {i.identifier for i in items if i.identifier}
    # `ranks_as_generator` rather than `is_generator`, which is the whole of
    # what this line asks: a recorded generator whose mechanism is spent did
    # *not* rank above every band, so "it ranks on its band alone" is true of
    # it and must not be dropped (`PL-T7QR`). Both are rank predicates, not
    # claim predicates, so a closed item is on no tier here whatever its
    # fields say - which the claim predicates reported otherwise (`PL-BBT8`).
    # The third reading is the rank a blocked head hands down to what it waits
    # on (`PL-QFWF`): without it the plan line told the build item a design
    # round filed that it ranks on its band alone, while `next` ranked it on
    # the tier.
    lifted = generator_blockers(items)
    unblocks = lifted.get(item.identifier, ())
    on_the_tier = (
        ranks_as_generator(item, known_ids)
        or ranks_as_generator_defect(item, config.generator_paths)
        or bool(unblocks)
    )
    closed = item.status in CLOSED_STATUSES
    # A blocked item is startable by nothing, so whatever tier it is on it is
    # not ranked there now - which the plan line and both tier lines below
    # asserted of `PL-MB2W` while `next` ranked its blockers instead (`PL-4RK2`).
    blocked = item.status == "blocked"
    placement = placement_line(
        plan.scope if plan is not None else None,
        item.identifier,
        ranks_above_bands=on_the_tier,
        closed=closed,
        blocked=blocked,
    )
    if placement:
        print(f"  plan: {placement}")
    if heads := generators_explaining(item.identifier, items):
        print(render.format_generators(heads))
    # The other half of the same edge. `show` on a *member* has named its head
    # since `PL-C97K`; `show` on the *head* printed nothing at all about the
    # cluster, so the surface a session reaches by naming a generator was the
    # one surface that could not say whether its repairs were owed. `done` on
    # the head means the cause was fixed, and on every head this project
    # carries it sits above members that are still open (`PL-XF5V`).
    if (cluster := clusters(items).get(item.identifier)) is not None:
        print(f"  root cause of {render.format_drain(cluster)}")
    # The recurrence verdict, directly under the cluster it qualifies. The
    # drain line above cannot carry it: a drained cluster and a spent mechanism
    # are different facts - one is how much of the damage is repaired, the
    # other is whether more is still arriving - and only the second decides
    # whether this outranks a `safety`-classed `P1`. Soundness is re-decided
    # here for the reason the `impairs-generators` block below re-decides its
    # own: an unsound claim ranks nothing, and a session believing otherwise is
    # what `docket check` exists to end.
    verdict_faults = generator_faults(item, known_ids)
    if item.generator:
        print(f"  generator: {item.generator}")
        if verdict_faults:
            print(f"    UNSOUND - {'; '.join(verdict_faults)}; ranks on its band until repaired")
        elif ranks_as_generator(item, known_ids) and blocked:
            print(_blocked_head_rank(item, items, lifted, flight.ids, _milestones(root, config)))
        elif ranks_as_generator(item, known_ids):
            print("    ranked on the generator tier - above every band but P0")
        elif closed:
            # Before `spent`, which would say "ranked on its own band" of an
            # item nothing ranks. A `live` verdict on a closed head is the case
            # that matters: its mechanism is still producing and only an open
            # item's claim can rank it, so the line says where rank comes from.
            print(
                "    closed, so on no tier whatever the verdict says"
                " - only an open item's claim ranks there"
            )
        else:
            print("    spent: recorded for the audit, ranked on its own band")
    elif verdict_faults:
        print(f"  generator: {'; '.join(verdict_faults)}")
    # The fact the cluster's members misread, beside the verdict, and faulted
    # the same way. It ranks nothing; it is what a capture and every other head
    # are compared against, so a head that states none - closed or open - is
    # one nothing will ever be compared with, and this says so on the surface
    # the head is read from (`PL-5MYR`).
    stated_faults = misread_faults(item, known_ids)
    if item.misread:
        print(f"  misread: {item.misread}")
        if stated_faults:
            print(f"    UNSOUND - {'; '.join(stated_faults)}")
    elif stated_faults:
        print(f"  misread: {'; '.join(stated_faults)}")
    if item.recurrences:
        # Where a reader sent here by `next` or the digest actually lands. Naming
        # the count and not the filings would be the partial answer this package
        # refuses: the whole worth of the field is that both briefs can be opened
        # and compared, which needs the ids (`PL-X5JR`).
        print(render.format_recurrences(item))
    if item.impairs_generators:
        # The promotion is invisible from the item file alone - `impairs-generators`
        # lifts this above every band but `P0`, and a session reading `P2` at the
        # top has no other way to learn that the ranking meant it. Soundness is
        # re-decided here rather than assumed from the field, for the reason
        # `plan.recommend` re-decides it: an unsound claim ranks nothing, and a
        # session believing otherwise is the failure `docket check` exists to end.
        faults = generator_defect_faults(item, config.generator_paths)
        print(f"  impairs generators: {item.impairs_generators}")
        if faults:
            print(f"    UNSOUND - {'; '.join(faults)}; ranks on its band alone until repaired")
        elif closed:
            print("    closed, so on no tier - only an open item's claim ranks there")
        elif blocked:
            # Only a generator head hands its rank down (`generator_blockers`),
            # so a blocked machinery defect is ranked by nothing until it can
            # start, and saying so is all this line can truthfully do.
            print(
                "    blocked, so ranked nowhere until it can start"
                " - then on the generator tier, above every band but P0"
            )
        else:
            print("    ranked on the generator tier - above every band but P0")
    if unblocks:
        # The line naming the head, because the rank is the head's and nothing
        # on this item's own face carries it: `blocked-by` is written on the
        # head alone, as `root-cause-of:` is. It says where the rank comes
        # from rather than that the item is ranked now, which a blocker that
        # is blocked itself is not.
        named = ", ".join(head.identifier for head in unblocks)
        print(
            f"  unblocks generator {named}: blocked on this item, so the head's rank passes"
            " here - the generator tier, above every band but P0"
        )
    inv = _invocation(args)
    if item.identifier in flight.ids and inv.git is not None:
        # The whole precedence read only where something is actually carrying
        # the item, which is the rare case. A session starting ordinary work
        # pays exactly what it paid before. Nothing is in flight under
        # `--no-git`, so the second test is for the type rather than the case.
        print(
            render.format_precedence(
                precedence(root, item.identifier, items_dir=inv.tracked, runner=inv.git), _now(args)
            )
        )
    elif edit := next((e for e in flight.editing if e.item_id == item.identifier), None):
        # The weaker mark, and only where the stronger one is silent. A session
        # that names an item reaches `show` and nothing else, so before this
        # the one thing it could not learn here was that another branch had
        # already written to the file it was about to write to (`PL-N1JK`).
        print(render.format_queue_edit(edit, _now(args)))
    if threads := _notes_threads(root, config, item.identifier):
        print(render.format_notes_threads(threads, item.identifier, config.notes_file))
    # Last before the brief, because the line it ends on past the threshold
    # asks for the brief to be read against the tree (`PL-TQN2`).
    if not closed:
        print(_since_filed(args, item, root, config))
    print()
    print(item.body.strip())
    _say_unread(flight)
    return 0


def _since_filed(args: argparse.Namespace, item: Item, root: Path, config: Config) -> str:
    """How long an open item has waited and what changed under its `touches` meanwhile.

    Here rather than only in the start mode's prose because `show` is what a
    session runs on every item it is about to start, however the item reached
    it - `next`, `next --oldest`, or the project owner naming it - so every
    start sees the facts without anybody remembering to look (`PL-TQN2`).

    An item with no `added:` says its age is unknown rather than printing
    nothing: an absent re-confirm line reads as "this item is young", which
    nothing established.
    """
    if item.added is None:
        return (
            "  filed: no `added:` date, so its age is not known -"
            " re-confirm the brief below against the tree before starting"
        )
    git = _invocation(args).git
    report = (
        SinceFiled.unread(root, item.touches, item.added, "`--no-git` asks git nothing")
        if git is None
        else since_filed(root, item.touches, item.added, runner=git)
    )
    return render.format_since_filed(report, args.today or date.today(), config.recheck_after_days)


def _notes_threads(root: Path, config: Config, identifier: str) -> tuple[notes.Thread, ...]:
    """The notes threads naming this id, or nothing where the project keeps none.

    Silent in three cases, all of which are "there is nothing to say": no
    `notes_file` configured, no such file in this checkout, no thread naming
    the id. A line reporting any of them would print on almost every `show`
    and change no decision, which `CLAUDE.md` calls a defect in the check
    rather than thoroughness (`PL-7QKY`).
    """

    if not config.notes_file:
        return ()
    return notes.concerning(notes.read(root / config.notes_file), identifier)


def _print_observed(args: argparse.Namespace, item: Item, flight: FlightReport) -> None:
    """What branches are already changing, as against what items declared.

    Printed under the declared answer rather than folded into it. The two are
    different kinds of evidence - a prediction written before the work, and a
    measurement taken during it - and a reader deciding whether to start needs
    to know which one fired, because only the second says the collision has
    already happened.
    """
    print()
    print("  Already changed on a branch in flight (observed, not declared):")
    inv = _invocation(args)
    if inv.git is None:
        # "Nothing has touched these files yet" would be a claim about a read
        # that was never made.
        print(f"    {NO_GIT}")
        return
    files = files_in_flight(inv.root, flight, runner=inv.git)
    observed = observed_conflicts(item, files)
    for entry in observed:
        print(f"    {entry.describe()} has changed:")
        for path in entry.paths:
            print(f"      {path}")
    if not observed:
        print("    nothing - which means no branch has touched these files *yet*,")
        print("    not that none will; and it says nothing about files this item")
        print("    touches without having declared them")
    if not files.known:
        print(f"    (this reading is partial: {files.declined})")
    if files.unreadable:
        print(f"    ({len(files.unreadable)} ref(s) unread: {', '.join(files.unreadable)})")


def _print_shared_files(conflicts: list[Conflict]) -> None:
    """The shared-file tier, one line per path rather than one per item.

    `shared_by_path` decides the grouping and the order; this only prints it.
    """
    groups = shared_by_path(conflicts)
    if not groups:
        print("    nothing")
        return
    for path, identifiers in groups:
        count = len(identifiers)
        print(f"    {path} - {count} item{'' if count == 1 else 's'}: {', '.join(identifiers)}")


def cmd_concurrent(args: argparse.Namespace) -> int:
    """What can be worked alongside what.

    Reports what is ruled out and why, never what is certified safe: the
    file lists are predictions made when each item was written, so an absence
    of declared overlap is an absence of evidence rather than evidence of
    absence.
    """
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    flight = _flight(args)
    candidates = sorted(report.open_items, key=lambda i: i.sort_key())

    if args.item:
        item = find_item(items, args.item)
        if item is None:
            print(f"no item matching '{args.item}'")
            return 1
        conflicts = conflicts_for(item, candidates)
        by_strength = {
            strength: [c for c in conflicts if c.strength == strength]
            for strength in (ORDERING, SAME_FILE, SAME_AREA)
        }
        blocked_ids = {c.other.identifier for c in conflicts}
        free = [
            c
            for c in candidates
            if c.identifier != item.identifier and c.identifier not in blocked_ids
        ]
        print(f"{item.identifier} {item.title}")
        if not item.touches:
            print("  declares no `touches`; nothing can be ruled out for it")
        print()
        print("  Cannot run alongside:")
        for conflict in by_strength[ORDERING] or []:
            print(f"    {conflict.describe()}")
        if not by_strength[ORDERING]:
            print("    nothing")
        print()
        print("  Shares a file - proceed, and land the smaller change first:")
        print("    (by path, rarest first: a path few items declare is the strong evidence)")
        _print_shared_files(by_strength[SAME_FILE])
        print()
        print("  Same area only - one declaration is coarser than the other:")
        for conflict in by_strength[SAME_AREA] or []:
            print(f"    {conflict.describe()}")
        if not by_strength[SAME_AREA]:
            print("    nothing")
        print()
        print("  No declared overlap (not a guarantee - verify before starting both):")
        for other in free:
            flag = " [IN FLIGHT]" if other.identifier in flight.ids else ""
            print(f"    {other.identifier} {other.title}{flag}")
        if not free:
            print("    nothing")
        _print_observed(args, item, flight)
        _say_unread(flight)
        return 0

    batch = parallel_batch(candidates, args.limit)
    print(f"A batch that can be worked at once ({len(batch)} items, best-first):")
    ordered = False
    for position, item in enumerate(batch):
        flag = " [IN FLIGHT]" if item.identifier in flight.ids else ""
        print(f"  {item.priority} {item.identifier} {item.title}{flag}")
        shared: dict[str, list[str]] = {}
        for conflict in conflicts_for(item, batch[:position]):
            for path in conflict.paths:
                shared.setdefault(path, []).append(conflict.other.identifier)
        ordered = ordered or bool(shared)
        for path, others in shared.items():
            print(f"      shares {path} with {', '.join(others)}")
    print()
    if ordered:
        print("Indented lines mark a shared file: those two are still both startable,")
        print("but decide which merges first rather than finding out at the merge.")
        print("Everything else here has no declared overlap - which is not a guarantee:")
    else:
        print("No declared overlap between these. That is not a guarantee: `touches` is")
    print("a prediction made when each item was written, so verify before starting.")
    waiting = sequenceable(candidates, batch)
    if waiting and args.limit is None:
        count = len(waiting)
        print()
        print(f"Outside the batch is not refused: {count} more items share a file with")
        print("something above, which orders the work rather than forbidding it.")
        print("`docket concurrent --limit N` fills the batch out with them.")
    _say_unread(flight)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """The project at feature altitude, plus whether a release is worth cutting."""
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    root = _invocation(args).root
    ready = readiness(items, read_version(root / config.version_file), config.minor_classes)
    rendered = render.format_status(report, ready, _flight(args), _plan(root, items, config))
    print(rendered if rendered else "Nothing open.")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """What to work on now, and why.

    Answers the question the queue exists to answer, so that "let\'s work on
    something" needs no reading. Preference goes to what the roadmap\'s current
    step includes, then to work that finishes a feature already underway,
    because a shipped feature is worth more than equal progress spread across
    several.

    The plan is read for the same reason `wave` reads it: without it, the
    command whose name promises the answer ranks strictly by band and leads
    with work the current step excludes. An unreadable or absent roadmap leaves
    `_plan` returning `None`, and the ranking falls back to what it was.

    An optional lane narrows the answer to one half of the project, so a
    session on the simulator and a session on the apparatus can both ask "what
    next" and never be handed the same item. The unfiltered answer is
    unchanged, and remains the default: the split is a tool for running two
    sessions at once, not a new way to read the queue.

    `--oldest` asks a different question of the same queue - owed work in the
    order it has waited - and `_next_oldest` answers it. Without the flag
    nothing below changes.
    """
    _, items, config = _load(args)
    lane = None if args.lane == "all" else args.lane
    if lane is not None and not config.workflow_paths:
        print(
            f"Cannot answer for the '{lane}' lane: no `workflow_paths` are declared in "
            f"{CONFIG_NAME}, so no item can be placed on either side of the project."
        )
        print(
            "Declare the paths holding the development apparatus there, or ask "
            "`docket next` without a lane."
        )
        return 1
    root = _invocation(args).root
    # The grooming count printed at the foot of a pick is the same claim the
    # digest's is, so it is built from the same inputs (`_complete_report`).
    report = _complete_report(root, items, config, args)
    plan = _plan(root, items, config)
    flight = _flight(args)
    if args.oldest:
        return _next_oldest(items, flight, config, args, plan, lane, report)
    picks = recommend(
        items,
        flight.ids,
        effort=args.effort,
        limit=args.limit,
        scope=plan.scope if plan is not None else None,
        lane=lane,
        workflow_paths=config.workflow_paths,
        generator_paths=config.generator_paths,
        protected_paths=config.protected_paths,
        gate_paths=config.gate_paths,
    )
    where = f" in the {lane} lane" if lane else ""
    if not picks:
        print(f"Nothing is ready to start{where}.")
        if report.untriaged:
            print(f"{len(report.untriaged)} untriaged item(s) are waiting: `docket list`.")
        _say_promotable(items)
        _say_unranked_generators(items, flight.ids, _milestones(root, config))
        _say_recurring(items, flight.ids)
        _say_lane_holdouts(items, flight, config, args, lane)
        _say_unread(flight)
        return 0
    print(f"{render.open_count(report)} open. Suggested next{where}:\n")
    for index, pick in enumerate(picks, start=1):
        print(f"  {index}. {pick.describe()}\n")
    if flight.ids:
        print(f"Excluded, already in flight: {', '.join(sorted(flight.ids))}")
    _say_promotable(items)
    _say_unranked_generators(items, flight.ids, _milestones(root, config))
    _say_recurring(items, flight.ids)
    _say_lane_holdouts(items, flight, config, args, lane)
    _say_answer_lane(items, flight, config, args, plan, lane, picks[0].item)
    if report.advisories:
        print(
            f"{len(report.advisories)} grooming advisory(ies) pending; `docket check` to see them."
        )
    _say_unread(flight)
    return 0


def _next_oldest(
    items: list[Item],
    flight: FlightReport,
    config: Config,
    args: argparse.Namespace,
    plan: Wave | None,
    lane: str | None,
    report: Report,
) -> int:
    """`docket next --oldest`: owed work in the order it has waited.

    A different question of the same queue, and `plan.longest_waiting` carries
    why it is asked. The ranking a bare `docket next` prints is untouched by
    the flag. The last line names that ranking's own pick, in the lane
    footer's shape, so a session handed off-gate work by age is never handed
    it silently.
    """
    today = args.today or date.today()
    scope = plan.scope if plan is not None else None
    waiting = longest_waiting(
        items,
        flight.ids,
        today=today,
        new_work_classes=config.new_work_classes,
        debt_classes=config.debt_classes,
        effort=args.effort,
        limit=args.limit,
        scope=scope,
        lane=lane,
        workflow_paths=config.workflow_paths,
        generator_paths=config.generator_paths,
        protected_paths=config.protected_paths,
        gate_paths=config.gate_paths,
    )
    where = f" in the {lane} lane" if lane else ""
    if waiting.picks:
        print(f"{render.open_count(report)} open. Owed work{where}, longest-waiting first:\n")
        for index, pick in enumerate(waiting.picks, start=1):
            print(f"  {index}. {pick.describe()}\n")
    else:
        print(f"No owed work is ready to start{where}.")
    _say_decisions(waiting.decisions, today, args.limit)
    if waiting.new_work:
        print(
            f"Left out as new work, classed {' or '.join(config.new_work_classes)}: "
            f"{waiting.new_work} item(s), which `docket next` still ranks."
        )
    if flight.ids:
        print(f"Excluded, already in flight: {', '.join(sorted(flight.ids))}")
    _say_promotable(items)
    # The lane's set-aside count is taken over the owed work alone, so it
    # describes the answer above rather than a queue it was never drawn from.
    owed = [i for i in items if not is_new_work(i, config.new_work_classes, config.debt_classes)]
    _say_lane_holdouts(owed, flight, config, args, lane)
    _say_plan_pick(items, flight, config, args, scope, lane)
    _say_unread(flight)
    return 0


def _say_decisions(decisions: list[Item], today: date, limit: int) -> None:
    """Name the owed work waiting on a decision, oldest first, beside `--oldest`'s picks.

    Named and never ranked, for the reason `plan.longest_waiting` gives. Cut to
    the picks' own limit with the rest counted, so a store holding forty open
    decisions prints one line rather than forty.
    """
    if not decisions:
        return
    shown = ", ".join(
        f"{item.identifier} ({waiting_since(item, today)})" for item in decisions[:limit]
    )
    rest = len(decisions) - limit
    more = f", and {rest} more (`--limit` shows them)" if rest > 0 else ""
    print(f"Waiting on a decision, oldest first ({len(decisions)}): {shown}{more}.")
    print(
        "  Not ranked above - each one's next step is the project owner's answer rather than "
        "a session's work, and ranked by age the oldest would hold the top for good."
    )


def _say_plan_pick(
    items: list[Item],
    flight: FlightReport,
    config: Config,
    args: argparse.Namespace,
    scope: Scope | None,
    lane: str | None,
) -> None:
    """Name the plan's own pick under `--oldest`'s, with the command that explains it.

    The lane footer's shape (`_say_answer_lane`), for the rule the `docket`
    skill's picking mode states: recommending off-gate work is allowed, and is
    never silent about being off-gate. Asked with the same lane and effort, so
    the two answers are one question put two ways.
    """
    found = recommend(
        items,
        flight.ids,
        effort=args.effort,
        limit=1,
        scope=scope,
        lane=lane,
        workflow_paths=config.workflow_paths,
        generator_paths=config.generator_paths,
        protected_paths=config.protected_paths,
        gate_paths=config.gate_paths,
    )
    if not found:
        return
    top = found[0].item
    command = "docket next"
    if lane:
        command += f" {lane}"
    if args.effort:
        command += f" --effort {args.effort}"
    where = f" in the {lane} lane" if lane else ""
    because = _band_and_place(scope, top)
    print(f"The plan's own pick{where} is {top.identifier} ({because}): `{command}`.")


def _say_promotable(items: list[Item]) -> None:
    """Name the blocked items whose every recorded blocker has since closed.

    `recommend` cannot offer them - `plan._startable` filters on `status` - and
    `docket check` has named them in an advisory all along, which is a command
    a session picking work has no reason to run. `next` prints the *number* of
    advisories pending and not the ids, so on 2026-09-17 the one item that
    would have unblocked three more of v0.5.0's own scope was reachable only by
    reading `blocked-by` on five items and resolving each root by hand
    (`PL-6T44`).

    Printed on the empty ranking too, and that is the case it exists for: a
    lane whose whole remainder is stale `blocked` says "nothing is ready to
    start" while naming nothing a session could do about it.

    Named, never ranked. `plan.promotable` carries the count that settled it -
    6 of 13 were genuinely startable, and ranking the other 7 would have put an
    unbuildable item into `P1` and onto the debt gate.
    """
    candidates = promotable(items)
    if not candidates:
        return
    print(
        f"Blocked on paper only, every recorded blocker closed: "
        f"{', '.join(item.identifier for item in candidates)}."
    )
    print(
        "  Not ranked above - a closed blocker is not evidence that nothing else holds an "
        "item, and 7 of 13 measured this way were held by something the field could not "
        "see. Read each against the tree, then `docket set <id> --status ready` or record "
        "what is really holding it."
    )


def _say_recurring(items: list[Item], in_flight: Collection[str]) -> None:
    """Name the open items the store has now absorbed three or more filings of.

    The counter's only output, and the design's whole point of restraint
    (project owner, 2026-09-20, ratified, over raising the matched item's
    `priority:`). `CLAUDE.md` ranks a root cause above every band but `P0`
    because "every session it stands through pays it again", and three separate
    sessions filing the same defect is that sentence measured rather than
    asserted - but the count is built from a title-similarity match, and
    `README.md` refuses to let one of those write `root-cause-of:` at all. So
    the line names the cluster and stops. A reader opens the briefs and writes
    the claim, or does not.

    Printed beside `_say_promotable` and for the same reason: `docket check`
    can only ever report this in an advisory, and a session picking work has no
    reason to run the checker.

    Takes the flight ids the ranking above already excluded on, because the
    claim a reader would write only moves a queue position and an item on a
    branch has none left to move (`PL-CJ5R`). Required rather than defaulted:
    both call sites hold the report, and a caller that quietly passed nothing
    would print the offer this argument exists to withhold.
    """
    candidates = recurring(items, in_flight)
    if not candidates:
        return
    print("Filed more than once, and never promoted for it:")
    for item in candidates:
        filed = ", ".join(sorted({f.identifier for f in live_recurrences(item) if f.identifier}))
        print(f"  {item.identifier} ({recurrence_count(item)} filings: {filed})")
    print(
        "  Not ranked above - the count comes from a title match, which may not buy a "
        "promotion. Read them against each other, and where they are one mechanism, "
        "record it: `docket set <id> --root-cause-of <ids> --generator <verdict> "
        "--misread <fact>`, the three fields `docket check` asks of a head."
    )


#: What a reader does about a blocked live head nothing ranks, shared by `next`
#: and `show` so the two surfaces cannot prescribe different remedies.
UNRANKED_REMEDY = (
    "a blocked head's rank passes one edge down, to the open items its own "
    "`blocked-by` names, and not along a chain nobody wrote for that. Where startable "
    "work sits behind it, write that work into the head's `blocked-by` and the rank "
    "passes there"
)


def _waiting_on(
    found: UnrankedGenerator, items: list[Item], milestones: MilestoneStates | None
) -> str:
    """What an unranked head waits on, each entry marked with why it carries nothing.

    A milestone is marked by what the roadmap says of it, and by what could not
    be read where it could not: `unranked_generators` has already dropped the
    ones that cleared, so what is left is unscoped, or ships with the head.
    """
    head = found.head
    if not found.waiting_on:
        if not [entry for entry in head.blocked_by if entry != head.identifier]:
            return "names no blocker in its `blocked-by` but itself, so nothing can carry its rank"
        cleared = "has closed or been scoped" if head.blocking_milestones else "has closed"
        return f"waits on nothing still open: every blocker its `blocked-by` names {cleared}"
    by_id = {item.identifier: item for item in items if item.identifier}
    parts = []
    for entry in found.waiting_on:
        if entry in head.blocking_milestones:
            if milestones is None:
                parts.append(f"{entry} (a milestone; the roadmap was not read to say if scoped)")
            elif milestones.is_cleared(entry):
                parts.append(f"{entry} (a milestone whose scope names it, so it waits to ship)")
            else:
                parts.append(f"{entry} (a milestone not yet scoped)")
        elif entry not in by_id:
            parts.append(f"{entry} (not in the store)")
        else:
            parts.append(f"{entry} ({by_id[entry].status})")
    said = f"waits on {', '.join(parts)}"
    if found.behind:
        said += f"; startable or in flight behind them: {', '.join(found.behind)}"
    return said


def _say_unranked_generators(
    items: list[Item], in_flight: Collection[str], milestones: MilestoneStates | None
) -> None:
    """Name the blocked live generator heads whose rank reaches nothing offered.

    The generator tier's own silent failure, printed beside `_say_promotable`
    for its reason: `next` is where a session choosing work looks, and a
    generator ranked by nothing is absent from the list above without a word
    (`PL-4RK2`). Named, never ranked - `plan.unranked_generators` says why the
    chain is not followed.

    Takes the flight ids the ranking excluded on: a blocker being worked on a
    branch is paying the head's edge down, so the head is not named for it.
    """
    found = unranked_generators(items, in_flight, milestones=milestones)
    if not found:
        return
    heads = "A live generator" if len(found) == 1 else "Live generators"
    print(f"{heads} that nothing ranks - blocked, and no item it waits on can start:")
    for entry in found:
        count = len(entry.head.root_cause_of)
        said = _waiting_on(entry, items, milestones)
        print(f"  {entry.head.identifier} (root cause of {count} items) {said}")
    print(f"  Not ranked above - {UNRANKED_REMEDY}.")


def _blocked_head_rank(
    head: Item,
    items: list[Item],
    lifted: dict[str, tuple[Item, ...]],
    in_flight: Collection[str],
    milestones: MilestoneStates | None,
) -> str:
    """Where a blocked live head's rank is now, for the line under its verdict.

    `show` said "ranked on the generator tier" of the head itself, which a
    blocked item is not, and named none of the blockers carrying the rank
    instead (`PL-4RK2`). Three answers, and each says which it is: ranked by
    nothing, in the shapes `plan.unranked_generators` names; carried by the
    open items `generator_blockers` lifts, each marked where it cannot be
    offered yet; or in flight, where no open item in this checkout carries it.
    """
    unranked = next(
        (
            u
            for u in unranked_generators(items, in_flight, milestones=milestones)
            if u.head.identifier == head.identifier
        ),
        None,
    )
    if unranked is not None:
        return (
            f"    blocked, and ranked by nothing: it {_waiting_on(unranked, items, milestones)}."
            f"\n    {UNRANKED_REMEDY[:1].upper()}{UNRANKED_REMEDY[1:]}."
        )
    by_id = {item.identifier: item for item in items if item.identifier}
    carriers = []
    for blocker in dict.fromkeys(head.blocking_items):
        if not any(h.identifier == head.identifier for h in lifted.get(blocker, ())):
            continue
        state = by_id[blocker].status
        if blocker in in_flight:
            carriers.append(f"{blocker} (in flight)")
        elif state in ("blocked", "untriaged"):
            carriers.append(f"{blocker} ({state})")
        else:
            carriers.append(blocker)
    if not carriers:
        return (
            "    blocked, so not ranked itself - no open item in this checkout carries its"
            " rank, and the work is in flight"
        )
    return (
        "    blocked, so not ranked itself - its rank, above every band but P0, passes to"
        f" the open items it waits on: {', '.join(carriers)}"
    )


def _say_lane_holdouts(
    items: list[Item],
    flight: FlightReport,
    config: Config,
    args: argparse.Namespace,
    lane: str | None,
) -> None:
    """Name the startable work no lane could claim, whenever a lane was asked for.

    Printed rather than left implicit because a lane is a filter, and a filter
    that silently drops a fifth of the queue is how work goes missing. Both
    kinds are recoverable and the sentences say how: an item reaching both
    halves is waiting for a session that can hold the whole change, and an item
    declaring no `touches` is waiting for somebody to write one.
    """
    if lane is None:
        return
    held = set_aside(items, flight.ids, workflow_paths=config.workflow_paths, effort=args.effort)
    if held.crossing:
        print(
            f"Set aside, reaching both halves ({len(held.crossing)}): "
            f"{', '.join(sorted(i.identifier for i in held.crossing))}. "
            f"`docket next` without a lane offers these."
        )
    if held.unplaced:
        print(
            f"Set aside, declaring no `touches` ({len(held.unplaced)}): "
            f"{', '.join(sorted(i.identifier for i in held.unplaced))}. "
            f"No lane can place these until they declare one."
        )


def _band_and_place(scope: Scope | None, item: Item) -> str:
    """The band and the gate relation - what "why this one" reduces to in a footer.

    Both are facts in the store rather than readings of it, which is what
    keeps this on the right side of scripting the judgment: the tool says
    where the item stands, and what the work buys stays prose somebody
    wrote. Before `PL-Z27P` the lane footer offered the other lane's pick as
    a bare id and title, so the one place the project owner meets the
    workflow lane carried no ranking information at all.
    """
    clause = placement_clause(scope, item.identifier)
    return f"{item.priority}, {clause}" if clause else item.priority


def _say_answer_lane(
    items: list[Item],
    flight: FlightReport,
    config: Config,
    args: argparse.Namespace,
    plan: Wave | None,
    lane: str | None,
    top: Item,
) -> None:
    """Name which lane the unfiltered answer sits in, and the other lane's pick.

    The mirror of `_say_lane_holdouts`, and it exists because that asymmetry
    is a defect: asking for a lane says what the lane hid, while asking for
    none said nothing about lanes at all - in the one call that hands over an
    answer, and the first command a session runs.

    That is where `PL-0D4X` went wrong. A session opened with the prompt "Next
    workflow item" ran the bare command, was handed the whole queue's top pick,
    and started it; the pick was product-lane work, correctly ranked, and
    nothing in front of the session said which half of the project it was in.
    The digest names both lanes at startup, but it is read once, it scrolls
    away, and it frames the split as advice "for a second session" rather than
    as an answer to a lane the prompt has already named.

    So this prints the fact the caller cannot get anywhere else - the lane of
    the answer they were just given - and the other lane's own pick beside it,
    which is what makes the mismatch visible without a second command. It says
    nothing when no boundary is declared, for the reason `Item.lane` fails
    closed: a project that has not drawn the line gets no lane rather than one
    drawn on its behalf.
    """
    if lane is not None or not config.workflow_paths:
        return

    def pick_for(wanted: str) -> Item | None:
        found = recommend(
            items,
            flight.ids,
            effort=args.effort,
            limit=1,
            scope=plan.scope if plan is not None else None,
            lane=wanted,
            workflow_paths=config.workflow_paths,
            generator_paths=config.generator_paths,
            protected_paths=config.protected_paths,
            gate_paths=config.gate_paths,
        )
        return found[0].item if found else None

    scope = plan.scope if plan is not None else None

    def name(wanted: str) -> str:
        # The payoff on its own line rather than inside the parentheses beside
        # the band: it is a sentence, and the marks in there are tokens. A
        # pick carrying none prints as it always did, so this costs a line
        # only where there is something to read on it.
        found = pick_for(wanted)
        if found is None:
            return "nothing startable"
        named = f"{found.identifier} ({_band_and_place(scope, found)}): {found.title}"
        return f"{named}\n  - payoff: {found.payoff}" if found.payoff else named

    top_lane = top.lane(config.workflow_paths)
    if top_lane in SELECTABLE_LANES:
        other = next(one for one in SELECTABLE_LANES if one != top_lane)
        because = _band_and_place(scope, top)
        print(
            f"Lane of this answer: {top.identifier} is {top_lane} work ({because}).\n"
            f"The {other} lane's own pick is {name(other)}\n"
            f"  - `docket next {other}` for its reason."
        )
        return

    # Crossing and unplaced work is nobody's lane, so there is no "the other
    # lane" to name and both are printed. The sentence says which of the two
    # it is, because they are recovered differently: a crossing item wants a
    # session that can hold the whole change, an unplaced one wants a `touches`.
    unplaceable = "reaches both halves" if top_lane == LANE_CROSSING else "declares no `touches`"
    named = "\n  ".join(f"{one}: {name(one)}" for one in SELECTABLE_LANES)
    print(
        f"Lane of this answer: {top.identifier} {unplaceable}, so no lane places it. "
        f"By lane:\n  {named}"
    )


def cmd_gate(args: argparse.Namespace) -> int:
    """Every open debt item in the store, split by feature: what a freeze starts from.

    `ROADMAP.md` records the frozen list by hand, and doing that means reading
    every open item's classes and status and splitting the result by scope.
    That is decidable, so it is decided here; freezing the list stays the
    deliberate act it is meant to be, and this command writes nothing.
    """
    _, items, config = _load(args)
    print(
        render.format_gate(
            gate(items, args.feature or "", config.debt_classes), config.debt_classes
        )
    )
    return 0


def cmd_feature(args: argparse.Namespace) -> int:
    """Progress by feature, so a half-finished one is visible as such."""
    _, items, _ = _load(args)
    groups = features(items)
    if not groups:
        print("no items are assigned to a feature")
        return 0
    if args.name and args.name not in groups:
        print(f"no feature named '{args.name}'")
        return 1
    wanted = [groups[args.name]] if args.name else list(groups.values())
    for feature in sorted(wanted, key=lambda f: (-f.progress, f.name)):
        state = "complete" if feature.is_complete else f"{len(feature.open_items)} left"
        print(f"{feature.name}: {len(feature.done)}/{len(feature.items)} done ({state})")
        for item in feature.items:
            print(f"  [{render.progress_mark(item)}] {item.identifier} {item.title}")
    return 0


def cmd_generators(args: argparse.Namespace) -> int:
    """How much of each generator's cluster is still open.

    `bin/docket feature <name>` answers "is that dealt with?" for a feature and
    nothing answered it for a generator, though a generator is the grouping
    `CLAUDE.md` ranks above every band but `P0`. The gap was not cosmetic: all
    eleven recorded heads are closed and 58 of the 99 items they name are not,
    so every surface a session sees says the generator work is finished. What
    finished is the *cause*; the repairs underneath it are what each head's
    brief is explicit about owing (`PL-XF5V`).

    With no argument it summarizes every cluster, rather than listing every
    member as `feature` does. The question is a whole-store one and its answer
    has to fit on a screen - 99 members do not - so the member list is what the
    id argument buys.

    An id may be a head or a member. A session usually holds a member's id,
    since that is what `next` hands it, and asking "how is my cluster doing"
    should not require first finding out what sits above it.

    Every head is printed with the one fact its members misread, and the
    pairs of heads whose member lists overlap follow the list (`PL-5MYR`).
    Heads were compared with nothing, so one record read by several readers
    got a head per reader. `--misread` prints only those lines, sorted by the
    fact so that heads stating one sit together - the list triage and grooming
    compare a capture against. Whether two lines name one record is judgment;
    the command makes it one screen, and flags the overlap it can decide.
    """
    _, items, config = _load(args)
    groups = clusters(items)
    if not args.head:
        pairs = overlaps(groups)
        if args.misread:
            print(render.format_misread(groups, pairs, unsound_generator_claims(items)))
            return 0
        print(
            render.format_clusters(
                groups,
                unsound_generator_claims(items),
                generator_defects(items, config.generator_paths),
                pairs,
            )
        )
        return 0

    item = find_item(items, args.head)
    if item is None:
        print(f"no item matching '{args.head}'")
        return 1
    if item.identifier in groups:
        print(render.format_cluster(groups[item.identifier]))
        return 0
    # A member resolves to the cluster above it. Where more than one generator
    # names it both are printed: `generators_explaining` already allows that,
    # and picking one of them here would be this package answering from a
    # partial read.
    heads = [groups[h.identifier] for h in generators_explaining(item.identifier, items)]
    if not heads:
        print(
            f"{item.identifier} carries no sound `root-cause-of:` and no generator names it, "
            f"so it is in no cluster"
        )
        return 1
    print("\n\n".join(render.format_cluster(cluster) for cluster in heads))
    return 0


def cmd_milestone(args: argparse.Namespace) -> int:
    _, items, _ = _load(args)
    groups = milestones(items)
    if not groups:
        print("no items are assigned to a milestone")
        return 0
    wanted = [groups[args.name]] if args.name and args.name in groups else list(groups.values())
    if args.name and args.name not in groups:
        print(f"no milestone named '{args.name}'")
        return 1
    for milestone in wanted:
        state = "complete" if milestone.is_complete else f"{len(milestone.outstanding)} outstanding"
        print(f"{milestone.name}: {len(milestone.done)}/{len(milestone.items)} done ({state})")
        for item in milestone.items:
            print(f"  [{render.progress_mark(item)}] {item.identifier} {item.title}")
    return 0


def _numbers_before_notes(
    directory: Path, ready: Readiness, root: Path, args: argparse.Namespace
) -> Readiness:
    """Write the `pr` each shipping closure is owed, while the notes can still use it.

    Exactly `_record_owed`'s reading, narrowed to the items about to ship:
    `closures_on_base` is the same call, so the cut and `docket record` cannot
    disagree about which number an item merged as. What differs is the moment.
    `record` runs after the cut and repairs the store alone; this runs before
    the render, which is the only point at which a bullet can be written
    correctly rather than repaired.

    The item files are written too, not only the objects the notes are built
    from. A cut that put the number in the notes and left the store owing it
    would trade one half of the same disagreement for the other, and `docket
    check`'s missing-`pr` advisory would still be counting these items.

    Never a refusal. A number the base cannot supply - a shallow clone whose
    history stops short of the merge, a closure that has not landed because it
    is closing on the release branch itself - leaves the bullet as it was, and
    `docket record` repairs it afterwards through `restate_references`. Holding
    the release for it would stop a cut over provenance that is one `git fetch`
    from recoverable, which is the wrong side to err on for the one command
    whose output is permanent.

    Measured before it was built: 128 of 853 bullets across 22 of this
    project's releases name no pull request, among them nine of `v0.4.22`'s
    fifteen and twelve of `v0.4.35`'s sixteen (`PL-W7WL`, filed four times from
    four separate cuts).
    """
    owed = {i.identifier: i.path for i in ready.shippable if not i.pr and i.path}
    inv = _invocation(args)
    # Under `--no-git`, or for a store git cannot address, there is no number
    # to read, and the bullet is left as it was for `docket record` to repair.
    if not owed or inv.git is None or not inv.tracked:
        return ready
    report = closures_on_base(root, owed, items_dir=inv.tracked, runner=inv.git)
    if not report.known:
        print(f"Declined to read which pull request each closure merged as: {report.declined}\n")
        return ready

    numbers = report.numbers
    verb = "would record" if args.dry_run else "recorded"
    shippable: list[Item] = []
    written = 0
    for item in ready.shippable:
        number = numbers.get(item.identifier)
        if item.pr or number is None:
            shippable.append(item)
            continue
        _write_pr(directory, item, str(number), args.dry_run)
        print(f"{item.identifier}: {verb} `pr: {number}`, so these notes can cite it")
        shippable.append(with_fields(item, pr=str(number)))
        written += 1

    # Said whether or not anything was written, for `PL-KX9N`'s reason: a
    # partially deepened clone answers for its newest closures and not for the
    # rest, so a run that recorded some numbers proves nothing about the others.
    unnamed = sorted(i for i in report.landed if i not in numbers)
    if unnamed and report.shallow:
        print(
            f"{len(unnamed)} shipping closure(s) record no `pr` and this checkout is a "
            f"shallow clone, so the merge that names the number can lie outside it. Their "
            f"bullets will cite the commit or nothing; `git fetch --unshallow origin` "
            f"before the cut is what lets them cite the pull request: {', '.join(unnamed)}"
        )
    if written or unnamed:
        print()
    return with_fields(ready, shippable=shippable)


def cmd_release(args: argparse.Namespace) -> int:
    """Cut a release from whatever is finished and has not shipped yet.

    Takes no list of items, on purpose. Requiring one would mean the release
    is only as complete as somebody's memory of what to put in it, and the
    store already knows exactly which finished work has not gone out.
    """
    directory, items, config = _load(args)
    root = _invocation(args).root
    git = _invocation(args).git
    current = read_version(root / config.version_file)
    # An interrupted cut is resumed, never cut around. The stamps go in one
    # file at a time and the notes are written after the whole loop, so a run
    # that dies inside it leaves work stamped with a release that has no
    # notes - and a plain re-run reads exactly those items as already shipped,
    # cuts the remainder under the same name and exits 0. Reclaiming them is
    # what makes the cut of a named version idempotent, which is the property
    # that holds however far the interrupted run got; `PL-1MKQ` carries the
    # observed case and why reordering the writes does not close it.
    #
    # The newest, in the store's pathological case of two. One run stamps one
    # name and the refusal below stops a second name being started while the
    # first is unfinished, so two can only arrive by hand - and the check
    # reports whichever this does not resume rather than leaving it silent.
    interrupted = unrecorded_milestones(items, notes_by_version(root), current)
    resuming = interrupted[-1] if interrupted else ""
    ready = readiness(items, current, config.minor_classes, resuming)

    if not ready.shippable:
        print(f"Nothing to release: no finished work since {current}.")
        return 0

    # Cutting a release on top of an untagged one extends a gap that cannot be
    # closed afterwards, so the refusal belongs here rather than in a reminder.
    # A dry run is allowed through with a warning: it exists to review the
    # notes and the bump, and withholding those would not make the tag appear.
    #
    # Unless the interrupted cut is the current version, which happens when it
    # got as far as its bump: `current` is then the release being finished
    # rather than one that shipped and wants a tag, and refusing on it would
    # block the only run that can write its notes.
    #
    # A git that will not say refuses too, in its own words (`PL-ZPDM`). This
    # read answered a silence with an empty set until then, and `is_untagged`
    # holds a project with no tags to nothing - so the gate skipped itself
    # whenever git failed, silently, which is the permissive direction on the
    # one check whose gap cannot be repaired afterwards.
    if git is not None and resuming.lstrip("v") != current.strip().lstrip("v"):
        existing = tags(root, runner=git)
        refusal = ""
        if not existing.known:
            refusal = _unreadable_tags_refusal(current, existing.declined)
        elif is_untagged(current, existing.names):
            refusal = _untagged_warning(current)
        if refusal:
            print(refusal)
            if not args.dry_run:
                return 1
            print()

    if resuming and args.version and args.version.strip().lstrip("v") != resuming.lstrip("v"):
        print(_unfinished_cut_refusal(resuming, ready, args.version.strip().lstrip("v")))
        return 1

    # A resumed cut needs no version named: the interrupted run named it, and
    # it is stamped on the items this one is picking back up.
    if args.version is None and not resuming and config.version_policy == "manual":
        print(f"{len(ready.shippable)} finished item(s) since {current}:")
        for item in ready.shippable:
            print(f"  {item.identifier} {item.title}")
        if ready.completed_features:
            print(f"Completes: {', '.join(ready.completed_features)}")
        print(
            f"\nThis project chooses versions by the capability boundary a release "
            f"crosses, not by incrementing. Name the version to cut it "
            f"(mechanical guess, for reference only: {ready.suggested_version})."
        )
        return 1

    version = (args.version or resuming or ready.suggested_version).lstrip("v")
    name = f"v{version}"

    # The one change no in-flight guard can see, because it carries no item id
    # by design (`PL-66FP`). Two questions, in the order their answers are
    # certain in: what the default branch already holds is a merge that has
    # happened, and what a ref is carrying is a claim that may yet be
    # abandoned. A dry run is allowed through either with the warning, on the
    # same reasoning as the untagged one above: it writes nothing, and
    # withholding the notes would not un-ship what already shipped.
    #
    # **The fetch is the part without which neither question is worth asking.**
    # The session that lost the v0.3.7 race cut from a checkout that did not
    # yet hold an item merged eight minutes before the winning release landed,
    # so every ref it could read was older than the collision it was in. This
    # is the rarest command here and the most expensive to get wrong, which is
    # what makes one network read proportionate where the digest's would not be.
    if git is not None:
        if not args.no_fetch:
            fetch_remote(root, runner=git)
        base = released_on_base(
            root, version_file=config.version_file, notes_dir=NOTES_DIR, runner=git
        )
        landed = (
            already_released(version, base.notes, base.version, config.version_file)
            if base.known
            else []
        )
        if landed:
            print(_duplicate_warning(name, base.base, landed))
            if not args.dry_run:
                return 1
            print()
        else:
            # **Both guards refuse on a read they could not complete**
            # (`PL-Q9Z1`). Each is looking for evidence that somebody else is
            # already cutting, and an absence of evidence is what a git that did
            # not answer produces - so proceeding on one is the v0.3.7
            # collision arriving through the guard built to stop it. This is the
            # rarest command here and the most expensive to get wrong, which is
            # what makes refusing the right side to err on.
            cuts = cuts_in_flight(root, notes_dir=NOTES_DIR, on_base=base.notes, runner=git)
            holders = [branch for branch in cuts.branches if not branch.mine]
            unread = "" if base.known else _base_unread(base.base)
            if holders:
                print(_parallel_cut_warning(holders))
                if not args.dry_run:
                    return 1
                print()
            elif unread or not cuts.known:
                print(_unreadable_cut_warning(unread or cuts.declined))
                if not args.dry_run:
                    return 1
                print()

    # **The numbers the base already knows, written on before the notes quote
    # them rather than after.** A closure lands with an empty `pr` by design -
    # the number does not exist when the commit that closes the item is made
    # (`PL-QS72`) - and the only thing that writes it is `docket record`, which
    # the documented cut runs *after* `make release`. So an item that merged
    # between the previous cut and this one shipped a bullet naming no pull
    # request, and no supported command could put one there afterwards: this
    # command answers `Nothing to release` once the version is cut, correctly,
    # because re-cutting a shipped release is what leaves two sets of notes
    # disagreeing about the same items (`PL-1MKQ`).
    #
    # Swapping the documented order was the other candidate and is weaker: it
    # removes nothing, it only asks every future cut to remember. This runs the
    # same reading `record` does, off the fetch the guards above have paid for
    # already, so it costs one history read and cannot be forgotten.
    ready = _numbers_before_notes(directory, ready, root, args)

    milestone = milestones(stamp(ready.shippable, name))[name]
    notes = release_notes(milestone, args.today or date.today())

    if resuming:
        already = sum(1 for item in ready.shippable if item.milestone)
        print(
            f"Resuming an interrupted cut of {resuming}: {already} of these "
            f"{len(ready.shippable)} item(s) were stamped by the run that stopped, and "
            f"{NOTES_DIR}/{notes_name(resuming)} was never written.\n"
        )
    print(f"{len(ready.shippable)} finished item(s) since {current}.")
    if ready.completed_features:
        print(f"Completes: {', '.join(ready.completed_features)}")
    if ready.partial_features:
        print(f"Partially advances: {', '.join(ready.partial_features)}")
    print(f"{current} -> {version}\n")
    print(notes)

    if args.dry_run:
        print("Dry run: nothing was changed.")
        return 0

    # Prove the bump before writing anything, so a version file the bump
    # rejects costs an exit code rather than a stamped store claiming a release
    # that never happened, with nothing recording which stamps to unpick.
    #
    # This settles the write that is *rejected*. The write that is
    # interrupted - a lost container part way through the loop below - is
    # settled by the resume above instead, because no ordering of these three
    # writes prevents it: the stamps go in a file at a time (`PL-1MKQ`).
    try:
        bump = prepare_bump(root / config.version_file, version)
    except (OSError, ValueError) as error:
        print(f"Cannot bump {config.version_file}, so nothing was stamped and nothing was written:")
        print(f"  {error}")
        return 1

    for item in stamp(ready.shippable, name):
        # `milestone:` is a field write, so it keeps the file it found, exactly
        # as `pr:` does. A cut stamps a whole batch at once, so one drifted name
        # among them would put a rename nobody asked for into the commit the
        # release tag points at (`PL-LBR6`).
        rewrite_item(directory, item)
    previous = bump.write()
    notes_path = root / NOTES_DIR / notes_name(version)
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text(notes, encoding="utf-8")
    print(f"Bumped {previous} -> {version} in {config.version_file}")
    print(f"Wrote {notes_path.relative_to(root)} and stamped {len(ready.shippable)} item(s)")
    print()
    print(_hand_off(root, config, name))
    return 0


def _hand_off(root: Path, config: Config, name: str) -> str:
    """Say where the mechanical half ends, what is stale, and what comes next.

    A release stops here on purpose. The roadmap's version row and baseline
    section say what the release was *for*, which is a judgment about the work
    rather than a fact about the store, so the sequence ends where the
    judgment starts. What it must not do is end silently: the alternative this
    replaces ran the project check straight into a failure caused by the edits
    nobody had been asked for yet, with the tree half updated - which teaches a
    maintainer to read a red check as the normal end of a release.
    """
    lines = ["Stopping here: the rest is prose, and the roadmap says what this release was for."]

    roadmap = root / config.roadmap_file
    if roadmap.is_file():
        stale = outstanding_roadmap_edits(roadmap.read_text(encoding="utf-8"), name)
        if stale:
            lines.append("")
            lines.append(f"Stale in {config.roadmap_file}, and owed by hand:")
            lines.extend(f"  - {statement}" for statement in stale)
        else:
            lines.append("")
            lines.append(f"{config.roadmap_file} already reads as {name}; nothing is owed there.")

    lines.append("")
    lines.append("Then:")
    lines.append(f"  {config.check_command}")
    lines.append("  review the diff and commit")
    # A bare token, never an angle-bracketed placeholder: a shell reads the
    # opening bracket as input redirection from a file named `merge`, so pasting
    # the line answered "no such file or directory: merge" and never reached git
    # at all - naming neither git, nor the tag, nor the thing that is missing.
    # `MERGE_COMMIT` fails as `fatal: Failed to resolve 'MERGE_COMMIT'`, which
    # does (`PL-HKF4`).
    lines.append(f'  git tag -a {name} MERGE_COMMIT -m "{name}"   # the merge commit on main')
    lines.append(f"  git push origin {name}")
    return "\n".join(lines)


def _unfinished_cut_refusal(resuming: str, ready: Readiness, requested: str) -> str:
    """Say which cut is unfinished, and that re-running it is the whole repair.

    Refused rather than warned, because cutting a second number over an
    unfinished first one is how one interrupted release becomes two: both
    stamp `milestone:` onto work the other claims, and the notes each writes
    are then permanently wrong about the same items. The version is the one
    thing this cannot infer past - the operator typed one and the store holds
    another - so it is also the only thing to ask.

    The command rather than the intent, for the reason `_untagged_warning`
    gives: a session told what to intend has to reconstruct how, at the moment
    it is trying to do something else.
    """
    already = sum(1 for item in ready.shippable if item.milestone)
    return "\n".join(
        [
            f"A cut of {resuming} was interrupted and has not been finished: {already} "
            f"item(s) carry `milestone: {resuming}` and",
            f"{NOTES_DIR}/{notes_name(resuming)} was never written. Cutting v{requested} "
            "on top would stamp a second release",
            "onto work the first one already claims, and neither set of notes could then be right.",
            "",
            f"Finish {resuming} first - the re-run picks the stamped items back up, so it "
            f"cuts all {len(ready.shippable)}:",
            "",
            f"  make release VERSION={resuming.lstrip('v')}",
        ]
    )


def _duplicate_warning(name: str, base: str, evidence: list[str]) -> str:
    """Say which release is already out, on what evidence, and how to move onto it.

    The evidence rather than the verdict alone, because the reader's next
    question is "says who" and the answer is two files they can go and look
    at. And the commands rather than "rebase first", for the reason
    `_untagged_warning` gives: a session told what to intend has to
    reconstruct how, at the moment it is trying to do something else.

    `git merge` rather than a rebase: the branch is pushed by the time another
    session could have merged past it, and rewriting a pushed branch is what
    `CLAUDE.md` refuses.
    """
    return "\n".join(
        [
            f"{name} is already released on {base}, so cutting it here would write a",
            "second copy of a release that has shipped:",
            "",
            *(f"  {statement}" for statement in evidence),
            "",
            "Another session cut it. Take what shipped, then ask what is left:",
            "",
            "  git fetch origin",
            f"  git merge {base}   # take {base}'s side on the version, lock and roadmap files",
            "  bin/docket release --dry-run",
        ]
    )


def _base_unread(base: str) -> str:
    """Why the default branch could not be read, for the release guards to quote."""
    return f"git would not say what {base or 'the default branch'} has already released"


def _unreadable_cut_warning(reason: str) -> str:
    """Refuse a cut whose duplicate-release guards could not be run.

    The guards above look for *evidence* that another session is already
    cutting, so their clean answer and their unread answer are the same shape -
    nothing found - and only the read itself can tell them apart (`PL-Q9Z1`).
    Cutting anyway is how v0.3.7 was cut twice (`PL-66FP`): the second cut
    stamps `milestone:` onto items the first already shipped, and the resolution
    is discarding one of them.
    """
    return "\n".join(
        [
            f"Cannot check whether another session is already cutting: {reason}.",
            "",
            "Both duplicate-release guards read git, and neither can tell a clean answer",
            "from one it never got - so this refuses rather than cutting on silence.",
            "",
            "  git fetch origin",
            "",
            "then run this again. `--dry-run` prints the notes without the guard.",
        ]
    )


def _parallel_cut_warning(holders: list[BranchCut]) -> str:
    """Say which ref is cutting what, when it did, and both ways out of it.

    Every unmerged cut rather than only one of the version being cut. Two
    concurrent releases under *different* numbers is the worse case, not the
    safer one: both stamp `milestone:` onto an overlapping set of items, so
    whichever merges second claims work the first already shipped.

    The date because it is the only thing separating a live session from a
    branch nobody will merge, and this reports rather than decides, the way
    `flight` and `stranded` do. Both remedies for the same reason - waiting is
    right for the first case and useless for the second, and the reader is the
    one who can tell them apart.
    """
    lines = []
    for branch in holders:
        versions = ", ".join(f"v{version}" for version in branch.versions)
        when = f", cut {branch.cut.isoformat()}" if branch.cut else ""
        lines.append(f"  {branch.ref} is cutting {versions}{when}")
    return "\n".join(
        [
            "A release is already being cut on a branch nothing has merged:",
            "",
            *lines,
            "",
            "Two cuts cannot both land - the second is resolved by discarding it, which",
            "is what happened to v0.3.7. Wait for it to merge, then:",
            "",
            "  git fetch origin",
            "  git merge origin/main",
            "  bin/docket release --dry-run",
            "",
            "If that branch is abandoned, recover what only it holds before dropping it:",
            "",
            "  bin/docket stranded",
        ]
    )


def _untagged_warning(version: str) -> str:
    """Say which tag is missing and give the commands, not the instruction.

    Asking someone to "tag v0.2.5" makes them go and reconstruct three
    commands at the moment they are trying to do something else.
    """
    name = f"v{version.lstrip('v')}"
    return "\n".join(
        [
            f"{name} shipped and carries no tag, so no commit in its span can be",
            "mapped to the release it went out in. That gap cannot be closed later",
            "with any confidence. Tag it first:",
            "",
            f'  git log --oneline --grep="Release {name}"   # find the commit',
            f'  git tag -a {name} RELEASE_COMMIT -m "{name}"   # the commit found above',
            f"  git push origin {name}",
        ]
    )


def _unreadable_tags_refusal(version: str, declined: str) -> str:
    """Refuse the cut where git would not say whether the last release is tagged.

    `_untagged_warning` is the wrong message here for the reason it is the
    right one there: it names a specific fact - this version carries no tag -
    and sends the operator to run three commands, the first of which may be
    pushing a tag that already exists. What is true is weaker and worth saying
    in its own words: nothing was read, so the gate did not run.

    Refusing rather than warning through, because the two costs are not
    comparable. A false refusal costs one re-run and prints exactly which
    question went unanswered; proceeding extends a gap `git describe
    --contains` can never close afterwards, on a cut nobody would think to
    re-examine. `--no-git` is the escape hatch for a checkout that genuinely
    has no git to ask, and it is named here rather than left to be found - as
    a flag rather than a command line, because the version being cut is not
    resolved until further down and a printed command carrying the wrong one
    is worse than no command at all.
    """
    name = f"v{version.lstrip('v')}"
    return "\n".join(
        [
            f"Cannot tell whether {name} is tagged, so the tag gate did not run:",
            f"{declined}.",
            "",
            f"Cutting on top of an untagged {name} leaves a gap that cannot be closed",
            "later with any confidence, so this refuses rather than assuming the tag",
            "is there. Check what git says, then re-run the cut:",
            "",
            "  git tag --list",
            "",
            "Where this checkout has no git to ask at all, re-run the same cut with",
            "`--no-git`, which turns this gate off along with the other git reads.",
        ]
    )


def cmd_delegable(args: argparse.Namespace) -> int:
    """Everything a worker may take, with the command that proves each one."""
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    print(render.format_delegable(report, _flight(args), config.protected_paths, config.gate_paths))
    return 0


def _guessed_base_refusal() -> str:
    """Refuse the audit where no candidate default branch resolved.

    The commission audit is a claim about what a branch changed *against a
    base*, so a base nobody established makes every one of its findings
    unfounded - and not visibly so. Measured 2026-09-22 on a checkout with no
    default branch: the audit reported `fatal: ambiguous argument
    'main...HEAD'...` as a path outside the commission and missed both files
    the branch had actually changed, because `changed_paths` read git's error
    text as paths.

    `changed_paths` now declines a base git cannot resolve (`PL-9RFP`), so
    without this refusal the audit would say it could not read the diff. The
    refusal still covers what that decline cannot. The first case is a guess
    that *resolves*: the local `main`, reached because `origin/main` went
    unread. Git answers that without complaint, against the wrong base. The
    second is a guess that does not resolve, where this names the one flag
    that fixes it.

    Refusing rather than reporting, because the direction is the one that
    cannot be recovered from. A refusal costs one re-run and says which ref to
    supply; a report names paths that do not exist while passing over the ones
    that do, on the check whose whole job is to certify a branch's scope.
    """
    return "\n".join(
        [
            "Cannot verify: no candidate default branch resolved in this checkout,",
            "so there is no base to audit the commission against "
            f"(tried {', '.join(DEFAULT_BRANCHES)}).",
            "",
            "Every finding here is a claim about what this branch changed relative to",
            "a base, so a guessed one would report paths that do not exist and pass",
            "over the ones that do. Name the base explicitly and re-run:",
            "",
            "  bin/docket verify <ID> --base <ref>",
            "",
            "`git fetch origin` first where the remote-tracking ref is merely missing.",
        ]
    )


def cmd_verify(args: argparse.Namespace) -> int:
    """Prove each item's work stayed inside the commission it was given.

    Exits non-zero when any check fails, so it can gate a worker's push as
    well as inform a reviewer. The reviewer still reads the new code; what
    this removes is the need to read the *whole diff* to find out whether
    there is any new code they were not expecting.

    Several ids may be given, because that is how delegated work comes back:
    one branch, one commit per item. Each item's own command still runs, so
    four can be accepted and the fifth rejected, but the project's own check
    runs once for the batch - it proves a property of the tree, and proving it
    six times over is the difference between a command a reviewer runs and one
    they learn to skip.

    `--self` says the caller is auditing its own branch rather than reviewing a
    delegated one, which is a different question and was answered wrongly
    before: four of the guards fire by construction on the path the project's
    own close-out prescribes. `verify_item`'s docstring carries which four and
    why. The integrity checks are unaffected either way.
    """
    _, items, config = _load(args)
    wanted = []
    for identifier in args.item:
        item = find_item(items, identifier)
        if item is None:
            print(f"no item matching '{identifier}'")
            return 1
        wanted.append(item)
    inv = _invocation(args)
    if inv.git is None:
        # A commission audit is a diff against a base, so with git asked
        # nothing there is no answer - and an audit must not pass unread.
        print("verify: `--no-git` asks git nothing, and the audit is a diff against a base")
        return 1
    root = inv.root
    base = args.base or default_base(root, runner=inv.git)
    if not resolved(base):
        print(_guessed_base_refusal())
        return 1
    reports = verify_batch(root, wanted, config, base, self_audit=args.self_audit)
    print("\n\n".join(report.describe() for report in reports))
    if len(reports) > 1:
        print(f"\n{config.check_command} ran once for the batch; it proves the tree, not an item.")
    if args.self_audit:
        print(
            "\nSelf-audit: the four commission checks reported rather than refused. "
            "A delegated review runs without `--self` and refuses on any of them."
        )
    return 0 if all(report.passed for report in reports) else 1


def cmd_wave(args: argparse.Namespace) -> int:
    """Which beat of the planning cadence is due, computed from the plan itself.

    The queue nags every session; the roadmap nags never, so "what next" gets
    answered from whatever ranks highest in the store - a question above that
    ranking's altitude. This answers the other one, and answers it the only way
    that survives a session with no memory: by reading the files.

    Exits non-zero when it cannot compute an answer - no roadmap, no timeline,
    a gate naming an item the store does not hold, or a plan whose numbering
    the project has stepped past - because a beat the tool is unsure of is
    worth less than an obvious failure to produce one.
    """
    _, items, config = _load(args)
    root = _invocation(args).root
    roadmap = root / config.roadmap_file
    if not roadmap.is_file():
        print(f"no {config.roadmap_file} to read: there is no plan to report a position on")
        return 1

    plan = wave(
        roadmap.read_text(encoding="utf-8"),
        read_version(root / config.version_file),
        frozenset(item.identifier for item in items if not item.is_open),
        frozenset(item.identifier for item in items),
        {item.identifier: item.blocked_by for item in items},
    )
    print(render.format_wave(plan, {item.identifier: item for item in items}))
    if (
        plan.step is None
        or plan.problems
        or plan.stale
        or (plan.gate is not None and plan.gate.unknown_ids)
    ):
        return 1
    return 0


def cmd_trend(args: argparse.Namespace) -> int:
    """How the balance between the two halves of the project has moved.

    The one command here that looks backwards. Everything else describes the
    project as it stands, so "is the apparatus taking more of the work than it
    used to" had no answer short of a session reading the store and the history
    and classifying both by hand.

    Refuses without `workflow_paths`, exactly as the lane arguments to `next`
    do and for the same reason: with no boundary declared there are no halves,
    and answering anyway would mean drawing the line on the project's behalf
    and presenting the result as its own.

    It reads git without fetching. Every question here is about this
    repository's own history, which a fetch does not change - unlike `branch`
    and `stranded`, whose findings are claims about what the *base* does not
    hold.
    """
    _, items, config = _load(args)
    if not config.workflow_paths:
        print(
            f"Cannot answer: no `workflow_paths` are declared in {CONFIG_NAME}, so "
            "nothing separates the apparatus from the product. Declaring them is "
            "what makes this - and `docket next product` / `docket next workflow` - "
            "answerable."
        )
        return 1
    inv = _invocation(args)
    history = Churn() if inv.git is None else churn(inv.root, runner=inv.git)
    report = analyze_trend(items, history, config, by=args.by, today=args.today or date.today())
    if history.declined:
        # A measurement with an unread stretch of history is not the measurement
        # it looks like, and the shape of a trend is exactly what a missing
        # stretch changes (`PL-Q9Z1`).
        print(f"Lines written: partial - {history.declined}.")
        print()
    print(render.format_trend(report))
    return 0


def cmd_stranded(args: argparse.Namespace) -> int:
    """Work that exists on a branch and nowhere this checkout can otherwise see.

    Two reads, printed together because a reader asking "is anything only on a
    branch" means both and would not think to run two commands. `stranded`
    answers it for items - which ids no other tree holds, and which of the ids
    the base *does* hold have a copy on some ref that is ahead of it
    (`PL-KSCW`); `orphaned` answers it for everything else, by content across
    the base, which is the half that was missing while a dropped commit
    touching a skill or `src/` went unreported (`PL-3D2M`).

    Exits zero whether or not it finds any: an item on a branch that is still
    being worked is the normal case, and the command cannot tell that from an
    item on a branch nobody will merge. Reporting is the whole job; deciding
    which of the two a branch is remains the reader's.

    **This fetches, and the library functions it calls do not**, exactly as
    `cmd_branch` does and for a sharper reason than that one has. Every finding
    below is a claim about what the default branch does *not* hold, so a base
    nobody refreshed reports whatever merged since the last fetch as lost - and
    the recovery this command hands over is a `git checkout` that overwrites
    the newer copy with the older one. That is not the hazard in theory: it
    happened on 2026-09-05, eight minutes after `#325` merged (`PL-KBFN`,
    `PL-39B7`). `--no-fetch` is for the caller that already fetched and for a
    checkout with no network; the report says which of the two happened.

    A stale base is not the only way that recovery went wrong, and the other
    way is now closed rather than caveated: a `git checkout` is printed only
    for an item the base does not hold at all. An item it holds is handed a
    diff to read, and a branch holding a copy the base is ahead of is not
    listed at all (`PL-MBTZ`).
    """
    _, items, _ = _load(args)
    inv = _invocation(args)
    # Before the fetch, because the fetch is the network: `stranded --no-git`
    # went there before it looked at the flag.
    if inv.git is None:
        print(NO_GIT)
        return 0
    if not args.no_fetch:
        fetch_remote(inv.root, runner=inv.git)
    report = _stranded(items, args, fetched=not args.no_fetch)
    if report is None:
        print(
            "the store is not below the repository root, so git cannot be asked "
            "which items exist only on a branch"
        )
        return 0
    print(render.format_stranded(report))
    left = _orphaned(args)
    if left is not None:
        print()
        print(render.format_orphaned(left))
    return 0


def cmd_branch(args: argparse.Namespace) -> int:
    """Where this branch stands against the default branch, asked again.

    The session-start hook asked it once, at session start, on a condition that
    develops during a session: another session merges while this one is still
    discussing what to build, and the base goes stale under it. Nothing looked
    again, so it surfaced at push time as a merge conflict.

    **This fetches, and the library function it calls does not.** The decision
    has to stay answerable from a bare checkout with no network, so
    `branch_state` reads only what the checkout holds - but a command whose one
    question is "has the base moved" would answer "current" from a ref nobody
    refreshed, which is a confident wrong answer of exactly the kind the rest
    of this package refuses to give. So the command refreshes first and says
    which of the two happened. `--no-fetch` is for the caller that already
    fetched - the hook among them - and for a checkout with no network.
    """
    inv = _invocation(args)
    if inv.git is None:
        # `--brief` and `--if-stale` print into something a session reads
        # whether or not it asked, so they say nothing, as for an absent base.
        if not (args.brief or args.if_stale):
            print(NO_GIT)
        return 0
    if not args.no_fetch:
        fetch_remote(inv.root, runner=inv.git)
    state = branch_state(inv.root, fetched=not args.no_fetch, runner=inv.git)
    if state.absent and (args.brief or args.if_stale):
        # Nothing to compare against, and both callers here are printing into
        # something a session reads whether or not it asked: a line explaining
        # why there is no position is worth having when a person asks, and is
        # noise when nobody did.
        return 0
    if args.if_stale and state.disposition == CURRENT:
        return 0
    print(render.format_branch_state(state, None if args.brief else _flight(args)))
    return 0


#: How long `open_pull_requests_command` is given. Short, because this sits in
#: front of an answer the command already has without it: the pull-request half
#: sharpens the report and is never what the report is for, so a slow forge
#: costs a reader seconds and then gets the unasked reading.
OPEN_LOOKUP_TIMEOUT = 8.0


def _open_pull_requests(
    args: argparse.Namespace, root: Path, config: Config
) -> Callable[[], Mapping[str, int | None] | None] | None:
    """A way to ask which branches have a pull request open, or None if there is none.

    A callable rather than an answer, so that a command with no branch to ask
    about reaches nothing at all.

    The answer maps each branch to its pull request's number, where the command
    printed one after the name - `claude/pl-k7qx-thing 920` - and to `None`
    where it printed the name alone, which is the whole of the contract a
    project's own command owes (`PL-7TVT`). A branch name cannot hold a space,
    so the first field is the name however the line continues.

    **Every way this can fail is a skip, never a failure**, which is the
    contract `tools/pr_title_check.py --discover` already holds to: no command
    configured, no token, no network, a forge that refused, a timeout, a
    command that is not there. `flight` has to answer from a bare or offline
    checkout, and a report that failed when it could not look would be worse
    than the gap it closes. What must never happen is a skip reading as
    "asked, and nothing is open" - it cannot here, because `None` reaches
    `SettledReport.asked` and the wording changes with it.
    """
    command = config.open_pull_requests_command
    if args.no_remote or not command:
        return None

    def ask() -> Mapping[str, int | None] | None:
        try:
            done = subprocess.run(
                shlex.split(command),
                cwd=root,
                capture_output=True,
                text=True,
                timeout=OPEN_LOOKUP_TIMEOUT,
                check=False,
            )
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
        if done.returncode != 0:
            return None
        found: dict[str, int | None] = {}
        for line in done.stdout.splitlines():
            fields = line.split()
            if not fields:
                continue
            number = fields[1].lstrip("#") if len(fields) > 1 else ""
            found.setdefault(fields[0], int(number) if number.isdigit() else None)
        return found

    return ask


def cmd_flight(args: argparse.Namespace) -> int:
    """Which items are being worked on a branch, and how long since each moved.

    Exits zero whether or not it finds any, for the reason `stranded` does:
    an unmerged branch is a live session or abandoned work, the command cannot
    tell which, and reporting is the whole job.

    **Except for the branches that have answered it themselves** (`PL-Q664`).
    `settled_branches` names the refs whose every claimed item is closed in
    their own copy and which no pull request is open on, and those move out of
    the list the age is meant to separate. It is asked here rather than inside
    `branches_in_flight` because that read is on the hot path of `next`,
    `show`, `list`, `triage` and the digest, and this one is wanted by the
    command whose whole question it is.
    """
    inv = _invocation(args)
    if inv.git is None:
        print(NO_GIT)
        return 0
    report = _flight(args)
    # One question to the forge for both readings, asked wherever a row exists:
    # the settled rows and the pull-request clause on every live row ask it the
    # same thing (`PL-7TVT`), and a report with no row asks nothing.
    lookup = _open_pull_requests(args, inv.root, inv.config)
    answer = lookup() if lookup is not None and report.branches else None
    opened = None if lookup is None else (lambda: answer)
    settled = settled_branches(
        inv.root, report, opened=opened, items_dir=inv.tracked, runner=inv.git
    )
    reviews = open_pull_requests(inv.root, report, opened=opened, runner=inv.git)
    print(render.format_flight(report, _now(args), settled, reviews))
    return 0


def _instant(text: str) -> datetime:
    """An ISO 8601 instant carrying its offset, for `--now`.

    A value without one is refused rather than read as UTC or as local time:
    an age is a subtraction, and a reference that means two different instants
    on two machines is the error `PL-3QM9` was.
    """
    value = datetime.fromisoformat(text)
    if value.tzinfo is None:
        raise argparse.ArgumentTypeError(f"{text!r} carries no UTC offset, e.g. +00:00")
    return value


def _now(args: argparse.Namespace) -> datetime:
    """The instant a branch's age is measured to.

    `--now` where given, and the clock where nothing is. `--today` alone names
    a day and no time, and is read as the last instant of it in UTC: a commit
    whose UTC date is earlier then ages by exactly the whole days between the
    two dates, which is what every age read under `--today` said before ages
    were measured in elapsed time (`PL-3QM9`), so a caller that states only a
    date is told nothing different about any earlier day.
    """
    now: datetime | None = getattr(args, "now", None)
    if now is not None:
        return now
    today: date | None = getattr(args, "today", None)
    if today is not None:
        return datetime.combine(today, time.max, tzinfo=UTC)
    return datetime.now(UTC)


def cmd_claim(args: argparse.Namespace) -> int:
    """Record that this branch holds the items named: `claiming.claim`, which says how.

    Exit 3 means another branch holds one of them first, and exit 4 that the
    claim was written but could not be pushed, so only this checkout can see it.
    Neither is a failure of the command; each is a different next step.
    """
    inv = _invocation(args)
    if inv.git is None:
        print("claim: `--no-git` asks git nothing, and a claim is a commit")
        return claiming.USAGE
    if not inv.tracked:
        print("claim: the store is not below the repository root, so no branch can hold its items")
        return claiming.USAGE
    written = claiming.claim(
        inv.root,
        args.ids,
        items_dir=inv.tracked,
        now=_now(args),
        over=args.over or "",
        reason=args.reason or "",
        trailers=args.trailer,
        fetch=not args.no_fetch,
        runner=inv.git,
    )
    for line in written.lines:
        print(line)
    return written.code


def cmd_yield(args: argparse.Namespace) -> int:
    """End this branch's claim on the items named without closing them."""
    inv = _invocation(args)
    if inv.git is None:
        print("yield: `--no-git` asks git nothing, and a yield is a commit")
        return claiming.USAGE
    if not inv.tracked:
        print("yield: the store is not below the repository root, so no branch can hold its items")
        return claiming.USAGE
    written = claiming.yield_claims(
        inv.root,
        args.ids,
        items_dir=inv.tracked,
        now=_now(args),
        trailers=args.trailer,
        runner=inv.git,
    )
    for line in written.lines:
        print(line)
    return written.code


def cmd_arm(args: argparse.Namespace) -> int:
    """Whether this branch's pull request may be armed: `arming.arm`, which says how.

    Exit 0 is `arm`, 1 is `hold` or `behind N` - the line printed says which -
    and 2 is `unknown`: something the answer rests on could not be read.
    """
    inv = _invocation(args)
    if inv.git is None:
        print("unknown - `--no-git` asks git nothing, and the answer is read from git")
        return arming.EXIT[arming.UNKNOWN]
    if not inv.tracked:
        print(
            "unknown - the store is not below the repository root, so no path can be told "
            "apart from it"
        )
        return arming.EXIT[arming.UNKNOWN]
    verdict = arming.arm(
        inv.root, items_dir=inv.tracked, now=_now(args), fetch=not args.no_fetch, runner=inv.git
    )
    for line in verdict.lines:
        print(line)
    return verdict.code


def cmd_record(args: argparse.Namespace) -> int:
    """Write a pull request number onto the items its merge commit closed.

    This is the write half of what `_check_closures` detects. The number does
    not exist when the closure is committed - that is why the closure travels
    with its work and the item lands with an empty `pr` (`PL-QS72`) - so
    something has to supply it afterwards. Until now that something was a
    session reading an advisory and retyping the number by hand, which cost a
    commit and usually a pull request of its own on every item that closed,
    turned `#229` and `#230` into duplicates of each other (`PL-QTSB`), and
    left `main` red whenever the squash subject named no id at all
    (`PL-2XTF`). None of that is judgment. The number is in the merge event,
    and this writes it.

    Takes the number rather than deriving it, which is the whole point: the
    caller that has it - the merge-time job, handed it by the event that fired
    it - needs no subject parsing and so cannot be defeated by a subject.
    `closed_by` supplies the other half, which is what the commit closed, and
    that is a tree comparison rather than a guess.

    An item already carrying a *different* number is refused rather than
    overwritten. Two numbers for one closure means one of them is wrong, and
    which is not something this can know; a wrong provenance recorded
    confidently is worse than the missing one this exists to supply.
    """
    directory, items, _ = _load(args)
    inv = _invocation(args)
    root, tracked = inv.root, inv.tracked
    if inv.git is None:
        print("record: `--no-git` asks git nothing, and only git can say what a merge closed")
        return 2
    if not tracked:
        print("record: the store is not below the repository root, so git cannot say what closed")
        return 2
    if args.number is None:
        if args.merge is not None:
            print("record: `--merge` names one commit, so it needs the number that merge is")
            return 2
        return _record_owed(directory, items, root, tracked, args)
    if args.number < 1:
        print(f"record: #{args.number} is not a pull request number")
        return 2

    merge = args.merge or "HEAD"
    report = closed_by(merge, root, items_dir=tracked, runner=inv.git)
    if not report.known:
        print(f"record: declined to read {report.declined}")
        return 2

    number = str(args.number)
    known = {item.identifier: item for item in items}
    written: list[str] = []
    unchanged: list[str] = []
    absent: list[str] = []
    conflicting: list[tuple[str, str]] = []
    for identifier, _path in report.closed:
        item = known.get(identifier)
        if item is None:
            absent.append(identifier)
        elif item.pr == number:
            unchanged.append(identifier)
        elif item.pr:
            conflicting.append((identifier, item.pr))
        else:
            _write_pr(directory, item, number, args.dry_run)
            written.append(identifier)

    verb = "would record" if args.dry_run else "recorded"
    for identifier in written:
        print(f"{identifier}: {verb} `pr: {number}`")
    for identifier in unchanged:
        print(f"{identifier}: already records `pr: {number}`; nothing to write")
    for identifier in absent:
        print(f"{identifier}: closed by `{merge}` but no longer in the store; nothing written")
    if not report.closed:
        print(f"`{merge}` closed no item, so #{number} is owed to nothing")
    for identifier, existing in conflicting:
        print(
            f"{identifier}: closed by `{merge}`, which is #{number}, but the item "
            f"records `pr: {existing}`. One of the two is wrong and this cannot tell "
            f"which, so neither was written."
        )
    return 1 if conflicting else 0


def _record_owed(
    directory: Path, items: Sequence[Item], root: Path, tracked: str, args: argparse.Namespace
) -> int:
    """Write every `pr` the default base is owed and can supply, in one pass.

    The normal form, and the one `make fix` runs. It asks exactly the question
    `check` already asks - which landed closures record no `pr`, and which
    number the base names for each - and writes the answer instead of printing
    it. The two cannot disagree, because there is only one reading:
    `closures_on_base` is the same call `cmd_check` makes.

    No `--merge`, because there is no one merge. A session that has been open a
    while may be owed numbers from several, and taking them from the base
    rather than from a commit is what lets the write ride whatever commit the
    session is about to make - which is the point. The field stops costing a
    commit of its own, which is what it cost when a session had to read an
    advisory and compose one (`PL-WTQR`, `PL-N5WZ`).

    A closure the base names no number for is left alone, and left to `check` -
    the command that decides whether that is provenance lost, a decline, or a
    truncated checkout. Writing nothing there is what makes this safe to run
    unattended.

    Which leaves the one case a session can act on itself, and it is the common
    one: an agent container clones `--depth 1`, so the commit that would name
    the number is usually outside the checkout entirely. That is a fetch away
    rather than lost, and saying only that no number was found sends a session
    to `check` for an answer it already has. So the depth is named, with the
    fetch that settles it. It is named whether or not anything was written,
    because a partially deepened clone answers for its newest closures and not
    for the rest (`PL-KX9N`).
    """
    known = {item.identifier: item for item in items}
    owed = {i.identifier: i.path for i in items if i.status == "done" and not i.pr and i.path}
    if not owed:
        print("record: every closure already records its pull request")
        _restate_notes(root, known, args.dry_run)
        return 0
    report = closures_on_base(root, owed, items_dir=tracked, runner=_invocation(args).git)
    if not report.known:
        print(f"record: declined to read {report.declined}")
        return 2

    numbers = report.numbers
    verb = "would record" if args.dry_run else "recorded"
    written = 0
    for identifier in sorted(report.landed):
        number = numbers.get(identifier)
        item = known.get(identifier)
        if number is None or item is None:
            continue
        _write_pr(directory, item, str(number), args.dry_run)
        print(f"{identifier}: {verb} `pr: {number}`")
        # The notes pass below reads this map, so the number has to be on it:
        # an item that is owed a `pr` *and* has already shipped is the case
        # where one run of this command repairs both halves, and it is exactly
        # the case a cut interrupted by a missing number leaves behind.
        known[identifier] = with_fields(item, pr=str(number))
        written += 1
    unnamed = sorted(identifier for identifier in report.landed if identifier not in numbers)
    if unnamed and report.shallow:
        print(
            f"record: this checkout is a shallow clone, so a closure's own merge commit - "
            f"or the parent that would prove it is one - can lie outside it. `git fetch "
            f"--unshallow origin` is what lets the remaining {len(unnamed)} be read"
        )
    _restate_notes(root, known, args.dry_run)
    if written:
        return 0
    if not report.landed:
        # The ordinary state of a session mid-item: the closure it just wrote
        # is `done` in the working tree and has not merged, so no number is
        # owed yet. Reporting the unlanded count as unnameable would be the
        # confident wrong answer - it reads as lost provenance and is not.
        print(
            f"record: {len(owed)} closure(s) record no `pr`, and none has reached "
            f"`{report.base}` yet, so no number is owed"
        )
    else:
        print(
            f"record: {len(report.landed)} landed closure(s) record no `pr`, and "
            f"`{report.base}` names a number for none of them; `docket check` says "
            f"whether that is provenance lost or a history this checkout cannot see"
        )
    return 0


def _restate_notes(root: Path, by_id: Mapping[str, Item], dry_run: bool) -> int:
    """Put the number on the released bullets that shipped before it existed.

    The other record owed the same fact. `pr` exists so a reader can get from
    a released item back to the change that made it, and a release's notes are
    where that reader is looking - so a number written onto the item and not
    onto the bullet has been recorded in the half nobody reads.

    It belongs to this command rather than to `release` because repair and
    prevention are different jobs. `_numbers_before_notes` stops the next cut
    producing one; nothing in a cut can reach a bullet that shipped two
    releases ago, and re-cutting that version to regenerate it is refused,
    correctly (`PL-1MKQ`). This is the only supported route to those lines, and
    `make fix` runs it, so the repair costs no commit of its own - the same
    property that made `record` the right home for the field itself.

    Not in the `--number` path above, and the boundary is a fact rather than a
    convenience: that path writes the number of a merge that has just
    happened, and an item cannot appear in a release's notes before it has
    merged. There is no bullet for it to repair.

    Only an append is ever made, so a run that finds nothing to add writes
    nothing at all - which is what lets this sit in `make fix` without
    producing a diff on a healthy tree. `restate_references` carries why the
    title is left alone.
    """
    directory = root / NOTES_DIR
    if not directory.is_dir():
        return 0
    verb = "would restate" if dry_run else "restated"
    total = 0
    for path in sorted(directory.glob("v*.md")):
        if not SEMVER_RE.match(path.stem):
            continue
        text = path.read_text(encoding="utf-8")
        restated, repaired = restate_references(text, by_id)
        if not repaired:
            continue
        if not dry_run:
            path.write_text(restated, encoding="utf-8")
        total += len(repaired)
        print(
            f"{NOTES_DIR}/{path.name}: {verb} {len(repaired)} bullet(s) that shipped "
            f"with no route back to the change: {', '.join(repaired)}"
        )
    return total


def _write_pr(directory: Path, item: Item, number: str, dry_run: bool) -> None:
    """Set one item's `pr`, leaving every other byte of the file as it was.

    `insert_field` rather than either of the writers that render from the
    parsed item, and the two reasons are the two defects this line has had.
    `write_item` derives the filename from the title, so on a file whose slug
    has drifted it turns one added line into a delete-plus-add - and the skill
    grants `record` its standing exemption from the in-flight guard on the
    grounds that two sessions running it write the same line and git merges
    them, which a rename defeats (`PL-LBR6`, `PL-5QLP`). `rewrite_item` keeps
    the name and still re-renders the block, so on a file whose keys are in
    some other order, or whose value runs over continuation lines, it removes
    lines as well as adding one - and `verify.sanctioned_queue_edit` reads a
    removal as an ordinary content edit, so the close-out that ran `record`
    exactly as instructed came back `REJECT` (`PL-7K8Y`).

    Both callers establish that the item records no `pr` before reaching here,
    which is what makes an insert the right operation: `cmd_record` sorts a
    conflicting number into its own report rather than overwriting it.
    """
    if not dry_run:
        insert_field(directory, item, "pr", number)


def build_parser() -> argparse.ArgumentParser:
    # The shared options are attached to the top-level parser *and* to every
    # subcommand, so `docket --items X check` and `docket check --items X` both
    # work. Argparse's default insists on the first, which is the one nobody
    # remembers under a deadline.
    # The shared options are accepted on either side of the subcommand, and
    # making that true takes more than attaching them twice. Argparse parses a
    # subcommand into its own namespace and copies the result back, so a
    # subparser's copy of `--items` lands on top of a value the user gave
    # before the subcommand - silently, leaving the tool to answer confidently
    # about the wrong store. The subcommand copies therefore write to their own
    # dests, and `main` merges them, so neither position can erase the other.
    def _shared(parser: argparse.ArgumentParser, suffix: str = "") -> None:
        parser.add_argument(
            "--items",
            type=Path,
            default=None,
            dest="items" + suffix,
            help="path to the item directory",
        )
        parser.add_argument(
            "--today",
            type=date.fromisoformat,
            default=None,
            dest="today" + suffix,
            help="reference date",
        )
        parser.add_argument(
            "--now",
            type=_instant,
            default=None,
            dest="now" + suffix,
            help="reference instant for a branch's age, ISO 8601 with its UTC offset",
        )
        parser.add_argument(
            "--no-git",
            action="store_true",
            default=False,
            dest="no_git" + suffix,
            help="ask git nothing: no branch detection, and none of the history reads "
            "behind a count",
        )

    common = argparse.ArgumentParser(add_help=False)
    _shared(common, "_sub")

    parser = argparse.ArgumentParser(prog="docket", description=__doc__.splitlines()[0])
    _shared(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    def add(
        name: str, help_text: str, *, allow_abbrev: bool = True, epilog: str | None = None
    ) -> argparse.ArgumentParser:
        return sub.add_parser(
            name, help=help_text, parents=[common], allow_abbrev=allow_abbrev, epilog=epilog
        )

    check_cmd = add("check", "validate the store")
    check_cmd.add_argument(
        "--verify",
        action="store_true",
        default=False,
        help="also run every open item's `verify:` command; slow, and for CI rather than a gate",
    )
    check_cmd.add_argument(
        "--verify-base",
        default="",
        metavar="REF",
        help="with --verify, replay only the items this branch changed against REF, "
        "plus the open items whose verify: command reads a file it changed (for a "
        "pull request, where the whole-store sweep answers about the store rather "
        "than about the change)",
    )
    check_cmd.set_defaults(func=cmd_check)
    add("list", "one line per open item").set_defaults(func=cmd_list)
    digest_cmd = add("digest", "the session-start summary")
    digest_cmd.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="also report the git calls this digest made and the ref set it walked",
    )
    digest_cmd.set_defaults(func=cmd_digest)
    flight_cmd = add("flight", "branches carrying item work")
    flight_cmd.add_argument(
        "--no-remote",
        action="store_true",
        default=False,
        help="do not ask the forge which branches have a pull request open; "
        "for an offline checkout, and for a caller wanting a reading of the tree alone",
    )
    flight_cmd.set_defaults(func=cmd_flight)
    branch_cmd = add("branch", "where this branch stands against the default branch")
    branch_cmd.add_argument(
        "--no-fetch",
        action="store_true",
        default=False,
        help="read the refs as they are; the caller refreshed them, or cannot",
    )
    branch_cmd.add_argument(
        "--brief",
        action="store_true",
        default=False,
        help="position and recovery command only, for a caller printing the rest itself",
    )
    branch_cmd.add_argument(
        "--if-stale",
        action="store_true",
        default=False,
        help="say nothing unless the branch is behind, for a caller that speaks unasked",
    )
    branch_cmd.set_defaults(func=cmd_branch)
    stranded_cmd = add("stranded", "work that exists only on a branch")
    stranded_cmd.add_argument(
        "--no-fetch",
        action="store_true",
        default=False,
        help="read the refs as they are; the caller refreshed them, or cannot",
    )
    stranded_cmd.set_defaults(func=cmd_stranded)

    trailer_help = (
        "an attribution line the commit must end with, such as Co-Authored-By; repeatable, "
        "and written into the record's own paragraph, since git reads a trailer from the last "
        "paragraph alone"
    )
    claim_cmd = add("claim", "record that this branch holds an item, in an empty commit")
    claim_cmd.add_argument("ids", nargs="+", metavar="ID", help="the items to claim")
    claim_cmd.add_argument(
        "--over",
        default=None,
        metavar="BRANCH",
        help="take the items over from the branch holding them; only on the owner's word, or "
        "with get_session showing that session ARCHIVED or failed",
    )
    claim_cmd.add_argument(
        "--reason", default=None, help="with --over, why: written into the commit's body"
    )
    claim_cmd.add_argument(
        "--trailer", action="append", default=[], metavar="'KEY: VALUE'", help=trailer_help
    )
    claim_cmd.add_argument(
        "--no-fetch",
        action="store_true",
        default=False,
        help="read the refs as they are before writing; the caller refreshed them, or cannot. "
        "The fetch after a push still runs",
    )
    claim_cmd.set_defaults(func=cmd_claim)
    yield_cmd = add("yield", "end this branch's claim on an item without closing it")
    yield_cmd.add_argument("ids", nargs="+", metavar="ID", help="the items to yield")
    yield_cmd.add_argument(
        "--trailer", action="append", default=[], metavar="'KEY: VALUE'", help=trailer_help
    )
    yield_cmd.set_defaults(func=cmd_yield)
    arm_cmd = add("arm", "whether this branch's pull request may be armed for auto-merge")
    arm_cmd.add_argument(
        "--no-fetch",
        action="store_true",
        default=False,
        help="read the refs as they are; the caller refreshed them, or cannot",
    )
    arm_cmd.set_defaults(func=cmd_arm)

    record = add("record", "write the pull request number onto the closures owed one")
    record.add_argument(
        "number",
        type=int,
        nargs="?",
        default=None,
        help="one pull request number; omit to write every number the base can supply",
    )
    record.add_argument(
        "--merge", default=None, help="with a number, the merge that closed them (default: HEAD)"
    )
    record.add_argument(
        "--dry-run", action="store_true", help="say what would be written, and write nothing"
    )
    record.set_defaults(func=cmd_record)
    add("triage", "what is untriaged, and the rules the answers must satisfy").set_defaults(
        func=cmd_triage
    )

    new = add("new", "capture one or more ideas")
    new.add_argument("title", nargs="+")
    # One comma-separated value, repeatable - never variadic. `nargs="*"` made
    # `--touches path "Some title"` consume the title and then report the title as
    # missing, which named the one thing that had been supplied. Comma-separated
    # is also how `touches` is spelled in the item file (`PL-YNCW`).
    new.add_argument(
        "--touches",
        action="append",
        metavar="A.PY,B.PY",
        help="comma-separated paths the work is expected to reach; may be repeated",
    )
    new.add_argument("--feature", default=None, help="group this with related work")
    new.set_defaults(func=cmd_new)

    # Beside `new`, because it is the only undo `new` has. No abbreviations, for
    # the reason `set` refuses them: every argument here is an id, and a
    # mistyped one writes a correction onto the wrong item.
    withdraw = add(
        "withdraw",
        "disown a recorded filing whose match was wrong",
        allow_abbrev=False,
        epilog="The entry stays in the file, marked withdrawn, and stops counting. "
        "`--because` names the item whose brief says why the match was wrong; a withdrawal "
        "is auditable only through that brief.",
    )
    withdraw.add_argument("item", help="the item carrying the entry")
    withdraw.add_argument("capture", help="the id of the filing to disown")
    withdraw.add_argument(
        "--because",
        required=True,
        metavar="PL-XXXX",
        help="the item whose brief says why this match was wrong",
    )
    withdraw.set_defaults(func=cmd_withdraw)

    # No abbreviations here, where argparse's default would turn `--pr 123` into
    # `--priority 123`: a field name on this command is exact, or it is unknown.
    setter = add(
        "set",
        "write triage's answers onto one item, in canonical field order",
        allow_abbrev=False,
        epilog="An empty value (--feature '') removes the field. `id`, `title` and `added` "
        "are the capture's, `pr` is written by `docket record` and `milestone` by "
        "`docket release`; none is set here.",
    )
    setter.add_argument("item")
    setter.add_argument("--priority", choices=PRIORITIES)
    setter.add_argument("--effort", choices=EFFORTS)
    setter.add_argument("--status", choices=STATUSES)
    for flag, metavar in (
        ("--classes", "A,B"),
        ("--touches", "A.PY,B.PY"),
        ("--blocked-by", "PL-XXXX,vX.Y.Z"),
        ("--root-cause-of", "PL-XXXX,PL-YYYY,PL-ZZZZ"),
    ):
        setter.add_argument(
            flag, action="append", metavar=metavar, help="comma-separated; may be repeated"
        )
    setter.add_argument("--feature")
    setter.add_argument("--closed", type=_closing_date, metavar="YYYY-MM-DD")
    setter.add_argument("--reason")
    setter.add_argument("--payoff", metavar="LINE")
    setter.add_argument("--deferred-from", metavar="vX.Y.Z - WHY")
    setter.add_argument("--verify", metavar="COMMAND")
    setter.add_argument("--not-delegable", metavar="WHY")
    setter.add_argument("--falsifies", metavar="FRAGMENT")
    setter.add_argument("--generator", metavar="live|spent - WHY")
    setter.add_argument("--misread", metavar="FACT")
    setter.add_argument("--impairs-generators", metavar="WHY")
    setter.add_argument(
        "--overwrite", action="store_true", help="replace a value the item already records"
    )
    setter.set_defaults(func=cmd_set)

    nxt = add("next", "what to work on now, and why")
    nxt.add_argument(
        "lane",
        nargs="?",
        default="all",
        choices=("all", *SELECTABLE_LANES),
        help="narrow to one half of the project, so two sessions do not collide",
    )
    nxt.add_argument(
        "--effort",
        choices=("S", "M", "L"),
        default=None,
        help="only work that fits the time available",
    )
    nxt.add_argument("--limit", type=int, default=3)
    nxt.add_argument(
        "--oldest",
        action="store_true",
        default=False,
        help="owed work longest-waiting first, P0 on top, so what newer work keeps "
        "outranking surfaces",
    )
    nxt.set_defaults(func=cmd_next)

    gate_cmd = add("gate", "every open debt item in the store, a freeze's starting list")
    gate_cmd.add_argument(
        "--feature",
        default=None,
        help="split by this feature; Required scope, read by wave, is what a milestone clears",
    )
    gate_cmd.set_defaults(func=cmd_gate)

    feature = add("feature", "progress by feature")
    feature.add_argument("name", nargs="?")
    feature.set_defaults(func=cmd_feature)

    generators = add("generators", "how much of each generator's cluster is still open")
    generators.add_argument(
        "head", nargs="?", help="one cluster's members; a member's id resolves to its head"
    )
    generators.add_argument(
        "--misread",
        action="store_true",
        help="print what each head's members misread, sorted by the fact, and the heads whose "
        "clusters overlap - the list triage and grooming compare a capture against",
    )
    generators.set_defaults(func=cmd_generators)

    show = add("show", "print one item")
    show.add_argument("item")
    show.set_defaults(func=cmd_show)

    concurrent = add("concurrent", "what can be worked at once")
    concurrent.add_argument("item", nargs="?", help="check against this item")
    concurrent.add_argument("--limit", type=int, default=None)
    concurrent.set_defaults(func=cmd_concurrent)

    milestone = add("milestone", "release membership and progress")
    milestone.add_argument("name", nargs="?")
    milestone.set_defaults(func=cmd_milestone)

    release = add("release", "cut a release from everything finished and unshipped")
    release.add_argument("version", nargs="?", help="override the inferred version")
    release.add_argument("--dry-run", action="store_true")
    release.add_argument(
        "--no-fetch",
        action="store_true",
        default=False,
        help="read the refs as they are; the caller refreshed them, or cannot",
    )
    release.set_defaults(func=cmd_release)

    add("delegable", "what a cheaper model may work, and what proves it").set_defaults(
        func=cmd_delegable
    )

    verify_cmd = add("verify", "prove an item's work stayed inside its commission")
    verify_cmd.add_argument("item", nargs="+", help="one or more item ids, verified as a batch")
    verify_cmd.add_argument(
        "--base",
        default=None,
        help="the ref the work branched from (default: origin/main where it resolves)",
    )
    verify_cmd.add_argument(
        "--self",
        dest="self_audit",
        action="store_true",
        help=(
            "this session is auditing its own branch, not reviewing a delegated one: "
            "report the four commission checks instead of refusing on them"
        ),
    )
    verify_cmd.set_defaults(func=cmd_verify)

    add("status", "the project at feature altitude").set_defaults(func=cmd_status)
    add("wave", "which beat of the planning cadence is due").set_defaults(func=cmd_wave)
    trend_cmd = add("trend", "how the workflow-to-product balance has moved over time")
    trend_cmd.add_argument(
        "--by",
        choices=(BY_WEEK, BY_DAY),
        default=BY_WEEK,
        help="period length (default: %(default)s)",
    )
    trend_cmd.set_defaults(func=cmd_trend)
    return parser


def merge_shared(args: argparse.Namespace) -> argparse.Namespace:
    """Fold the subcommand's copy of a shared option onto the top-level one.

    Whichever position supplied a value wins; supplying it in both is not an
    error, since they cannot disagree without the user having written the flag
    twice on purpose.
    """
    for name in ("items", "today", "now", "no_git"):
        sub = getattr(args, name + "_sub", None)
        if sub:
            setattr(args, name, sub)
        delattr(args, name + "_sub")
    if args.now is not None and args.today is None:
        # One reference, not two: a caller placing "now" has placed "today",
        # and every command reading the date alone should agree with the one
        # reading the instant.
        args.today = args.now.date()
    return args


#: What a command exits with when its reader stopped reading before it finished:
#: 128 + SIGPIPE, which a shell reports for `yes | head -1` and git exits with
#: for the same event, so `set -o pipefail` reads docket the way it reads them.
#: Not 1, which `check` and `verify` return to mean the answer was no, and never
#: 0: the command did not finish, so it cannot report that it passed.
READER_CLOSED = 141


def main(argv: Sequence[str] | None = None) -> int:
    args = merge_shared(build_parser().parse_args(argv))
    try:
        status = int(args.func(args))
        # Here rather than at interpreter exit, where a reader that closed
        # before the last buffered chunk would be reported as an ignored
        # exception and the exit status changed to 120.
        sys.stdout.flush()
        return status
    except BrokenPipeError:
        return _reader_closed()
    finally:
        # The one thing a `cat-file --batch` must not do is outlive the command
        # that opened it, and a command that raised opened one just the same.
        invocation: Invocation | None = getattr(args, _INVOCATION_ATTR, None)
        if invocation is not None and invocation.git is not None:
            invocation.git.close()


def _reader_closed() -> int:
    """End the command quietly: whoever was reading its output has stopped.

    `bin/docket next | head -3` is the cheap way to read a pick, and `head`
    closes the pipe after three lines, so the next write fails. That is the
    reader's choice rather than a fault, and a traceback there reads as the
    queue tool crashing at the moment a session decides whether to trust it
    (`PL-VJPJ`). The recipe is Python's own, from "Note on SIGPIPE" in the
    `signal` documentation: catch the error at the entry point, then point
    stdout at the null device so the interpreter's flush at exit cannot fail a
    second time on the bytes still buffered.

    Every `BrokenPipeError` that reaches `main` is stdout's. The only other
    pipes docket writes to are its own to git, and `GitRunner` answers a dead
    `cat-file --batch` with `git show` instead of raising, which
    `test_a_batch_that_dies_mid_command_is_replaced_rather_than_raising` pins.

    Not by restoring SIGPIPE's default disposition, which that same note warns
    against, and which would cost something specific here: a batch process
    that died mid-command would then kill docket outright, where today it is
    replaced and the command still answers.
    """
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    os.close(devnull)
    return READER_CLOSED


if __name__ == "__main__":  # pragma: no cover - exercised via __main__.py
    raise SystemExit(main())
