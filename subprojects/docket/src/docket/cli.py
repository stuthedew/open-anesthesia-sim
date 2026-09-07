"""The command line.

Each command answers one question a session or a maintainer actually asks,
and answers it in as few lines as the answer allows. Nothing here reads the
whole store into a person's attention when a summary would do.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import replace as with_fields
from datetime import date
from pathlib import Path

from . import render
from .checks import analyze
from .concurrency import (
    ORDERING,
    SAME_AREA,
    SAME_FILE,
    conflicts_for,
    observed_conflicts,
    parallel_batch,
    sequenceable,
)
from .config import CONFIG_NAME, Config
from .config import load as load_config
from .model import LANE_CROSSING, SELECTABLE_LANES, Item
from .plan import OfferedReport, features, gate, recommend, set_aside
from .release import (
    NOTES_DIR,
    already_released,
    is_untagged,
    milestones,
    notes_name,
    outstanding_roadmap_edits,
    prepare_bump,
    read_version,
    readiness,
    release_notes,
    stamp,
)
from .roadmap import Wave, wave
from .store import find_item, new_id, read_items, write_item
from .trend import BY_DAY, BY_WEEK
from .trend import analyze as analyze_trend
from .vcs import (
    CURRENT,
    BranchCut,
    Churn,
    CutsInFlight,
    FlightReport,
    OrphanedReport,
    StrandedReport,
    branch_state,
    branches_in_flight,
    changed_items,
    churn,
    closed_by,
    closures_on_base,
    cuts_in_flight,
    default_base,
    fetch_remote,
    files_in_flight,
    lost,
    merged_pull_requests,
    orphaned,
    precedence,
    records_on_base,
    released_on_base,
    stranded,
    tags,
)
from .verify import already_passing, verify_batch

CAPTURE_TEMPLATE = """**Problem.** {title}

**Why it matters.**

**Where.**

