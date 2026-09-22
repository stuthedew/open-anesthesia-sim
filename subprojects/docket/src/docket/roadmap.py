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
from dataclasses import dataclass, field

from .model import MILESTONE_BLOCKER_RE
from .release import SEMVER_RE
from .store import ID_PATTERN

# --- markdown primitives ----------------------------------------------------

HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*#*\s*$")
TABLE_ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")
#: A top-level list entry: a bullet, or a numbered item. Both are entries,
#: because `ROADMAP.md` writes v0.5.0's `Required scope` as bullets and
#: v0.6.0's as a numbered list - so a reader that knew only the bullet was
#: blind to a whole milestone's worth of entries.
LIST_ENTRY_RE = re.compile(r"^(?:[-*]|\d+\.)\s+(?P<text>\S.*)$")


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


def released_versions(rows: Iterable[VersionRow]) -> frozenset[str]:
    """The versions the table records as shipped, as the table writes them.

    One site for the rule because two readers now ask it - `stale_milestones`
    and the `ReleaseTrain.released` it is handed - and `COMPLETED` is matched as
    a substring, so a second copy would be a second place for the substring to
    drift.
    """
    return frozenset(row.version for row in rows if COMPLETED in row.status)


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
#: The heading whose whole meaning is exclusion. Read separately from
#: `SCOPE_SUBSECTION` because the two answer opposite questions about the same
#: id, and a milestone naming one id under both has contradicted itself -
#: which `tools/doc_check.py` fails on, per `PL-NBCS`.
EXCLUDED_SUBSECTION = "explicitly out of scope"
REQUIRED_SUBSECTIONS = ("goal", SCOPE_SUBSECTION, "definition of done", "explicitly out of scope")

# An item id at the head of a gate entry, possibly the second of a pair
# ("PL-Z4GF **and PL-SWFM**"), possibly wrapped in emphasis. Only the head of
# the entry is read: an id mentioned later in the sentence is prose about
# another item, not a second thing the entry is waiting on.
LEADING_ID_RE = re.compile(rf"^[*_\s]*(?:and[*_\s]+)?[*_\s]*(?P<id>{ID_PATTERN})")

# An id wherever it sits in a sentence. Left to `Explicitly out of scope`,
# whose heading has already said what every id beneath it means, because
# elsewhere the sentence around an id is unreadable and a section says far
# more about an id than "this is mine".
#
# Membership is read from *where* an id is written, never from the fact that
# it is written. A milestone's section names ids for at least four reasons -
# an entry of its frozen list, scope the milestone clears itself, commentary
# on an entry ("blocked by PL-ZQ9C above"), and an exclusion set out at length
# ("PL-68XK ... is *not* admitted by this rule") - and only the first two are
# membership. Counting every mention read the exclusions as the opposite of
# what they say, which is queue item PL-HDY6.
#
# So each structure is read by its own grammar, and nothing else in the
# section is read at all:
#
# - the frozen list, by its entries' heads, because an entry is one bullet per
#   problem and an id later in the sentence is prose about another item;
# - `Required scope`, by the `(queue item ...)` slot the entries declare in -
#   see `DECLARATION_RE`. Reading that subsection *in full* was the same
#   over-read one level down: naming the id that re-briefed an entry is how
#   this document records provenance, so every correct maintenance edit added
#   a member, the count drifted as the file was kept up to date, and three
#   separate items were filed to patch one reading of it (`PL-HWW1`);
# - `Explicitly out of scope`, in full, which is what this pattern is left
#   for. The heading states the claim, so no id under it needs a grammar of
#   its own to say which claim is being made.
#
# What this costs is stated rather than hidden: scope written without a slot
# is not read, so an entry declaring nothing places nothing. That is the safe
# direction to fail, and it is no longer silent - `tools/doc_check.py` fails
# an entry that declares none where the section's other entries declare, so
# the cost is paid by a loud failure rather than by a quiet undercount.
SECTION_ID_RE = re.compile(ID_PATTERN)

