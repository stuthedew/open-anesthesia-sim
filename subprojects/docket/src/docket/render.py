"""Turning the store into the few lines a reader actually needs.

Every output here is sized against what it costs to read. The digest is
injected into a session's context and resent on every turn, so it is a
handful of lines and says nothing that cannot be acted on. The listing
replaces reading the store, so it carries exactly the fields a choice
between items turns on and no prose. Printing what a decision needs, rather
than the documents that contain it, is the cheapest optimization available
here and the one that compounds.
"""

from __future__ import annotations

from .checks import REQUIRED_BRIEF, Report
from .concurrency import undeclared
from .config import Config
from .model import PRIORITIES, Item
from .plan import Gate, effort_total
from .roadmap import CLEAR, FREEZE, IMPLEMENT, RELEASE, STEP_SEPARATOR, Wave


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _counts(report: Report) -> str:
    counts = report.counts
    return ", ".join(f"{n} {p}" for p, n in counts.items())


def _marks(item: Item, in_flight: set[str], protected: tuple[str, ...] = ()) -> str:
    marks = [m for m in (item.effort, item.status) if m]
    if item.milestone:
        marks.append(item.milestone)
    if item.identifier in in_flight:
        marks.append("IN FLIGHT")
    if item.model_guidance is not None:
        marks.append(f"{item.model_guidance}, strongest model")
    elif item.delegability(protected) is None:
        marks.append("delegable")
    return ", ".join(marks)


def format_list(
    report: Report, in_flight: set[str] | None = None, protected_paths: tuple[str, ...] = ()
) -> str:
    """One line per open item: the queue without the briefs."""
    flight = in_flight or set()
    if not report.open_items and not report.untriaged:
        return ""

    lines = [f"Docket: {len(report.open_items)} open - {_counts(report)}."]
    ordered = sorted(report.open_items, key=lambda i: i.sort_key())
    width = max((len(i.identifier) for i in ordered), default=0)
    for item in ordered:
        lines.append(
            f"{item.priority} {item.identifier:<{width}} {item.title} "
            f"({_marks(item, flight, protected_paths)})"
        )

    if report.untriaged:
        lines.append("")
        lines.append(f"Untriaged ({_plural(len(report.untriaged), 'item', 'items')}):")
        for item in sorted(report.untriaged, key=lambda i: i.sort_key()):
            lines.append(f"   {item.identifier:<{width}} {item.title}")
    lines.append("Read an item's brief before starting it; this listing is for choosing.")
    return "\n".join(lines)


def format_delegable(report: Report, in_flight: set[str], protected_paths: tuple[str, ...]) -> str:
    """The worker's whole reading list: what may be worked, and what proves it.

    A separate answer from `next`, deliberately. `next` answers "what should
    *I* do now" - it ranks, limits, and explains itself, because a session
    picks one thing. A worker wants the opposite: everything it is allowed to
    touch, with each item's proof command beside it, so a batch can be started
    without opening a single file first.
    """
    candidates = [
        item
        for item in sorted(report.open_items, key=lambda i: i.sort_key())
        if item.delegability(protected_paths) is None and item.identifier not in in_flight
    ]
    if not candidates:
        return (
            "Nothing is delegable right now.\n"
            "An item qualifies when it is ready, is not safety- or science-classed, "
            "names a `verify:` command,\nand declares `touches` outside the "
            "protected paths. `docket list` shows what is open."
        )

    width = max(len(item.identifier) for item in candidates)
    lines = [f"{len(candidates)} item(s) may be worked by a cheaper model, best-first:", ""]
    for item in candidates:
        lines.append(f"  {item.priority} {item.identifier:<{width}} {item.title}")
        lines.append(f"  {'':<{width + 6}}verify: {item.verify}")
        lines.append("")
    lines.append("Read each item's brief before starting it, and follow docs/worker.md.")
    lines.append("Anything not listed here is not yours to take, whatever its priority.")
    return "\n".join(lines)


