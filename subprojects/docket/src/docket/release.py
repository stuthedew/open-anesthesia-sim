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
from typing import TYPE_CHECKING

from .model import Item

if TYPE_CHECKING:  # `roadmap` reads this module's version grammar, so the
    from .roadmap import Wave  # runtime import would close the cycle.

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


@dataclass(frozen=True)
class PreparedBump:
    """A version bump proved possible, holding the bytes it has yet to write.

    Cutting a release writes two things - the `milestone:` stamp on every
    item going out, and the version - and neither order is safe while the
    bump can still fail on the file it is about to rewrite. Stamping first
    left the store recording a release that never happened, with nothing
    saying which stamps to unpick; bumping first would leave a version
    claiming items it had not stamped.

    Separating the proof from the write removes the choice. Everything the
    bump can reject - an absent file, a file carrying no version field - is
    settled here, before the first stamp is written, and what survives is a
    path and the text to put at it.
    """

    path: Path
    previous: str
    text: str

    def write(self) -> str:
        """Put the prepared text in place, returning the version it replaced."""
        self.path.write_text(self.text, encoding="utf-8")
        return self.previous


def prepare_bump(pyproject: Path, version: str) -> PreparedBump:
    """Read and validate the single source of the project version.

    One string in one file. A project that resolves its displayed version
    from package metadata has nothing else to update; a second hard-coded
    copy somewhere else is a second thing to forget.

    Raises on a file that is absent or carries no version field. `read_version`
    tolerates both, because a store may be consulted away from any project;
    bumping is the operation that requires a version to exist.
    """
    text = pyproject.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if match is None:
        raise ValueError(f"{pyproject}: no version field to bump")
    return PreparedBump(
        path=pyproject,
        previous=match.group(2),
        text=VERSION_RE.sub(rf"\g<1>{version}\g<3>", text, count=1),
    )


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


# What the plan says about the version a bump has arrived at, as three answers.
# Two of them are the interesting ones, and they are opposite failures: the
# number is spoken for, or the number is free but is not the one the plan is
# waiting to cut.
STANDS = "stands"
PLANNED = "planned"
RESERVED = "reserved"


@dataclass(frozen=True)
class ReleaseOffer:
    """Whether a release may be recommended, and under which version.

    `Readiness` reads the store and only the store. That is what makes it
    honest about what is finished and blind to what a version *means*: the
    number it suggests is arithmetic on the last one, and a project that plans
    in versions has usually spent that number already. Where it has, cutting
    the suggestion is not a smaller release than the plan's - it is the plan's
    milestone going out under its own name with most of it missing, which a
    tag makes permanent and a reader has no way to see through afterwards.

    So this is the readiness answer with the plan folded in, as three
    outcomes: the number is free (`STANDS`), the plan names a different one to
    cut (`PLANNED`), or the plan has already given the number to a step it has
    not finished (`RESERVED`, and there is nothing to offer).

    Only the step the project is standing on is consulted, which is the whole
    of the question. Every step above it has shipped, and no bump from the
    current version can reach past the one immediately ahead.
    """

    kind: str
    #: The version to cut. Under `RESERVED` it is the version *not* to cut:
    #: the one the bump arrived at and the plan has spoken for.
    version: str
    #: The roadmap's own name for the step the answer turns on - "the workflow
    #: works", not "v0.2.8". Empty under `STANDS`, where no step is involved.
    milestone: str


def release_offer(ready: Readiness, plan: Wave | None) -> ReleaseOffer:
    """Reconcile the version a bump arrived at with the one the plan has planned.

    The plan is allowed to be absent or unreadable - `wave` declines rather
    than guesses, and a project with no roadmap is a legitimate state - and
    the offer then stands, because there is no plan for it to contradict.
    """
    from .roadmap import RELEASE

    suggested = ready.suggested_version.lstrip("v")
    if plan is None or plan.step is None or plan.step.version is None:
        return ReleaseOffer(STANDS, suggested, "")

    planned = "{}.{}.{}".format(*plan.step.version)
    if plan.beat == RELEASE:
        # The plan is itself asking for a release, so the only thing left to
        # disagree about is the number - and there the plan wins: it named the
        # version when the milestone was scoped, the bump inferred one from a
        # class label.
        if planned == suggested:
            return ReleaseOffer(STANDS, suggested, "")
        return ReleaseOffer(PLANNED, planned, plan.step.name)
    if planned == suggested:
        return ReleaseOffer(RESERVED, suggested, plan.step.name)
    return ReleaseOffer(STANDS, suggested, "")


def stamp(items: list[Item], version: str) -> list[Item]:
    """Record which release a batch of finished work went out in."""
    return [item.__class__(**{**item.__dict__, "milestone": version}) for item in items]


def outstanding_roadmap_edits(roadmap: str, version: str) -> list[str]:
    """The roadmap statements a cut release has just made wrong.

    Reported, never written. The version table's milestone column and the
    baseline section say what a release was *for*, which is a judgment about
    the work rather than a fact about the store - a generated row would either
    be thin or would overwrite something considered. What a tool can do is say
    exactly which statements are now stale, so the hand-off names them instead
    of leaving the next command to discover them as a test failure.

    Each string is one wrong statement, phrased as the state of the file
    rather than as an instruction, so a reader can check it against what they
    are looking at.
    """
    # Imported here rather than at module scope: `roadmap` reads this module's
    # version grammar, so a top-level import would close the cycle.
    from .roadmap import BASELINE_MARK, VERSION_TABLE_HEADING, baseline_heading, parse_version_table

    name = version.lstrip("v")
    rows = parse_version_table(roadmap)
    if not rows:
        return [f'there is no version table under "{VERSION_TABLE_HEADING}"']

    owed: list[str] = []
    row = next((candidate for candidate in rows if candidate.version == name), None)
    if row is None:
        owed.append(f"the version table has no row for v{name}")
    elif not row.is_baseline:
        owed.append(f'the v{name} row (line {row.line}) is not marked "{BASELINE_MARK}"')
    owed.extend(
        f'the v{other.version} row (line {other.line}) is still marked "{BASELINE_MARK}"'
        for other in rows
        if other.is_baseline and other.version != name
    )

    heading = baseline_heading(roadmap)
    if heading is None:
        owed.append('there is no "Current baseline: vX.Y.Z" heading')
    elif heading[1] != name:
        owed.append(f"the baseline heading (line {heading[0]}) still names v{heading[1]}")
    return owed
