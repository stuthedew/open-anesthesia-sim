"""Tests for the plan as a structure: the release train, the sections, the beat.

The value of `wave` is entirely in being right about a project it is not
looking at from the inside, so every beat has a fixture that produces it and
an assertion on the answer. The fixture roadmap deliberately reproduces the
shapes this repository's own file has that a naive parser gets wrong: the
milestone *sections* are written with a plain hyphen while the timeline *rows*
use an em dash, the milestone whose whole content is a gate carries no
"Required scope" of its own, and a section names ids it does not mean to claim
- mid-entry, in a paragraph excluding one at length, and under "Explicitly out
of scope".
"""

from __future__ import annotations

from docket.checks import Report
from docket.model import parse_item
from docket.render import format_digest, format_wave
from docket.roadmap import (
    CLEAR,
    EXCLUDED,
    FREEZE,
    IMPLEMENT,
    IN_SCOPE,
    OUT_OF_SCOPE,
    RELEASE,
    SCOPE,
    UNPLACED,
    baseline_heading,
    milestone_scope,
    milestone_states,
    parse_milestones,
    parse_timeline,
    parse_version_table,
    scope_status,
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
  two lines the way the real file wraps them, and not to be confused with
  PL-VWXY, which is prose about another item
- Not an entry at all: a bullet that opens with prose, not an id.

PL-STVW (a fourth problem) is a different case and is *not* admitted by this
rule: it predates the freeze and was excluded from the approved list
deliberately.

**Cleared by v0.4.0 itself.** PL-MNPQ appears in Required scope below and is
cleared by the milestone rather than before it.

### Required scope

A displayed clinical unit (queue item PL-MNPQ).

### Definition of done

The learner can run one case.

### Explicitly out of scope for v0.4.0

Forking, and horizontal panning of the chart (queue item PL-Z7LY).

## Planned milestones

Nothing yet.
"""

GATE_IDS = frozenset({"PL-001", "PL-BCDF", "PL-GHJK", "PL-KLMN"})
KNOWN = GATE_IDS | {"PL-MNPQ"}

#: The same roadmap with one entry of the frozen list *also* named in the
#: milestone's own `Required scope` - the arrangement `ROADMAP.md` § "Debt
#: inside the milestone's own scope" carves out, and which Gate 1 writes in
#: prose as "Cleared by v0.5.0 itself". A variant rather than a change to the
#: fixture above, so the entry and id counts every other test asserts stay put.
SELF_CLEARING = ROADMAP.replace(
    "- Not an entry at all:",
    "- PL-SLF9 (M) An entry the milestone's own Required scope names\n- Not an entry at all:",
).replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "A displayed clinical unit (queue item PL-MNPQ), and the decomposition\n(queue item PL-SLF9).",
)
SELF_KNOWN = KNOWN | {"PL-SLF9"}


def _wave(
    version: str,
    closed: frozenset[str] = frozenset(),
    roadmap: str = ROADMAP,
    blockers: dict[str, tuple[str, ...]] | None = None,
    known: frozenset[str] = KNOWN,
):
    return wave(roadmap, version, closed, known, blockers or {})


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


def test_an_entry_sequenced_past_the_milestone_is_not_clearable() -> None:
    """`PL-SL70`: an entry waiting on a later release is open, and is not work
    this gate can be asked for. It stays on the frozen list and out of the
    count the beat is taken from."""
    plan = _wave("0.2.5", frozenset({"PL-001"}), blockers={"PL-KLMN": ("v0.4.0",)})
    assert plan.beat == CLEAR
    assert plan.gate is not None
    assert len(plan.gate.entries) == 3 and len(plan.gate.outstanding) == 2
    assert [entry.ids for entry in plan.gate.blocked_outside] == [("PL-KLMN",)]
    assert [entry.ids for entry in plan.gate.clearable] == [("PL-BCDF", "PL-GHJK")]


def test_a_gate_whose_remainder_all_waits_on_later_work_hands_the_beat_on() -> None:
    """The failure that split the count in two: read from every open entry,
    `clear the gate` stayed the beat forever on a list whose remainder nobody
    could close before the milestone it gates."""
    plan = _wave(
        "0.2.5", frozenset({"PL-001", "PL-BCDF", "PL-GHJK"}), blockers={"PL-KLMN": ("v0.4.0",)}
    )
    assert plan.gate is not None and plan.gate.is_clear
    assert len(plan.gate.outstanding) == 1 and plan.beat == RELEASE


def test_an_entry_waiting_on_another_entry_of_the_same_gate_stays_clearable() -> None:
    """Sequencing inside the list is the gate being worked in order, not the
    gate waiting on something outside itself."""
    plan = _wave("0.2.5", frozenset({"PL-001"}), blockers={"PL-KLMN": ("PL-BCDF",)})
    assert plan.gate is not None and not plan.gate.blocked_outside


def test_the_walk_follows_a_chain_out_through_an_entry_of_the_gate() -> None:
    """`PL-3355` reaches the Qt port through `PL-25KS`, so a single hop would
    have stopped at a gate entry and read the whole chain as clearable."""
    plan = _wave(
        "0.2.5", frozenset({"PL-001"}), blockers={"PL-KLMN": ("PL-BCDF",), "PL-BCDF": ("PL-MNPQ",)}
    )
    assert plan.gate is not None
    assert [entry.ids for entry in plan.gate.blocked_outside] == [
        ("PL-BCDF", "PL-GHJK"),
        ("PL-KLMN",),
    ]


def test_a_blocker_that_has_already_closed_holds_nothing() -> None:
    """`PL-9SH6` read `blocked` for the hour after `PL-H46J` merged. A closed
    blocker is sequencing that has happened, not work outside the gate."""
    plan = _wave("0.2.5", frozenset({"PL-001", "PL-MNPQ"}), blockers={"PL-KLMN": ("PL-MNPQ",)})
    assert plan.gate is not None and not plan.gate.blocked_outside


def test_two_entries_waiting_on_each_other_stay_inside_the_gate() -> None:
    """A cycle is stuck, but it is stuck on the list - and the count that has
    to show that is the one the gate is being asked for."""
    plan = _wave(
        "0.2.5", frozenset({"PL-001"}), blockers={"PL-KLMN": ("PL-BCDF",), "PL-BCDF": ("PL-KLMN",)}
    )
    assert plan.gate is not None and not plan.gate.blocked_outside


# --- debt the milestone clears itself (PL-WZBX) ------------------------------


def test_an_entry_the_milestones_own_scope_names_is_not_this_gates_to_clear() -> None:
    """`ROADMAP.md` § "Debt inside the milestone's own scope": debt a milestone
    exists to clear is cleared *by* it, and the gate is open once everything
    outside that scope is clear. The test is `Required scope` membership, so
    the three entries the scope does not name stay this gate's work."""
    plan = _wave("0.2.5", frozenset(), roadmap=SELF_CLEARING, known=SELF_KNOWN)

    assert plan.gate is not None
    assert len(plan.gate.entries) == 4
    assert [entry.ids for entry in plan.gate.self_cleared] == [("PL-SLF9",)]
    assert [entry.ids for entry in plan.gate.clearable] == [
        ("PL-001",),
        ("PL-BCDF", "PL-GHJK"),
        ("PL-KLMN",),
    ]
    assert plan.beat == CLEAR


def test_a_gate_is_open_when_its_only_open_entries_are_the_milestone_s_own_scope() -> None:
    """The failure `PL-WZBX` was filed on: read from every open entry, the beat
    stayed `clear the gate` for work that implementing the milestone is what
    closes, and the transition the cadence specifies never arrived."""
    plan = _wave("0.2.5", frozenset(GATE_IDS), roadmap=SELF_CLEARING, known=SELF_KNOWN)

    assert plan.gate is not None and plan.gate.is_clear
    assert len(plan.gate.outstanding) == 1 and not plan.gate.clearable
    assert plan.beat != CLEAR


def test_an_entry_read_off_the_frozen_list_alone_is_not_the_milestones_scope() -> None:
    """`scope_ids` is the union of the frozen list and `Required scope`, and
    reading placement from it here would make every entry its own excuse. The
    narrower `own_scope_ids` is what the rule names, and this is the guard."""
    plan = _wave("0.2.5", frozenset(), roadmap=ROADMAP)

    assert plan.gate is not None and not plan.gate.self_cleared


def test_an_entry_the_milestone_names_and_a_later_release_holds_reads_as_blocked() -> None:
    """Both carve-outs at once. The milestone cannot simply clear an entry that
    waits on work off the list, so `blocked_outside` is computed first and the
    two stay disjoint - the reassuring half would otherwise hide the
    constraint, and the three counts would stop adding up to the open one."""
    plan = _wave(
        "0.2.5",
        frozenset(),
        roadmap=SELF_CLEARING,
        blockers={"PL-SLF9": ("v0.9.0",)},
        known=SELF_KNOWN,
    )

    assert plan.gate is not None
    assert [entry.ids for entry in plan.gate.blocked_outside] == [("PL-SLF9",)]
    assert not plan.gate.self_cleared
    assert len(plan.gate.clearable) + len(plan.gate.self_cleared) + len(
        plan.gate.blocked_outside
    ) == len(plan.gate.outstanding)


def test_the_wave_block_names_what_the_milestone_clears_itself() -> None:
    """The split is only worth computing if the reader is told which of the
    three a given id is in, which is where the beat's own count comes from."""
    from docket.render import format_wave

    printed = format_wave(_wave("0.2.5", frozenset(), roadmap=SELF_CLEARING, known=SELF_KNOWN))

    assert "3 this gate can clear, 1 the milestone clears itself" in printed
    assert "cleared by the milestone itself: PL-SLF9" in printed
    assert "clear the gate - 3 entries of 4 still open here, 1 the milestone clears itself" in (
        printed
    )


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


# The self-gating pair below stand on the same row of the same timeline with
# the same gate clear, and differ only in whether that milestone records a
# scope of its own. Removing the patch-track row is what puts the step on the
# v0.4.0 milestone row rather than on the patch track between the two.
_ON_THE_GATES_OWN_ROW = ROADMAP.replace(
    "| — | **v0.3.x — a readability pass** | A patch, not a milestone. | — |\n", ""
)
_SELF_GATING = _ON_THE_GATES_OWN_ROW.replace(
    "### Required scope\n\nA displayed clinical unit (queue item PL-MNPQ).",
    "### What the list is\n\nThe frozen list above is the whole of this milestone.",
)


def test_a_self_gating_milestone_is_a_release_once_its_gate_clears() -> None:
    """v0.2.8's shape: the frozen list is the milestone's own scope, so
    clearing it finishes the milestone and the act due is to cut the release.

    Distinct from Gate 0's exception above, where the gate ships as an earlier
    version than the section recording it: here the two are the same version,
    so version order alone cannot tell this from the implementation case.
    """
    plan = _wave("0.3.0", frozenset(GATE_IDS), roadmap=_SELF_GATING)
    assert plan.step is not None and plan.step.label == "v0.4.0 — the teachable case"
    assert plan.gate is not None and plan.gate.is_clear
    assert plan.gate.milestone.version == plan.step.version
    assert plan.beat == RELEASE
    assert plan.subject == "v0.4.0 — the teachable case"


def test_a_self_gating_milestone_with_scope_of_its_own_is_still_implementation() -> None:
    """The same row, the same clear gate, and the opposite answer: a milestone
    recording a gate *and* a required scope clears the gate in order to
    implement that scope, which is the cadence's ordinary case."""
    plan = _wave("0.3.0", frozenset(GATE_IDS), roadmap=_ON_THE_GATES_OWN_ROW)
    assert plan.step is not None and plan.step.label == "v0.4.0 — the teachable case"
    assert plan.gate is not None and plan.gate.milestone.version == plan.step.version
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


def test_a_section_places_the_ids_its_two_scope_structures_name() -> None:
    """Two structures place an id, and each is read by its own grammar.

    A gate entry is one bullet per problem, so it is read by the bullet's
    head. `Required scope` is read whole - a milestone names what it covers in
    whatever grammar the sentence wanted, mid-bullet as "(queue item
    PL-MNPQ)" or in a paragraph, and the heading has already said that
    everything under it is scope.
    """
    assert set(_section((0, 4, 0)).scope_ids) == {
        "PL-001",
        "PL-BCDF",
        "PL-GHJK",
        "PL-KLMN",
        "PL-MNPQ",
    }
    assert _section((0, 3, 0)).scope_ids == ()


def test_an_id_named_for_exclusion_or_for_reference_is_placed_nowhere() -> None:
    """Naming is not membership, or the more carefully a decision is written
    down the more ids the reader mis-places (queue item PL-HDY6).

    Three shapes, all of them in the real file: an id mentioned inside another
    entry, a paragraph excluding one at length, and a queue item listed under
    "Explicitly out of scope". The first would survive a rule that read the
    section's lists and skipped its prose, which is why the frozen list is
    read by its entries' heads rather than by its bullets.
    """
    placed = set(_section((0, 4, 0)).scope_ids)
    scope = milestone_scope(parse_milestones(ROADMAP), _section((0, 4, 0)))

    assert not placed & {"PL-VWXY", "PL-STVW", "PL-Z7LY"}
    assert scope.placement("PL-STVW") == UNPLACED


def test_an_exclusion_the_reader_cannot_see_is_silence_not_the_opposite() -> None:
    """The cost of the rule above, stated where it is paid.

    v0.4.0 lists PL-Z7LY under "Explicitly out of scope", and the reader says
    nothing about it in either direction: it no longer claims the id as
    v0.4.0's scope, and it does not report the exclusion either. `unplaced` is
    the honest answer to a sentence it cannot read, and it is the safe one -
    an unread mention makes no claim, where the over-read one it replaces told
    a session that work a milestone excludes was work that milestone was
    waiting on.
    """
    scope = milestone_scope(parse_milestones(ROADMAP), _section((0, 3, 0)))

    assert scope.placement("PL-Z7LY") == UNPLACED
    assert scope.milestone("PL-Z7LY") == ""


#: v0.4.0's `Required scope` rewritten as bullets, the second of which names an
#: id **in order to exclude it** - the shape `ROADMAP.md` carried for `PL-B9PY`
#: until `PL-NBCS` moved it out.
SCOPE_BULLET_EXCLUSION_ROADMAP = ROADMAP.replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
    "- Stage 3, the decomposition proper, is **not** in scope: it is queue item\n"
    "  PL-WXYZ and stays at Gate 1, because only v0.5.0 needs it.",
)


