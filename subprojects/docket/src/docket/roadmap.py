"""`ROADMAP.md` as a structure, so the plan can be read rather than recalled.

A queue answers "which item next". It cannot answer "what is the project
*doing* next", because that question is settled by the plan and the plan is
prose. This module reads the three parts of that prose which are not prose at
all - the release train, the milestone sections, and the frozen debt list a
milestone records - and hands them to `wave` as a position on the cadence.

**It computes; it decides nothing.** Whether the sentence beside a timeline
row is still true, whether a gate *should* open early, whether a scoped
milestone is scoped well: none of that is derivable from the file, so none of
it is attempted. A line guessing at any of it would be worse than no line,
because it would look authoritative.

The grammar lives here rather than in `tools/doc_check.py`, where it started,
because two copies of it would drift and the drift would be silent. `docket`
is the thing that reasons about project state and already reads the version
and the store; `doc_check` is a checker that needs the same grammar to hold
the table to it. Both are standard-library only and both must run in a bare
checkout with no virtualenv, so the constraint that shaped the parser is
identical on either side.

The three markdown primitives at the top are exported for the same reason:
`doc_check` reads a table of its own with them, and a second implementation
of "the rows under this heading" is a second thing to keep true.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass

from .release import SEMVER_RE
from .store import ID_PATTERN

# --- markdown primitives ----------------------------------------------------

HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*#*\s*$")
TABLE_ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")
BULLET_RE = re.compile(r"^[-*]\s+(?P<text>\S.*)$")


def table_rows(text: str, heading: str, level: int = 2) -> Iterator[tuple[int, list[str]]]:
    """Yield the rows of the first markdown table under `heading`.

    `level` is the heading's depth, so a table under a `###` subsection can be
    read as readily as one under a `##` section. Any heading at or above that
    depth ends the search, which is what stops a table further down the file
    being mistaken for this one.
    """
    lines = text.splitlines()
    in_section = False
    started = False
    for index, line in enumerate(lines, start=1):
        heading_match = HEADING_RE.match(line)
        if heading_match is not None and len(heading_match.group("hashes")) <= level:
            if started:
                return
            in_section = (
                len(heading_match.group("hashes")) == level
                and heading_match.group("title").strip() == heading
            )
            continue
        if not in_section:
            continue
        match = TABLE_ROW_RE.match(line)
        if match is None:
            if started:
                return
            continue
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if all(set(cell) <= set("-: ") and cell for cell in cells):
            started = True
            continue
        if started:
            yield index, cells


# --- the version table ------------------------------------------------------

# Which version the project is *on* is stated in three places that must agree:
# the version file, one row of this table, and the prose heading below it. The
# grammar of the row is read here for the same reason the timeline's is - two
# copies of it would drift, and the drift would be in the one document that
# says which release is current.
VERSION_TABLE_HEADING = "Versioning decision"
# The status cell marking a release as shipped. Matched as a substring: this
# project writes "Completed / current baseline" on the row it is standing on.
COMPLETED = "Completed"
BASELINE_MARK = "current baseline"
BASELINE_HEADING_RE = re.compile(r"^Current baseline:\s*v?(?P<version>\d+\.\d+\.\d+)\b")


@dataclass(frozen=True)
class VersionRow:
    """One row of the version table: a release, and what is claimed about it."""

    line: int
    version: str
    status: str

    @property
    def is_baseline(self) -> bool:
        return BASELINE_MARK in self.status.casefold()


def parse_version_table(text: str) -> list[VersionRow]:
    """Read the version table, skipping rows whose first cell is not a version.

    A row that does not open with a version is not a release row - the table
    is written by hand and may carry one - so it is passed over rather than
    reported. What the table must get right is the releases it *does* name,
    and that is what the checker asks about.
    """
    rows: list[VersionRow] = []
    for line, cells in table_rows(text, VERSION_TABLE_HEADING):
        if len(cells) < 2 or SEMVER_RE.match(cells[0]) is None:
            continue
        rows.append(VersionRow(line=line, version=cells[0].lstrip("v"), status=cells[1]))
    return rows


def baseline_heading(text: str) -> tuple[int, str] | None:
    """The version named by the `## Current baseline: vX.Y.Z` heading, if any."""
    for index, line in enumerate(text.splitlines(), start=1):
        heading = HEADING_RE.match(line)
        if heading is None:
            continue
        match = BASELINE_HEADING_RE.match(heading.group("title").strip())
        if match is not None:
            return index, match.group("version")
    return None


# --- the release train ------------------------------------------------------

TIMELINE_HEADING = "The timeline"

# The release train's row grammar. A step is bold, and is one of four things:
# a milestone carrying a concrete version, a patch track carrying a `x`
# placeholder, a numbered gate, or an unnumbered marker such as "MVP complete".
# The separator is the em dash the table is written with; spelling it out here
# is what makes a hyphen typed in its place a failure rather than a silent
# reclassification of the row as a marker.
#
# Milestone *section* headings are written with a plain hyphen instead, and are
# matched below by searching for the version rather than by splitting on a
# separator - assuming one punctuation mark for both would read the table and
# the sections inconsistently, which is the kind of near-miss that produces a
# confident wrong answer.
STEP_SEPARATOR = "—"

BOLD_RE = re.compile(r"^\*\*(?P<label>.+)\*\*$")
MILESTONE_RE = re.compile(
    rf"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+) {STEP_SEPARATOR} (?P<name>\S.*)$"
)
PATCH_TRACK_RE = re.compile(
    rf"^v(?P<major>\d+)\.(?P<minor>\d+)\.x {STEP_SEPARATOR} (?P<name>\S.*)$"
)
GATE_RE = re.compile(r"^Gate (?P<number>\d+)$")
ORDINAL_RE = re.compile(r"^(?P<number>\d+)\+?$")
# A step that opens like a version but matches neither version form. Caught
# separately so a typo (`v0.4` , `v0.4.0 - name`) fails loudly instead of
# passing as a marker with an odd name.
VERSIONISH_RE = re.compile(r"^v\d")


@dataclass(frozen=True)
class TimelineStep:
    """One row of `ROADMAP.md`'s release train, as the grammar reads it."""

    line: int
    # The `#` column. `None` for a row written `—`, which marks something
    # that sits on the timeline without being a step of its own: the patch
    # track under a milestone, and the "MVP complete" boundary.
    ordinal: int | None
    kind: str  # "milestone" | "patch-track" | "gate" | "marker"
    label: str  # the step cell, without its bold markers
    # Milestone rows only. A patch track carries no patch number by
    # construction, and a gate deliberately has no version at all.
    version: tuple[int, int, int] | None
    name: str  # the prose after the version or gate number


