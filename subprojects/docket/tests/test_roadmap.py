"""Tests for the plan as a structure: the release train, the sections, the beat.

The value of `wave` is entirely in being right about a project it is not
looking at from the inside, so every beat has a fixture that produces it and
an assertion on the answer. The fixture roadmap deliberately reproduces the
two shapes this repository's own file has that a naive parser gets wrong: the
milestone *sections* are written with a plain hyphen while the timeline *rows*
use an em dash, and the milestone whose whole content is a gate carries no
"Required scope" of its own.
"""

from __future__ import annotations

from docket.checks import Report
from docket.model import parse_item
from docket.render import format_digest
from docket.roadmap import (
    CLEAR,
    FREEZE,
    IMPLEMENT,
    IN_SCOPE,
    OUT_OF_SCOPE,
    RELEASE,
    SCOPE,
    UNPLACED,
    baseline_heading,
    milestone_scope,
    parse_milestones,
    parse_timeline,
    parse_version_table,
    wave,
)

ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.3.0 — the foundation** | Gate 0's frozen list. | 2 M |
| — | **v0.3.x — a readability pass** | A patch, not a milestone. | — |
| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |
| 3 | **Gate 1** | Frozen when v0.5.0 is scoped. | — |
| 4 | **v0.5.0 — the case you can branch** | Not yet scoped. | — |
| — | **MVP complete** | Run, branch, compare. | — |

## Completed: v0.2.0 - two agents

### Goal

Shipped.

### Required scope

Done (queue item PL-PQRS).

### Definition of done

Met.

### Explicitly out of scope for v0.2.0

Everything else.

## Next milestone: v0.3.0 - the foundation

### Goal

Clear the inherited backlog. It has no scope of its own to specify: the list
frozen under v0.4.0 below is the specification.

### Definition of done

Every entry on Gate 0's list is closed.

### Explicitly out of scope for v0.3.0

New capability of any kind.

## Milestone after next: v0.4.0 - the teachable case

### Goal

Make the model teachable.

### Debt gate: the frozen list

**Frozen 2026-08-25, the day this milestone was scoped.** Three entries, of
which none were done on the day it was written down.

- PL-001 (M) A first debt entry
- PL-BCDF **and PL-GHJK** (S) — one problem, two ids, one entry
- PL-KLMN (S) A third entry, wrapped across
  two lines the way the real file wraps them
- Not an entry at all: a bullet that opens with prose, not an id.

**Cleared by v0.4.0 itself.** PL-MNPQ appears in Required scope below and is
cleared by the milestone rather than before it.

### Required scope

A displayed clinical unit (queue item PL-MNPQ).

### Definition of done

The learner can run one case.

### Explicitly out of scope for v0.4.0

Forking.

## Planned milestones

Nothing yet.
"""

GATE_IDS = frozenset({"PL-001", "PL-BCDF", "PL-GHJK", "PL-KLMN"})
KNOWN = GATE_IDS | {"PL-MNPQ"}


def _wave(version: str, closed: frozenset[str] = frozenset(), roadmap: str = ROADMAP):
    return wave(roadmap, version, closed, KNOWN)


# --- the release train ------------------------------------------------------


def test_the_timeline_reads_as_four_kinds_of_row() -> None:
    steps, problems = parse_timeline(ROADMAP)
    assert problems == []
    assert [step.kind for step in steps] == [
        "milestone",
        "patch-track",
        "milestone",
        "gate",
        "milestone",
        "marker",
    ]


def test_a_hyphen_where_the_em_dash_belongs_is_a_grammar_breach() -> None:
    """The row separator is spelled out, so a hyphen fails rather than passing
    as a marker whose name happens to open with a version."""
    _, problems = parse_timeline(ROADMAP.replace("v0.4.0 — the teachable", "v0.4.0 - the"))
    assert any("opens like a version" in problem for problem in problems)


# --- milestone sections -----------------------------------------------------


def test_a_section_heading_is_found_by_its_version_not_its_separator() -> None:
    """The sections are written with a hyphen and the timeline with an em dash.

    Assuming one punctuation mark for both is the mistake that would read this
    file confidently and wrongly, so the version is what identifies a section.
    """
    sections = parse_milestones(ROADMAP)
    assert [section.version for section in sections] == [(0, 2, 0), (0, 3, 0), (0, 4, 0)]
    assert [section.name for section in sections] == [
        "two agents",
        "the foundation",
        "the teachable case",
    ]


def test_a_milestone_missing_a_required_subsection_does_not_read_as_scoped() -> None:
    """v0.3.0 has no "Required scope" by design; the test is structural only."""
    sections = {section.version: section for section in parse_milestones(ROADMAP)}
    assert sections[(0, 4, 0)].is_scoped
    assert not sections[(0, 3, 0)].is_scoped


def test_a_gate_records_entries_not_every_id_in_its_prose() -> None:
    """Entries are the gate's size, and only bullets that open with an id are
    entries: the paragraph naming what the milestone clears itself, and the
    bullet written as prose, are a person's summary rather than the list."""
    gate = {section.version: section for section in parse_milestones(ROADMAP)}[(0, 4, 0)]
    assert [entry.ids for entry in gate.gate_entries] == [
        ("PL-001",),
        ("PL-BCDF", "PL-GHJK"),
        ("PL-KLMN",),
    ]
    assert "PL-MNPQ" not in {identifier for entry in gate.gate_entries for identifier in entry.ids}