def format_digest(
    report: Report,
    in_flight: set[str] | None = None,
    ready: object = None,
    plan: Wave | None = None,
) -> str:
    """The few lines injected into session context at startup.

    The release line is here rather than left for someone to ask about,
    because nobody asks. Finished work sits unshipped until a person happens
    to wonder, and the store already knows when there is enough of it to be
    worth raising. The plan line is here for the same reason and a sharper
    one: the queue nags every session and the roadmap nags never, so "what
    next" gets answered from whatever ranks highest in the store - a question
    one level below the altitude that should decide it.

    Every line is resent on every turn of the session, so the plan gets one:
    the beat and the step, and `docket wave` for the rest.
    """
    flight = in_flight or set()
    if not report.items:
        return ""

    lines = [f"Docket: {len(report.open_items)} open - {_counts(report)}."]
    for item in sorted(report.open_items, key=lambda i: i.sort_key()):
        if item.priority != "P0":
            continue
        lines.append(
            f"  P0 (before feature work): {item.identifier} {item.title} ({_marks(item, flight)})"
        )

    top = next((i for i in sorted(report.open_items, key=lambda i: i.sort_key())), None)
    if top is not None and top.priority != "P0":
        lines.append(f"  Top: {top.identifier} {top.title} ({_marks(top, flight)})")

    if flight:
        lines.append(
            f"  In flight on a branch: {', '.join(sorted(flight))} - do not start these again."
        )
    if report.untriaged:
        lines.append(
            f"  {_plural(len(report.untriaged), 'item', 'items')} untriaged; "
            "`bin/docket triage` to fold them into the queue."
        )
    if report.errors:
        lines.append(f"  {_plural(len(report.errors), 'error', 'errors')}; run `make docket`.")
    if report.advisories:
        lines.append(
            f"  Grooming due: {_plural(len(report.advisories), 'advisory', 'advisories')} "
            "(`make docket` to see them)."
        )
    if ready is not None and getattr(ready, "is_worth_cutting", False):
        completes = (
            f", completing {', '.join(ready.completed_features)}"  # type: ignore[attr-defined]
            if ready.completed_features  # type: ignore[attr-defined]
            else ""
        )
        lines.append(
            f"  Releasable: {len(ready.shippable)} finished item(s) since "  # type: ignore[attr-defined]
            f"{ready.current_version}{completes}. Offer {ready.suggested_version} "  # type: ignore[attr-defined]
            "before taking new work."
        )
    if plan is not None and plan.step is not None:
        position = (
            f"step {plan.step.ordinal} of {plan.total_steps}"
            if plan.step.ordinal is not None
            else "between numbered steps"
        )
        unparsed = " Timeline does not parse cleanly - check `wave`." if plan.problems else ""
        lines.append(
            f"Plan: {plan.version or 'unknown'}, {position} ({plan.step.label}). "
            f"Beat: {_beat_line(plan)}.{unparsed}"
        )
    lines.append(
        "`bin/docket status` shows the project by feature; `list` every item; `wave` the plan."
    )
    return "\n".join(lines)


def format_triage(report: Report, config: Config) -> str:
    """Every untriaged item, what is unset on it, and the rules that bind the answer.

    A worklist and a constraint sheet, deliberately not a recommendation. What
    an item is worth, how big it is, and what it belongs with are judgments,
    and a tool that guessed at them would produce something that looks
    authoritative and is not. What *is* mechanical is which fields are still
    empty and which rules `docket check` will apply the moment the status
    changes - and that is exactly what a session otherwise reloads a 300-line
    skill to recall, and then finds out afterwards whether it recalled
    correctly.

    The constraints are read from the settings and the checker rather than
    restated here, so they cannot drift from what the checker will actually
    say.
    """
    if not report.untriaged:
        return "Nothing is untriaged."

    lines = [f"{_plural(len(report.untriaged), 'item is', 'items are')} untriaged.", ""]
    for item in sorted(report.untriaged, key=lambda i: i.sort_key()):
        lines.append(f"{item.identifier}  {item.title}")
        lines.append(f"  unset: {_unset(item)}")
        missing = [
            marker for marker in (*REQUIRED_BRIEF, "**Done when.**") if marker not in item.body
        ]
        if missing:
            lines.append(f"  brief still missing: {', '.join(missing)}")
        declared = _declared(item)
        if declared:
            lines.append(f"  declared: {declared}")
        lines.append("")
        lines.extend(
            f"    {line}" if line.strip() else "" for line in item.body.strip().splitlines()
        )
        lines.append("")

    lines.append("The rules these answers have to satisfy:")
    lines.extend(f"  - {rule}" for rule in _triage_rules(report, config))
    lines.append("")
    lines.append("What each item is worth, how big it is and what it belongs with are not")
    lines.append("computed here. This prints the rules; applying them is yours.")
    return "\n".join(lines)