def parse_timeline(text: str) -> tuple[list[TimelineStep], list[str]]:
    """Read the release train from `ROADMAP.md`, with any grammar breaches.

    Returns the steps in the order the table lists them, and the problems that
    stop a row being read. Callers wanting the plan use the steps; the checker
    reports the problems. What a row *means* - whether the prose beside it is
    still true, whether the milestone is scoped well - is judgment, and is
    deliberately not attempted here.
    """
    steps: list[TimelineStep] = []
    problems: list[str] = []

    for line, cells in table_rows(text, TIMELINE_HEADING, level=3):
        if len(cells) < 2:
            problems.append(f"line {line}: timeline row has no step column")
            continue
        ordinal_cell, step_cell = cells[0], cells[1]

        bold = BOLD_RE.match(step_cell)
        if bold is None:
            problems.append(f"line {line}: timeline step {step_cell!r} is not bold")
            continue
        label = bold.group("label")

        ordinal: int | None = None
        if ordinal_cell != STEP_SEPARATOR:
            ordinal_match = ORDINAL_RE.match(ordinal_cell)
            if ordinal_match is None:
                problems.append(
                    f"line {line}: timeline number {ordinal_cell!r} is neither a number,"
                    f" a number with '+', nor {STEP_SEPARATOR!r}"
                )
                continue
            ordinal = int(ordinal_match.group("number"))

        milestone = MILESTONE_RE.match(label)
        patch_track = PATCH_TRACK_RE.match(label)
        gate = GATE_RE.match(label)
        if milestone is not None:
            version = (
                int(milestone.group("major")),
                int(milestone.group("minor")),
                int(milestone.group("patch")),
            )
            kind, name = "milestone", milestone.group("name")
        elif patch_track is not None:
            version = (int(patch_track.group("major")), int(patch_track.group("minor")), -1)
            kind, name = "patch-track", patch_track.group("name")
        elif gate is not None:
            version, kind, name = None, "gate", gate.group("number")
        elif VERSIONISH_RE.match(label):
            problems.append(
                f"line {line}: timeline step {label!r} opens like a version but matches"
                f" neither 'vX.Y.Z {STEP_SEPARATOR} name' nor 'vX.Y.x {STEP_SEPARATOR} name'"
            )
            continue
        else:
            version, kind, name = None, "marker", label

        steps.append(
            TimelineStep(
                line=line, ordinal=ordinal, kind=kind, label=label, version=version, name=name
            )
        )

    problems.extend(_timeline_order(steps))
    return steps, problems