**Done when.**
"""


def find_root(start: Path | None = None) -> Path:
    """The repository root, or the working directory if there is no checkout."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def _load(args: argparse.Namespace) -> tuple[Path, list[Item], Config]:
    """Resolve the store and the settings that govern it.

    Settings come from beside the store, not from wherever the command was
    run. Pointing `--items` at another project's queue and silently applying
    this project's policy to it would be wrong in exactly the way that is hard
    to notice - the answers look right and are governed by the wrong rules.
    """
    root = args.items.parent if args.items else find_root()
    config = load_config(root)
    directory = args.items or (root / config.items_dir)
    return directory, read_items(directory), config


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
    """
    if getattr(args, "no_git", False):
        return FlightReport()
    root, items_dir = _tracked(args)
    return branches_in_flight(root, items_dir=items_dir)


def _tracked(args: argparse.Namespace) -> tuple[Path, str]:
    """The repository root, and the queue directory beneath it as git spells it.

    Resolved from the store exactly as `_load` resolves it - `--items` wins
    over the setting, because a command pointed at one queue must not be
    answered about another. `branches_in_flight` decides whether a commit was
    recording an item or working on it by whether its whole diff sits in this
    directory, so the wrong directory here reads every commit as work.

    A store outside the repository comes back as the empty prefix, which no
    path git prints can match, so every commit keeps its claim. That is the
    same direction `_stranded` takes on the same question and the same one the
    reading itself prefers: an item wrongly left marked is picked around, an
    item wrongly unmarked is two sessions on one piece of work.
    """
    root = args.items.parent if args.items else find_root()
    directory = args.items or (root / load_config(root).items_dir)
    try:
        return root, directory.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return root, ""


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
    root: Path,
    directory: Path,
    items: Sequence[Item],
    args: argparse.Namespace,
    *,
    fetched: bool = False,
) -> StrandedReport | None:
    """What exists only on a branch, or `None` when the question cannot be asked.

    The store is passed in rather than re-read: what this session can already
    see is exactly what must not be reported back to it, and the caller has it.

    A store outside the repository is `None` rather than an answer. Git can
    only be asked about paths it tracks, and searching the wrong path would
    find no items and report every branch as stranding all of its own.

    `fetched` is the caller's, because the two callers refresh differently and
    neither should refresh twice. `cmd_stranded` fetches for itself; the digest
    is run by a hook that has just fetched through `docket branch`, and a
    second fetch would cost every session start a network round trip for an
    answer it already has.
    """
    if getattr(args, "no_git", False):
        return None
    try:
        tracked = directory.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None
    return stranded(root, {item.identifier for item in items}, items_dir=tracked, fetched=fetched)


def _orphaned(root: Path, args: argparse.Namespace) -> OrphanedReport | None:
    """Work a branch carries that its own pull request left behind, or `None`.

    Unlike `_stranded` this needs neither the store nor a store inside the
    repository: the question is about the tree as a whole, which is the point
    of it. Only `--no-git` turns it off, for the same reason it turns the rest
    off - a caller that has said not to ask git must not be asked git.
    """
    if getattr(args, "no_git", False):
        return None
    return orphaned(root)


def cmd_check(args: argparse.Namespace) -> int:
    # The repository root, not the store beneath it: `_load` returns the item
    # directory, and the roadmap `_offered` reads sits a level above it.
    _, items, config = _load(args)
    root = args.items.parent if args.items else find_root()
    # The only command that asks git anything, because it is the only one whose
    # answer depends on what has merged. `None` comes back from a checkout too
    # shallow to be trusted, and the provenance check is skipped rather than
    # run against a truncated history.
    report = analyze(
        items,
        args.today or date.today(),
        config,
        history=merged_pull_requests(root),
        offered=_offered(root, items, config, args),
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
        # healthier the store got the more the gate cost - and the advisory in
        # `_check_slow_commands` puts the floor at about 19 s even with the
        # slow commands narrowed, because it is set by the size of the queue.
        #
        # `None` rather than an empty report, which is the same path `list`,
        # `digest` and `next` take: `checks.py` reads it as "a caller that did
        # not ask" and says nothing, which is what a caller that was never the
        # right one to ask should produce. A line on every `make check` saying
        # the replay did not run would be an advisory nobody reads.
        #
        # `--verify-base` narrows it further, to the items this branch changed
        # against that ref (`PL-SDHR`). The same argument one step on: if a
        # pre-commit gate cannot have changed whether another item's work
        # merged, neither can a pull request, and the sweep costs 87 s of the
        # quality job's 152 s on every push to every open pull request while
        # growing with the queue rather than with the change. CI scopes on
        # `pull_request` and sweeps on `push` to the default branch, which is
        # the one event where the answer is a fact about that branch.
        landed=(
            already_passing(
                root,
                items,
                scoped_to=changed_items(root, args.verify_base, items_dir=config.items_dir),
                scope_base=args.verify_base,
            )
            if args.verify and args.verify_base
            else already_passing(root, items)
            if args.verify
            else None
        ),
        # Only the closures in question are asked about, because each costs a
        # `git show`: an item is judged for a missing `pr` once its closure
        # stands on the default base, and until then it is still in flight.
        closures=closures_on_base(
            root,
            {i.identifier: i.path for i in items if i.status == "done" and not i.pr and i.path},
            items_dir=config.items_dir,
        ),
        # The same `git show`, asked of the other half of a closure: not "has
        # this landed" but "does it still record the command that proved it".
        # Every closed item is offered and the reader narrows to the ones this
        # checkout changed, which is usually none - a diff rather than a read
        # per item, so it costs what the line above already costs.
        records=records_on_base(
            root,
            {i.identifier: i.path for i in items if i.status == "done" and i.path},
            items_dir=config.items_dir,
        ),
        # Asked of the branch rather than of the default branch, and that is
        # the whole point: a squash merge makes the branch's commits ancestors
        # of nothing, so the objects proving what it carried stop being
        # reachable. Run here, on a pull request, the evidence is still intact.
        lost=lost(root, items_dir=config.items_dir),
        # Read rather than asked of git: a stamped `milestone:` is judged
        # against the version the project is actually on, and an absent
        # version file leaves the question unasked rather than answered.
        version=read_version(root / config.version_file),
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
    picks = recommend(list(items), flight.ids, scope=plan.scope if plan is not None else None)
    return OfferedReport(
        ids=frozenset(pick.item.identifier for pick in picks), declined=render.format_unread(flight)
    )


def cmd_list(args: argparse.Namespace) -> int:
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    rendered = render.format_list(report, _flight(args), config.protected_paths)
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
        )
    except (OSError, ValueError, KeyError):
        return None


def cmd_digest(args: argparse.Namespace) -> int:
    directory, items, config = _load(args)
    if not items:
        return 0
    root = args.items.parent if args.items else find_root()
    report = analyze(
        items, args.today or date.today(), config, offered=_offered(root, items, config, args)
    )
    ready = readiness(items, read_version(root / config.version_file), config.minor_classes)
    rendered = render.format_digest(
        report,
        _flight(args),
        ready,
        _plan(root, items, config),
        _stranded(root, directory, items, args),
        config.workflow_paths,
        _orphaned(root, args),
        _cuts(root, config, args) if ready.is_worth_cutting else None,
    )
    if rendered:
        print(rendered)
    return 0


def _cuts(root: Path, config: Config, args: argparse.Namespace) -> CutsInFlight | None:
    """Which refs are mid-release, read only where a release is being offered.

    Gated on the offer rather than run for every digest: it costs a walk of the
    unlanded refs (measured 103 ms on this repository), and a session not being
    offered a release has nothing to be warned off. It does not fetch - the
    digest's hook already did, and this must stay answerable in a checkout with
    no network.
    """
    if getattr(args, "no_git", False):
        return None
    base = released_on_base(root, version_file=config.version_file, notes_dir=NOTES_DIR)
    return cuts_in_flight(root, notes_dir=NOTES_DIR, on_base=base.notes)


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
    print(render.format_triage(report, config, _flight(args)))
    return 0


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
    taken = {item.identifier for item in items}
    for title in args.title:
        taken.add(_capture(directory, title, taken, args))
    return 0


def _capture(directory: Path, title: str, taken: set[str], args: argparse.Namespace) -> str:
    identifier = new_id(taken)
    item = Item(
        identifier=identifier,
        title=title,
        priority="",
        effort="",
        status="untriaged",
        classes=(),
        touches=tuple(args.touches or ()),
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
    """
    _, items, _ = _load(args)
    item = find_item(items, args.item)
    if item is None:
        print(f"no item matching '{args.item}'")
        return 1
    flight = _flight(args)
    print(f"{item.identifier} {item.title}")
    print(f"  {item.priority or '-'} · {item.effort or '-'} · {item.status}")
    if item.touches:
        print(f"  touches: {', '.join(item.touches)}")
    if item.milestone:
        print(f"  milestone: {item.milestone}")
    if item.identifier in flight.ids:
        # The whole precedence read only where something is actually carrying
        # the item, which is the rare case. A session starting ordinary work
        # pays exactly what it paid before.
        root, items_dir = _tracked(args)
        print(
            render.format_precedence(
                precedence(root, item.identifier, items_dir=items_dir), args.today or date.today()
            )
        )
    elif edit := next((e for e in flight.editing if e.item_id == item.identifier), None):
        # The weaker mark, and only where the stronger one is silent. A session
        # that names an item reaches `show` and nothing else, so before this
        # the one thing it could not learn here was that another branch had
        # already written to the file it was about to write to (`PL-N1JK`).
        print(render.format_queue_edit(edit, args.today or date.today()))
    print()
    print(item.body.strip())
    _say_unread(flight)
    return 0


