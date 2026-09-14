---
id: PL-FWJF
title: The Qt port is the next substantial work but sits on a — timeline row, so bin/docket wave anchors on v0.5.0 and every port item reads as placed by no section
priority: P2
effort: M
status: done
classes: defect
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-14
closed: 2026-09-14
verify: uv run pytest subprojects/docket/tests/test_roadmap.py && grep -q 'def test_a_section_bearing_row_without_a_number_is_the_beat_once_the_gate_is_clear' subprojects/docket/tests/test_roadmap.py
---


**Problem.** The Qt port is the next substantial work but sits on a — timeline row, so bin/docket wave anchors on v0.5.0 and every port item reads as placed by no section

**Found while landing `PL-RKWB`** (the 2026-09-14 decision moving the Qt port
ahead of v0.5.0's display half).

**What happens.** `bin/docket wave` anchors its `Scope` on the next *numbered*
milestone, which is v0.5.0. The port sits on a `—` row, like the `v0.4.x` track
and the `MVP complete` marker, so its own `Required scope` is never read. Every
port item therefore prints the third relation - "Placed by no section of v0.5.0:
neither its frozen list nor its `Required scope` names this id" - which is
literally true and reads as *unplaced* at the exact moment the port is the work
the plan calls for. `PL-G59B` is `P1` and ranks third in `bin/docket next` with
that sentence under it.

Naming the build items in the port's `Required scope` was done under `PL-RKWB`
and does not fix this: the section is correct, and nothing reads it.

**Two candidate answers, and the choice is the project owner's** because it is a
question about the plan's shape rather than about the tool:

1. **Number the timeline row.** The port is a milestone by this file's own test
   - its own goal, required scope, definition of done and out-of-scope list -
   and it now sits between Gate 1 and v0.5.0 as the next substantial work. This
   renumbers rows 5-9 and is the honest reading of what the row has become.
2. **Teach `wave` to anchor on any section-bearing row**, numbered or not. This
   leaves the plan alone and fixes the reading for the `v0.4.x` track too, which
   has the same shape and the same blind spot.

Option 1 is a roadmap edit; option 2 is apparatus work in
`subprojects/docket/`. They are not exclusive.

**Why it matters.** The skill's own guidance says "placed nowhere" is the
relation that goes wrong, because silence is indistinguishable from not having
looked. A session offered `PL-G59B` today reads that it is placed by nothing
while the timeline places it ahead of the milestone it is being compared
against - and the rule is to say what the gate says before recommending
off-gate work, which here would state the opposite of the plan.

**Done when** a port item offered by `bin/docket next` carries a placement
sentence that agrees with the timeline.

**Verified 2026-09-14, and half of it has moved since capture.** The port now
*has* a section - `## v0.4.26 - the interface moves to Qt`, with its own Goal,
`Required scope` and Definition of done - so "every port item reads as placed by
no section" is no longer true; `bin/docket next` places `PL-G59B` by it. What
remains true is the anchoring half, and it is the consequential one:
`bin/docket wave` still reports `Step: between numbered steps (- on the
timeline): v0.4.x - the code is the model`, `Next: Gate 1`, `Scope: the Required
scope of v0.5.0` and `Beat: implement v0.5.0`, with no mention of the port's row at
all - even though the timeline places that row *between* Gate 1 and v0.5.0.

**Why it matters.** `wave` is what the `docket` skill tells a session to read
first, above the queue, precisely because the queue cannot say which beat is
due. It is now naming the wrong milestone: the next substantial work is the Qt
port, and a session following `wave` starts v0.5.0's Required scope instead - on
the surface the port is about to rewrite. The cause is that the anchor is found
by scanning for the next *numbered* step, and the port deliberately sits on a
`-` row; that is the general defect, and `PL-VFD8` is the same blind spot
reported from the reserved-version side.

**Done when.** `bin/docket wave` anchors on a `-` timeline row that carries its
own scoped section, so a project standing between Gate 1 and v0.5.0 is told the
beat is v0.4.25, with that section's `Required scope` counted the way v0.5.0's
is. A numbered step behind an unstarted `-` row does not become the beat.

**Re-checked 2026-09-14 after `#576` merged.** `v0.4.25` was cut and the
port's section renumbered to `v0.4.26`; `bin/docket wave` still reports
`Beat: implement v0.5.0`, so the anchoring defect survived the renumber
intact - which is the point, since it is about the row's shape rather than
its number.

**Decided 2026-09-14: option 2** (project owner, in the session that cut
v0.4.25). Option 1 buys one row and churns the plan; option 2 fixes the
reading for every `—` row that bears a section.

**Done 2026-09-14.** Two readings changed, both in
`subprojects/docket/src/docket/roadmap.py`:

- `wave` binds the beat's milestone to the first section-bearing timeline row
  between the project and the gated milestone, numbered or not, once the gate
  is clear (`_due_before`). The row's own `Required scope` decides `implement`
  or `release` for it exactly as `_release_due`'s third arrangement does for
  the milestone itself, and the gated milestone returns as the beat when the
  row's number is cut. Only a row whose section records its own scope is read;
  a row with no section, or none with a `Required scope`, is passed over and
  the beat stays on the gated milestone - stated in the docstring rather than
  guessed at. The `v0.4.x` row is passed over by the same test, because a
  patch-track heading has two numbers and `SECTION_VERSION_RE` wants three, so
  it can bear no section - which is what keeps it the step while the port is
  the work.
- `milestone_scope` no longer reads "below the anchor" as "released". `wave`
  hands it the unreleased sections alone, so released is decided by the version
  the project is on, and an unreleased section below the anchor - the port
  while Gate 1 is the beat - places its ids as later work mapped to it, where
  before they were placed by nobody.

`render.py`'s beat sentence says whose gate cleared when the beat's milestone
is not the one that recorded it, because "its gate is clear" of the port would
name a gate it does not have. Live, `bin/docket wave` now prints `implement
v0.4.26 — the interface moves to Qt - the timeline puts it before v0.5.0 — the
case you can branch, whose gate is clear, 4 of 26 Required scope ids closed and
22 still open`, and `bin/docket next` places a port item with `In scope for
v0.4.26 — the interface moves to Qt, which the step the project is on (v0.4.x —
the code is the model) comes before`.

**A consequence worth knowing.** v0.5.0's open `Required scope` ids now read as
later work - `scoped to v0.5.0, which the current step has not reached` - and
rank below unplaced items, which is what the timeline says. The row's prose
that the port-neutral spine is untouched by the port is judgment the tool does
not read, so a session offering one of those items says so itself.

**`PL-VFD8` and `PL-188T` stay open.** No new carrier was added to `Wave`; the
fix binds the existing `milestone` carrier to the row the timeline puts first.
That reserves the port's own number while the port is the beat's milestone,
which is `PL-188T`'s arrangement, and a test in `test_release.py` pins it - but
their "Done when" is the guard answering from every version the roadmap names
ahead, and a row with no section still binds nothing (`PL-VFD8`'s v0.6.0).
`PL-B5DW` captures the one thing the sweep found: `docket status`'s plan header
still calls the anchor "the step the project is on".
