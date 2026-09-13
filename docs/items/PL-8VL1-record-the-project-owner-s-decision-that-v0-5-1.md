---
id: PL-8VL1
title: "Record the project owner's decision that v0.5.1 reserves for planned-milestone item 34's tiled layout: panels as independent widgets in nested splitters, with the handles inert until item 34"
priority: P3
effort: S
status: done
classes: planning, docs
feature: qt-port
milestone: v0.4.15
touches: ROADMAP.md
added: 2026-09-12
closed: 2026-09-12
pr: 502
verify: python3 tools/doc_check.py check && grep -qF 'reserves for planned-milestone item 34' ROADMAP.md
---

**Problem.** Record the project owner's decision that v0.5.1 reserves for
planned-milestone item 34's tiled layout: panels as independent widgets in
nested splitters, with the handles inert until item 34.

**Where the decision came from.** Planned-milestone item 34 (Blender-style
window management) was captured the same day, from the project owner's own
note, and left unplaced — `ROADMAP.md` records placement as theirs. The live
question was what v0.5.1 does about it, and it had a deadline the item did not:
that release rewrites every layout in the dashboard onto Qt, so a layout
architecture decided after it is a layout decided twice. Three answers were
put; the owner took the middle one on 2026-09-12.

- **Build the tiled shell in v0.5.1.** Scope creep on an already-scoped port
  that has `PL-GS3R` (the P1 `safety`-classed chord-width item) sequenced
  behind it.
- **Reserve for it.** Taken.
- **Ignore it.** Lays out every panel twice, which is the argument this
  milestone already makes for absorbing planned-milestone item 33.

**Why reserving is close to free.** `PL-B9PY` (decompose `SimulationView` so
two runs can be rendered at once) ships in v0.5.0 and already records that "the
Qt view is built decomposed from the start". The components therefore exist by
a decision already taken; the only thing this adds is the container they go
into — nested `QSplitter`s rather than fixed layouts.

**Why the handles are inert, which is the part that needed deciding rather
than recording.** A draggable splitter is something a learner can do that they
cannot do today. v0.5.1's § "Fixes this port carries, and why that is not scope
creep" excludes new capability "whatever its size", and its definition of done
is parity meaning "identical except for this list" — checkable only while that
enumeration stays closed. `PL-16ZC` (a show/hide control for the clinical
references and control marks) is the precedent: small, squarely in the
rewritten surface, and excluded for being a control that does not exist today.
Live handles would sit on the same side of that line. Item 34 turns them live
as its first step.

**Outcome.** One passage under v0.5.1's Required scope item 2 ("The
dashboard"), recording the reservation, the near-zero cost, and the inert-handle
constraint with the parity argument behind it.