# The slot that *declares* membership, and the run of ids it may hold. An
# entry writes "(queue item `PL-T691`)" after its bold title, or "(queue items
# `PL-1FT6` and `PL-HJPY`)" where one entry completes two. `ROADMAP.md` was
# already written this way - 58 of its 76 `Required scope` entries, and 39 of
# the 39 belonging to a milestone not yet released - so this promotes the
# file's own idiom to a rule rather than asking the document to be rewritten
# (`PL-HWW1`).
#
# The run stops at the first token that is neither an id nor a connective, so
# a citation *inside* the parenthetical is prose like any other: v0.5.0's
# fourth entry reads "(queue item PL-8LXM, moved with `PL-2FM6` into the
# `v0.4.x` track on 2026-09-08 and shipped there)" and declares one item.
DECLARATION_RE = re.compile(r"\(queue items?\b")
DECLARED_ID_RE = re.compile(rf"^[`,\s]*(?:and[`\s]+)?[`\s]*(?P<id>{ID_PATTERN})`?")


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
class ScopeEntry:
    """One entry of a `Required scope` list: what it declares, and what it says.

    `ids` is the entry's declaration slot alone - see `DECLARATION_RE` - so an
    entry citing three items in its prose and declaring one carries one id.
    Empty where the entry declares nothing, which is a fault
    `tools/doc_check.py` reports rather than a shape to drop here.
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
    #: The `Required scope` half of `scope_ids`, alone - the ids its entries
    #: *declare*, in the order they are written, never the ids its prose cites
    #: (`DECLARATION_RE`). The union above answers
    #: placement, where a gate entry and a scope entry are both "this milestone
    #: names it"; this answers whether the milestone's *own* content is
    #: finished, which the gate half would contaminate - a gate can be clear
    #: with entries still open, deferred to work outside it (`PL-KD98`).
    #:
    #: It answers a second question for the same reason: only this subsection
    #: can contradict `Explicitly out of scope`, so `tools/doc_check.py` reads
    #: it rather than `scope_ids` when it fails a milestone naming one id under
    #: both headings (`PL-NBCS`). A gate entry excluded by the same section
    #: would be a different claim, and not one anybody has made.
    own_scope_ids: tuple[str, ...] = ()
    #: The ids named under `Explicitly out of scope for vX.Y.Z`. Fed into
    #: placement for the *anchor's* section alone (`PL-6P9Y`), never for
    #: another section's: an exclusion recorded by a milestone the project has
    #: already passed says what was true then, and one recorded by a milestone
    #: it has not reached is a decision that milestone's own scoping round may
    #: still revisit. `Scope.excluded` is where that narrowing is applied.
    excluded_ids: tuple[str, ...] = ()
    #: Every entry of the `Required scope` list, each with the ids it declares.
    #: `own_scope_ids` is what places an item and is read from the subsection
    #: whole; this is the same subsection split into the units a *rule* is
    #: stated over, which is what lets `tools/doc_check.py` name the entry that
    #: declares nothing. Empty for a section recording no scope subsection, and
    #: for one whose scope is a paragraph rather than a list.
    scope_entries: tuple[ScopeEntry, ...] = ()

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


def _deduped(ids: Iterable[str]) -> tuple[str, ...]:
    """The ids, first occurrence kept, in the order they were read."""
    seen: dict[str, None] = {}
    for identifier in ids:
        seen.setdefault(identifier, None)
    return tuple(seen)


def _scope_ids(entries: Sequence[GateEntry], scope_ids: Iterable[str]) -> tuple[str, ...]:
    """The section's frozen entries and its own scope, deduplicated in order.

    The gate half is taken from the parsed entries rather than re-read, so the
    ids a gate holds and the ids it places cannot drift apart.
    """
    return _deduped([identifier for entry in entries for identifier in entry.ids] + list(scope_ids))


def list_entries(lines: Sequence[str], start: int) -> Iterator[tuple[int, str]]:
    """Each top-level list entry under one `###` heading, as (line, joined text).

    `start` is the heading's line number, so reading begins on the line after
    it and stops at the next heading of the same depth or shallower - the same
    bound `_subsection_ids` uses, for the same reason.

    Continuation lines are folded into the entry they open, because an entry
    routinely wraps and a phrase split across the break would be invisible to
    every reader of this - the declaration slot included, where a pair of ids
    can wrap between them. A nested bullet folds in too: `LIST_ENTRY_RE`
    anchors at the margin, so only a top-level marker starts an entry.

    One walker and three readers - the frozen list, `Required scope`, and the
    exclusion advisory in `tools/doc_check.py` - because what an entry *is* is
    one question, and it was answered in three places that could drift.
    """
    line_number = 0
    parts: list[str] = []
    for index in range(start, len(lines)):
        line = lines[index]
        heading = HEADING_RE.match(line)
        if heading is not None and len(heading.group("hashes")) <= 3:
            break
        entry = LIST_ENTRY_RE.match(line)
        if entry is not None:
            if parts:
                yield line_number, " ".join(parts)
            line_number, parts = index + 1, [entry.group("text")]
        elif parts and line.strip() and line[:1].isspace():
            parts.append(line.strip())
        elif parts:
            yield line_number, " ".join(parts)
            parts = []
    if parts:
        yield line_number, " ".join(parts)


def _subsection_text(lines: Sequence[str], start: int) -> str:
    """Everything under one `###` heading, joined into a single line.

    Joined rather than read line by line because the declaration slot wraps:
    "(queue items `PL-1FT6` and `PL-HJPY`)" is one statement however the
    paragraph breaks, and a line-at-a-time reader would drop its second id with
    nothing reporting the loss.

    The whole subsection rather than its entries, because a milestone with one
    thing to say writes a sentence rather than a list - v0.2.0's scope is a
    paragraph - and the slot is the statement wherever it is written. The entry
    unit is what `tools/doc_check.py` needs, and it reads `scope_entries`.
    """
    end = len(lines)
    for index in range(start, len(lines)):
        heading = HEADING_RE.match(lines[index])
        if heading is not None and len(heading.group("hashes")) <= 3:
            end = index
            break
    return " ".join(line.strip() for line in lines[start:end])


def _declared_ids(text: str) -> tuple[str, ...]:
    """Every id declared in a `(queue item ...)` slot of `text`, in order.

    Each slot is walked to its first token that is neither an id nor a
    connective, so a pair declares two and a parenthetical that goes on to cite
    another item declares only what it opened with.
    """
    ids: list[str] = []
    for opening in DECLARATION_RE.finditer(text):
        rest = text[opening.end() :]
        while True:
            match = DECLARED_ID_RE.match(rest)
            if match is None:
                break
            ids.append(match.group("id"))
            rest = rest[match.end() :]
    return tuple(ids)


def _gate_entries(lines: Sequence[str], start: int) -> tuple[GateEntry, ...]:
    """Read the list entries under a gate heading, ignoring its prose.

    An entry is a top-level list entry that opens with an item id. The prose
    around it - why the list was frozen, how many were done on some past date,
    which of them the milestone clears itself - is left where it is: it is a
    person's summary of the same facts, and reading it would mean parsing
    sentences.
    """
    entries: list[GateEntry] = []
    for line_number, text in list_entries(lines, start):
        ids = _leading_ids(text)
        if ids:
            entries.append(GateEntry(line=line_number, ids=ids, text=text))
    return tuple(entries)


def _scope_entries(lines: Sequence[str], start: int) -> tuple[ScopeEntry, ...]:
    """Read the entries of a `Required scope` list, declarations and all.

    Every entry, including one declaring nothing: an empty `ids` is exactly
    what `tools/doc_check.py` fails on, so dropping those here would leave the
    rule unenforceable from the only place that can see them.
    """
    return tuple(
        ScopeEntry(line=line_number, ids=_deduped(_declared_ids(text)), text=text)
        for line_number, text in list_entries(lines, start)
    )


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
    excluded: int | None = None

    def flush() -> None:
        if version is None:
            return
        heading_line, heading_title = gate or (0, "")
        entries = _gate_entries(lines, heading_line) if gate else ()
        own_scope = _deduped(_declared_ids(_subsection_text(lines, scope))) if scope else ()
        scope_entries = _scope_entries(lines, scope) if scope else ()
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
                scope_ids=_scope_ids(entries, own_scope),
                own_scope_ids=own_scope,
                excluded_ids=_deduped(_subsection_ids(lines, excluded)) if excluded else (),
                scope_entries=scope_entries,
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
            subsections, gate, scope, excluded = [], None, None, None
        elif version is not None and depth == 3:
            subsections.append(heading_title)
            if heading_title.lower().startswith(GATE_SUBSECTION):
                gate = (index, heading_title)
            elif heading_title.lower().startswith(SCOPE_SUBSECTION):
                scope = index
            elif heading_title.lower().startswith(EXCLUDED_SUBSECTION):
                excluded = index
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
    #: The ids each milestone's own section places - its frozen list, then the
    #: ids under `Required scope`. `MilestoneSection.scope_ids` is the same
    #: reading `check_gate_dispositions` uses, so an id a section merely
    #: mentions is not in it (`PL-NBCS`).
    claimed: Mapping[str, frozenset[str]] = field(default_factory=dict)
    #: The versions the version table marks Completed. `cleared` deliberately
    #: folds these in with the scoped ones, because a milestone blocker asks
    #: whether the scoping round has happened and a shipped milestone's has.
    #: This keeps them separable for the one question that needs the
    #: difference: whether an item ships *with* a milestone (`PL-L09X`).
    released: frozenset[str] = frozenset()

    def is_known(self, version: str) -> bool:
        return version in self.known

    def is_cleared(self, version: str) -> bool:
        return version in self.cleared

    def ships_with(self, version: str, identifier: str) -> bool:
        """Whether `identifier` is claimed by `version` and `version` has not shipped.

        `blocked-by: vX.Y.Z` carries one relation - blocked until that
        milestone is **scoped** - and `PL-W8XP` built it for exactly that: an
        item that cannot be designed until the milestone settles what it
        requires. The project also needs a second relation it has no field
        for: *ships with* that milestone, which is `PL-GS3R`'s case. It is
        fully designed and waits for the port to **land**, because building it
        on the toolkit being replaced costs frame time the port makes free.

        Scoping `v0.5.1` cleared its blocker and could never have unblocked
        it, so `docket check` began advising on every run that it was "ready
        to promote" - the opposite of the truth, and a standing false advisory
        is what `CLAUDE.md`'s "a check earns its place every run" is against.

        No field was added for it, because the roadmap already says it: the
        milestone's own `Required scope` names the item. So this reads what is
        written rather than asking anyone to write it twice, which is the
        cheaper of the two shapes `PL-L09X` costed.
        """
        return version not in self.released and identifier in self.claimed.get(version, frozenset())


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
    claimed = {
        _rendered(section.version): frozenset(section.scope_ids)
        for section in sections
        if section.scope_ids
    }
    return MilestoneStates(
        known=frozenset(known),
        cleared=frozenset(cleared),
        claimed=claimed,
        released=frozenset(released),
    )


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
class Sequenced:
    """A gate entry blocked outside the list whose blockers the plan schedules first.

    The timeline puts the section placing every blocker it waits on *ahead* of
    the gate's own milestone, so the entry clears in the ordinary course of the
    plan and needs nothing from anybody. Reported apart from an entry waiting
    on work placed later or by no section, which is excused for as long as
    nobody decides otherwise; printed identically, the second hid behind the
    first (`PL-7CSP`).
    """

    entry: GateEntry
    #: The label of the latest row scheduling one of its blockers - the row the
    #: entry actually waits for.
    row: str


@dataclass(frozen=True)
class GateStatus:
    """A frozen debt list, counted against the store that holds its items."""

    milestone: MilestoneSection
    entries: tuple[GateEntry, ...]
    cleared: tuple[GateEntry, ...]
    outstanding: tuple[GateEntry, ...]
    #: Open entries the gate cannot clear, because clearing them needs work the
    #: gate does not contain - a later milestone, or an item off the list. A
    #: subset of `outstanding`, never a fourth partition of `entries`: the
    #: frozen list keeps every id it froze, and this says which of them the
    #: beat below cannot honestly ask for.
    blocked_outside: tuple[GateEntry, ...]
    #: Open entries the milestone clears *itself*, because its own `Required
    #: scope` names them. `ROADMAP.md` § "Debt inside the milestone's own
    #: scope" is the rule and states the test in one sentence - "whether the
    #: item appears in the milestone's `Required scope`" - and then says the
    #: gate "is open when everything *outside* the milestone's scope is clear".
    #: So this is the gate's second carve-out beside `blocked_outside`, and
    #: the two are subsets of `outstanding` for the same reason: the frozen
    #: list keeps every id it froze, and these say which of them the beat
    #: cannot honestly ask for before the milestone begins.
    #:
    #: Disjoint from `blocked_outside`, which is computed first and wins. An
    #: entry that is milestone work *and* waits on work off the list is not
    #: something the milestone can simply clear, and filing it under this
    #: heading would hide the constraint behind the reassuring half of it.
    self_cleared: tuple[GateEntry, ...]
    #: Ids the gate names that the store does not hold. A gate cannot be shown
    #: clear while one of these stands: the entry may be a typo or a file that
    #: never existed, and either way its state is unknown rather than closed.
    unknown_ids: tuple[str, ...]
    #: The subset of `blocked_outside` whose off-list blockers the release train
    #: schedules ahead of this gate's milestone, each with the row it waits for.
    #: A refinement of the count rather than a fourth partition: what the gate
    #: can be asked for is unchanged, and `clearable` still reads
    #: `blocked_outside` whole. Empty where `gate_status` was given no train,
    #: because the split is then not attempted rather than guessed.
    sequenced_ahead: tuple[Sequenced, ...] = ()
    #: For each entry blocked outside the list, every open id it waits on that
    #: the list does not hold - transitively, so the figure is what clearing
    #: the entry costs rather than where the walk first left the list. Keyed by
    #: entry because only the `waiting_outside` half of `blocked_outside` is
    #: reported against it: an entry the plan sequences ahead of the gate is
    #: paid for by the rows before it, and charging the reader for it here
    #: would make the plan's own ordering look like unbudgeted work. Defaulted
    #: for a status built by hand; `gate_status` always fills it.
    prerequisites: Mapping[GateEntry, frozenset[str]] = field(default_factory=dict)

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(identifier for entry in self.entries for identifier in entry.ids)

    @property
    def _outside(self) -> frozenset[str]:
        """The distinct ids the entries waiting outside the gate wait on, of any kind."""
        waiting = set(self.waiting_outside)
        found: set[str] = set()
        for entry, prerequisites in self.prerequisites.items():
            if entry in waiting:
                found |= prerequisites
        return frozenset(found)

    @property
    def outside_items(self) -> tuple[str, ...]:
        """The distinct open queue items those entries are waiting on.

        What clearing them costs beyond the gate's own count, and the number
        the beat was missing: `4 open - 1 this gate can clear, 3 waiting on
        work outside it` named the hole without sizing it, so a reader took
        four items for the whole of the work where it was one plus thirteen
        (`PL-FCM3`).

        Distinct, because two entries waiting on one item are one piece of
        work; summing per entry would overstate exactly what the old line
        understated. Sorted for a stable line rather than by any ranking - the
        queue ranks work, and a report that quietly invented a second order
        would be read as one.
        """
        return tuple(sorted(i for i in self._outside if MILESTONE_BLOCKER_RE.match(i) is None))

    @property
    def outside_milestones(self) -> tuple[str, ...]:
        """The distinct milestone versions those entries are waiting on.

        Counted apart from the items because a milestone is not work anybody
        can pick up, so folding one into the item count would restate the same
        overstatement with the sign reversed. Told from an item by the grammar
        `Item.blocking_items` uses rather than by absence from the store, which
        keeps the partition fail-closed the same way: a typo stays an item and
        is refused by name where `checks.py` already refuses unrecognised
        blockers, instead of being silently counted as a milestone.
        """
        return tuple(
            sorted(
                (i for i in self._outside if MILESTONE_BLOCKER_RE.match(i) is not None),
                key=lambda version: version_tuple(version) or (0, 0, 0),
            )
        )

    @property
    def waiting_outside(self) -> tuple[GateEntry, ...]:
        """`blocked_outside` less the sequenced: entries waiting on work the plan
        places after this gate's milestone, or places nowhere at all."""
        sequenced = {sequenced.entry for sequenced in self.sequenced_ahead}
        return tuple(entry for entry in self.blocked_outside if entry not in sequenced)

    @property
    def clearable(self) -> tuple[GateEntry, ...]:
        """The open entries this gate can actually close before its milestone.

        What the beat is counted from, and what `is_clear` reads. Two kinds of
        open entry are not it. An entry waiting on a version later than the
        gated milestone, or on an item the list does not hold, is open and is
        not work this gate can be asked to finish - counting it leaves the beat
        asking for a target the plan forbids, which is what `PL-SL70` was filed
        on. An entry the milestone's own `Required scope` names is the same
        failure one rule along: the roadmap's carve-out has it cleared *by* the
        milestone, so a beat counting it keeps saying `clear the gate` for work
        that implementing the milestone is what closes (`PL-WZBX`).
        """
        held = set(self.blocked_outside) | set(self.self_cleared)
        return tuple(entry for entry in self.outstanding if entry not in held)

    @property
    def is_clear(self) -> bool:
        return not self.clearable and not self.unknown_ids


