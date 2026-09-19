---
id: PL-YS9F
title: outstanding_roadmap_edits states both edits for a milestone number a cut has exactly reached because it cannot read the beat that decides which; the plan computed before the bump knows
priority: P3
effort: S
status: ready
classes: defect
feature: timeline-arrangement
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_release.py
added: 2026-09-19
verify: grep -q 'def test_the_reached_number_statement_reads_the_plan' subprojects/docket/tests/test_release.py
---

**Problem.** outstanding_roadmap_edits states both edits for a milestone number a cut has exactly reached because it cannot read the beat that decides which; the plan computed before the bump knows

**Found 2026-09-19 closing `PL-2T03`.** `outstanding_roadmap_edits(roadmap,
version)` reads the roadmap and the cut version alone, and at the hand-off the
version table lacks the cut's own row by construction - so a milestone row
whose number the cut has exactly reached is ambiguous from the file: either
this release *is* that milestone, and its table row and section heading are
owed, or a patch has taken the milestone's number and the row owes a new one.
The statement names both edits and leaves the reading to the operator. The
plan computed *before* the bump knows which: a `release` beat whose
`release_version` is the cut version is the first reading, and anything else
is the second.

**Why it matters.** The hand-off is read once, at the moment the operator is
doing something else; a line that asks them to decide costs more than a line
that tells them.

**Done when.** `cmd_release` computes the plan before bumping and hands it to
`_hand_off`, `outstanding_roadmap_edits` takes it as an optional argument so
the reached-number statement is decisive where a plan is available and
unchanged where one is not, and a test in
`subprojects/docket/tests/test_release.py` pins both readings.