#: The same excluding bullet with its id in the **declaration slot** rather
#: than in the sentence - the shape that still claims the id once membership is
#: declared, because the slot is read and the sentence around it never is.
SCOPE_DECLARATION_EXCLUSION_ROADMAP = ROADMAP.replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
    "- **Stage 3, the decomposition proper, is not in scope** (queue item\n"
    "  PL-WXYZ): it stays at Gate 1, because only v0.5.0 needs it.",
)


def test_an_id_a_scope_bullet_names_only_to_exclude_it() -> None:
    """Reads as scope, and this test exists to say that it still does.

    The declaration slot is read and the sentence around it is not, so a bullet
    that *declares* an id while saying it is out of scope claims it exactly as
    an including bullet would. No grammar separates the two, and none is
    attempted: the candidate that made the parser guess at the sentence was
    refused, because a phrasing it missed would print a wrong placement
    silently - which is the failure being removed rather than a smaller version
    of it.

    `PL-NBCS` is the case, and this is deliberately a *characterisation* test
    rather than a fix. The fix is that the exclusion moves under the other
    heading, where `excluded_ids` parses it apart from scope;
    `tools/doc_check.py` fails the contradiction that leaves behind and advises
    on this shape. What `PL-HWW1` changed is the other half, two tests up: the
    same sentence with the id *outside* the slot now claims nothing.
    """
    sections = parse_milestones(SCOPE_DECLARATION_EXCLUSION_ROADMAP)
    section = next(one for one in sections if one.version == (0, 4, 0))

    assert "PL-WXYZ" in section.own_scope_ids
    assert milestone_scope(sections, section).placement("PL-WXYZ") == IN_SCOPE
    assert "PL-WXYZ" not in section.excluded_ids