@dataclass(frozen=True)
class ScopeStatus:
    """A milestone's own `Required scope`, counted against the store that holds it.

    The gate's counterpart, and deliberately a much simpler object. A gate is a
    list of *entries*, because one problem may have surfaced under two ids and
    be frozen as a single bullet; `Required scope` is prose with ids written
    into whatever grammar the sentence wanted, so there is no entry to count
    and the honest unit is the id. `SECTION_ID_RE` explains why the two
    subsections are read by different grammars, and it is the same reading
    `Scope.placement` already rests on - this adds no parser, only the split
    (`PL-KD98`).

    **No blocker walk, unlike `GateStatus.clearable`.** A gate entry deferred to
    work outside the list is open and is not something *this gate* can be asked
    to finish, so the beat counts it out. A scope id is not the same question:
    the milestone ships when its scope is done, and an id it cannot reach yet
    means the milestone is not ready whoever is at fault. Counting it out would
    offer a release for a milestone with work still in it, which is the failure
    `ReleaseOffer` exists to prevent, so the strict reading is the safe one.
    """

    milestone: MilestoneSection
    ids: tuple[str, ...]
    closed: tuple[str, ...]
    outstanding: tuple[str, ...]
    #: Ids the scope names that the store does not hold. Read exactly as
    #: `GateStatus.unknown_ids` is: a typo or a file that never existed leaves
    #: the id's state unknown rather than closed, so it withholds completeness
    #: instead of being counted either way.
    unknown_ids: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        """Whether every id this milestone's own scope names has closed.

        False for a milestone that records no `Required scope` ids at all, which
        is deliberate: an empty scope is not a finished one. A section whose
        frozen list *is* its content records no scope subsection, and
        `_release_due` reaches that arrangement by its own test rather than
        through this.
        """
        return bool(self.ids) and not self.outstanding and not self.unknown_ids


def scope_status(
    section: MilestoneSection, closed_ids: frozenset[str], known_ids: frozenset[str]
) -> ScopeStatus:
    """Split a milestone's own `Required scope` into closed, open and unknown."""
    closed = tuple(i for i in section.own_scope_ids if i in closed_ids)
    unknown = tuple(i for i in section.own_scope_ids if i not in known_ids)
    outstanding = tuple(i for i in section.own_scope_ids if i in known_ids and i not in closed_ids)
    return ScopeStatus(
        milestone=section,
        ids=section.own_scope_ids,
        closed=closed,
        outstanding=outstanding,
        unknown_ids=unknown,
    )


# What a milestone section says about an id, as four answers rather than two.
IN_SCOPE = "in-scope"
UNPLACED = "unplaced"
OUT_OF_SCOPE = "out-of-scope"
#: The anchor's own `Explicitly out of scope` heading names it. Distinct from
#: `OUT_OF_SCOPE`, which says a *later* milestone places the id and is a
#: statement about timing - "the current step has not reached it" is the
#: sentence that answer prints, and it is not what an exclusion means
#: (`PL-6P9Y`).
EXCLUDED = "excluded"


