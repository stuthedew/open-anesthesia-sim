---
id: PL-YS9F
title: outstanding_roadmap_edits states both edits for a milestone number a cut has exactly reached because it cannot read the beat that decides which; the plan computed before the bump knows
priority: P3
effort: S
status: done
classes: defect
feature: timeline-arrangement
milestone: v0.5.12
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_release.py
added: 2026-09-19
closed: 2026-09-26
pr: 1044
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

**Worked.** 2026-09-26, on `claude/pl-batch-07-nxa7vx`. `cmd_release` reads
the plan with `cli._plan` just before `prepare_bump`, after the dry-run return,
so a dry run pays nothing for it, and hands it to `_hand_off`, which passes it
to `outstanding_roadmap_edits(roadmap, version, plan=None)`. There a
`release` beat whose `release_version` is the cut's own number becomes
`releasing=True`, any other beat `False`, and no plan `None`, handed to a new
optional `releasing` argument on `roadmap.stale_milestones`; its other caller,
`ReleaseTrain`'s own `stale` read, passes nothing and is unchanged. The first
reading's statement names the table row only, as the combined statement
always did: the brief's Problem line also mentions the section heading, but
`roadmap.py` treats a milestone heading's prefix as editorial and nothing
checks it. One case the brief did not name: a resumed cut whose interrupted
run already bumped reads the version it is finishing, so the plan it could
compute is the post-bump one, and it passes no plan and keeps both readings.
Tests in `subprojects/docket/tests/test_release.py`: a `SCOPED_PORT_ROADMAP`
fixture (`PORT_CUT_ROADMAP` with the port given a frozen list, a Required
scope, a definition of done and an out-of-scope list, so `wave` gives it a
`release` or `implement` beat); the brief's named test over the three
readings; one replacing the beat's number by hand with `dataclasses.replace`,
so a `release` beat for another version is shown to be the second reading;
and an end-to-end cut on `_TrainRepo`, which fails when the plan is read after
the bump, checked by reading it there on a scratch edit.