# --- the four beats, plus the release the gate exception adds ----------------


def test_an_open_gate_is_the_beat_whatever_else_is_written() -> None:
    """The acceptance case: a version below the first timeline milestone, a
    gate recorded under the milestone after it, and work still open on it."""
    plan = _wave("0.2.5", frozenset({"PL-001"}))
    assert plan.beat == CLEAR
    assert plan.step is not None and plan.step.label == "v0.3.0 — the foundation"
    assert plan.step.ordinal == 1 and plan.total_steps == 4
    assert plan.next_step is not None and plan.next_step.kind == "patch-track"
    assert plan.gate is not None
    assert len(plan.gate.entries) == 3 and len(plan.gate.ids) == 4
    assert len(plan.gate.cleared) == 1 and len(plan.gate.outstanding) == 2


def test_an_entry_holding_two_ids_clears_only_when_both_do() -> None:
    half = _wave("0.2.5", frozenset({"PL-001", "PL-BCDF", "PL-KLMN"}))
    assert half.beat == CLEAR
    assert [entry.ids for entry in half.gate.outstanding] == [("PL-BCDF", "PL-GHJK")]

    both = _wave("0.2.5", frozenset(GATE_IDS))
    assert both.gate is not None and both.gate.is_clear


def test_a_clear_gate_below_the_milestone_that_recorded_it_is_a_release() -> None:
    """Gate 0's exception: the gate work ships as a version of its own, so the
    beat after clearing it is to cut that release, not to start v0.4.0."""
    plan = _wave("0.2.5", frozenset(GATE_IDS))
    assert plan.beat == RELEASE
    assert plan.subject == "v0.3.0 — the foundation"


def test_a_clear_gate_at_its_own_milestone_is_implementation() -> None:
    plan = _wave("0.3.0", frozenset(GATE_IDS))
    assert plan.beat == IMPLEMENT
    assert plan.subject == "v0.4.0 — the teachable case"


def test_a_scoped_milestone_with_no_gate_recorded_wants_its_list_frozen() -> None:
    """`ROADMAP.md`: a milestone whose gate has not been recorded has not been
    scoped, whatever else has been written about it."""
    without_gate = ROADMAP.replace("### Debt gate: the frozen list", "### Notes on the debt")
    plan = _wave("0.3.0", roadmap=without_gate)
    assert plan.beat == FREEZE
    assert plan.subject == "v0.4.0 — the teachable case"
    assert plan.gate is None


def test_a_milestone_with_no_section_at_all_wants_scoping() -> None:
    """The wave rolls: v0.4.0 is released, and v0.5.0 is a line on the
    timeline with nothing written under it."""
    plan = _wave("0.4.0", frozenset(GATE_IDS))
    assert plan.beat == SCOPE
    assert plan.subject == "v0.5.0 — the case you can branch"
    assert plan.gate is None
    assert plan.step is not None and plan.step.kind == "gate"


def test_a_version_past_every_milestone_stands_on_the_row_after_the_last() -> None:
    """Standing on a marker or a gate is a real position on the plan, not a
    gap in it, so the row after the last released milestone is the answer."""
    plan = _wave("9.9.9", frozenset(GATE_IDS))
    assert plan.step is not None and plan.step.label == "MVP complete"
    assert plan.beat == SCOPE and plan.subject == ""


def test_a_timeline_the_version_has_run_off_the_end_of_reports_no_step() -> None:
    """Nothing is left to stand on, and inventing a step would be a guess at
    what comes after the plan."""
    ended = ROADMAP.replace("| — | **MVP complete** | Run, branch, compare. | — |\n", "")
    plan = _wave("9.9.9", frozenset(GATE_IDS), roadmap=ended)
    assert plan.step is None
    assert plan.beat == SCOPE and plan.subject == ""


# --- what a milestone section says about an item ----------------------------


def _section(version: tuple[int, int, int]):
    return {section.version: section for section in parse_milestones(ROADMAP)}[version]


def test_a_section_names_the_ids_it_covers_wherever_they_sit_in_the_prose() -> None:
    """Scope is read differently from the gate list above it, and has to be.

    A gate entry is one bullet per problem, so it is read by the bullet's head.
    A milestone names the items it covers in whatever grammar the sentence
    wanted - mid-bullet as "(queue item PL-MNPQ)", or in the paragraph saying
    which ones it clears itself - and reading only bullet heads misses both.
    """
    assert set(_section((0, 4, 0)).item_ids) == {
        "PL-001",
        "PL-BCDF",
        "PL-GHJK",
        "PL-KLMN",
        "PL-MNPQ",
    }
    assert _section((0, 3, 0)).item_ids == ()