def _print_observed(args: argparse.Namespace, item: Item, flight: FlightReport) -> None:
    """What branches are already changing, as against what items declared.

    Printed under the declared answer rather than folded into it. The two are
    different kinds of evidence - a prediction written before the work, and a
    measurement taken during it - and a reader deciding whether to start needs
    to know which one fired, because only the second says the collision has
    already happened.
    """
    files = files_in_flight(args.items.parent if args.items else find_root(), flight)
    observed = observed_conflicts(item, files)
    print()
    print("  Already changed on a branch in flight (observed, not declared):")
    for entry in observed:
        print(f"    {entry.describe()} has changed:")
        for path in entry.paths:
            print(f"      {path}")
    if not observed:
        print("    nothing - which means no branch has touched these files *yet*,")
        print("    not that none will; and it says nothing about files this item")
        print("    touches without having declared them")
    if files.unreadable:
        print(f"    ({len(files.unreadable)} ref(s) unread: {', '.join(files.unreadable)})")


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
        for conflict in by_strength[SAME_FILE] or []:
            print(f"    {conflict.describe()}")
        if not by_strength[SAME_FILE]:
            print("    nothing")
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
        print("`docket concurrent --limit <n>` fills the batch out with them.")
    _say_unread(flight)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """The project at feature altitude, plus whether a release is worth cutting."""
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    root = args.items.parent if args.items else find_root()
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
    root = args.items.parent if args.items else find_root()
    report = analyze(
        items, args.today or date.today(), config, offered=_offered(root, items, config, args)
    )
    plan = _plan(root, items, config)
    flight = _flight(args)
    picks = recommend(
        items,
        flight.ids,
        effort=args.effort,
        limit=args.limit,
        scope=plan.scope if plan is not None else None,
        lane=lane,
        workflow_paths=config.workflow_paths,
    )
    where = f" in the {lane} lane" if lane else ""
    if not picks:
        print(f"Nothing is ready to start{where}.")
        if report.untriaged:
            print(f"{len(report.untriaged)} untriaged item(s) are waiting: `docket list`.")
        _say_lane_holdouts(items, flight, config, args, lane)
        _say_unread(flight)
        return 0
    print(f"{len(report.open_items)} open. Suggested next{where}:\n")
    for index, pick in enumerate(picks, start=1):
        print(f"  {index}. {pick.describe()}\n")
    if flight.ids:
        print(f"Excluded, already in flight: {', '.join(sorted(flight.ids))}")
    _say_lane_holdouts(items, flight, config, args, lane)
    _say_answer_lane(items, flight, config, args, plan, lane, picks[0].item)
    if report.advisories:
        print(
            f"{len(report.advisories)} grooming advisory(ies) pending; `docket check` to see them."
        )
    _say_unread(flight)
    return 0


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
        )
        return found[0].item if found else None

    def name(wanted: str) -> str:
        found = pick_for(wanted)
        return f"{found.identifier} ({found.title})" if found else "nothing startable"

    top_lane = top.lane(config.workflow_paths)
    if top_lane in SELECTABLE_LANES:
        other = next(one for one in SELECTABLE_LANES if one != top_lane)
        print(
            f"Lane of this answer: {top.identifier} is {top_lane} work. "
            f"The {other} lane's own pick is {name(other)} - `docket next {other}`."
        )
        return

    # Crossing and unplaced work is nobody's lane, so there is no "the other
    # lane" to name and both are printed. The sentence says which of the two
    # it is, because they are recovered differently: a crossing item wants a
    # session that can hold the whole change, an unplaced one wants a `touches`.
    why = "reaches both halves" if top_lane == LANE_CROSSING else "declares no `touches`"
    named = "; ".join(f"{one} {name(one)}" for one in SELECTABLE_LANES)
    print(f"Lane of this answer: {top.identifier} {why}, so no lane places it. By lane: {named}.")