def test_the_exclusion_heading_is_parsed_apart_from_required_scope() -> None:
    """The two headings answer opposite questions, so they are read separately.

    `scope_ids` merges the frozen list with `Required scope` because placement
    does not care which structure placed an id. The contradiction check does
    care, because only `Required scope` can contradict `Explicitly out of
    scope`, so each is kept as its own tuple.

    Parsed and not yet *placed*: making an exclusion speak in the ranking is
    `PL-6P9Y`. An exclusion recorded by a milestone the project has already
    passed says what was true then, and `wave` hands `milestone_scope` no
    released section - so the answer here stays `UNPLACED`, as the test above
    this one asserts.
    """
    section = _section((0, 4, 0))

    assert section.excluded_ids == ("PL-Z7LY",)
    assert section.own_scope_ids == ("PL-MNPQ",)
    assert "PL-Z7LY" not in section.own_scope_ids


#: v0.4.0's `Required scope` written the way the real file writes an entry: the
#: member declared in the `(queue item ...)` slot after the bold title, and the
#: item that re-briefed the entry cited in the prose beside it. Naming the id
#: that changed an entry is how `ROADMAP.md` records provenance throughout, so
#: the citation is the shape that has to *not* count (`PL-HWW1`).
SCOPE_CITATION_ROADMAP = ROADMAP.replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "- **A displayed clinical unit** (queue item PL-MNPQ). **Re-briefed\n"
    "  2026-09-14** (`PL-VWXY`): the noun was stale, not the scope.",
)

#: One entry declaring two items, wrapped across a line break - the arrangement
#: a pair takes when the title runs long, and the reason a declaration is read
#: from the subsection's joined text rather than line by line.
SCOPE_PAIR_ROADMAP = ROADMAP.replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
    "- **One problem, two items** (queue items `PL-BCDF`\n"
    "  and `PL-GHJK`).",
)

#: A *numbered* `Required scope` list, which is what v0.6.0's section carries.
#: The entry unit has to read both forms or half the file's scope entries are
#: invisible to the rule that holds each one to a declaration.
SCOPE_NUMBERED_ROADMAP = ROADMAP.replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "1. **A displayed clinical unit** (queue item PL-MNPQ).\n"
    "2. **A second entry** (queue item `PL-RSTW`).",
)


def test_required_scope_places_only_declared_ids() -> None:
    """The declaration slot is the record; a citation beside it places nothing.

    `Required scope` was read *in full*, so an id cited in an entry's prose
    became a member of the release - and citing the id that re-briefed an entry
    is how this document records provenance, so the count drifted every time
    the file was maintained correctly rather than badly. `PL-HWW1` made the
    `(queue item ...)` slot the statement and left everything around it prose.
    """
    sections = parse_milestones(SCOPE_CITATION_ROADMAP)
    section = next(one for one in sections if one.version == (0, 4, 0))
    scope = milestone_scope(sections, section)

    assert section.own_scope_ids == ("PL-MNPQ",)
    assert "PL-VWXY" not in section.scope_ids
    assert scope.placement("PL-MNPQ") == IN_SCOPE
    assert scope.placement("PL-VWXY") == UNPLACED


def test_a_declaration_wrapped_across_a_line_break_is_read_whole() -> None:
    """Both halves of a pair count, and the line break between them is nothing.

    The slot is found in the subsection's joined text for this reason: read
    line by line, the second id of a wrapped pair would be dropped silently,
    which is the direction of failure the declaration rule exists to remove.
    """
    section = next(one for one in parse_milestones(SCOPE_PAIR_ROADMAP) if one.version == (0, 4, 0))

    assert section.own_scope_ids == ("PL-MNPQ", "PL-BCDF", "PL-GHJK")


def test_a_numbered_scope_entry_is_an_entry_like_a_bulleted_one() -> None:
    """v0.6.0's list is numbered and v0.5.0's is bulleted; both are entries.

    The ids are the same either way, because the slot is read from the whole
    subsection. What needs the entry unit is the per-entry rule
    `tools/doc_check.py` applies, which is why the entries are parsed here
    rather than only their ids.
    """
    section = next(
        one for one in parse_milestones(SCOPE_NUMBERED_ROADMAP) if one.version == (0, 4, 0)
    )

    assert section.own_scope_ids == ("PL-MNPQ", "PL-RSTW")
    assert [entry.ids for entry in section.scope_entries] == [("PL-MNPQ",), ("PL-RSTW",)]


def test_an_id_a_scope_entry_names_only_in_prose_is_not_claimed() -> None:
    """The shape `ROADMAP.md` carried for `PL-B9PY`, and what the rule does to it.

    The bullet says "it is queue item PL-WXYZ" in a sentence whose whole point
    is that the id is *not* in scope, and no grammar could separate that from
    an including sentence. The declaration rule does not try: the id is outside
    the `(queue item ...)` slot, so it is prose and places nothing. The test
    below keeps the other half - a declaration inside an excluding sentence is
    still read as scope, because the parser reads the slot and never the
    sentence.
    """
    sections = parse_milestones(SCOPE_BULLET_EXCLUSION_ROADMAP)
    section = next(one for one in sections if one.version == (0, 4, 0))

    assert "PL-WXYZ" not in section.own_scope_ids
    assert milestone_scope(sections, section).placement("PL-WXYZ") == UNPLACED


def test_an_out_of_scope_id_is_reported_excluded() -> None:
    """The anchor's own exclusions speak, which is `PL-6P9Y`.

    v0.4.0 names `PL-Z7LY` under "Explicitly out of scope for v0.4.0", and that
    heading's whole meaning is exclusion - as decidable as the ids under
    `Required scope` and the opposite claim. Reported as `unplaced`, an id the
    milestone has ruled out ranked level with work nobody has ruled on.

    The *anchor's* exclusions and no others, which is why the test above this
    one still answers `UNPLACED` for the same id against a v0.3.0 anchor: an
    exclusion recorded by a milestone the project has passed says what was true
    then.
    """
    sections = parse_milestones(ROADMAP)
    scope = milestone_scope(sections, _section((0, 4, 0)))

    assert scope.placement("PL-Z7LY") == EXCLUDED
    assert scope.milestone("PL-Z7LY") == ""


def test_the_scope_places_an_id_by_the_milestone_whose_section_names_it() -> None:
    scope = milestone_scope(parse_milestones(ROADMAP), _section((0, 3, 0)))

    assert scope.placement("PL-MNPQ") == OUT_OF_SCOPE
    assert scope.milestone("PL-MNPQ") == "v0.4.0"
    assert scope.placement("PL-ZZZZ") == UNPLACED


def test_a_released_milestones_section_places_nothing() -> None:
    """Its narrative records where a problem was raised, not what is current.

    Released is decided by the version the project is on: `wave` hands
    `milestone_scope` the unreleased sections alone, so v0.2.0's section never
    reaches it and PL-PQRS is placed by nobody. Read directly with every
    section, `milestone_scope` would report it as later work - which is the
    right answer for an unreleased section below the anchor (`PL-FWJF`) and
    the wrong one for a shipped one, and only `wave` knows which it is.
    """
    plan = _wave("0.2.5", frozenset(GATE_IDS))

    assert plan.scope.anchor == "v0.4.0 — the teachable case"
    assert plan.scope.placement("PL-PQRS") == UNPLACED
    assert plan.scope.placement("PL-MNPQ") == IN_SCOPE


def test_the_wave_carries_the_scope_of_the_milestone_the_beat_is_about() -> None:
    plan = _wave("0.2.5")

    assert plan.beat == CLEAR
    assert plan.scope.anchor == "v0.4.0 — the teachable case"
    assert plan.scope.placement("PL-001") == IN_SCOPE


def test_clearing_a_gate_leaves_the_gated_milestones_own_scope_out_of_the_step() -> None:
    """The regression for PL-1J0P, and the half that was a ranking defect.

    A milestone section places ids through two structures, and while its gate
    is open only one of them is work the current step includes: `ROADMAP.md`
    has the gate clear *before* the milestone it gates is implemented. Reading
    the whole section as current work offered v0.4.0's `Required scope` as
    v0.3.0's, which is the one thing the gate exists to stop - and `docket
    next` really was offering it, three deep, when this was found.
    """
    plan = _wave("0.2.5")

    assert plan.beat == CLEAR
    assert plan.scope.clearing
    assert plan.scope.placement("PL-001") == IN_SCOPE
    assert plan.scope.placement("PL-MNPQ") == OUT_OF_SCOPE
    assert plan.scope.milestone("PL-MNPQ") == "v0.4.0"


