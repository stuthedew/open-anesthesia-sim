"""Releases: what has shipped since the last version, and what to call the next.

**A milestone records what went out, it does not plan what will.** That
direction matters more than it looks. The obvious design is the other one -
assign items to `v0.3.0`, then ship when they are all closed - and it fails
in practice, because it makes shipping depend on somebody having done the
bookkeeping in advance. Anyone who forgets is told their release is empty
while a fortnight of finished work sits outside it.

So an item that is `done` with no `milestone` is simply unreleased, which is
the state finished work is naturally in. Cutting a release stamps that work
with the version it went out in. Nothing has to be decided up front, nothing
is forgotten, and the question "is it worth cutting one?" becomes answerable
by reading the store rather than by remembering what was promised.

Planning ahead is what `feature` is for. A feature says what a group of items
is *for*; a milestone says which release it left in.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .model import Item

VERSION_RE = re.compile(r'^(version\s*=\s*")([^"]+)(")', re.M)
SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class Milestone:
    """One release: the items in it, and whether they are finished."""

    name: str
    items: list[Item]

    @property
    def done(self) -> list[Item]:
        return [item for item in self.items if item.status == "done"]

    @property
    def outstanding(self) -> list[Item]:
        return [item for item in self.items if item.is_open]

    @property
    def is_complete(self) -> bool:
        return bool(self.items) and not self.outstanding

    @property
    def version(self) -> str:
        """The version string this milestone ships, without its leading `v`."""
        return self.name.lstrip("v")


def unreleased(items: list[Item]) -> list[Item]:
    """Finished work that has not gone out in any version yet.

    This is the default state of a closed item, not a state anyone has to put
    it into, which is the whole point: no one has to predict at capture time
    which release something will land in.
    """
    return sorted(
        (i for i in items if i.status == "done" and not i.milestone),
        key=lambda i: (i.closed or date.min, i.identifier),
    )


def milestones(items: list[Item]) -> dict[str, Milestone]:
    """Group items by the release they belong to, newest name last."""
    grouped: dict[str, list[Item]] = {}
    for item in items:
        if item.milestone:
            grouped.setdefault(item.milestone, []).append(item)
    return {
        name: Milestone(name, sorted(grouped[name], key=lambda i: i.sort_key()))
        for name in sorted(grouped, key=version_key)
    }


def version_key(name: str) -> tuple[int, ...]:
    """Sort versions numerically, so v0.10.0 follows v0.9.0 rather than v0.1.0."""
    match = SEMVER_RE.match(name.strip())
    if match is None:
        return (0, 0, 0)
    return tuple(int(part) for part in match.groups())


def suggest_version(current: str, items: list[Item], minor_classes: tuple[str, ...]) -> str:
    """The version a set of finished work should ship as.

    New functionality is a minor bump and everything else is a patch, which is
    the semantic-versioning rule stated in terms the items already carry. A
    major bump is deliberately not inferred: breaking a published interface is
    a decision somebody makes, not a fact derivable from a class label.
    """
    match = SEMVER_RE.match(current.strip())
    if match is None:
        return current
    major, minor, patch = (int(part) for part in match.groups())
    if any(cls in minor_classes for item in items for cls in item.classes):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def is_untagged(version: str, existing: frozenset[str]) -> bool:
    """Whether an already-shipped version has no tag, in a project that tags.

    A release cut without a tag leaves a permanent gap: `git describe
    --contains` resolves nothing for any commit in its span, so the question
    "which release did this change go out in" stops having an answer, and it
    cannot be repaired later with any confidence once the history has moved
    on. Refusing the *next* release is what turns that from a thing somebody
    remembers into a thing that cannot silently lapse.

    A project with no tags at all is not held to this. Its emptiness says the
    project does not tag releases, and adopting the practice is its decision,
    not this tool's.
    """
    if not version or not existing:
        return False
    name = version.lstrip("v")
    return f"v{name}" not in existing and name not in existing


def read_version(pyproject: Path) -> str:
    """The project's current version, or empty when there is none to read.

    A missing or version-less file is a legitimate state - a store consulted
    on its own, or a project that does not version - so it reports nothing
    rather than raising. Bumping is the operation that requires a version to
    exist, and that one still fails loudly.
    """
    if not pyproject.is_file():
        return ""
    match = VERSION_RE.search(pyproject.read_text(encoding="utf-8"))
    return match.group(2) if match else ""


def bump_version(pyproject: Path, version: str) -> str:
    """Rewrite the single source of the project version.

    One string in one file. A project that resolves its displayed version
    from package metadata has nothing else to update; a second hard-coded
    copy somewhere else is a second thing to forget.
    """
    text = pyproject.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if match is None:
        raise ValueError(f"{pyproject}: no version field to bump")
    previous = match.group(2)
    pyproject.write_text(VERSION_RE.sub(rf"\g<1>{version}\g<3>", text, count=1), encoding="utf-8")
    return previous


def release_notes(milestone: Milestone, today: date) -> str:
    """Write the release notes from the items themselves.

    Generated rather than composed, so the notes cannot claim something the
    items do not, and so nothing shipped goes unmentioned because whoever
    wrote the notes forgot it.
    """
    lines = [f"## {milestone.name} - {today.isoformat()}", ""]
    by_class: dict[str, list[Item]] = {}
    for item in milestone.done:
        key = item.classes[0] if item.classes else "other"
        by_class.setdefault(key, []).append(item)
    for name in sorted(by_class):
        lines.append(f"### {name}")
        lines.append("")
        for item in by_class[name]:
            # The pull request in preference to the commit: it is what a reader
            # can still follow after a squash-merge discards the branch, and a
            # bare `#48` renders as a link where these notes are read.
            reference = (
                f" — #{item.pr}" if item.pr else (f" — `{item.commit}`" if item.commit else "")
            )
            lines.append(f"- {item.identifier} {item.title}{reference}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class Readiness:
    """Whether there is enough finished work to be worth cutting a release.

    Deliberately advisory. It reports what is shippable and what the version
    would be; it does not decide that a release should happen, because that
    depends on things no store knows - whether a demo is on Friday, whether
    the next item is nearly done, whether anyone wants to review it.
    """

    shippable: list[Item]
    completed_features: list[str]
    partial_features: list[str]
    current_version: str
    suggested_version: str

    @property
    def is_worth_cutting(self) -> bool:
        """Whether to raise it unprompted.

        A finished feature is worth mentioning on its own, however few items
        it took. Otherwise it takes a few closed items before the suggestion
        is more useful than it is noise.
        """
        return bool(self.completed_features) or len(self.shippable) >= 3


def readiness(items: list[Item], current_version: str, minor_classes: tuple[str, ...]) -> Readiness:
    """What could ship right now, and what it would be called."""
    from .plan import features as group_features

    shippable = unreleased(items)
    shipped_ids = {item.identifier for item in shippable}

    completed: list[str] = []
    partial: list[str] = []
    for name, feature in group_features(items).items():
        if not any(i.identifier in shipped_ids for i in feature.items):
            continue
        (completed if feature.is_complete else partial).append(name)

    return Readiness(
        shippable=shippable,
        completed_features=sorted(completed),
        partial_features=sorted(partial),
        current_version=current_version,
        suggested_version=suggest_version(current_version, shippable, minor_classes),
    )


def stamp(items: list[Item], version: str) -> list[Item]:
    """Record which release a batch of finished work went out in."""
    return [item.__class__(**{**item.__dict__, "milestone": version}) for item in items]