def cmd_gate(args: argparse.Namespace) -> int:
    """The debt a milestone has to clear, computed from the store.

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
            mark = "x" if item.status == "done" else " "
            print(f"  [{mark}] {item.identifier} {item.title}")
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
            mark = "x" if item.status == "done" else " "
            print(f"  [{mark}] {item.identifier} {item.title}")
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    """Cut a release from whatever is finished and has not shipped yet.

    Takes no list of items, on purpose. Requiring one would mean the release
    is only as complete as somebody's memory of what to put in it, and the
    store already knows exactly which finished work has not gone out.
    """
    directory, items, config = _load(args)
    root = args.items.parent if args.items else find_root()
    current = read_version(root / config.version_file)
    ready = readiness(items, current, config.minor_classes)

    if not ready.shippable:
        print(f"Nothing to release: no finished work since {current}.")
        return 0

    # Cutting a release on top of an untagged one extends a gap that cannot be
    # closed afterwards, so the refusal belongs here rather than in a reminder.
    # A dry run is allowed through with a warning: it exists to review the
    # notes and the bump, and withholding those would not make the tag appear.
    if not getattr(args, "no_git", False) and is_untagged(current, tags(root)):
        print(_untagged_warning(current))
        if not args.dry_run:
            return 1
        print()

    if args.version is None and config.version_policy == "manual":
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

    version = (args.version or ready.suggested_version).lstrip("v")
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
    if not getattr(args, "no_git", False):
        if not args.no_fetch:
            fetch_remote(root)
        base = released_on_base(root, version_file=config.version_file, notes_dir=NOTES_DIR)
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
        elif holders := [
            branch
            for branch in cuts_in_flight(root, notes_dir=NOTES_DIR, on_base=base.notes).branches
            if not branch.mine
        ]:
            print(_parallel_cut_warning(holders))
            if not args.dry_run:
                return 1
            print()

    milestone = milestones(stamp(ready.shippable, name))[name]
    notes = release_notes(milestone, args.today or date.today())

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

    # Prove the bump before writing anything: a release records all of itself
    # or none of it. Stamping first and bumping afterwards meant a version file
    # the bump rejects left the store claiming a release that never happened,
    # with nothing recording which stamps to unpick.
    try:
        bump = prepare_bump(root / config.version_file, version)
    except (OSError, ValueError) as error:
        print(f"Cannot bump {config.version_file}, so nothing was stamped and nothing was written:")
        print(f"  {error}")
        return 1

    for item in stamp(ready.shippable, name):
        original = next(i for i in items if i.identifier == item.identifier)
        write_item(directory, item, replace=directory / original.path)
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
    lines.append(f'  git tag -a {name} <merge commit> -m "{name}"')
    lines.append(f"  git push origin {name}")
    return "\n".join(lines)


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
            f'  git tag -a {name} <commit> -m "{name}"',
            f"  git push origin {name}",
        ]
    )


def cmd_delegable(args: argparse.Namespace) -> int:
    """Everything a worker may take, with the command that proves each one."""
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    print(render.format_delegable(report, _flight(args), config.protected_paths))
    return 0


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
    """
    _, items, config = _load(args)
    wanted = []
    for identifier in args.item:
        item = find_item(items, identifier)
        if item is None:
            print(f"no item matching '{identifier}'")
            return 1
        wanted.append(item)
    root = args.items.parent if args.items else find_root()
    base = args.base or default_base(root)
    reports = verify_batch(root, wanted, config, base)
    print("\n\n".join(report.describe() for report in reports))
    if len(reports) > 1:
        print(f"\n{config.check_command} ran once for the batch; it proves the tree, not an item.")
    return 0 if all(report.passed for report in reports) else 1


