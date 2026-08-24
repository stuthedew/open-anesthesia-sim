"""Milestones, and the version bump that closes one.

A milestone is a named set of items and the version that ships when they are
all done. Keeping the membership on the items themselves rather than in a
separate manifest means assigning work to a release is a one-field edit to
one file - no shared list to contend over, and no way for the manifest and
the items to disagree about what is in the release.

The bump itself is mechanical: check every member is closed, rewrite one
version string, and write the notes from the items. Mechanical work that
recurs every release belongs in code, where it is deterministic and
testable, rather than in a checklist somebody follows by hand.
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


def read_version(pyproject: Path) -> str:
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
            reference = f" — `{item.commit}`" if item.commit else ""
            lines.append(f"- {item.identifier} {item.title}{reference}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