def _timeline_order(steps: Sequence[TimelineStep]) -> Iterator[str]:
    """Report rows that read correctly but sit in the wrong place."""
    previous_ordinal: int | None = None
    previous_version: tuple[int, int, int] | None = None
    previous_gate: int | None = None
    latest_milestone: tuple[int, int] | None = None

    for step in steps:
        if step.ordinal is not None:
            if previous_ordinal is not None and step.ordinal <= previous_ordinal:
                yield (
                    f"line {step.line}: timeline number {step.ordinal} does not follow"
                    f" {previous_ordinal}"
                )
            previous_ordinal = step.ordinal

        if step.kind == "milestone" and step.version is not None:
            if previous_version is not None and step.version <= previous_version:
                yield (
                    f"line {step.line}: milestone {step.label!r} is not later than the"
                    f" milestone above it"
                )
            previous_version = step.version
            latest_milestone = step.version[:2]

        if step.kind == "patch-track" and step.version is not None:
            series = step.version[:2]
            if latest_milestone is None or series != latest_milestone:
                above = (
                    "no milestone"
                    if latest_milestone is None
                    else f"v{latest_milestone[0]}.{latest_milestone[1]}"
                )
                yield (
                    f"line {step.line}: patch track {step.label!r} does not belong to"
                    f" {above}, the milestone above it"
                )

        if step.kind == "gate":
            number = int(step.name)
            if previous_gate is not None and number <= previous_gate:
                yield f"line {step.line}: Gate {number} does not follow Gate {previous_gate}"
            previous_gate = number


# --- milestone sections and the gates they record ---------------------------

# A milestone's section is found by the version in its heading, not by the
# words around it: this repository writes "Completed:", "Current baseline:",
# "Next milestone:" and "Milestone after next:", and which prefix a milestone
# carries is editorial. The version is the identity.
SECTION_VERSION_RE = re.compile(r"\bv(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\b")
# Punctuation a heading may put between the version and the milestone's name.
SECTION_SEPARATORS = " -–—: "

# The four subsections `ROADMAP.md`'s development rules require of a scoped
# milestone, matched as prefixes because the last of them names its version
# ("Explicitly out of scope for v0.4.0").
# Where a milestone records the debt list frozen when it was scoped, and where
# it states the scope it clears itself. These two subsections are the whole of
# what places an id; the reasoning is beneath `SECTION_ID_RE`.
GATE_SUBSECTION = "debt gate"
SCOPE_SUBSECTION = "required scope"
REQUIRED_SUBSECTIONS = ("goal", SCOPE_SUBSECTION, "definition of done", "explicitly out of scope")

# An item id at the head of a gate entry, possibly the second of a pair
# ("PL-Z4GF **and PL-SWFM**"), possibly wrapped in emphasis. Only the head of
# the entry is read: an id mentioned later in the sentence is prose about
# another item, not a second thing the entry is waiting on.
LEADING_ID_RE = re.compile(rf"^[*_\s]*(?:and[*_\s]+)?[*_\s]*(?P<id>{ID_PATTERN})")

# An id wherever it sits in a sentence. Used only inside the two subsections
# that record membership, because the sentence around an id is unreadable and
# a section says far more about an id than "this is mine".
#
# Membership is read from *where* an id is written, never from the fact that
# it is written. A milestone's section names ids for at least four reasons -
# an entry of its frozen list, scope the milestone clears itself, commentary
# on an entry ("blocked by PL-ZQ9C above"), and an exclusion set out at length
# ("PL-68XK ... is *not* admitted by this rule") - and only the first two are
# membership. Counting every mention read the exclusions as the opposite of
# what they say, which is queue item PL-HDY6.
#
# So each of the two structures is read by its own grammar, and nothing else
# in the section is read at all:
#
# - the frozen list, by its entries' heads, because an entry is one bullet per
#   problem and an id later in the sentence is prose about another item;
# - `Required scope`, in full, because a milestone names what it covers in
#   whatever grammar the sentence wanted - "(queue item PL-DHV7)" mid-bullet,
#   or a paragraph - and the heading has already declared that everything
#   under it is scope.
#
# What this costs is stated rather than hidden: scope recorded *only* in the
# section's prose is not read, so an id named nowhere but a paragraph is
# placed nowhere. That is the safe direction to fail. An unread mention makes
# no claim, where an over-read one tells a session that work the milestone
# excludes is the work the milestone is waiting on.
SECTION_ID_RE = re.compile(ID_PATTERN)