def _unset(item: Item) -> str:
    """The fields triage exists to fill, marking the ones the checker requires."""
    fields = [
        ("priority", item.priority, True),
        ("effort", item.effort, True),
        ("classes", ", ".join(item.classes), False),
        ("touches", ", ".join(item.touches), False),
        ("feature", item.feature, False),
    ]
    names = [f"{name}*" if required else name for name, value, required in fields if not value]
    return (", ".join(names) + "   (* required by `docket check`)") if names else "nothing"


def _declared(item: Item) -> str:
    parts = []
    if item.classes:
        parts.append(f"classes {', '.join(item.classes)}")
    if item.touches:
        parts.append(f"touches {', '.join(item.touches)}")
    if item.feature:
        parts.append(f"feature {item.feature}")
    return "; ".join(parts)


def _triage_rules(report: Report, config: Config) -> list[str]:
    """The constraints, stated with the counts that make each one checkable."""
    counts = report.counts
    top = next((p for p in PRIORITIES if counts.get(p)), PRIORITIES[0])
    rules = [
        f"{'/'.join(config.safety_classes)} classes force P0 or P1; `docket check` "
        "rejects them at P2 or P3.",
        f"the top band is {top}, holding {counts.get(top, 0)} of the "
        f"{config.top_band_limit} a session can choose between at a glance.",
        f"process work ({', '.join(config.process_classes)}) does not enter the top "
        "band ahead of the product work already in it - an item counts as process "
        "work only when every one of its classes is in that set.",
    ]
    if config.protected_paths:
        rules.append(
            f"`touches` naming {', '.join(config.protected_paths)} makes the item "
            "non-delegable whatever proves it, so a cheaper model can never take it."
        )
    if config.verify_required_from is not None:
        rules.append(
            "an item set to `ready` must name a `verify:` command, or record in "
            "`not-delegable` why no command can prove it. Run the command before "
            "writing it down."
        )
    rules.append(
        "a status past `untriaged` needs the full brief: "
        f"{', '.join((*REQUIRED_BRIEF, '**Done when.**'))}."
    )
    return rules


def format_gate(gate: Gate, debt_classes: tuple[str, ...]) -> str:
    """The debt owed before a milestone, as the two lists a gate record holds.

    Recording Gate 0 by hand meant reading every open item's classes and
    status, applying the rule, splitting the result by scope and typing the
    ids into the plan - a full pass over 48 items, repeated before every
    milestone. All of that is in the front matter, and none of it needs
    judgment. What still does is whether each item is really debt and whether
    the gate should open, which is why this prints two lists and no verdict.
    """
    if not gate.items:
        subject = f" carrying `{gate.feature}`" if gate.feature else ""
        return f"No open debt{subject}. Nothing to clear."

    lines = [
        f"{_plural(len(gate.items), 'open debt item', 'open debt items')}"
        + (f", against the `{gate.feature}` milestone." if gate.feature else ".")
    ]

    lines.append("")
    lines.append(
        f"Cleared before it begins - {len(gate.outside)} ({effort_total(gate.outside)}):"
        if gate.feature
        else f"Open debt - {len(gate.outside)} ({effort_total(gate.outside)}):"
    )
    lines.extend(_gate_lines(gate.outside))

    if gate.feature:
        lines.append("")
        lines.append(
            f"Cleared by the milestone itself - {len(gate.inside)} ({effort_total(gate.inside)}):"
        )
        lines.extend(_gate_lines(gate.inside))
        if not gate.inside:
            lines.append("  nothing carries that feature")

    lines.append("")
    lines.append(f"Debt is an open item classed {', '.join(debt_classes)}, or at needs-decision.")
    lines.append("Whether each of these is really debt, whether the gate should open, and")
    lines.append("what goes into the plan are not decided here. Recording it is a deliberate act.")
    return "\n".join(lines)