def test_the_scope_places_an_id_by_the_milestone_whose_section_names_it() -> None:
    scope = milestone_scope(parse_milestones(ROADMAP), _section((0, 3, 0)))

    assert scope.placement("PL-MNPQ") == OUT_OF_SCOPE
    assert scope.milestone("PL-MNPQ") == "v0.4.0"
    assert scope.placement("PL-ZZZZ") == UNPLACED


def test_a_released_milestones_section_places_nothing() -> None:
    """Its narrative records where a problem was raised, not what is current."""
    scope = milestone_scope(parse_milestones(ROADMAP), _section((0, 4, 0)))

    assert scope.placement("PL-PQRS") == UNPLACED
    assert scope.placement("PL-MNPQ") == IN_SCOPE


def test_the_wave_carries_the_scope_of_the_milestone_the_beat_is_about() -> None:
    plan = _wave("0.2.5")

    assert plan.beat == CLEAR
    assert plan.scope.anchor == "v0.4.0 — the teachable case"
    assert plan.scope.placement("PL-001") == IN_SCOPE


def test_a_plan_with_no_milestone_to_anchor_on_places_nothing() -> None:
    scope = milestone_scope(parse_milestones(ROADMAP), None)

    assert scope.anchor == ""
    assert scope.placement("PL-001") == UNPLACED


# --- what the answer refuses to do ------------------------------------------


def test_a_gate_naming_an_item_the_store_does_not_hold_is_not_clear() -> None:
    """An id the store cannot account for leaves the entry's state unknown, and
    an unknown entry is reported rather than counted as closed."""
    plan = wave(ROADMAP, "0.2.5", frozenset(GATE_IDS), KNOWN - {"PL-KLMN"})
    assert plan.gate is not None
    assert plan.gate.unknown_ids == ("PL-KLMN",)
    assert not plan.gate.is_clear
    assert plan.beat == CLEAR


def test_the_same_inputs_give_the_same_answer() -> None:
    first = _wave("0.2.5", frozenset({"PL-001"}))
    second = _wave("0.2.5", frozenset({"PL-001"}))
    assert first == second


def test_an_unreadable_version_still_reports_the_top_of_the_timeline() -> None:
    """A project with no version is a legitimate state; guessing which
    milestone it is on would not be."""
    plan = _wave("")
    assert plan.step is not None and plan.step.ordinal == 1
    assert plan.beat == CLEAR


VERSION_TABLE = """# Roadmap

## Versioning decision

Prose about how versions are chosen.

| Version | Status | Milestone |
| --- | --- | --- |
| v0.2.4 | Completed | The one before. |
| v0.2.5 | Completed / current baseline | The current one. |
| later | To be decided | Not a version at all. |

## Current baseline: v0.2.5

What it is.
"""


def test_the_version_table_reads_its_release_rows() -> None:
    rows = parse_version_table(VERSION_TABLE)

    assert [row.version for row in rows] == ["0.2.4", "0.2.5"]
    assert [row.is_baseline for row in rows] == [False, True]


def test_a_row_that_names_no_version_is_passed_over_not_reported() -> None:
    """The table is written by hand; what it must get right is the releases."""
    assert all(row.version != "later" for row in parse_version_table(VERSION_TABLE))


def test_the_baseline_heading_is_read_by_its_version() -> None:
    assert baseline_heading(VERSION_TABLE) == (13, "0.2.5")


def test_a_file_with_no_baseline_heading_names_none() -> None:
    assert baseline_heading(ROADMAP) is None


# --- the digest line --------------------------------------------------------

DIGEST_ITEM = """---
id: PL-001
title: An item
priority: P2
effort: S
status: ready
classes: perf
touches: a.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def _digest(plan: object = None) -> str:
    return format_digest(Report(items=[parse_item(DIGEST_ITEM)]), set(), None, plan)


def test_the_digest_carries_the_beat_so_a_session_need_not_ask() -> None:
    """PL-F58L: the queue nagged every session and the roadmap nagged none."""
    plan = _wave("0.2.5", frozenset({"PL-001"}))
    stated = [line for line in _digest(plan).splitlines() if line.startswith("Plan:")]

    assert len(stated) == 1
    assert "clear the gate" in stated[0]
    assert "step 1 of" in stated[0]


def test_the_digest_says_nothing_about_a_plan_it_was_not_given() -> None:
    assert not any(line.startswith("Plan:") for line in _digest().splitlines())


def test_the_plan_costs_the_digest_exactly_one_line() -> None:
    """The digest is resent on every turn of the session, so its length is a cost."""
    plan = _wave("0.2.5", frozenset({"PL-001"}))

    assert len(_digest(plan).splitlines()) == len(_digest().splitlines()) + 1


def test_a_timeline_that_does_not_parse_says_so_rather_than_stating_a_step() -> None:
    """A step read off a broken table is a plausible wrong answer, not an answer."""
    hyphenated = ROADMAP.replace("v0.3.0 —", "v0.3.0 -")
    plan = _wave("0.2.5", frozenset({"PL-001"}), roadmap=hyphenated)
    stated = next(line for line in _digest(plan).splitlines() if line.startswith("Plan:"))

    assert "does not parse cleanly" in stated