@dataclass(frozen=True)
class GateEntry:
    """One line of a frozen debt list: the ids it holds, and what it says.

    Entries rather than ids are the gate's size, because one problem may have
    surfaced under two ids and be recorded as a single entry. Both numbers are
    reported; neither is inferred from the other.
    """

    line: int
    ids: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class MilestoneSection:
    """One `## ... vX.Y.Z ...` section of the roadmap, as far as it is decidable."""

    line: int
    title: str
    version: tuple[int, int, int]
    name: str
    subsections: tuple[str, ...]
    gate_heading: str
    gate_line: int
    gate_entries: tuple[GateEntry, ...]
    #: The ids this section *places*: its frozen list's entries, then the ids
    #: named under `Required scope`, in the order they appear. An id the
    #: section merely mentions is absent, deliberately - see `SECTION_ID_RE`.
    scope_ids: tuple[str, ...]

    @property
    def label(self) -> str:
        rendered = "v{}.{}.{}".format(*self.version)
        return f"{rendered} {STEP_SEPARATOR} {self.name}" if self.name else rendered

    @property
    def is_scoped(self) -> bool:
        """Whether the section carries the four subsections scoping requires.

        A structural test, and only that. It says the headings are present, not
        that what is written under them is any good - which is judgment, and
        belongs to the person reading the section rather than to this.
        """
        lowered = tuple(title.lower() for title in self.subsections)
        return all(
            any(title.startswith(required) for title in lowered)
            for required in REQUIRED_SUBSECTIONS
        )

    @property
    def records_a_gate(self) -> bool:
        return bool(self.gate_entries)

    @property
    def records_its_own_scope(self) -> bool:
        """Whether the section carries a `Required scope` of its own.

        Structural, like `is_scoped`, and narrower: it asks for that one
        subsection rather than all four, because one thing turns on it that
        the others do not. A section recording a gate and no scope of its own
        is a milestone whose frozen list *is* its content - `ROADMAP.md` says
        exactly that of v0.2.8 - so clearing that list finishes the milestone
        instead of unblocking work that follows it.
        """
        lowered = (title.lower() for title in self.subsections)
        return any(title.startswith(SCOPE_SUBSECTION) for title in lowered)


def _leading_ids(text: str) -> tuple[str, ...]:
    ids: list[str] = []
    rest = text
    while True:
        match = LEADING_ID_RE.match(rest)
        if match is None:
            return tuple(ids)
        ids.append(match.group("id"))
        rest = rest[match.end() :]


def _subsection_ids(lines: Sequence[str], start: int) -> Iterator[str]:
    """Every item id named under one `###` heading, in the order they appear.

    `start` is the heading's line number, so reading begins on the line after
    it and stops at the next heading of the same depth or shallower - the same
    bound `_gate_entries` uses, for the same reason.
    """
    for index in range(start, len(lines)):
        heading = HEADING_RE.match(lines[index])
        if heading is not None and len(heading.group("hashes")) <= 3:
            return
        for match in SECTION_ID_RE.finditer(lines[index]):
            yield match.group(0)


def _scope_ids(entries: Sequence[GateEntry], scope_ids: Iterable[str]) -> tuple[str, ...]:
    """The section's frozen entries and its own scope, deduplicated in order.

    The gate half is taken from the parsed entries rather than re-read, so the
    ids a gate holds and the ids it places cannot drift apart.
    """
    seen: dict[str, None] = {}
    for entry in entries:
        for identifier in entry.ids:
            seen.setdefault(identifier, None)
    for identifier in scope_ids:
        seen.setdefault(identifier, None)
    return tuple(seen)


def _gate_entries(lines: Sequence[str], start: int) -> tuple[GateEntry, ...]:
    """Read the list entries under a gate heading, ignoring its prose.

    An entry is a top-level bullet that opens with an item id. The prose around
    it - why the list was frozen, how many were done on some past date, which
    of them the milestone clears itself - is left where it is: it is a person's
    summary of the same facts, and reading it would mean parsing sentences.
    """
    entries: list[GateEntry] = []
    line_number = 0
    parts: list[str] = []

    def flush() -> None:
        if not parts:
            return
        text = " ".join(parts)
        ids = _leading_ids(text)
        if ids:
            entries.append(GateEntry(line=line_number, ids=ids, text=text))

    for index in range(start, len(lines)):
        line = lines[index]
        heading = HEADING_RE.match(line)
        if heading is not None and len(heading.group("hashes")) <= 3:
            break
        bullet = BULLET_RE.match(line)
        if bullet is not None:
            flush()
            line_number, parts = index + 1, [bullet.group("text")]
        elif parts and line.strip() and line[:1].isspace():
            parts.append(line.strip())
        elif parts:
            flush()
            parts = []
    flush()
    return tuple(entries)