def test_a_gate_shipping_as_its_own_version_names_the_step_apart_from_the_anchor() -> None:
    """The label half of PL-1J0P: two names, and they are not the same name.

    `wave` reports v0.3.0 as the step while the gate is recorded under v0.4.0,
    so a caller that prints only the anchor and calls it the current step
    contradicts `wave` in the same session.
    """
    plan = _wave("0.2.5")

    assert plan.step is not None
    assert plan.step.label == "v0.3.0 — the foundation"
    assert plan.scope.anchor == "v0.4.0 — the teachable case"
    assert plan.scope.step_label == "v0.3.0 — the foundation"


def test_the_gated_milestones_own_scope_is_current_work_once_its_gate_is_clear() -> None:
    """The guard against over-narrowing: the exclusion above is the beat's, not
    the section's. Once every gate entry closes, `Required scope` is what the
    milestone is for and ranks as current work again."""
    plan = _wave("0.2.5", GATE_IDS)

    assert plan.beat != CLEAR
    assert not plan.scope.clearing
    assert plan.scope.placement("PL-MNPQ") == IN_SCOPE


def test_reading_a_section_directly_still_places_its_whole_scope() -> None:
    """`milestone_scope` is given no beat, so the narrowing is opt-in: a caller
    asking what a section places means the section, not the cadence."""
    scope = milestone_scope(parse_milestones(ROADMAP), _section((0, 4, 0)))

    assert not scope.clearing
    assert scope.step_label == ""
    assert scope.placement("PL-MNPQ") == IN_SCOPE


def test_a_plan_with_no_milestone_to_anchor_on_places_nothing() -> None:
    scope = milestone_scope(parse_milestones(ROADMAP), None)

    assert scope.anchor == ""
    assert scope.placement("PL-001") == UNPLACED


# --- a section-bearing row the `#` column skips (`PL-FWJF`) ------------------

#: The same roadmap with a `—` row between the patch track and v0.4.0 that
#: bears a section of its own - the Qt port's shape: not a step by the `#`
#: column, numbered as a patch, placed between the gate and the milestone that
#: recorded it, and carrying a `Required scope`. Standing on the patch track
#: with the gate clear, this row is the work the plan lists next, and it is
#: what anchoring on the next *numbered* milestone read straight past.
PORT_ROADMAP = ROADMAP.replace(
    "| 2 | **v0.4.0 — the teachable case** |",
    "| — | **v0.3.5 — the interface port** | Scoped below. A patch, on the timeline. | 1 L |\n"
    "| 2 | **v0.4.0 — the teachable case** |",
).replace(
    "## Milestone after next: v0.4.0 - the teachable case",
    """## v0.3.5 - the interface port

### Goal

Move the dashboard.

### Required scope

The chart (queue item PL-PRT7).

### Definition of done

Parity.

### Explicitly out of scope for v0.3.5

Compare mode.

## Milestone after next: v0.4.0 - the teachable case""",
)
PORT_KNOWN = KNOWN | {"PL-PRT7"}


def _ported(version: str, closed: frozenset[str] = frozenset()):
    return _wave(version, closed, roadmap=PORT_ROADMAP, known=PORT_KNOWN)


def test_a_section_bearing_row_without_a_number_is_the_beat_once_the_gate_is_clear() -> None:
    """The port's arrangement: the beat is the row's own work, the step stays
    on the patch track - which bears no section by grammar and is passed over,
    as the live `v0.4.x` row is - and the scope anchors on the row, so its ids
    read as the current step's and the gated milestone's own scope as later.
    Before this, `wave` printed `implement v0.4.0` and the port's ids were
    placed by no section."""
    plan = _ported("0.3.0", frozenset(GATE_IDS))

    assert plan.step is not None and plan.step.kind == "patch-track"
    assert plan.gate is not None and plan.gate.is_clear
    assert plan.beat == IMPLEMENT
    assert plan.subject == "v0.3.5 — the interface port"
    assert plan.milestone is not None and plan.milestone.version == (0, 3, 5)
    assert plan.own_scope is not None and plan.own_scope.milestone.version == (0, 3, 5)
    assert plan.scope.anchor == "v0.3.5 — the interface port"
    assert plan.scope.step_label == "v0.3.x — a readability pass"
    assert plan.scope.placement("PL-PRT7") == IN_SCOPE
    assert plan.scope.placement("PL-MNPQ") == OUT_OF_SCOPE
    assert plan.scope.milestone("PL-MNPQ") == "v0.4.0"


def test_the_beat_names_whose_gate_cleared_when_the_row_takes_none_of_its_own() -> None:
    """ "Its gate is clear" of the port would name a gate it does not have."""
    printed = format_wave(_ported("0.3.0", frozenset(GATE_IDS)))

    assert (
        "Beat      implement v0.3.5 — the interface port - the timeline puts it before "
        "v0.4.0 — the teachable case, whose gate is clear, 0 of 1 Required scope ids "
        "closed and 1 still open"
    ) in printed
    assert "Scope     the Required scope of v0.3.5 — the interface port (1 id)" in printed


def test_the_row_is_a_release_once_its_own_scope_closes() -> None:
    plan = _ported("0.3.0", frozenset(GATE_IDS | {"PL-PRT7"}))

    assert plan.beat == RELEASE
    assert plan.subject == "v0.3.5 — the interface port"
    assert (plan.release_version, plan.release_name) == ((0, 3, 5), "the interface port")


def test_once_the_row_ships_the_beat_returns_to_the_gated_milestone() -> None:
    """Released is decided by the version: once the row's number is cut the
    project stands on the row after it, the gated milestone's own scope is the
    beat again, and the shipped section places nothing - its ids are unplaced
    rather than later work."""
    plan = _ported("0.3.5", frozenset(GATE_IDS | {"PL-PRT7"}))

    assert plan.step is not None and plan.step.label == "v0.4.0 — the teachable case"
    assert plan.beat == IMPLEMENT and plan.subject == "v0.4.0 — the teachable case"
    assert plan.scope.placement("PL-MNPQ") == IN_SCOPE
    assert plan.scope.placement("PL-PRT7") == UNPLACED


def test_while_the_gate_is_open_the_rows_scope_is_work_the_step_has_not_reached() -> None:
    """The gate is the beat whatever else is written. The row below the anchor
    is unreleased rather than released, so its ids are later work mapped to the
    row - where reading "below the anchor" as "released" placed them nowhere."""
    plan = _ported("0.3.0")

    assert plan.beat == CLEAR
    assert plan.scope.anchor == "v0.4.0 — the teachable case"
    assert plan.scope.placement("PL-PRT7") == OUT_OF_SCOPE
    assert plan.scope.milestone("PL-PRT7") == "v0.3.5"


def test_a_row_bearing_no_section_between_the_gate_and_its_milestone_is_passed_over() -> None:
    """The limit, stated: a `—` row with nothing written under it cannot be
    counted, so the beat names the gated milestone as it did before."""
    unscoped = ROADMAP.replace(
        "| 2 | **v0.4.0 — the teachable case** |",
        "| — | **v0.3.5 — the interface port** | Not yet scoped. | — |\n"
        "| 2 | **v0.4.0 — the teachable case** |",
    )
    plan = _wave("0.3.0", frozenset(GATE_IDS), roadmap=unscoped)

    assert plan.beat == IMPLEMENT and plan.subject == "v0.4.0 — the teachable case"
    assert plan.scope.anchor == "v0.4.0 — the teachable case"


# --- what the answer refuses to do ------------------------------------------


def test_a_gate_naming_an_item_the_store_does_not_hold_is_not_clear() -> None:
    """An id the store cannot account for leaves the entry's state unknown, and
    an unknown entry is reported rather than counted as closed."""
    plan = wave(ROADMAP, "0.2.5", frozenset(GATE_IDS), KNOWN - {"PL-KLMN"}, {})
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
    return format_digest(Report(items=[parse_item(DIGEST_ITEM)]), None, None, plan)


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