@dataclass(frozen=True)
class Scope:
    """Where the plan places an item, relative to the beat now due.

    Four answers, and the last two are why there are four. An id the milestone
    the current beat is about places is work this step includes. An id only a
    *later* milestone places is work this step has not reached. An id the
    anchor's own section names under `Explicitly out of scope` is work the
    roadmap has ruled out, which is a decision rather than a delay. An id no
    section places is none of those: the roadmap places most of the queue
    nowhere, and reading that silence as exclusion would be a verdict rather
    than a fact.

    A *released* section places nothing either. Its narrative names the items
    it discussed, which records where a problem was raised rather than what is
    current work - `PL-026` sits in v0.2.7's release narrative and on v0.4.0's
    frozen gate list, and only the second of those says anything about what to
    do now. Released is decided by the version the project is on, never by
    position relative to the anchor: `wave` hands `milestone_scope` the
    unreleased sections alone, and an unreleased section *below* the anchor is
    work the step has not reached. The Qt port is that shape - numbered v0.4.26
    and placed between Gate 1's row and v0.5.0's - so while the gate is the
    beat its ids are later work mapped to the port, where reading "below the
    anchor" as "released" left them placed by nobody (`PL-FWJF`).

    Three structures are the whole of the evidence, per `SECTION_ID_RE`: the
    frozen list a section records, the declarations under its `Required
    scope`, and - for the anchor alone - the ids under its `Explicitly out of
    scope`. So a milestone that records scope in a sentence carrying no
    declaration records it invisibly here, and one that excludes something in
    prose under another heading excludes it invisibly too, which is the same
    silence rather than its opposite. Both limitations are recorded in the
    README beside the concurrency one; `tools/doc_check.py` fails the first of
    them where a section's own entries show what it meant to write.
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
    #: Ids the anchor's own section names under `Explicitly out of scope`.
    #: Consulted last, after both placements: a milestone excluding work that a
    #: *later* milestone then took on is placed by the later one, which is the
    #: more useful answer and the more recent decision. So this speaks only
    #: where nothing else places the id, which is the case it exists for - an
    #: id the roadmap has ruled on, ranked level with work nobody has ruled on.
    excluded: frozenset[str] = frozenset()
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
        if identifier in self.excluded:
            return EXCLUDED
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

    `sections` are the sections still ahead of the project - `wave` passes the
    unreleased ones, which is what makes a released section place nothing.
    They are read in the order given, which for `wave` is the release train's
    row order (`ReleaseTrain.ahead`) and for a caller reading sections directly
    is whatever it passed. So the *earliest* section placing an id is the one
    reported: an item placed by both v0.3.0 and v0.4.0 is v0.3.0's, and saying
    so is what stops the marking overstating how far off the work is. That
    holds for a section below the anchor too, which is where the port sits
    while the gate above it is being cleared (`PL-FWJF`). An anchor the caller
    left out of `sections` is sorted in by version, which is the grammar's own
    order for milestone rows and the only one such a caller has stated.

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
    placed = frozenset(anchor.scope_ids)
    if clearing_gate is None:
        current = placed
    else:
        current = frozenset(
            identifier for entry in clearing_gate.entries for identifier in entry.ids
        )
    later: dict[str, str] = {}
    # The anchor is read at its own position in the order, so that an id it
    # shares with a section below it is reported as the earlier section's. It
    # contributes only what `current` left out, which is empty unless a gate is
    # being cleared; sorted in rather than assumed present, so a caller passing
    # sections without it still has the anchor's own scope placed.
    ordered = list(sections)
    if anchor not in ordered:
        ordered = sorted([*ordered, anchor], key=lambda candidate: candidate.version)
    for section in ordered:
        ids = (
            placed - current if section.version == anchor.version else frozenset(section.scope_ids)
        )
        label = "v{}.{}.{}".format(*section.version)
        for identifier in sorted(ids):
            if identifier not in current:
                later.setdefault(identifier, label)
    return Scope(
        anchor=anchor.label,
        current=current,
        later=later,
        excluded=frozenset(anchor.excluded_ids),
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
    #: released, as `ReleaseTrain` resolves it. `None` when the timeline is
    #: unreadable or empty.
    step: TimelineStep | None
    next_step: TimelineStep | None
    #: How many numbered steps the timeline carries, for "step 1 of 9".
    total_steps: int
    #: The open gate, when one is recorded under a milestone not yet released.
    gate: GateStatus | None
    #: The beat's milestone's own `Required scope`, counted - `None` when no
    #: gate is recorded or that milestone records no scope subsection. Usually
    #: the gate's milestone; the section on a row the timeline puts before it
    #: while that row is the beat's work. Distinct from `scope` below, which
    #: answers placement for any id; this answers whether the milestone's own
    #: content is finished.
    own_scope: ScopeStatus | None
    #: The milestone the beat is about, when the roadmap has a section for it.
    #: Read off the timeline row rather than the `#` column: a section-bearing
    #: `—` row between a clear gate and the milestone that recorded it is the
    #: beat's work while its scope is open, whatever number it takes
    #: (`_due_before`).
    milestone: MilestoneSection | None
    #: Which items that milestone names, and which a later one names instead.
    scope: Scope
    #: Every version the roadmap names ahead of the current one, from the
    #: release train's rows and from the milestone sections both, nearest
    #: first. Carried rather than left to `release_offer` to recompute: the
    #: rows and the sections are already parsed here, and a reader of the plan
    #: asking "is this number spent?" is asking about the plan rather than
    #: about the position `step` and `milestone` describe.
    reserved: tuple[ReservedVersion, ...]
    beat: str
    #: What the beat is to be done to, named as the roadmap names it.
    subject: str
    #: Grammar breaches in the timeline table. `doc_check` reports these as
    #: errors; here they are carried so a caller can say the answer rests on a
    #: table that does not parse cleanly.
    problems: tuple[str, ...]
    #: The version a `release` beat is asking for, and the roadmap's own name
    #: for it; `None` and `""` on every other beat. Carried rather than left to
    #: `release_offer` to read off `step`, which is right for two of the three
    #: release arrangements and wrong for the third: it releases the milestone
    #: while the project still stands on the patch-track row beneath it, whose
    #: `(0, 4, -1)` is a track marker rather than a number anything can be cut
    #: at. Read from there the offer falls back to the bump's own arithmetic and
    #: prints `0.4.21` directly above a beat reading `release v0.5.0` - a
    #: reader-visible contradiction, which is the failure `PL-D2GW` and
    #: `PL-Q2BJ` already cost (`PL-KD98`).
    release_version: tuple[int, int, int] | None = None
    release_name: str = ""
    #: Statements the plan and the project disagree on - a milestone row the
    #: version has passed with no release of that number recorded, a section no
    #: row places - from `ReleaseTrain.stale`, plus the two the store answers and
    #: the train cannot: a row recorded as released whose section's own scope is
    #: still open (`stale_scopes`), or whose frozen list holds an open entry no
    #: section ahead places (`stale_gates`). Distinct from `problems`, which are breaches
    #: of the table's grammar: these rows parse, and the beat above them is
    #: computed from an arrangement one of the files has made stale.
    stale: tuple[str, ...] = ()


def version_tuple(version: str) -> tuple[int, int, int] | None:
    """`"0.2.5"` as a comparable triple, or `None` when it is not a version."""
    match = SEMVER_RE.match(version.strip())
    if match is None:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


# --- the release train, resolved once ---------------------------------------


@dataclass(frozen=True)
class ReleaseTrain:
    """`ROADMAP.md`'s release train as an arrangement: the rows in table order,
    the row the project stands on, and the section each milestone row bears.

    Resolved once, by `release_train`, and handed to everything downstream that
    asks what comes before what. Before it existed each consumer re-derived the
    arrangement by comparing `(major, minor, patch)` tuples, and the comparison
    agreed with the table until it did not: a gate-only milestone reached from
    a row that was not its own fell through to `implement`, a blocker the
    timeline scheduled ahead of the gate printed like one nothing scheduled,
    and the plan header called the anchor the step while `wave` named another
    row - each found separately, each patched at its own site (`PL-2T03`,
    naming `PL-Y1L0`, `PL-J45M`, `PL-7CSP` and `PL-B5DW`). The table's row
    order **is** the arrangement - `_timeline_order` fails a milestone row
    written out of it - so this carries the order, and nothing downstream
    compares versions to recover it.

    Two things stay by version, deliberately, because they are not arrangement.
    Which sections are *released* is decided by the version the project is on
    (`Scope` records why), and a section is bound to its row by the version
    both carry, which is identity rather than order. Where the two files that
    state the project's position disagree - a milestone number the version has
    passed with no release of it recorded, a section the table places nowhere -
    `stale` says so, and nothing here resolves it.
    """

    steps: tuple[TimelineStep, ...]
    #: Every milestone section, in the version order `parse_milestones` returns.
    sections: tuple[MilestoneSection, ...]
    current: tuple[int, int, int] | None
    #: The versions the version table records as shipped. `current` is where the
    #: project stands; this is what it has released, which is the other half of
    #: every statement in `stale` - carried rather than re-parsed because
    #: `stale_scopes` and `stale_gates` need the same reading and
    #: `release_train` has already made it.
    released: frozenset[str]
    #: The index of the row the project stands on: the one after the last
    #: milestone row it has released (`_current_step`). `None` when the
    #: timeline is empty or the version has run off its end.
    position: int | None
    #: The unreleased sections in the train's order: those a row bears, by row,
    #: then any no row bears, by version among themselves - the plan does not
    #: say where those come, and `stale` reports each of them.
    ahead: tuple[MilestoneSection, ...]
    #: Grammar breaches in the table, from `parse_timeline`.
    problems: tuple[str, ...]
    #: Statements the plan and the project disagree on. Each is a fact about
    #: two files, reported so a reader can go and repair one of them.
    stale: tuple[str, ...]

    @property
    def step(self) -> TimelineStep | None:
        return self.steps[self.position] if self.position is not None else None

    @property
    def next_step(self) -> TimelineStep | None:
        if self.position is None or self.position + 1 >= len(self.steps):
            return None
        return self.steps[self.position + 1]

    @property
    def total_steps(self) -> int:
        """How many numbered steps the timeline carries, for "step 1 of 9"."""
        return sum(1 for step in self.steps if step.ordinal is not None)

    def row(self, section: MilestoneSection) -> int | None:
        """The index of the milestone row bearing `section`, or `None`.

        Bound by the version both carry, which is identity rather than
        arrangement: a section is *about* the release its heading names, and
        the row is where the plan puts that release.
        """
        for index, step in enumerate(self.steps):
            if step.kind == "milestone" and step.version == section.version:
                return index
        return None

    def section(self, step: TimelineStep) -> MilestoneSection | None:
        """The section a milestone row bears, or `None` for a row bearing none."""
        if step.kind != "milestone" or step.version is None:
            return None
        return next((s for s in self.sections if s.version == step.version), None)

    def places(self, identifier: str) -> MilestoneSection | None:
        """The first unreleased section, in the train's order, that places the id.

        The same two structures `Scope` reads - the frozen list and `Required
        scope` - so an id a section merely mentions is placed by nobody here
        too (`SECTION_ID_RE`).
        """
        return next((s for s in self.ahead if identifier in s.scope_ids), None)

    def row_placing(self, identifier: str) -> int | None:
        """The index of the row whose section places the id.

        `None` when no unreleased section places it, and also when the one
        that does has no row: the plan then names the work without saying
        where it comes, which is no arrangement to compare against.
        """
        section = self.places(identifier)
        return self.row(section) if section is not None else None


def release_train(roadmap: str, version: str) -> ReleaseTrain:
    """Read the release train once: the rows, the position, and what is ahead."""
    steps, problems = parse_timeline(roadmap)
    sections = parse_milestones(roadmap)
    version_rows = parse_version_table(roadmap)
    current = version_tuple(version)
    position = _current_step(steps, current)

    rows: dict[tuple[int, int, int], int] = {}
    for index, step in enumerate(steps):
        if step.kind == "milestone" and step.version is not None:
            rows.setdefault(step.version, index)
    unreleased = [s for s in sections if current is None or s.version > current]
    placed = sorted((s for s in unreleased if s.version in rows), key=lambda s: rows[s.version])
    unplaced = [s for s in unreleased if s.version not in rows]

    stale = stale_milestones(steps, sections, version_rows, current)
    stale.extend(
        f"line {section.line}: the {section.label} section has no timeline row, so the plan"
        " does not say where it comes"
        for section in unplaced
    )
    return ReleaseTrain(
        steps=tuple(steps),
        sections=tuple(sections),
        current=current,
        released=released_versions(version_rows),
        position=position,
        ahead=tuple(placed + unplaced),
        problems=tuple(problems),
        stale=tuple(stale),
    )


def stale_milestones(
    steps: Sequence[TimelineStep],
    sections: Sequence[MilestoneSection],
    rows: Sequence[VersionRow],
    reached: tuple[int, int, int] | None,
) -> list[str]:
    """The milestone rows numbered at or below `reached` with no release of that
    number in the version table, each as a statement of the two files.

    Two files state where the project is - the version it carries and the
    plan's numbering - and this is where they disagree without either being
    malformed. A patch cut at or past a milestone's number while that
    milestone is unshipped leaves its row numbered behind the project, and the
    train then stands on the row after it: the owner's placement of that
    milestone is reversed by a release that never touched it, and nothing
    reported it (`PL-Y1L0`). The version table is the record of what shipped -
    every release writes a row there - so a milestone number the project has
    reached with no row is either the release being cut right now or a number
    the plan needs to give back, and each statement says which edit its case
    owes. A table recording nothing is no record to compare against and
    answers nothing here; `outstanding_roadmap_edits` reports that on its own.
    """
    recorded = released_versions(rows)
    if not recorded or reached is None:
        return []
    by_version = {section.version: section for section in sections}
    statements: list[str] = []
    for step in steps:
        if step.kind != "milestone" or step.version is None or step.version > reached:
            continue
        number = "{}.{}.{}".format(*step.version)
        if number in recorded:
            continue
        section = by_version.get(step.version)
        where = f"timeline line {step.line}"
        where += f", section line {section.line}" if section is not None else ", no section"
        if step.version == reached:
            statements.append(
                f"{step.label} ({where}) is numbered v{number}, which the project has reached"
                f" with no v{number} release in the version table: its table row is owed if"
                " this release is that milestone, and a new number if it is not"
            )
        else:
            statements.append(
                f"{step.label} ({where}) is numbered v{number}, which the project has passed"
                f" with no v{number} release in the version table: the row and its section"
                " owe a number the project has not passed"
            )
    return statements


def _released_rows(train: ReleaseTrain) -> Iterator[tuple[TimelineStep, str, MilestoneSection]]:
    """Each milestone row the version table records as released, with its number
    and the section it bears - the rows `stale_scopes` and `stale_gates` read.

    Numbered at or below the version the project is on *and* written into the
    version table: a number the project has passed with no row there is
    `stale_milestones`' statement instead. A row bearing no section has no
    placing structure to be stale in, so it is passed over here.
    """
    if train.current is None:
        return
    for step in train.steps:
        if step.kind != "milestone" or step.version is None or step.version > train.current:
            continue
        number = "{}.{}.{}".format(*step.version)
        section = train.section(step)
        if number in train.released and section is not None:
            yield step, number, section


def stale_scopes(
    train: ReleaseTrain, closed_ids: frozenset[str], known_ids: frozenset[str]
) -> list[str]:
    """The milestone rows the version table records as released whose section's
    own `Required scope` still holds open ids, each as a statement.

    The complement of `stale_milestones` above, and the case that one cannot
    reach. A patch cut at a milestone's own number writes that number into the
    version table, so from then on the row reads as released: the section leaves
    `ReleaseTrain.ahead`, the beat moves to the next row, and the statement made
    once at the hand-off - `outstanding_roadmap_edits`, which names both
    readings of a number the cut has exactly reached - has scrolled by. The
    owner's placement of that milestone is then reversed by a release that never
    touched it, with nothing saying so, which is `PL-Y1L0`'s failure surviving
    its own fix (`PL-LN3T`).

    Only the store separates the port shipped from the port skipped, because
    both leave the same table row. So this and `stale_gates` are the statements
    in `Wave.stale` that are not a fact about two files, and the reason they are
    computed in `wave` rather than in `release_train`, which reads no store.

    Open is `ScopeStatus.outstanding`: an id the store holds and has not closed.
    An id the store does not hold is `unknown_ids` and is passed over, for the
    reason that field already records - it withholds completeness rather than
    establishing that work is outstanding, so it cannot carry the claim this
    statement makes. A section recording no `Required scope` of its own says
    nothing here either, which is v0.3.0's shape: its whole content is the gate
    recorded under the milestone after it.
    """
    statements: list[str] = []
    for step, number, section in _released_rows(train):
        scope = scope_status(section, closed_ids, known_ids)
        if not scope.outstanding:
            continue
        statements.append(
            f"{step.label} (timeline line {step.line}, section line {section.line}) is numbered"
            f" v{number}, which the version table records as released while"
            f" {len(scope.outstanding)} of {len(scope.ids)} ids in its own Required scope are still"
            f" open ({', '.join(scope.outstanding)}): the scope owes those closures if this release"
            " was that milestone, and the row owes a number the project has not reached if it"
            " was not"
        )
    return statements


def stale_gates(
    train: ReleaseTrain, closed_ids: frozenset[str], known_ids: frozenset[str]
) -> list[str]:
    """The milestone rows the version table records as released whose section's
    own frozen list still holds open entries no section ahead places, each as a
    statement.

    `stale_scopes` in a section's other placing structure (`PL-SZJ2`). A
    released section leaves `ReleaseTrain.ahead`, and `wave` counts only the
    first gate recorded there, so a list shipped with entries open is counted by
    nothing and printed nowhere. v0.2.8 is the shape that makes it more than
    bookkeeping: its whole content is its list, so releasing it with an entry
    open is `PL-Y1L0`'s reversal with no `Required scope` for `stale_scopes` to
    catch it in.

    Open is narrower than `GateStatus.outstanding`, and is not `clearable`
    either. `ROADMAP.md` § "The cadence" beat 3 lets an entry be *deferred to a
    later gate* rather than cleared, on terms of which one is decidable: the
    deferral names the later gate the entry lands in. So an open entry a
    section ahead places - `ReleaseTrain.places`, the two structures `Scope`
    reads - has been carried rather than dropped, which is Gate 1's `PL-WZVZ`
    on Gate 2's list, and counting it would call every such deferral stale.
    `clearable` would excuse something else: an entry waiting on work off the
    list, which with nothing ahead holding it is the entry *deferred to
    nowhere* that the cadence names as the illegitimate case.

    Two kinds of id are passed over. One the section's own `Required scope`
    also names is `stale_scopes`' statement already, and printing it twice
    would read as two problems. One the store does not hold is unknown rather
    than open, for the reason `ScopeStatus.unknown_ids` records.
    """
    statements: list[str] = []
    for step, number, section in _released_rows(train):
        own_scope = frozenset(section.own_scope_ids)
        dropped = 0
        unplaced: list[str] = []
        for entry in section.gate_entries:
            open_here = [
                identifier
                for identifier in entry.ids
                if identifier in known_ids
                and identifier not in closed_ids
                and identifier not in own_scope
                and train.places(identifier) is None
            ]
            if open_here:
                dropped += 1
                unplaced.extend(open_here)
        if not dropped:
            continue
        statements.append(
            f"{step.label} (timeline line {step.line}, section line {section.line}) is numbered"
            f" v{number}, which the version table records as released while {dropped} of"
            f" {len(section.gate_entries)} entries on its frozen list are still open and placed"
            f" by no section ahead ({', '.join(unplaced)}): the list owes those closures, or a"
            " deferral to a later gate that holds them, if this release was that milestone,"
            " and the row owes a number the project has not reached if it was not"
        )
    return statements


def _blockers_outside(
    identifier: str,
    blockers: Mapping[str, Sequence[str]],
    gate_ids: frozenset[str],
    closed_ids: frozenset[str],
    seen: set[str],
) -> frozenset[str]:
    """The open blockers this id waits on that the frozen list does not hold.

    Follows `blocked-by` from the id, skipping blockers that have already
    closed, and collects each one at which the walk leaves the list. Two kinds
    of entry leave it, and they are one fact rather than two special cases: a
    milestone version is never an item on the list, and an item off the list
    is work the gate was not frozen to contain. A blocker that is *itself* a
    gate entry keeps the walk inside, so a list that sequences its own entries
    still reads as clearable.

    Transitive because the sequencing is. `PL-3355` waits on `PL-25KS`, the
    dashboard port, which the plan places in a release after the milestone
    this gate guards; one hop would have stopped at a gate entry's blocker
    without asking what that blocker waits on in turn.

    The walk does not continue *past* a blocker off the list: where the plan
    places that blocker is the plan's business, and what it waits on in turn
    is that milestone's. Collecting the frontier rather than answering at the
    first crossing is what lets `gate_status` say *where* each one sits
    (`PL-7CSP`); an empty answer means the walk never left the list.

    A cycle adds nothing on its second visit: two entries waiting on each
    other are stuck, but they are stuck *inside* the gate, and saying
    otherwise would move a deadlock out of the count that should show it.
    """
    if identifier in seen:
        return frozenset()
    seen.add(identifier)
    outside: set[str] = set()
    for blocker in blockers.get(identifier, ()):
        if blocker in closed_ids:
            continue
        if blocker not in gate_ids:
            outside.add(blocker)
            continue
        outside |= _blockers_outside(blocker, blockers, gate_ids, closed_ids, seen)
    return frozenset(outside)


def _prerequisites_outside(
    identifier: str,
    blockers: Mapping[str, Sequence[str]],
    gate_ids: frozenset[str],
    closed_ids: frozenset[str],
    seen: set[str],
) -> frozenset[str]:
    """Every open id this one waits on, at any depth, that the frozen list does not hold.

    The cost question, where `_blockers_outside` answers the placement one, and
    the two part company at the first crossing. That walk stops there on
    purpose - where the plan puts a blocker off the list is the plan's business
    - so what it returns is a frontier and not a total, and asking it for the
    total reproduces the defect this was filed on one level down. Of the open
    items carrying an open blocker on 2026-09-20, 38% waited on something their
    immediate blockers waited on in turn, and across that set the frontier
    undercounted the open prerequisites by 31% (`PL-FCM3`).

    So this one continues past the crossing, and collects an id whenever the
    list does not hold it. A blocker the list *does* hold is already counted as
    an open entry of the gate, so collecting it here too would charge the
    reader twice for one piece of work - the walk still follows it, because an
    entry on the list may itself wait on something off it.

    A milestone version names no item and carries no blockers of its own, so
    the walk stops on it having collected it; `GateStatus.outside_milestones`
    is where it is told apart from an id, and on the grammar rather than on
    absence from the store.

    Cycle-safe on `seen`, which is what keeps the session-start digest from
    dying of recursion on two items waiting on each other: `_plan` declines on
    `OSError`, `ValueError` and `KeyError`, and a `RecursionError` is none of
    the three, so the digest would not degrade - it would fail.
    """
    if identifier in seen:
        return frozenset()
    seen.add(identifier)
    outside: set[str] = set()
    for blocker in blockers.get(identifier, ()):
        if blocker in closed_ids:
            continue
        if blocker not in gate_ids:
            outside.add(blocker)
        outside |= _prerequisites_outside(blocker, blockers, gate_ids, closed_ids, seen)
    return frozenset(outside)


def gate_status(
    milestone: MilestoneSection,
    closed_ids: frozenset[str],
    known_ids: frozenset[str],
    blockers: Mapping[str, Sequence[str]],
    train: ReleaseTrain | None = None,
) -> GateStatus:
    """Count a frozen list against the store, entry by entry.

    An entry is cleared when every id it holds is closed - `done` or `dropped`,
    which the store already distinguishes - because an entry holding two ids
    for one problem is not half finished when one of them closes.

    `blockers` is each item's `blocked-by`, and it splits the open entries in
    two. An entry waiting on something the list does not hold cannot be closed
    by clearing this gate, whatever order the gate is worked in, so it is
    reported apart from the ones that can - see `GateStatus.blocked_outside`.
    It stays on the list either way: the list is frozen, and this is a count
    of what it can be asked for today rather than an edit to it.

    The milestone's own `Required scope` splits them a third way, on the
    carve-out `ROADMAP.md` § "Debt inside the milestone's own scope" states:
    debt the milestone exists to clear is cleared *by* it, and the gate is
    open once everything outside that scope is clear. `own_scope_ids` is that
    subsection alone, which is what the rule names - the union `scope_ids`
    would fold the frozen list back in and make every entry its own excuse.

    `train`, when given, answers one more question about each entry blocked
    outside: whether the plan schedules the work it waits on *ahead* of this
    gate's milestone, in which case it clears in the ordinary course and needs
    nothing from anybody. That is `sequenced_ahead`, and it is a second answer
    from the walk already happening rather than a new traversal - the frontier
    the walk stopped on, read against where the train places each id. An entry
    is sequenced only where *every* blocker it stopped on is placed by a row
    before the gate's; one placed later, or by no section, leaves it waiting
    outside. Without a train the split is not attempted (`PL-7CSP`).

    `prerequisites` answers the remaining question about those entries, and is
    the one place a second walk is worth its cost: how *much* is outside, which
    the frontier cannot say because it stops at the first crossing. See
    `_prerequisites_outside`, and `GateStatus.outside_items` for what is then
    reported from it (`PL-FCM3`).

    **The section's group headings are not read, and are not the test.** Gate 1
    writes the same split in prose - "Cleared by v0.5.0 itself" - and the two
    disagreed on three ids when this was built: `PL-2FM6` and `PL-8LXM` sit
    under the `v0.4.x` track's heading and `PL-GVXP` under the product lane's,
    while all three appear in v0.5.0's `Required scope`. All three had closed,
    so nothing rode on it; the rule is followed rather than the heading because
    the rule is what `ROADMAP.md` states as the test, and because `_gate_entries`
    deliberately does not parse a person's summary of the same facts.
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
    gate_ids = frozenset(identifier for entry in milestone.gate_entries for identifier in entry.ids)
    outside: dict[GateEntry, frozenset[str]] = {}
    for entry in outstanding:
        frontier = frozenset().union(
            *(
                _blockers_outside(identifier, blockers, gate_ids, closed_ids, set())
                for identifier in entry.ids
                if identifier not in closed_ids
            )
        )
        if frontier:
            outside[entry] = frontier
    blocked_outside = tuple(entry for entry in outstanding if entry in outside)
    prerequisites = {
        entry: frozenset().union(
            *(
                _prerequisites_outside(identifier, blockers, gate_ids, closed_ids, set())
                for identifier in entry.ids
                if identifier not in closed_ids
            )
        )
        for entry in blocked_outside
    }
    sequenced: list[Sequenced] = []
    gate_row = train.row(milestone) if train is not None else None
    if train is not None and gate_row is not None:
        for entry in blocked_outside:
            rows = [train.row_placing(blocker) for blocker in sorted(outside[entry])]
            ahead = [row for row in rows if row is not None and row < gate_row]
            if len(ahead) == len(rows):
                sequenced.append(Sequenced(entry=entry, row=train.steps[max(ahead)].label))
    held = set(blocked_outside)
    own_scope = frozenset(milestone.own_scope_ids)
    # Every *open* id, rather than every id: an entry holding a closed id and an
    # open one is asked only for the half that is left. An unknown id counts
    # against it, because an id the store cannot place is not one the milestone
    # can be shown to carry - `unknown_ids` withholds `is_clear` anyway, and
    # agreeing with it here keeps the two from disagreeing on one entry.
    self_cleared = tuple(
        entry
        for entry in outstanding
        if entry not in held
        and all(
            identifier in closed_ids or (identifier in known_ids and identifier in own_scope)
            for identifier in entry.ids
        )
    )
    return GateStatus(
        milestone=milestone,
        entries=milestone.gate_entries,
        cleared=tuple(cleared),
        outstanding=tuple(outstanding),
        blocked_outside=blocked_outside,
        self_cleared=self_cleared,
        unknown_ids=tuple(unknown),
        sequenced_ahead=tuple(sequenced),
        prerequisites=prerequisites,
    )