def parse_milestones(text: str) -> list[MilestoneSection]:
    """Read every milestone section of the roadmap, in version order."""
    lines = text.splitlines()
    found: list[MilestoneSection] = []

    line_number = 0
    title = ""
    version: tuple[int, int, int] | None = None
    name = ""
    subsections: list[str] = []
    gate: tuple[int, str] | None = None
    scope: int | None = None

    def flush() -> None:
        if version is None:
            return
        heading_line, heading_title = gate or (0, "")
        entries = _gate_entries(lines, heading_line) if gate else ()
        found.append(
            MilestoneSection(
                line=line_number,
                title=title,
                version=version,
                name=name,
                subsections=tuple(subsections),
                gate_heading=heading_title,
                gate_line=heading_line,
                gate_entries=entries,
                scope_ids=_scope_ids(entries, _subsection_ids(lines, scope) if scope else ()),
            )
        )

    for index, line in enumerate(lines, start=1):
        heading = HEADING_RE.match(line)
        if heading is None:
            continue
        depth = len(heading.group("hashes"))
        heading_title = heading.group("title").strip()
        if depth <= 2:
            flush()
            match = SECTION_VERSION_RE.search(heading_title) if depth == 2 else None
            if match is None:
                version = None
                continue
            line_number, title = index, heading_title
            version = (
                int(match.group("major")),
                int(match.group("minor")),
                int(match.group("patch")),
            )
            name = heading_title[match.end() :].strip(SECTION_SEPARATORS)
            subsections, gate, scope = [], None, None
        elif version is not None and depth == 3:
            subsections.append(heading_title)
            if heading_title.lower().startswith(GATE_SUBSECTION):
                gate = (index, heading_title)
            elif heading_title.lower().startswith(SCOPE_SUBSECTION):
                scope = index
    flush()

    return sorted(found, key=lambda section: section.version)


# --- milestones an item may wait on -----------------------------------------


@dataclass(frozen=True)
class MilestoneStates:
    """Which milestone versions the roadmap names, and which of them are scoped.

    The two answers a `blocked-by: v0.5.0` needs and the store cannot give.
    `known` is what makes a typo an error rather than a permanent block;
    `scoped` is what makes the edge clear itself.
    """

    #: Every version the roadmap names as a milestone, written `vX.Y.Z`. Read
    #: from the timeline *and* from the section headings, because a milestone
    #: is placed on the timeline long before it has a section - which is
    #: exactly the interval a milestone blocker exists to cover.
    known: frozenset[str]
    #: The subset a milestone blocker is satisfied by. Two ways in, and the
    #: second is not redundant. Carrying the four subsections scoping requires
    #: is the intended one - structural, per `MilestoneSection.is_scoped`: it
    #: says the headings are there, never that what is written under them is
    #: any good. Having *shipped* is the other, because a released milestone
    #: was scoped whether or not its section still shows it: v0.2.8 and v0.3.0
    #: both carry sections that answer `is_scoped` False, v0.2.8 because
    #: `ROADMAP.md` says its frozen list *is* its content. Without this a
    #: blocker naming either would never clear and nothing would report it,
    #: which is the silent-wrong outcome this field exists to remove.
    cleared: frozenset[str]

    def is_known(self, version: str) -> bool:
        return version in self.known

    def is_cleared(self, version: str) -> bool:
        return version in self.cleared


def _rendered(version: tuple[int, int, int]) -> str:
    return "v{}.{}.{}".format(*version)


def milestone_states(text: str) -> MilestoneStates:
    """Read which milestones the roadmap names and which of them are settled.

    Patch tracks are deliberately absent. A `v0.4.x` row carries no patch
    number by construction, so nothing writable in `blocked-by` names one, and
    a milestone blocker is about a scoping round rather than about a track that
    freezes no gate.
    """
    steps, _ = parse_timeline(text)
    known = {
        _rendered(step.version)
        for step in steps
        if step.kind == "milestone" and step.version is not None
    }
    sections = parse_milestones(text)
    known.update(_rendered(section.version) for section in sections)

    cleared = {_rendered(section.version) for section in sections if section.is_scoped}
    released = {f"v{row.version}" for row in parse_version_table(text) if COMPLETED in row.status}
    known.update(released)
    cleared.update(released)
    return MilestoneStates(known=frozenset(known), cleared=frozenset(cleared))