def _gate_lines(items: list[Item]) -> list[str]:
    if not items:
        return ["  nothing"]
    width = max(len(item.identifier) for item in items)
    lines = []
    for item in items:
        marks = ", ".join(item.classes) or "no classes"
        if item.status != "ready":
            marks = f"{item.status}, {marks}"
        lines.append(
            f"  {item.priority} {item.effort or '-'} {item.identifier:<{width}} "
            f"{item.title} ({marks})"
        )
    return lines


def format_check(report: Report) -> str:
    """The full report: everything wrong, and everything worth a second look."""
    lines = [
        f"docket: {len(report.open_items)} open ({_counts(report)}), "
        f"{len(report.untriaged)} untriaged, "
        f"{_plural(len(report.errors), 'error', 'errors')}, "
        f"{_plural(len(report.advisories), 'advisory', 'advisories')}"
    ]
    if report.errors:
        lines += ["", "Errors (the store is wrong; fix before committing):"]
        lines += [f"  {message}" for message in report.errors]
    if report.advisories:
        lines += ["", "Grooming advisories (judgment needed; nothing is failing):"]
        lines += [f"  {message}" for message in report.advisories]

    silent = undeclared(report.open_items)
    if silent:
        lines += [
            "",
            f"{_plural(len(silent), 'item declares', 'items declare')} no `touches`, so "
            "concurrency cannot be reasoned about for them:",
            f"  {', '.join(i.identifier for i in silent)}",
        ]
    if not report.errors and not report.advisories:
        lines.append("No errors, nothing due for grooming.")
    return "\n".join(lines)


def format_priority_groups(items: list[Item]) -> str:
    """The queue grouped by band, for a human reading the whole thing."""
    lines: list[str] = []
    for priority in PRIORITIES:
        band = [i for i in items if i.priority == priority]
        if not band:
            continue
        lines.append(f"{priority} ({len(band)})")
        for item in sorted(band, key=lambda i: i.sort_key()):
            lines.append(f"  {item.identifier} {item.title}")
    return "\n".join(lines)