# The fixture roadmap ends at v0.4.0, so nothing it holds is *later* than the
# milestone the beat is about. Giving v0.5.0 a section of its own is what makes
# an out-of-scope id exist at all, and it reproduces this repository's own
# shape: a step on v0.2.8's gate, and science work a later milestone places.
SCOPED_ROADMAP = ROADMAP.replace(
    "## Planned milestones",
    """## Milestone after that: v0.5.0 - the case you can branch

### Goal

Branching, later.

### Required scope

Validation against a published measurement (queue item PL-WXYZ).

### Definition of done

The learner can branch a case.

### Explicitly out of scope for v0.5.0

Everything else.

## Planned milestones""",
)

LATER_ITEM = """---
id: PL-WXYZ
title: Work a later milestone places
priority: P1
effort: S
status: ready
classes: science
touches: b.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def _scoped_wave():
    """A plan anchored on v0.4.0, with v0.5.0 placing `PL-WXYZ` beyond it."""
    return wave(SCOPED_ROADMAP, "0.2.5", frozenset(), KNOWN | {"PL-WXYZ"}, {})


def _digest_of(*bodies: str, plan: object = None) -> str:
    return format_digest(Report(items=[parse_item(body) for body in bodies]), None, None, plan)


def test_the_digest_top_line_leads_with_work_the_current_step_scopes() -> None:
    """PL-Q2BJ: the two lines sat in one block of output and disagreed.

    `PL-WXYZ` outranks `PL-001` on priority and would lead a sort of the
    store, exactly as `PL-9Y42` led every real session's digest while the
    beat two lines below said clear v0.2.8's gate. The plan is what breaks
    the tie, so the digest asks it rather than sorting.
    """
    top = next(
        line
        for line in _digest_of(DIGEST_ITEM, LATER_ITEM, plan=_scoped_wave()).splitlines()
        if line.strip().startswith("Top:")
    )

    assert "PL-001" in top
    assert "PL-WXYZ" not in top


def test_the_digest_names_the_milestone_when_only_out_of_scope_work_is_ready() -> None:
    """Hiding the item would be a verdict; saying which section places it is a fact."""
    top = next(
        line
        for line in _digest_of(LATER_ITEM, plan=_scoped_wave()).splitlines()
        if line.strip().startswith("Top:")
    )

    assert "PL-WXYZ" in top
    assert "scoped to v0.5.0, not this step" in top


def test_the_digest_top_line_still_answers_with_no_plan_to_scope_it() -> None:
    """An absent or unreadable roadmap leaves the ranking where it was."""
    top = next(
        line
        for line in _digest_of(DIGEST_ITEM, LATER_ITEM).splitlines()
        if line.strip().startswith("Top:")
    )

    assert "PL-WXYZ" in top
    assert "scoped to" not in top


def test_a_timeline_that_does_not_parse_says_so_rather_than_stating_a_step() -> None:
    """A step read off a broken table is a plausible wrong answer, not an answer."""
    hyphenated = ROADMAP.replace("v0.3.0 —", "v0.3.0 -")
    plan = _wave("0.2.5", frozenset({"PL-001"}), roadmap=hyphenated)
    stated = next(line for line in _digest(plan).splitlines() if line.startswith("Plan:"))

    assert "does not parse cleanly" in stated


# --- which milestones an item may be blocked on (`PL-W8XP`) ------------------

MILESTONE_STATES_ROADMAP = """# Plan

## Versioning decision

| Version | Status | Milestone |
| --- | --- | --- |
| v0.4.0 | Completed | The teachable case |
| v0.5.0 | Planned | The case you can branch |

## The plan

### The timeline

| # | Step | Notes | Effort |
| --- | --- | --- | --- |
| 1 | **v0.5.0 — the case you can branch** | scoped below | - |
| 2 | **v0.4.x — the code is the model** | a patch track | - |
| 3 | **Gate 1** | not a version at all | - |
| 4 | **v0.6.0 — the machine** | placed, not scoped | - |

## v0.5.0 - the case you can branch

### Goal

g

### Required scope

r

### Definition of done

d

### Explicitly out of scope for v0.5.0

o

## v0.7.0 - a section with no timeline row

Placed by its section alone.
"""


def test_milestone_states_reads_the_timeline_and_the_sections() -> None:
    """Both, because a milestone is placed on the timeline long before it has a
    section - which is exactly the interval a milestone blocker covers."""
    states = milestone_states(MILESTONE_STATES_ROADMAP)

    assert states.is_known("v0.6.0")  # timeline only
    assert states.is_known("v0.7.0")  # section only
    assert not states.is_known("v9.9.9")


def test_only_a_milestone_with_the_four_subsections_is_cleared() -> None:
    states = milestone_states(MILESTONE_STATES_ROADMAP)

    assert states.is_cleared("v0.5.0")
    assert not states.is_cleared("v0.6.0")
    assert not states.is_cleared("v0.7.0")


def test_a_completed_release_is_cleared_without_a_scoped_section() -> None:
    """`ROADMAP.md`'s own v0.2.8 and v0.3.0 sections answer `is_scoped` False,
    so a structural test alone would never clear a blocker naming one."""
    states = milestone_states(MILESTONE_STATES_ROADMAP)

    assert states.is_known("v0.4.0") and states.is_cleared("v0.4.0")


def test_a_patch_track_and_a_gate_are_not_milestones() -> None:
    """Neither carries a version writable in `blocked-by`: `v0.4.x` has no patch
    number by construction, and a gate has no version at all."""
    states = milestone_states(MILESTONE_STATES_ROADMAP)

    assert not any(version.startswith("v0.4.") and version != "v0.4.0" for version in states.known)
    assert "Gate 1" not in states.known


# --- ships with, rather than blocked until scoped (`PL-L09X`) ---------------

SHIPS_WITH_ROADMAP = MILESTONE_STATES_ROADMAP.replace(
    "### Required scope\n\nr\n",
    "### Required scope\n\n- **The chord-width rule** (queue item PL-GS3R).\n",
    1,
)


def test_an_item_a_scoped_unshipped_milestone_places_ships_with_it() -> None:
    """The relation `blocked-by` has no field for, read from what is written.

    `blocked-by: vX.Y.Z` means blocked until that milestone is *scoped*, which
    is what `PL-W8XP` built it for. `PL-GS3R`'s case is the other one: fully
    designed, and waiting for the milestone to *land*. Scoping cleared the
    blocker and could never have unblocked the item.
    """
    states = milestone_states(SHIPS_WITH_ROADMAP)

    assert states.is_cleared("v0.5.0"), "the milestone is scoped, which is the premise"
    assert states.ships_with("v0.5.0", "PL-GS3R")


def test_an_item_the_milestone_does_not_place_does_not_ship_with_it() -> None:
    """Narrow deliberately: the original advisory is correct for these.

    An item waiting on the scoping round, which has now happened, really is
    ready to promote. Suppressing that too would trade a false advisory for a
    silence, which is the worse of the two.
    """
    states = milestone_states(SHIPS_WITH_ROADMAP)

    assert not states.ships_with("v0.5.0", "PL-XXXX")


def test_a_shipped_milestone_no_longer_holds_what_it_placed() -> None:
    """Once it lands there is nothing left to wait for, so the relation ends."""
    shipped = SHIPS_WITH_ROADMAP.replace(
        "| v0.5.0 | Planned | The case you can branch |",
        "| v0.5.0 | Completed | The case you can branch |",
        1,
    )
    states = milestone_states(shipped)

    assert "v0.5.0" in states.released
    assert not states.ships_with("v0.5.0", "PL-GS3R")


# --- the milestone's own scope, and the third way to reach a release ---------
#
# `PL-KD98`. Reading only the two version-order arrangements, a milestone
# recording a gate *and* a `Required scope` could never reach the `release`
# beat, whatever the state of that scope - and both v0.4.0 and v0.5.0 are that
# shape. The fixture's v0.4.0 is too: its gate holds four ids and its
# `Required scope` names `PL-MNPQ`, so closing the gate alone leaves the
# milestone unfinished and closing `PL-MNPQ` as well finishes it.

#: A scope id the store does not hold, added to the same subsection.
_UNKNOWN_IN_SCOPE = ROADMAP.replace(
    "A displayed clinical unit (queue item PL-MNPQ).",
    "A displayed clinical unit (queue item PL-MNPQ), and one more (queue item PL-XQZ0).",
)


def test_the_scope_split_counts_ids_rather_than_entries() -> None:
    """`Required scope` is prose with ids written into it, so there is no entry
    to count - which is why `SECTION_ID_RE` reads the subsection in full and
    why this is the only honest unit."""
    section = next(s for s in parse_milestones(ROADMAP) if s.version == (0, 4, 0))

    assert section.own_scope_ids == ("PL-MNPQ",)
    assert section.scope_ids == ("PL-001", "PL-BCDF", "PL-GHJK", "PL-KLMN", "PL-MNPQ")

    status = scope_status(section, frozenset(), KNOWN)
    assert (status.closed, status.outstanding, status.unknown_ids) == ((), ("PL-MNPQ",), ())
    assert not status.is_complete
    assert scope_status(section, frozenset({"PL-MNPQ"}), KNOWN).is_complete


def test_a_scope_id_the_store_does_not_hold_withholds_completeness() -> None:
    """Read exactly as `GateStatus.unknown_ids` is: a typo or a file that never
    existed leaves the id's state unknown rather than closed."""
    plan = _wave("0.3.0", frozenset(GATE_IDS | {"PL-MNPQ"}), roadmap=_UNKNOWN_IN_SCOPE)

    assert plan.own_scope is not None
    assert plan.own_scope.unknown_ids == ("PL-XQZ0",)
    assert not plan.own_scope.is_complete
    assert plan.beat == IMPLEMENT