# --- where the project is on the cadence ------------------------------------

# The four beats `ROADMAP.md` specifies per milestone, plus the one the
# project's Gate 0 exception adds: a gate that earns a release of its own is
# released before the milestone it gates is implemented.
SCOPE = "scope"
FREEZE = "freeze"
CLEAR = "clear"
RELEASE = "release"
IMPLEMENT = "implement"


@dataclass(frozen=True)
class GateStatus:
    """A frozen debt list, counted against the store that holds its items."""

    milestone: MilestoneSection
    entries: tuple[GateEntry, ...]
    cleared: tuple[GateEntry, ...]
    outstanding: tuple[GateEntry, ...]
    #: Ids the gate names that the store does not hold. A gate cannot be shown
    #: clear while one of these stands: the entry may be a typo or a file that
    #: never existed, and either way its state is unknown rather than closed.
    unknown_ids: tuple[str, ...]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(identifier for entry in self.entries for identifier in entry.ids)

    @property
    def is_clear(self) -> bool:
        return not self.outstanding and not self.unknown_ids


# What a milestone section says about an id, as three answers rather than two.
IN_SCOPE = "in-scope"
UNPLACED = "unplaced"
OUT_OF_SCOPE = "out-of-scope"


@dataclass(frozen=True)
class Scope:
    """Where the plan places an item, relative to the beat now due.

    Three answers, and the middle one is why there are three. An id the
    milestone the current beat is about places is work this step includes. An
    id only a *later* milestone places is work this step has not reached. An
    id no section places is neither: the roadmap places most of the queue
    nowhere, and reading that silence as exclusion would be a verdict rather
    than a fact.

    A section *earlier* than the anchor places nothing either. A released
    milestone's narrative names the items it discussed, which records where a
    problem was raised rather than what is current work - `PL-026` sits in
    v0.2.7's release narrative and on v0.4.0's frozen gate list, and only the
    second of those says anything about what to do now.

    Two structures are the whole of the evidence, per `SECTION_ID_RE`: the
    frozen list a section records, and its `Required scope`. So a milestone
    that records scope in prose alone records it invisibly here - and one that
    excludes something in prose alone excludes it invisibly too, which is the
    same silence rather than its opposite. Both limitations are recorded in
    the README beside the concurrency one.
    """

    #: The milestone the current beat is about, labelled as the roadmap does.
    #: Empty when there is no such milestone, which leaves every id unplaced.
    anchor: str
    #: Ids the *current step* includes. Usually the anchor's own section, but
    #: while a gate is being cleared it is the gate's entries alone - see
    #: `milestone_scope`.
    current: frozenset[str]
    #: Ids only a later milestone places, mapped to the earliest such one.
    #: While a gate is being cleared this also holds the anchor's own scope,
    #: mapped to the anchor, because that work the step has not reached either.
    later: Mapping[str, str]
    #: The timeline row the project stands on, when the roadmap lets a gate
    #: ship as a different version from the milestone recording it. Empty when
    #: the step and the anchor are the same milestone, which is the ordinary
    #: case and needs no distinguishing.
    step_label: str = ""
    #: Whether `current` is a gate's entries rather than a milestone's whole
    #: section. A caller naming where an id sits needs this and `step_label`
    #: separately: they answer "on a gate?" and "which row?", and the beat can
    #: move off the gate while the two labels still differ.
    clearing: bool = False

    def placement(self, identifier: str) -> str:
        if identifier in self.current:
            return IN_SCOPE
        if identifier in self.later:
            return OUT_OF_SCOPE
        return UNPLACED

    def milestone(self, identifier: str) -> str:
        """The later milestone naming this id, as `v0.4.0`, or `""`."""
        return self.later.get(identifier, "")