def cmd_wave(args: argparse.Namespace) -> int:
    """Which beat of the planning cadence is due, computed from the plan itself.

    The queue nags every session; the roadmap nags never, so "what next" gets
    answered from whatever ranks highest in the store - a question above that
    ranking's altitude. This answers the other one, and answers it the only way
    that survives a session with no memory: by reading the files.

    Exits non-zero when it cannot compute an answer - no roadmap, no timeline,
    or a gate naming an item the store does not hold - because a beat the tool
    is unsure of is worth less than an obvious failure to produce one.
    """
    _, items, config = _load(args)
    root = args.items.parent if args.items else find_root()
    roadmap = root / config.roadmap_file
    if not roadmap.is_file():
        print(f"no {config.roadmap_file} to read: there is no plan to report a position on")
        return 1

    plan = wave(
        roadmap.read_text(encoding="utf-8"),
        read_version(root / config.version_file),
        frozenset(item.identifier for item in items if not item.is_open),
        frozenset(item.identifier for item in items),
    )
    print(render.format_wave(plan))
    if plan.step is None or plan.problems or (plan.gate is not None and plan.gate.unknown_ids):
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
    root = args.items.parent if args.items else find_root()
    history = Churn() if args.no_git else churn(root)
    report = analyze_trend(items, history, config, by=args.by, today=args.today or date.today())
    print(render.format_trend(report))
    return 0


def cmd_stranded(args: argparse.Namespace) -> int:
    """Work that exists on a branch and nowhere this checkout can otherwise see.

    Two reads, printed together because a reader asking "is anything only on a
    branch" means both and would not think to run two commands. `stranded`
    answers it for items, by id across trees; `orphaned` answers it for
    everything else, by content across the base - which is the half that was
    missing while a dropped commit touching a skill or `src/` went unreported
    (`PL-3D2M`).

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
    """
    directory, items, _ = _load(args)
    root = args.items.parent if args.items else find_root()
    if not args.no_fetch:
        fetch_remote(root)
    report = _stranded(root, directory, items, args, fetched=not args.no_fetch)
    if report is None:
        print("branch detection is off (`--no-git`), so nothing was read")
        return 0
    print(render.format_stranded(report))
    left = _orphaned(root, args)
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
    root = args.items.parent if args.items else find_root()
    if not args.no_fetch:
        fetch_remote(root)
    state = branch_state(root, fetched=not args.no_fetch)
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