def test_a_milestone_whose_own_scope_has_closed_is_a_release() -> None:
    """The third arrangement, on the live shape: the gate is clear, the
    milestone's `Required scope` has closed, and the project is standing on a
    patch-track row - not a milestone, and carrying `-1` for its patch rather
    than a release number.

    That last part is why the arrangement cannot rest on `step`. `_current_step`
    puts the project on the row after the last milestone it released, which here
    is `v0.3.x` - so an arrangement reading `step.version` would have declined
    on exactly the project that filed the item.
    """
    plan = _wave("0.3.0", frozenset(GATE_IDS | {"PL-MNPQ"}))

    assert plan.step is not None and plan.step.kind == "patch-track"
    assert plan.step.version == (0, 3, -1)
    assert plan.gate is not None and plan.gate.is_clear
    assert plan.own_scope is not None and plan.own_scope.is_complete
    assert plan.beat == RELEASE
    assert plan.subject == "v0.4.0 — the teachable case"


def test_the_release_beat_carries_the_version_the_step_cannot_name() -> None:
    """`release_offer` reads these rather than `plan.step`, which names no
    version on the patch-track row the arrangement above stands on."""
    plan = _wave("0.3.0", frozenset(GATE_IDS | {"PL-MNPQ"}))

    assert (plan.release_version, plan.release_name) == ((0, 4, 0), "the teachable case")


def test_an_unfinished_scope_leaves_the_beat_at_implement() -> None:
    """The other half of the same test, and the cadence's ordinary case: the
    gate cleared so the scope could be implemented, and it has not been."""
    plan = _wave("0.3.0", frozenset(GATE_IDS))

    assert plan.own_scope is not None and not plan.own_scope.is_complete
    assert plan.beat == IMPLEMENT
    assert (plan.release_version, plan.release_name) == (None, "")


def test_gate_zeros_exception_still_wins_over_a_finished_scope() -> None:
    """Order is load-bearing. Under Gate 0's exception the frozen list ships as
    its own earlier version *first*, so a gated milestone whose scope happened
    to be complete must not be offered ahead of the release its gate earned."""
    plan = _wave("0.2.5", frozenset(GATE_IDS | {"PL-MNPQ"}))

    assert plan.own_scope is not None and plan.own_scope.is_complete
    assert plan.beat == RELEASE
    assert plan.subject == "v0.3.0 — the foundation"
    assert plan.release_version == (0, 3, 0)


def test_a_milestone_recording_no_scope_subsection_has_no_split_to_report() -> None:
    """v0.2.8's shape reaches `release` by the second arrangement, not this one,
    and an empty scope is not a finished one."""
    plan = _wave("0.3.0", frozenset(GATE_IDS), roadmap=_SELF_GATING)

    assert plan.own_scope is None
    assert plan.beat == RELEASE


# --- the release train, resolved once (`PL-2T03`) ----------------------------


def test_the_train_resolves_the_position_once() -> None:
    """Every arrangement question is put to one object: the row the project
    stands on, the order of the sections ahead of it, and which row bears which
    section. Released stays decided by the version; what comes before what is
    the table's row order, and nothing downstream compares versions to recover
    it."""
    from docket.roadmap import release_train

    train = release_train(SCOPED_ROADMAP, "0.3.0")

    assert train.position == 1
    assert train.step is not None and train.step.kind == "patch-track"
    assert [section.version for section in train.ahead] == [(0, 4, 0), (0, 5, 0)]
    assert (train.row(train.ahead[0]), train.row(train.ahead[1])) == (2, 4)
    assert train.places("PL-MNPQ") is train.ahead[0]
    assert train.places("PL-WXYZ") is train.ahead[1]
    assert train.row_placing("PL-WXYZ") == 4
    # v0.2.0 has shipped, so the id its section names is placed by nobody.
    assert train.places("PL-PQRS") is None
    assert train.problems == () and train.stale == ()


def test_a_gate_only_milestone_reached_from_another_row_is_a_release() -> None:
    """`PL-J45M`: the frozen list is the milestone's whole content and it has
    cleared, but the project stands on the patch track beneath it rather than
    on the milestone's own row. The second arrangement compared positions, so
    this fell through to `implement` - a finished milestone told it was
    unfinished - and `release_offer` carried a guard for exactly that
    fall-through."""
    gate_only = ROADMAP.replace(
        "### Required scope\n\nA displayed clinical unit (queue item PL-MNPQ).",
        "### What the list is\n\nThe frozen list above is the whole of this milestone.",
    )
    plan = _wave("0.3.0", frozenset(GATE_IDS), roadmap=gate_only)

    assert plan.step is not None and plan.step.kind == "patch-track"
    assert plan.gate is not None and plan.gate.is_clear
    assert plan.own_scope is None
    assert plan.beat == RELEASE
    assert plan.subject == "v0.4.0 — the teachable case"
    assert (plan.release_version, plan.release_name) == ((0, 4, 0), "the teachable case")


def test_implement_is_never_a_fall_through() -> None:
    """The other half of the same fix: `implement` is returned only where the
    milestone's own scope counts open work, so there is always a count to print
    beside the word and nothing downstream has to guess whether the classifier
    meant "unfinished" or "unrecognised"."""
    for roadmap in (ROADMAP, _ON_THE_GATES_OWN_ROW, PORT_ROADMAP):
        plan = _wave("0.3.0", frozenset(GATE_IDS), roadmap=roadmap, known=PORT_KNOWN)

        assert plan.beat == IMPLEMENT
        assert plan.own_scope is not None and not plan.own_scope.is_complete


def test_a_blocker_the_timeline_schedules_ahead_of_the_gate_reads_as_sequenced() -> None:
    """`PL-7CSP`: two gate entries wait on work off the list. The plan
    schedules one blocker on the port's row - before the gated milestone - and
    the other nowhere. Both stay carved out of what the gate can clear; what
    changes is that the report stops printing them as one case."""
    blockers = {"PL-001": ("PL-PRT7",), "PL-KLMN": ("PL-ZZZZ",)}
    plan = _wave("0.3.0", roadmap=PORT_ROADMAP, blockers=blockers, known=PORT_KNOWN | {"PL-ZZZZ"})
    gate = plan.gate

    assert gate is not None and plan.beat == CLEAR
    assert [entry.ids for entry in gate.blocked_outside] == [("PL-001",), ("PL-KLMN",)]
    assert [(held.entry.ids, held.row) for held in gate.sequenced_ahead] == [
        (("PL-001",), "v0.3.5 — the interface port")
    ]
    assert [entry.ids for entry in gate.waiting_outside] == [("PL-KLMN",)]
    assert [entry.ids for entry in gate.clearable] == [("PL-BCDF", "PL-GHJK")]

    printed = format_wave(plan)
    assert (
        "1 this gate can clear, 1 sequenced ahead of it, 1 waiting on 1 open item outside it"
    ) in printed
    assert "sequenced ahead of the gate, on v0.3.5 — the interface port: PL-001" in printed
    assert "blocked outside the gate: PL-KLMN" in printed
    assert "what they wait on: PL-ZZZZ" in printed
    assert (
        "clear the gate - 1 entry of 3 still open here, 1 sequenced ahead of it, "
        "1 blocked outside it by 1 open item"
    ) in printed
    # One open item, not two: `PL-001` waits on `PL-PRT7` off the list as well,
    # and the plan already pays for it on an earlier row. Charging the gate for
    # it would price the plan's own ordering as unbudgeted work (`PL-FCM3`).
    assert gate.outside_items == ("PL-ZZZZ",)