def milestone_scope(
    sections: Sequence[MilestoneSection],
    anchor: MilestoneSection | None,
    *,
    clearing_gate: GateStatus | None = None,
    step_label: str = "",
) -> Scope:
    """Read each milestone section for the ids it places, against the anchor.

    `sections` is expected in version order, so the *earliest* later milestone
    placing an id is the one reported: an item placed by both v0.3.0 and
    v0.4.0 is v0.3.0's, and saying so is what stops the marking overstating
    how far off the work is.

    **`clearing_gate` narrows the anchor to its gate.** A section places ids
    through two structures, and while a gate is open only one of them is work
    the current step includes: `ROADMAP.md` has the gate clear *before* the
    milestone it gates is implemented, so an id in that milestone's `Required
    scope` is work the step has not reached, exactly like an id a later
    milestone names. Passing the gate says the beat is to clear it, and the
    anchor's non-gate scope moves into `later` under the anchor's own version.

    Without it the anchor's whole section is the current step, which is right
    once the gate is clear and the milestone is being implemented, and is what
    a caller reading a section directly means. It is opt-in for that reason
    rather than inferred here: this function is given no beat (queue item
    PL-1J0P).
    """
    if anchor is None:
        return Scope(anchor="", current=frozenset(), later={})
    anchor_label = "v{}.{}.{}".format(*anchor.version)
    placed = frozenset(anchor.scope_ids)
    if clearing_gate is None:
        current = placed
        later: dict[str, str] = {}
    else:
        current = frozenset(
            identifier for entry in clearing_gate.entries for identifier in entry.ids
        )
        later = {identifier: anchor_label for identifier in placed - current}
    for section in sections:
        if section.version <= anchor.version:
            continue
        label = "v{}.{}.{}".format(*section.version)
        for identifier in section.scope_ids:
            if identifier not in current:
                later.setdefault(identifier, label)
    return Scope(
        anchor=anchor.label,
        current=current,
        later=later,
        step_label=step_label,
        clearing=clearing_gate is not None,
    )


@dataclass(frozen=True)
class Wave:
    """The project's position on the rolling-wave cadence, and nothing more.

    Every field is read off a file: the version from `pyproject.toml`, the step
    from the release train, the gate from the milestone section that records it
    and the item statuses that clear it. What none of them say is whether the
    plan is still the right plan, and this does not guess.
    """

    version: str
    #: The row the project is on: the one after the last milestone it has
    #: released. `None` when the timeline is unreadable or empty.
    step: TimelineStep | None
    next_step: TimelineStep | None
    #: How many numbered steps the timeline carries, for "step 1 of 9".
    total_steps: int
    #: The open gate, when one is recorded under a milestone not yet released.
    gate: GateStatus | None
    #: The milestone the beat is about, when the roadmap has a section for it.
    milestone: MilestoneSection | None
    #: Which items that milestone names, and which a later one names instead.
    scope: Scope
    beat: str
    #: What the beat is to be done to, named as the roadmap names it.
    subject: str
    #: Grammar breaches in the timeline table. `doc_check` reports these as
    #: errors; here they are carried so a caller can say the answer rests on a
    #: table that does not parse cleanly.
    problems: tuple[str, ...]


def version_tuple(version: str) -> tuple[int, int, int] | None:
    """`"0.2.5"` as a comparable triple, or `None` when it is not a version."""
    match = SEMVER_RE.match(version.strip())
    if match is None:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def gate_status(
    milestone: MilestoneSection, closed_ids: frozenset[str], known_ids: frozenset[str]
) -> GateStatus:
    """Count a frozen list against the store, entry by entry.

    An entry is cleared when every id it holds is closed - `done` or `dropped`,
    which the store already distinguishes - because an entry holding two ids
    for one problem is not half finished when one of them closes.
    """
    cleared: list[GateEntry] = []
    outstanding: list[GateEntry] = []
    unknown: list[str] = []
    for entry in milestone.gate_entries:
        missing = [identifier for identifier in entry.ids if identifier not in known_ids]
        unknown.extend(missing)
        if not missing and all(identifier in closed_ids for identifier in entry.ids):
            cleared.append(entry)
        else:
            outstanding.append(entry)
    return GateStatus(
        milestone=milestone,
        entries=milestone.gate_entries,
        cleared=tuple(cleared),
        outstanding=tuple(outstanding),
        unknown_ids=tuple(unknown),
    )


def _current_step(
    steps: Sequence[TimelineStep], version: tuple[int, int, int] | None
) -> int | None:
    """The index of the row the project is on.

    The row after the last milestone it has released, which is not the same as
    the first milestone above the current version: a gate, a patch track or a
    boundary marker can sit between them, and standing on one of those is a
    real position on the plan rather than a gap in it.
    """
    if not steps:
        return None
    if version is None:
        return 0
    released = [
        index
        for index, step in enumerate(steps)
        if step.kind == "milestone" and step.version is not None and step.version <= version
    ]
    if not released:
        return 0
    following = released[-1] + 1
    return following if following < len(steps) else None