def cmd_flight(args: argparse.Namespace) -> int:
    """Which items are being worked on a branch, and how long since each moved.

    Exits zero whether or not it finds any, for the reason `stranded` does:
    an unmerged branch is a live session or abandoned work, the command cannot
    tell which, and reporting is the whole job.
    """
    root, items_dir = _tracked(args)
    report = branches_in_flight(root, items_dir=items_dir)
    print(render.format_flight(report, args.today or date.today()))
    return 0


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
    root = args.items.parent if args.items else find_root()
    try:
        tracked = directory.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        print("record: the store is outside the repository, so git cannot say what closed")
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
    report = closed_by(merge, root, items_dir=tracked)
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
    owed = {i.identifier: i.path for i in items if i.status == "done" and not i.pr and i.path}
    if not owed:
        print("record: every closure already records its pull request")
        return 0
    report = closures_on_base(root, owed, items_dir=tracked)
    if not report.known:
        print(f"record: declined to read {report.declined}")
        return 2

    numbers = report.numbers
    known = {item.identifier: item for item in items}
    verb = "would record" if args.dry_run else "recorded"
    written = 0
    for identifier in sorted(report.landed):
        number = numbers.get(identifier)
        item = known.get(identifier)
        if number is None or item is None:
            continue
        _write_pr(directory, item, str(number), args.dry_run)
        print(f"{identifier}: {verb} `pr: {number}`")
        written += 1
    unnamed = sorted(identifier for identifier in report.landed if identifier not in numbers)
    if unnamed and report.shallow:
        print(
            f"record: this checkout is a shallow clone, so a closure's own merge commit - "
            f"or the parent that would prove it is one - can lie outside it. `git fetch "
            f"--unshallow origin` is what lets the remaining {len(unnamed)} be read"
        )
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


def _write_pr(directory: Path, item: Item, number: str, dry_run: bool) -> None:
    """Set one item's `pr`, leaving every other field exactly as it was."""
    if not dry_run:
        write_item(directory, with_fields(item, pr=number), replace=directory / item.path)


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
            "--no-git",
            action="store_true",
            default=False,
            dest="no_git" + suffix,
            help="skip branch detection",
        )

    common = argparse.ArgumentParser(add_help=False)
    _shared(common, "_sub")

    parser = argparse.ArgumentParser(prog="docket", description=__doc__.splitlines()[0])
    _shared(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, help=help_text, parents=[common])

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
        help="with --verify, replay only the items this branch changed against REF "
        "(for a pull request, where the whole-store sweep answers about the store "
        "rather than about the change)",
    )
    check_cmd.set_defaults(func=cmd_check)
    add("list", "one line per open item").set_defaults(func=cmd_list)
    add("digest", "the session-start summary").set_defaults(func=cmd_digest)
    add("flight", "branches carrying item work").set_defaults(func=cmd_flight)
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
    new.add_argument("--touches", nargs="*", help="paths the work is expected to reach")
    new.add_argument("--feature", default=None, help="group this with related work")
    new.set_defaults(func=cmd_new)

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
    nxt.set_defaults(func=cmd_next)

    gate_cmd = add("gate", "the open debt a milestone has to clear")
    gate_cmd.add_argument(
        "--feature", default=None, help="the milestone's feature; its items clear with it"
    )
    gate_cmd.set_defaults(func=cmd_gate)

    feature = add("feature", "progress by feature")
    feature.add_argument("name", nargs="?")
    feature.set_defaults(func=cmd_feature)

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
    for name in ("items", "today", "no_git"):
        sub = getattr(args, name + "_sub", None)
        if sub:
            setattr(args, name, sub)
        delattr(args, name + "_sub")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = merge_shared(build_parser().parse_args(argv))
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover - exercised via __main__.py
    raise SystemExit(main())
