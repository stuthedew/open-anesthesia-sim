"""The command line.

Each command answers one question a session or a maintainer actually asks,
and answers it in as few lines as the answer allows. Nothing here reads the
whole store into a person's attention when a summary would do.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from . import render
from .checks import analyze
from .concurrency import conflicts_for, parallel_batch
from .config import Config
from .config import load as load_config
from .model import Item
from .plan import features, gate, recommend
from .release import (
    bump_version,
    is_untagged,
    milestones,
    outstanding_roadmap_edits,
    read_version,
    readiness,
    release_notes,
    stamp,
)
from .roadmap import Wave, wave
from .store import find_item, new_id, read_items, write_item
from .vcs import (
    StrandedReport,
    branches_in_flight,
    default_base,
    in_flight_ids,
    merged_pull_requests,
    stranded,
    tags,
)
from .verify import verify_batch

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


def _flight(args: argparse.Namespace) -> set[str]:
    if getattr(args, "no_git", False):
        return set()
    return in_flight_ids(find_root())


def _stranded(
    root: Path, directory: Path, items: Sequence[Item], args: argparse.Namespace
) -> StrandedReport | None:
    """What exists only on a branch, or `None` when the question cannot be asked.

    The store is passed in rather than re-read: what this session can already
    see is exactly what must not be reported back to it, and the caller has it.

    A store outside the repository is `None` rather than an answer. Git can
    only be asked about paths it tracks, and searching the wrong path would
    find no items and report every branch as stranding all of its own.
    """
    if getattr(args, "no_git", False):
        return None
    try:
        tracked = directory.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None
    return stranded(root, {item.identifier for item in items}, items_dir=tracked)


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
    )
    print(render.format_check(report))
    return 1 if report.errors else 0


def _offered(
    root: Path, items: Sequence[Item], config: Config, args: argparse.Namespace
) -> frozenset[str]:
    """The ids `next` would suggest, as the grooming advisories read them.

    Deliberately the default offering - the same limit for every caller,
    ignoring `--effort` and `--limit` - because an advisory that changed with
    the flags of the command that happened to print it would report a
    different count in `check` than in `next`, and the count is the thing a
    session is being asked to act on.
    """
    plan = _plan(root, items, config)
    picks = recommend(list(items), _flight(args), scope=plan.scope if plan is not None else None)
    return frozenset(pick.item.identifier for pick in picks)


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
    )
    if rendered:
        print(rendered)
    return 0


def cmd_triage(args: argparse.Namespace) -> int:
    """Everything untriaged, with what is unset on it and what the rules require.

    Prints; decides nothing. The digest already tells every session that items
    are waiting - what it could not do is put the rules in front of the
    session at the moment it applies them.
    """
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    print(render.format_triage(report, config))
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
    _, items, _ = _load(args)
    item = find_item(items, args.item)
    if item is None:
        print(f"no item matching '{args.item}'")
        return 1
    print(f"{item.identifier} {item.title}")
    print(f"  {item.priority or '-'} · {item.effort or '-'} · {item.status}")
    if item.touches:
        print(f"  touches: {', '.join(item.touches)}")
    if item.milestone:
        print(f"  milestone: {item.milestone}")
    print()
    print(item.body.strip())
    return 0


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
        blocked = conflicts_for(item, candidates)
        blocked_ids = {c.other.identifier for c in blocked}
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
        for conflict in blocked or []:
            print(f"    {conflict.describe()}")
        if not blocked:
            print("    nothing")
        print()
        print("  No declared overlap (not a guarantee - verify before starting both):")
        for other in free:
            flag = " [IN FLIGHT]" if other.identifier in flight else ""
            print(f"    {other.identifier} {other.title}{flag}")
        if not free:
            print("    nothing")
        return 0

    batch = parallel_batch(candidates, args.limit)
    print(f"A batch that can be worked at once ({len(batch)} items, best-first):")
    for item in batch:
        flag = " [IN FLIGHT]" if item.identifier in flight else ""
        print(f"  {item.priority} {item.identifier} {item.title}{flag}")
    print()
    print("No declared overlap between these. That is not a guarantee: `touches` is")
    print("a prediction made when each item was written, so verify before starting.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """The project at feature altitude, plus whether a release is worth cutting."""
    _, items, config = _load(args)
    report = analyze(items, args.today or date.today(), config)
    root = args.items.parent if args.items else find_root()
    ready = readiness(items, read_version(root / config.version_file), config.minor_classes)
    rendered = render.format_status(report, ready, _flight(args))
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
    """
    _, items, config = _load(args)
    root = args.items.parent if args.items else find_root()
    report = analyze(
        items, args.today or date.today(), config, offered=_offered(root, items, config, args)
    )
    plan = _plan(root, items, config)
    flight = _flight(args)
    picks = recommend(
        items,
        flight,
        effort=args.effort,
        limit=args.limit,
        scope=plan.scope if plan is not None else None,
    )
    if not picks:
        print("Nothing is ready to start.")
        if report.untriaged:
            print(f"{len(report.untriaged)} untriaged item(s) are waiting: `docket list`.")
        return 0
    print(f"{len(report.open_items)} open. Suggested next:\n")
    for index, pick in enumerate(picks, start=1):
        print(f"  {index}. {pick.describe()}\n")
    if flight:
        print(f"Excluded, already in flight: {', '.join(sorted(flight))}")
    if report.advisories:
        print(
            f"{len(report.advisories)} grooming advisory(ies) pending; `docket check` to see them."
        )
    return 0


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

    for item in stamp(ready.shippable, name):
        original = next(i for i in items if i.identifier == item.identifier)
        write_item(directory, item, replace=directory / original.path)
    previous = bump_version(root / config.version_file, version)
    notes_path = root / "docs" / "releases" / f"{name}.md"
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


def cmd_stranded(args: argparse.Namespace) -> int:
    """Items that exist on a branch and nowhere this checkout's store can see.

    Exits zero whether or not it finds any: an item on a branch that is still
    being worked is the normal case, and the command cannot tell that from an
    item on a branch nobody will merge. Reporting is the whole job; deciding
    which of the two a branch is remains the reader's.
    """
    directory, items, _ = _load(args)
    root = args.items.parent if args.items else find_root()
    report = _stranded(root, directory, items, args)
    if report is None:
        print("branch detection is off (`--no-git`), so nothing was read")
        return 0
    print(render.format_stranded(report))
    return 0


def cmd_flight(args: argparse.Namespace) -> int:
    branches = branches_in_flight(find_root())
    if not branches:
        print("no branch names carry an item id")
        return 0
    for branch in branches:
        print(f"{branch.item_id}  {branch.name}")
    return 0


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

    add("check", "validate the store").set_defaults(func=cmd_check)
    add("list", "one line per open item").set_defaults(func=cmd_list)
    add("digest", "the session-start summary").set_defaults(func=cmd_digest)
    add("flight", "branches carrying item work").set_defaults(func=cmd_flight)
    add("stranded", "items that exist only on a branch").set_defaults(func=cmd_stranded)
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