def test_a_blocker_placed_at_or_after_the_gate_is_not_sequenced_ahead_of_it() -> None:
    """Placed by the gated milestone's own scope, by a later milestone, or by
    no section: three placements, one verdict, because none of them clears
    before the gate does. An entry with one blocker sequenced ahead and one
    placed nowhere waits outside too - it needs the second regardless."""
    blockers = {"PL-001": ("PL-MNPQ",), "PL-KLMN": ("PL-WXYZ",), "PL-BCDF": ("PL-PRT7", "PL-ZZZZ")}
    ported_and_scoped = SCOPED_ROADMAP.replace(
        "| 2 | **v0.4.0 — the teachable case** |",
        "| — | **v0.3.5 — the interface port** | Scoped below. | 1 L |\n"
        "| 2 | **v0.4.0 — the teachable case** |",
    ).replace(
        "## Milestone after next: v0.4.0 - the teachable case",
        PORT_ROADMAP[
            PORT_ROADMAP.index("## v0.3.5 - the interface port") : PORT_ROADMAP.index(
                "## Milestone after next: v0.4.0 - the teachable case"
            )
        ]
        + "## Milestone after next: v0.4.0 - the teachable case",
    )
    plan = _wave(
        "0.2.5",
        roadmap=ported_and_scoped,
        blockers=blockers,
        known=PORT_KNOWN | {"PL-WXYZ", "PL-ZZZZ"},
    )
    gate = plan.gate

    assert gate is not None
    assert gate.sequenced_ahead == ()
    assert len(gate.waiting_outside) == 3 and gate.clearable == ()


def test_the_gate_sizes_the_work_its_entries_wait_on_outside_it() -> None:
    """`PL-FCM3`: the count line named the hole and never sized it, so `4 open -
    1 this gate can clear, 3 waiting on work outside it` read as four items of
    work where it was one plus thirteen. Distinct across entries and open only:
    two entries waiting on one item are one piece of work, and a blocker that
    has already closed is not remaining cost."""
    blockers = {"PL-KLMN": ("PL-8888", "PL-BBBB", "PL-CLSD"), "PL-001": ("PL-BBBB",)}
    plan = _wave(
        "0.3.0",
        frozenset({"PL-CLSD"}),
        blockers=blockers,
        known=KNOWN | {"PL-8888", "PL-BBBB", "PL-CLSD"},
    )
    gate = plan.gate

    assert gate is not None and plan.beat == CLEAR
    assert [entry.ids for entry in gate.waiting_outside] == [("PL-001",), ("PL-KLMN",)]
    assert gate.outside_items == ("PL-8888", "PL-BBBB")

    printed = format_wave(plan)
    assert "1 this gate can clear, 2 waiting on 2 open items outside it" in printed
    assert "blocked outside the gate: PL-001, PL-KLMN" in printed
    assert "what they wait on: PL-8888, PL-BBBB" in printed
    assert (
        "clear the gate - 1 entry of 3 still open here, 2 blocked outside it by 2 open items"
    ) in printed


def test_a_prerequisite_standing_behind_another_prerequisite_is_counted() -> None:
    """The half a frontier cannot answer. `_blockers_outside` stops where the
    walk first leaves the list, which is the right answer to *where* the work
    sits and the wrong one to *how much* of it there is: 38% of the open items
    carrying a blocker on 2026-09-20 waited on something their own blockers
    waited on in turn, so stopping at the crossing would have restated this
    item's defect one level down (`PL-FCM3`)."""
    blockers = {"PL-KLMN": ("PL-8888",), "PL-8888": ("PL-BBBB",), "PL-BBBB": ("PL-CCCC",)}
    plan = _wave("0.3.0", blockers=blockers, known=KNOWN | {"PL-8888", "PL-BBBB", "PL-CCCC"})
    gate = plan.gate

    assert gate is not None
    assert [entry.ids for entry in gate.waiting_outside] == [("PL-KLMN",)]
    assert gate.outside_items == ("PL-8888", "PL-BBBB", "PL-CCCC")
    assert "1 waiting on 3 open items outside it" in format_wave(plan)


def test_a_cycle_among_prerequisites_is_counted_once_rather_than_forever() -> None:
    """Two items waiting on each other. The walk has to stop, and stopping is
    not a nicety: `_plan` declines on `OSError`, `ValueError` and `KeyError`,
    so a `RecursionError` would take the session-start digest down rather than
    degrade it."""
    blockers = {"PL-KLMN": ("PL-8888",), "PL-8888": ("PL-BBBB",), "PL-BBBB": ("PL-8888",)}
    plan = _wave("0.3.0", blockers=blockers, known=KNOWN | {"PL-8888", "PL-BBBB"})

    assert plan.gate is not None
    assert plan.gate.outside_items == ("PL-8888", "PL-BBBB")


def test_a_milestone_a_gate_entry_waits_on_is_not_counted_as_an_open_item() -> None:
    """A `blocked-by` may name a milestone, and two of the store's do. It is a
    real prerequisite and is not an item anybody can pick up, so it is named
    and counted apart - folding it into the item count would overstate the
    work by exactly the argument this item made for understating it."""
    blockers = {"PL-KLMN": ("PL-8888", "v0.9.0")}
    plan = _wave("0.3.0", blockers=blockers, known=KNOWN | {"PL-8888"})
    gate = plan.gate

    assert gate is not None
    assert gate.outside_items == ("PL-8888",)
    assert gate.outside_milestones == ("v0.9.0",)

    printed = format_wave(plan)
    assert "1 waiting on v0.9.0 and 1 open item outside it" in printed
    # Named in the count above and not repeated here: this line is what a
    # reader can go and open, and a version is not a file.
    assert "what they wait on: PL-8888" in printed


def test_the_plan_header_names_the_step_apart_from_the_anchor() -> None:
    """`PL-B5DW`: `format_status`'s header called the anchor "the step the
    project is on" while `wave`, on the same tree, named the patch-track row as
    the step. The row is named apart from the anchor whenever `Scope` carries
    it, on the implementing beat and the clearing beat both."""
    from docket.render import _plan_header

    implementing = _ported("0.3.0", frozenset(GATE_IDS))
    assert _plan_header(implementing.scope, ())[0] == (
        "Plan: v0.3.5 — the interface port, the milestone due next; "
        "the project stands on v0.3.x — a readability pass."
    )

    clearing = _wave("0.2.5")
    assert _plan_header(clearing.scope, ())[0] == (
        "Plan: clearing the debt gate recorded under v0.4.0 — the teachable case; "
        "the project stands on v0.3.0 — the foundation."
    )

    same_row = _wave("0.3.0", frozenset(GATE_IDS), roadmap=_ON_THE_GATES_OWN_ROW)
    assert same_row.scope.step_label == ""
    assert _plan_header(same_row.scope, ())[0] == (
        "Plan: v0.4.0 — the teachable case, the step the project is on."
    )


#: `PORT_ROADMAP` with a version table recording the foundation and a patch cut
#: past the port's number - the arrangement `PL-Y1L0` measured, where the plan
#: was stepped past a milestone that never shipped and nothing said so.
RECORDED_PORT_ROADMAP = PORT_ROADMAP.replace(
    "## The plan",
    """## Versioning decision

| Version | Status | Milestone |
| --- | --- | --- |
| v0.3.0 | Completed | The foundation. |
| v0.3.6 | Completed / current baseline | A patch, cut past the port. |

## The plan""",
)


