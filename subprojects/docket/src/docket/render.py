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


def _marks(item: Item, in_flight: set[str]) -> str:
    marks = [m for m in (item.effort, item.status) if m]
    if item.milestone:
        marks.append(item.milestone)
    if item.identifier in in_flight:
        marks.append("IN FLIGHT")
    if item.model_guidance is not None:
        marks.append(f"{item.model_guidance}, strongest model")
    return ", ".join(marks)


def format_list(report: Report, in_flight: set[str] | None = None) -> str:
    """One line per open item: the queue without the briefs."""
    flight = in_flight or set()
    if not report.open_items and not report.untriaged:
        return ""

    lines = [f"Docket: {len(report.open_items)} open - {_counts(report)}."]
    ordered = sorted(report.open_items, key=lambda i: i.sort_key())
    width = max((len(i.identifier) for i in ordered), default=0)
    for item in ordered:
        lines.append(
            f"{item.priority} {item.identifier:<{width}} {item.title} ({_marks(item, flight)})"
        )

    if report.untriaged:
        lines.append("")
        lines.append(f"Untriaged ({_plural(len(report.untriaged), 'item', 'items')}):")
        for item in sorted(report.untriaged, key=lambda i: i.sort_key()):
            lines.append(f"   {item.identifier:<{width}} {item.title}")
    lines.append("Read an item's brief before starting it; this listing is for choosing.")
    return "\n".join(lines)


def format_digest(report: Report, in_flight: set[str] | None = None) -> str:
    """The few lines injected into session context at startup."""
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
    lines.append("`bin/docket list` shows the queue; read an item's brief before starting it.")
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
