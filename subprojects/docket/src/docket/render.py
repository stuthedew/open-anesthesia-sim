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

from .checks import Report
from .concurrency import undeclared
from .model import PRIORITIES, Item


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
    report: Report,
    in_flight: set[str] | None = None,
    protected_paths: tuple[str, ...] = (),
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


def format_digest(report: Report, in_flight: set[str] | None = None, ready: object = None) -> str:
    """The few lines injected into session context at startup.

    The release line is here rather than left for someone to ask about,
    because nobody asks. Finished work sits unshipped until a person happens
    to wonder, and the store already knows when there is enough of it to be
    worth raising.
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
    lines.append("`bin/docket status` shows the project by feature; `list` shows every item.")
    return "\n".join(lines)


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