def _shipping_the_gate(step: TimelineStep | None, gate: GateStatus) -> bool:
    """Whether a clear gate leaves a release to cut rather than work to start.

    Two arrangements put the gate's work in the release the project is
    standing on, and they are different shapes rather than one comparison
    written loosely:

    - the step is an *earlier* milestone than the section that recorded the
      gate, so that gate earns a version of its own and ships before the
      milestone it gates is implemented - Gate 0's exception, where the list
      frozen under v0.4.0 ships as v0.3.0;
    - the step *is* that section, and the section records no scope of its
      own, so its frozen list is the whole of its content - `ROADMAP.md`'s
      v0.2.8, whose list "is its own scope, recorded under a gate heading
      because that subsection is what `bin/docket wave` reads". Clearing it
      finishes the milestone, so the act due is to cut the release.

    A milestone recording a gate *and* a scope of its own is neither: its gate
    clears so that its scope can be implemented, which is the cadence's
    ordinary case and stays an implementation. That is why the second
    arrangement asks about the scope subsection and not only the version - the
    two are indistinguishable by version order alone.
    """
    if step is None or step.kind != "milestone" or step.version is None:
        return False
    if step.version < gate.milestone.version:
        return True
    return step.version == gate.milestone.version and not gate.milestone.records_its_own_scope


def wave(roadmap: str, version: str, closed_ids: frozenset[str], known_ids: frozenset[str]) -> Wave:
    """Read the plan and the store, and say which beat of the cadence is due.

    The composition, in the order the cadence runs:

    - an open gate recorded under a milestone not yet released is always the
      beat, because the cadence clears a gate before the milestone it gates is
      implemented;
    - a gate that is clear leaves either a release to cut, when the step the
      project stands on is the milestone that carries the gate's work, or the
      milestone that recorded the gate to implement - `_shipping_the_gate`
      holds the two arrangements that make it a release;
    - with no gate recorded, the next milestone either has its four scoping
      subsections and wants its gate frozen, or does not and wants scoping.

    Note what decides the first branch: the *gate record*, not the milestone
    section the step happens to sit in. `ROADMAP.md` says a milestone whose
    gate has not been recorded has not been scoped, and it lets one milestone's
    gate be released as another version - so asking each step's own section
    whether it looks scoped would report v0.3.0, whose whole content is the
    gate recorded under v0.4.0, as unscoped work waiting to be written.
    """
    steps, problems = parse_timeline(roadmap)
    sections = parse_milestones(roadmap)
    current = version_tuple(version)

    index = _current_step(steps, current)
    step = steps[index] if index is not None else None
    next_step = steps[index + 1] if index is not None and index + 1 < len(steps) else None
    total = sum(1 for candidate in steps if candidate.ordinal is not None)

    unreleased = [section for section in sections if current is None or section.version > current]
    recorded = [section for section in unreleased if section.records_a_gate]
    gate = gate_status(recorded[0], closed_ids, known_ids) if recorded else None

    # Declared, not inferred: two of the three branches below bind a section
    # and the third may find none, so the union is the real type of the
    # variable rather than a widening of the first branch's.
    milestone: MilestoneSection | None

    clearing: GateStatus | None = None

    if gate is not None and not gate.is_clear:
        beat, milestone, subject = CLEAR, gate.milestone, gate.milestone.label
        clearing = gate
    elif gate is not None:
        if _shipping_the_gate(step, gate):
            assert step is not None  # narrowed by `_shipping_the_gate`
            beat, milestone, subject = RELEASE, gate.milestone, step.label
        else:
            beat, milestone, subject = IMPLEMENT, gate.milestone, gate.milestone.label
    else:
        ahead = [
            candidate
            for candidate in steps
            if candidate.kind == "milestone"
            and candidate.version is not None
            and (current is None or candidate.version > current)
        ]
        target = ahead[0] if ahead else None
        milestone = next(
            (
                section
                for section in sections
                if target is not None and section.version == target.version
            ),
            None,
        )
        scoped = milestone is not None and milestone.is_scoped
        beat = FREEZE if scoped else SCOPE
        subject = target.label if target is not None else ""

    return Wave(
        version=version,
        step=step,
        next_step=next_step,
        total_steps=total,
        gate=gate,
        milestone=milestone,
        scope=milestone_scope(
            sections,
            milestone,
            clearing_gate=clearing,
            # Only when they differ: naming the step where it *is* the anchor
            # would invite a caller to print a distinction that is not there.
            step_label=(
                step.label
                if step is not None and milestone is not None and step.version != milestone.version
                else ""
            ),
        ),
        beat=beat,
        subject=subject,
        problems=tuple(problems),
    )