def _current_step(
    steps: Sequence[TimelineStep], version: tuple[int, int, int] | None
) -> int | None:
    """The index of the row the project is on.

    The row after the last milestone it has released, which is not the same as
    the first milestone above the current version: a gate, a patch track or a
    boundary marker can sit between them, and standing on one of those is a
    real position on the plan rather than a gap in it. A milestone row is one
    by its label rather than by the `#` column, so a `—` row carrying a version
    is released, and stepped past, exactly as a numbered one is.
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


def _due_before(train: ReleaseTrain, milestone: MilestoneSection) -> MilestoneSection | None:
    """The section-bearing timeline row the plan puts before `milestone`, if any.

    The rows from the one the project stands on up to the gated milestone's
    own are read in table order, numbered or not. The `#` column says whether a
    row is a step of its own, and the Qt port was not one: it sat on a `—` row
    between Gate 1 and v0.5.0, took a patch number, and carried a section with
    a `Required scope`. Anchoring on the next *numbered* milestone read straight
    past it, so `wave` printed `implement v0.5.0` for the whole of the port and
    `docket next` told every session the port's items were placed by no section
    (`PL-FWJF`).

    Only a row whose section records its own scope is returned, because that is
    the one thing here that can be counted. A row with no section, or a section
    with no `Required scope`, says nothing this can read and is passed over
    rather than named as unfinished. A patch-track row bears no section by
    grammar - `SECTION_VERSION_RE` wants three numbers and `v0.4.x` has two - and
    is passed over the same way, which is what keeps `v0.4.x` the step the
    project stands on while the port is the work.

    "Before" is the table's row order and nothing else. It used to be a version
    comparison the grammar made agree with row order for milestone rows
    (`PL-2T03`); the train carries the order now, so a milestone no row bears
    has nothing before it here, and `ReleaseTrain.stale` says so rather than
    this guessing. A row placed above its gate's row is still not told apart
    from one below it, deliberately: an open gate is the beat whatever else is
    written, and this is consulted only once the gate is clear.
    """
    end = train.row(milestone)
    if train.position is None or end is None:
        return None
    for step in train.steps[train.position : end]:
        section = train.section(step)
        if section is not None and section.records_its_own_scope:
            return section
    return None


@dataclass(frozen=True)
class ReservedVersion:
    """A version the roadmap has already spent, and what it spent it on.

    A version is spoken for by being *named* ahead of the current one. That is
    the whole rule, and it is a property of the file rather than of where a
    reader stands in it - which is what makes the set of them finite and
    readable in one pass, rather than a list of bindings to extend the next
    time the plan is arranged differently (`PL-VFD8`).
    """

    version: tuple[int, int, int]
    #: The roadmap's own name for what holds it - "the schematic", not
    #: "v0.6.0". The timeline row's wording where there is a row, because the
    #: release train is where the plan places a milestone first; the section's
    #: where there is only a section, or where the row is a baseline stub
    #: carrying no name of its own.
    name: str


def _reserved_versions(
    steps: Sequence[TimelineStep],
    sections: Sequence[MilestoneSection],
    current: tuple[int, int, int] | None,
) -> tuple[ReservedVersion, ...]:
    """Every version the roadmap names ahead of the current one, nearest first.

    Two sources, because the plan states a version in two places and a
    milestone spends months holding only one of them: a timeline row is written
    when the milestone is *placed*, a section when it is *scoped*. Reading both
    covers the window between, and reading them *by version* rather than by
    position means no arrangement of rows can hide one - which is the property
    the reservation had been missing. It had been read off whichever object
    `wave` bound, and the same defect then arrived four times through four
    arrangements, each fixed by adding the binding that had just bitten
    (`PL-D2GW`, `PL-KD98`, `PL-6T4L`, `PL-188T`).

    Patch-track rows are left out by kind. The track promises no particular
    number by construction - that is what `v0.4.x` means - so it reserves
    none, and its `(0, 4, -1)` would in any case match no suggestion.
    Milestone rows and sections at or below the current version are released,
    and a bump only ever suggests a number above it.
    """
    names: dict[tuple[int, int, int], str] = {}
    for step in steps:
        if step.kind != "milestone" or step.version is None:
            continue
        if current is not None and step.version <= current:
            continue
        names.setdefault(step.version, step.name)
    for section in sections:
        if current is not None and section.version <= current:
            continue
        if not names.get(section.version):
            names[section.version] = section.name
    return tuple(ReservedVersion(version, names[version]) for version in sorted(names))


@dataclass(frozen=True)
class ReleaseDue:
    """The release a clear gate leaves to cut: how the roadmap labels it, its
    version, and its own name. Version and name are carried rather than derived
    because the caller cannot recover them from the label, and because the three
    arrangements below read them off two different objects."""

    label: str
    version: tuple[int, int, int]
    name: str


def _release_due(
    train: ReleaseTrain, gate: GateStatus, own_scope: ScopeStatus | None
) -> ReleaseDue | None:
    """What a clear gate leaves to release, or `None` when it leaves work.

    Three arrangements put a release in front of the milestone's own
    implementation, and they are different shapes rather than one comparison
    written loosely:

    - the row the project stands on is a milestone the table puts *before* the
      section that recorded the gate, so that gate earns a version of its own
      and ships before the milestone it gates is implemented - Gate 0's
      exception, where the list frozen under v0.4.0 ships as v0.3.0;
    - the section that recorded the gate records no scope of its own, so its
      frozen list is the whole of its content - `ROADMAP.md`'s v0.2.8, whose
      list "is its own scope, recorded under a gate heading because that
      subsection is what `bin/docket wave` reads". Clearing it finishes the
      milestone, so the act due is to cut the release, **from whichever row
      the project stands on**. This used to ask that the row be the milestone's
      own, so a finished gate-only milestone reached from the patch track
      beneath it fell through to `implement` - and `release_offer` grew a guard
      for exactly that fall-through, which went with it (`PL-J45M`);
    - the section records a scope of its own **and every id in it has closed**.
      Its gate cleared so that scope could be implemented, which is the
      cadence's ordinary case - and the case ends when the scope does.

    **The third was missing, and its absence was unconditional** (`PL-KD98`).
    Reading the first two alone, a milestone recording a gate *and* a scope was
    neither, so `wave` could never reach `release` for that shape whatever the
    state of its scope - and both v0.4.0 and v0.5.0 are that shape. The beat
    stayed `implement` on a finished milestone, and the digest turned the
    non-answer into an assertion: `No release to offer: the roadmap gives 0.4.0
    to "the teachable case", which is unfinished`. The project owner asked for
    the cut anyway and was right. The wording is now true because the
    computation is, rather than by being softened around a construction.

    The first arrangement is tested before the others, and the order is
    load-bearing: under Gate 0's exception the gate ships as its own earlier
    version *first*, so a gated milestone whose scope happened to be complete
    would otherwise be offered ahead of the release its own gate earned.

    `None` now means exactly one thing: the milestone records a scope of its
    own and that scope is open. `implement` is a count rather than a
    fall-through, and `wave` always has an `own_scope` to print beside it.
    """
    step = train.step
    gate_row = train.row(gate.milestone)
    if (
        step is not None
        and step.kind == "milestone"
        and step.version is not None
        and train.position is not None
        and gate_row is not None
        and train.position < gate_row
    ):
        return ReleaseDue(step.label, step.version, step.name)
    section = gate.milestone
    if not section.records_its_own_scope:
        return ReleaseDue(section.label, section.version, section.name)
    if own_scope is not None and own_scope.is_complete:
        return ReleaseDue(section.label, section.version, section.name)
    return None


def wave(
    roadmap: str,
    version: str,
    closed_ids: frozenset[str],
    known_ids: frozenset[str],
    blockers: Mapping[str, Sequence[str]],
) -> Wave:
    """Read the plan and the store, and say which beat of the cadence is due.

    The composition, in the order the cadence runs:

    - an open gate recorded under a milestone not yet released is always the
      beat, because the cadence clears a gate before the milestone it gates is
      implemented - open meaning it holds entries this gate can clear, so a
      list whose remainder all waits on a later milestone is clear here and
      hands the beat on rather than repeating a target nobody can reach;
    - a gate that is clear leaves either a release to cut, when the step the
      project stands on is the milestone that carries the gate's work, or the
      milestone that recorded the gate to implement - `_release_due`
      holds the three arrangements that make it a release - unless the
      timeline puts a section-bearing row between the project and that
      milestone, numbered or not, in which case that row's own scope is the
      work and decides `implement` or `release` for it first (`_due_before`);
    - with no gate recorded, the next milestone either has its four scoping
      subsections and wants its gate frozen, or does not and wants scoping.

    Note what decides the first branch: the *gate record*, not the milestone
    section the step happens to sit in. `ROADMAP.md` says a milestone whose
    gate has not been recorded has not been scoped, and it lets one milestone's
    gate be released as another version - so asking each step's own section
    whether it looks scoped would report v0.3.0, whose whole content is the
    gate recorded under v0.4.0, as unscoped work waiting to be written.

    Every question of arrangement - which section records the next gate, what
    comes before what, which row the project stands on - is put to one
    `ReleaseTrain`, resolved first and handed down. The version is compared
    once, to decide which sections are released; nothing below compares it to
    recover an order the table already states (`PL-2T03`).
    """
    train = release_train(roadmap, version)
    step = train.step

    recorded = next((section for section in train.ahead if section.records_a_gate), None)
    gate = (
        gate_status(recorded, closed_ids, known_ids, blockers, train=train)
        if recorded is not None
        else None
    )
    own_scope = (
        scope_status(gate.milestone, closed_ids, known_ids)
        if gate is not None and gate.milestone.records_its_own_scope
        else None
    )

    # Declared, not inferred: two of the three branches below bind a section
    # and the third may find none, so the union is the real type of the
    # variable rather than a widening of the first branch's.
    milestone: MilestoneSection | None

    clearing: GateStatus | None = None
    due: ReleaseDue | None = None

    if gate is not None and not gate.is_clear:
        beat, milestone, subject = CLEAR, gate.milestone, gate.milestone.label
        clearing = gate
    elif gate is not None:
        before = _due_before(train, gate.milestone)
        if before is not None:
            # The cadence reaches the gated milestone only once the row before
            # it has shipped, so that row's own scope is what the beat counts,
            # split between the two beats exactly as `_release_due`'s third
            # arrangement splits the milestone's own.
            own_scope = scope_status(before, closed_ids, known_ids)
            if own_scope.is_complete:
                due = ReleaseDue(before.label, before.version, before.name)
                beat, milestone, subject = RELEASE, before, due.label
            else:
                beat, milestone, subject = IMPLEMENT, before, before.label
        else:
            due = _release_due(train, gate, own_scope)
            if due is not None:
                beat, milestone, subject = RELEASE, gate.milestone, due.label
            else:
                beat, milestone, subject = IMPLEMENT, gate.milestone, gate.milestone.label
    else:
        # The first milestone row at or after the position, whether or not a
        # section exists for it yet: a milestone is placed on the train long
        # before it is scoped, and the beat asks for the scoping.
        target = (
            next(
                (
                    candidate
                    for candidate in train.steps[train.position :]
                    if candidate.kind == "milestone" and candidate.version is not None
                ),
                None,
            )
            if train.position is not None
            else None
        )
        milestone = train.section(target) if target is not None else None
        scoped = milestone is not None and milestone.is_scoped
        beat = FREEZE if scoped else SCOPE
        subject = target.label if target is not None else ""

    return Wave(
        version=version,
        step=step,
        next_step=train.next_step,
        total_steps=train.total_steps,
        gate=gate,
        own_scope=own_scope,
        milestone=milestone,
        scope=milestone_scope(
            train.ahead,
            milestone,
            clearing_gate=clearing,
            # Only when they differ: naming the step where it *is* the anchor
            # would invite a caller to print a distinction that is not there.
            # Rows rather than versions, so a section no row bears is always
            # named apart from the row the project stands on.
            step_label=(
                step.label
                if step is not None
                and milestone is not None
                and train.position != train.row(milestone)
                else ""
            ),
        ),
        reserved=_reserved_versions(train.steps, train.sections, train.current),
        beat=beat,
        subject=subject,
        release_version=due.version if due is not None else None,
        release_name=due.name if due is not None else "",
        problems=train.problems,
        stale=(
            train.stale
            + tuple(stale_scopes(train, closed_ids, known_ids))
            + tuple(stale_gates(train, closed_ids, known_ids))
        ),
    )