def test_a_milestone_row_the_version_has_passed_without_a_release_is_reported() -> None:
    """`PL-Y1L0`: released stays decided by the version, so the cut stepped the
    plan past the port; what is no longer true is that nothing reports it. The
    version table is the record of what shipped, and a milestone number the
    project has passed with no row there is a statement about two files."""
    plan = _wave("0.3.6", frozenset(GATE_IDS), roadmap=RECORDED_PORT_ROADMAP, known=PORT_KNOWN)

    assert plan.step is not None and plan.step.label == "v0.4.0 — the teachable case"
    assert plan.beat == IMPLEMENT and plan.subject == "v0.4.0 — the teachable case"
    (statement,) = plan.stale
    assert statement.startswith("v0.3.5 — the interface port (timeline line ")
    assert ", section line " in statement
    assert "which the project has passed with no v0.3.5 release in the version table" in statement
    assert "The plan and the project disagree" in format_wave(plan)
    assert "the beat rests on a stale plan - check `wave`." in _digest(plan)


def test_a_milestone_number_the_version_has_just_reached_names_both_edits() -> None:
    """The cut that took the port's own number: the table lacks the row for the
    release being cut too, so the statement says which edit each reading owes
    rather than deciding whether this release is the port."""
    plan = _wave("0.3.5", frozenset(GATE_IDS), roadmap=RECORDED_PORT_ROADMAP, known=PORT_KNOWN)

    (statement,) = plan.stale
    assert "which the project has reached with no v0.3.5 release" in statement
    assert "its table row is owed if this release is that milestone" in statement


def test_a_roadmap_recording_no_release_has_nothing_to_compare_the_version_against() -> None:
    """No version table is no record, and the fixtures above carry none: the
    step and the beat are computed as before, and nothing is called stale."""
    plan = _ported("0.3.6", frozenset(GATE_IDS))

    assert plan.step is not None and plan.step.label == "v0.4.0 — the teachable case"
    assert plan.stale == ()
    assert "The plan and the project disagree" not in format_wave(plan)


def test_a_section_no_row_bears_is_reported_rather_than_placed_by_guess() -> None:
    """A section the table does not place has no arrangement to read. It still
    places its ids, after every section a row bears, and the plan says so
    instead of ordering it by a version comparison nobody wrote down."""
    rowless = SCOPED_ROADMAP.replace(
        "| 4 | **v0.5.0 — the case you can branch** | Not yet scoped. | — |\n", ""
    )
    plan = _wave("0.2.5", roadmap=rowless, known=KNOWN | {"PL-WXYZ"})

    (statement,) = plan.stale
    assert statement.startswith("line ")
    assert statement.endswith(
        "the v0.5.0 — the case you can branch section has no timeline row, "
        "so the plan does not say where it comes"
    )
    assert plan.scope.placement("PL-WXYZ") == OUT_OF_SCOPE
    assert plan.scope.milestone("PL-WXYZ") == "v0.5.0"


def test_the_digest_does_not_call_a_rowless_section_a_numbering_lag() -> None:
    """`PL-DK8Y`: the digest's one sentence stands over all four kinds of
    statement `Wave.stale` carries, and this is the kind it used to misname.
    Nothing here is behind anything - the timeline places the section nowhere,
    so a reader sent to the timeline's numbers is sent to the wrong file."""
    rowless = SCOPED_ROADMAP.replace(
        "| 4 | **v0.5.0 — the case you can branch** | Not yet scoped. | — |\n", ""
    )
    plan = _wave("0.2.5", roadmap=rowless, known=KNOWN | {"PL-WXYZ"})
    digest = _digest(plan)

    (statement,) = plan.stale
    assert "has no timeline row" in statement
    assert "the beat rests on a stale plan - check `wave`." in digest
    assert "numbering is behind" not in digest


#: `RECORDED_PORT_ROADMAP` with the port's own number recorded as shipped - the
#: state a patch cut at that number leaves behind, one run after the statement
#: above was printed at the hand-off.
SHIPPED_PORT_ROADMAP = RECORDED_PORT_ROADMAP.replace(
    "| v0.3.6 | Completed / current baseline | A patch, cut past the port. |",
    "| v0.3.5 | Completed | A patch that took the port's own number. |\n"
    "| v0.3.6 | Completed / current baseline | A patch, cut past the port. |",
)


def test_a_released_milestone_row_with_its_scope_still_open_is_reported() -> None:
    """`PL-LN3T`: the residual of the case above. Once the cut has written the
    port's number into the version table the row reads as released, its section
    leaves `ahead`, and the hand-off's statement is gone - so only the store
    distinguishes the port shipped from the port skipped, and it says open."""
    plan = _wave("0.3.6", frozenset(GATE_IDS), roadmap=SHIPPED_PORT_ROADMAP, known=PORT_KNOWN)

    assert plan.step is not None and plan.step.label == "v0.4.0 — the teachable case"
    (statement,) = plan.stale
    assert statement.startswith("v0.3.5 — the interface port (timeline line ")
    assert ", section line " in statement
    assert "which the version table records as released" in statement
    assert "1 of 1 ids in its own Required scope are still open (PL-PRT7)" in statement
    assert "the row owes a number the project has not reached if it was not" in statement
    assert "The plan and the project disagree" in format_wave(plan)


def test_a_released_milestone_whose_scope_has_closed_says_nothing() -> None:
    """The statement above has to be silent on every milestone that genuinely
    shipped, or it prints on this repository's own file for every release it
    has ever made."""
    plan = _wave("0.3.6", GATE_IDS | {"PL-PRT7"}, roadmap=SHIPPED_PORT_ROADMAP, known=PORT_KNOWN)

    assert plan.stale == ()
    assert "The plan and the project disagree" not in format_wave(plan)


#: `SHIPPED_PORT_ROADMAP` with the port's `Required scope` replaced by a frozen
#: list holding the same one entry - v0.2.8's shape, where the list is the
#: milestone's whole content - so the released row's only placing structure is
#: the one `stale_scopes` does not read.
GATE_ONLY_SHIPPED_ROADMAP = SHIPPED_PORT_ROADMAP.replace(
    "### Required scope\n\nThe chart (queue item PL-PRT7).",
    "### Debt gate: the frozen list\n\n- PL-PRT7 (M) The chart",
)


def test_a_released_milestone_row_with_its_frozen_list_still_open_is_reported() -> None:
    """`PL-SZJ2`: `PL-LN3T`'s case in a section's other placing structure. The
    released section leaves `ahead`, so no gate counts its list, and an open
    entry no later section places has dropped out of the plan - which, before
    this, `wave` printed nowhere at all."""
    plan = _wave(
        "0.3.6", frozenset(GATE_IDS), roadmap=GATE_ONLY_SHIPPED_ROADMAP, known=PORT_KNOWN
    )

    assert plan.gate is not None and plan.gate.milestone.label == "v0.4.0 — the teachable case"
    (statement,) = plan.stale
    assert statement.startswith("v0.3.5 — the interface port (timeline line ")
    assert "which the version table records as released" in statement
    assert "1 of 1 entries on its frozen list are still open and placed by no" in statement
    assert "section ahead (PL-PRT7)" in statement
    assert "the row owes a number the project has not reached if it was not" in statement
    assert "The plan and the project disagree" in format_wave(plan)


def test_a_released_frozen_list_entry_deferred_to_a_later_gate_says_nothing() -> None:
    """A deferral on `ROADMAP.md` § "The cadence" beat 3's terms leaves the entry
    open on the list it was frozen on and names the later gate that now holds
    it, which is Gate 1's `PL-WZVZ` on this repository's own file. Counting
    every open entry would call that stale, and `wave` would exit non-zero on a
    deferral done exactly as the cadence asks."""
    deferred = GATE_ONLY_SHIPPED_ROADMAP.replace(
        "- PL-KLMN (S)", "- PL-PRT7 (M) The chart, deferred from the port\n- PL-KLMN (S)"
    )
    plan = _wave("0.3.6", frozenset(GATE_IDS), roadmap=deferred, known=PORT_KNOWN)

    assert plan.gate is not None and "PL-PRT7" in plan.gate.ids
    assert plan.stale == ()
    cleared = _wave(
        "0.3.6", GATE_IDS | {"PL-PRT7"}, roadmap=GATE_ONLY_SHIPPED_ROADMAP, known=PORT_KNOWN
    )
    assert cleared.stale == ()
