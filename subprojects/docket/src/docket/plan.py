"""Choosing what to work on, and grouping work into things worth shipping.

Two failure modes this module exists to prevent, both of them expensive and
neither visible from a single item.

The first is scatter: picking the highest-priority item each time produces a
project where fifteen features are each five percent done and nothing is
finished. Work that belongs to a feature already underway is worth more than
equally-ranked work that starts a new one, because a finished feature can
ship and a half-finished one cannot.

The second is starting what someone else is already doing. That is knowable
from branch names, so it is checked rather than left to memory.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import EFFORTS, PRIORITIES, Item


@dataclass(frozen=True)
class Feature:
    """A coherent chunk of functionality, which may span several items."""

    name: str
    items: list[Item]

    @property
    def done(self) -> list[Item]:
        return [i for i in self.items if i.status == "done"]

    @property
    def open_items(self) -> list[Item]:
        return [i for i in self.items if i.is_open]

    @property
    def is_complete(self) -> bool:
        return bool(self.items) and not self.open_items

    @property
    def progress(self) -> float:
        return len(self.done) / len(self.items) if self.items else 0.0

    @property
    def is_underway(self) -> bool:
        """Started but not finished - the state worth finishing before starting more."""
        return bool(self.done) and bool(self.open_items)


@dataclass(frozen=True)
class Gate:
    """The debt owed before a milestone begins, split by who clears it.

    The split is the whole of the answer. Debt inside the milestone's own
    scope is cleared *by* it - requiring otherwise is a rule with no
    satisfying order, since the milestone exists to clear those items - while
    everything else is cleared first. Which side an item falls on is decided
    by the `feature` it carries, which is a fact in the file rather than a
    reading of the milestone's prose.
    """

    feature: str
    #: Cleared by the milestone itself: open debt carrying its feature.
    inside: list[Item]
    #: Cleared before it begins: everything else that is open debt.
    outside: list[Item]

    @property
    def items(self) -> list[Item]:
        return self.outside + self.inside


def effort_total(items: list[Item]) -> str:
    """The sizes in a batch, largest first: the shape a plan records them in."""
    counts = {effort: sum(1 for i in items if i.effort == effort) for effort in reversed(EFFORTS)}
    parts = [f"{count} {effort}" for effort, count in counts.items() if count]
    unsized = sum(1 for i in items if i.effort not in EFFORTS)
    if unsized:
        parts.append(f"{unsized} unsized")
    return ", ".join(parts) if parts else "nothing"


def is_debt(item: Item, debt_classes: tuple[str, ...]) -> bool:
    """Whether an open item is recorded debt rather than new work.

    Two rules, and the second wins where they meet. Debt is what the classes
    say it is - `defect`, `safety`, `science`, `refactor`, `perf` here - and
    an unanswered decision is debt whatever it is about, because a decision
    left open stops being one anybody can make. So a `feature`-classed item
    sitting at `needs-decision` is debt: what is owed is the decision, not the
    feature.
    """
    if not item.is_open:
        return False
    if item.status == "needs-decision":
        return True
    return any(cls in debt_classes for cls in item.classes)


def gate(items: list[Item], feature: str, debt_classes: tuple[str, ...]) -> Gate:
    """Compute a milestone's debt gate: the open debt, split by feature.

    It computes the list and nothing else. Whether an item is *really* debt,
    whether the gate should open, and what is written into the plan are
    judgments, and recording the frozen list stays a deliberate act - the
    command removes the transcription, not the decision.
    """
    debt = sorted((i for i in items if is_debt(i, debt_classes)), key=lambda i: i.sort_key())
    inside = [i for i in debt if feature and i.feature == feature]
    outside = [i for i in debt if not (feature and i.feature == feature)]
    return Gate(feature=feature, inside=inside, outside=outside)


def features(items: list[Item]) -> dict[str, Feature]:
    grouped: dict[str, list[Item]] = {}
    for item in items:
        if item.feature:
            grouped.setdefault(item.feature, []).append(item)
    return {
        name: Feature(name, sorted(grouped[name], key=lambda i: i.sort_key()))
        for name in sorted(grouped)
    }


@dataclass(frozen=True)
class Recommendation:
    """One suggested next piece of work, and why it is being suggested."""

    item: Item
    reason: str

    def describe(self) -> str:
        marks = [m for m in (self.item.effort, self.item.status) if m]
        if self.item.model_guidance:
            marks.append(f"{self.item.model_guidance} - use your strongest model")
        head = f"{self.item.priority} {self.item.identifier} {self.item.title}"
        return f"{head} ({', '.join(marks)})\n    {self.reason}"


def recommend(
    items: list[Item],
    in_flight: set[str] | None = None,
    *,
    effort: str | None = None,
    limit: int = 3,
) -> list[Recommendation]:
    """Rank the work worth starting now.

    Order of precedence, highest first: anything at `P0`, because that is what
    `P0` means; then work that finishes a feature already underway; then the
    highest-priority item that is ready to start. Items already in flight on a
    branch are excluded outright rather than ranked low - recommending work
    somebody is doing is worse than recommending nothing.
    """
    flight = in_flight or set()
    startable = [
        item
        for item in items
        if item.is_open
        and not item.is_untriaged
        and item.status != "blocked"
        and item.identifier not in flight
        and (effort is None or item.effort == effort)
    ]
    underway = {
        item.identifier: feature
        for feature in features(items).values()
        if feature.is_underway
        for item in feature.open_items
    }

    def rank(item: Item) -> tuple[int, int, int, str]:
        """Band first, then whether it finishes something already started.

        The feature preference is a tie-breaker inside a band, never across
        bands. Finishing work matters, but not more than the priority does: a
        P1 defect does not wait because a P3 feature is half built.
        """
        band = PRIORITIES.index(item.priority) if item.priority in PRIORITIES else len(PRIORITIES)
        finishes = 0 if item.identifier in underway else 1
        return (band, finishes, item.sort_key()[1], item.identifier)

    ranked: list[Recommendation] = []
    for item in sorted(startable, key=rank):
        if item.priority == "P0":
            reason = "P0: this comes before feature work."
        elif item.identifier in underway:
            feature = underway[item.identifier]
            reason = (
                f"Finishes '{feature.name}', which is {int(feature.progress * 100)}% done "
                f"({len(feature.open_items)} item(s) left). A shipped feature beats "
                f"progress on several."
            )
        else:
            reason = f"Highest-priority work that is ready to start ({item.priority})."
        ranked.append(Recommendation(item, reason))

    return ranked[:limit]


def blocked_summary(items: list[Item]) -> list[tuple[Item, list[str]]]:
    """Blocked items and what they are waiting on, for a grooming pass."""
    return [(item, list(item.blocked_by)) for item in items if item.status == "blocked"]