def format_status(report: Report, ready: object = None, in_flight: set[str] | None = None) -> str:
    """The whole project at feature altitude, which is the altitude decisions happen at.

    `format_list` answers "which item", and that is the wrong question to open
    with. Nobody decides what to do next by reading twenty-three item titles;
    they decide by knowing which halves of the project are underway, which
    have not started, and what is urgent enough to ignore all of that. So this
    leads with features, names only the next item inside each, and keeps the
    individually-urgent work in a section of its own.
    """
    from .plan import features as group_features

    flight = in_flight or set()
    grouped = group_features(report.items)
    lines: list[str] = []

    underway = [f for f in grouped.values() if f.is_underway]
    not_started = [f for f in grouped.values() if f.open_items and not f.done]
    complete = [f for f in grouped.values() if f.is_complete]

    def next_in(feature: object) -> str:
        candidates = sorted(
            (i for i in feature.open_items if i.status != "blocked"),  # type: ignore[attr-defined]
            key=lambda i: i.sort_key(),
        )
        if not candidates:
            return "all remaining work is blocked"
        item = candidates[0]
        mark = " [IN FLIGHT]" if item.identifier in flight else ""
        return f"next: {item.identifier} {item.title} ({item.effort}){mark}"

    if underway:
        lines.append("Underway")
        for feature in sorted(underway, key=lambda f: -f.progress):
            lines.append(
                f"  {feature.name:<20} {len(feature.done)}/{len(feature.items)}  {next_in(feature)}"
            )
    if not_started:
        lines.append("")
        lines.append("Not started")
        for feature in sorted(not_started, key=lambda f: f.name):
            efforts = ", ".join(sorted({i.effort for i in feature.open_items if i.effort}))
            lines.append(f"  {feature.name:<20} 0/{len(feature.items)}  ({efforts})")

    loose = [
        i
        for i in report.open_items
        if not i.feature and i.status != "blocked" and i.identifier not in flight
    ]
    if loose:
        lines.append("")
        lines.append("Outside any feature - picked on priority alone")
        for item in sorted(loose, key=lambda i: i.sort_key())[:5]:
            note = f" - {item.model_guidance}" if item.model_guidance else ""
            lines.append(f"  {item.priority} {item.identifier} {item.title} ({item.effort}{note})")

    if complete:
        lines.append("")
        lines.append(f"Finished: {', '.join(sorted(f.name for f in complete))}")

    if ready is not None and getattr(ready, "shippable", None):
        lines.append("")
        done_note = (
            f", completing {', '.join(ready.completed_features)}"  # type: ignore[attr-defined]
            if ready.completed_features  # type: ignore[attr-defined]
            else ", completing no feature yet"
        )
        lines.append(
            f"Unreleased: {len(ready.shippable)} finished item(s) since "  # type: ignore[attr-defined]
            f"{ready.current_version}{done_note}."  # type: ignore[attr-defined]
        )
        lines.append(f"  Next version would be {ready.suggested_version}.")  # type: ignore[attr-defined]
    return "\n".join(lines)


def format_wave(plan: Wave) -> str:
    """Where the project stands on the cadence, and nothing about whether it should.

    Five lines at most, because this is read at the top of a session beside
    the digest, not studied. Each one states a fact with the file it came from
    behind it; none of them says whether the plan is still the right plan.
    """
    lines = [f"Version   {plan.version or 'unknown'}"]

    if plan.step is None:
        lines.append("Step      the timeline names no step after this version")
    else:
        position = (
            f"step {plan.step.ordinal} of {plan.total_steps}"
            if plan.step.ordinal is not None
            else f"between numbered steps ({STEP_SEPARATOR} on the timeline)"
        )
        lines.append(f"Step      {position}: {plan.step.label}")
    if plan.next_step is not None:
        lines.append(f"Next      {plan.next_step.label}")

    gate = plan.gate
    if gate is not None:
        entries = _plural(len(gate.entries), "entry", "entries")
        ids = _plural(len(gate.ids), "id", "ids")
        lines.append(f'Gate      recorded under "{gate.milestone.title}" ({entries}, {ids})')
        lines.append(f"          {len(gate.cleared)} cleared, {len(gate.outstanding)} open")
        if gate.outstanding:
            open_ids = [identifier for entry in gate.outstanding for identifier in entry.ids]
            lines.append(f"          {', '.join(open_ids)}")
        if gate.unknown_ids:
            lines.append(
                f"          not in the store, so not countable: {', '.join(gate.unknown_ids)}"
            )

    lines.append(f"Beat      {_beat_line(plan)}")
    if plan.problems:
        lines.append("")
        lines.append("The timeline table does not parse cleanly, so the step above may be wrong:")
        lines.extend(f"  {problem}" for problem in plan.problems)
    return "\n".join(lines)


def _beat_line(plan: Wave) -> str:
    """The beat, said as an instruction, with the count that makes it checkable."""
    if plan.beat == CLEAR and plan.gate is not None:
        remaining = _plural(len(plan.gate.outstanding), "entry", "entries")
        return f"clear the gate - {remaining} of {len(plan.gate.entries)} still open"
    if plan.beat == RELEASE:
        return f"release {plan.subject} - its gate is clear"
    if plan.beat == IMPLEMENT:
        return f"implement {plan.subject} - its gate is clear"
    if plan.beat == FREEZE:
        return f"freeze and record {plan.subject}'s debt list in its section"
    if plan.subject:
        return f"scope {plan.subject} here, which freezes its gate"
    return "scope the next milestone; the timeline names none after this version"
