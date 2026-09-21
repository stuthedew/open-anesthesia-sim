---
id: PL-N3N5
title: A failed run's marks still stand as reachable: _bookmark_standings never sees that start() refuses to resume it, so every mark on it reads as not yet
priority: P1
effort: S
status: done
classes: defect, safety
milestone: v0.5.0
touches: src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_bookmarks.py, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py, docs/MODEL.md
added: 2026-09-20
closed: 2026-09-21
pr: 819
payoff: stops the marks panel telling a learner a mark is still ahead of a run that cannot be resumed without a reset
verify: grep -q 'def test_a_failed_run_s_marks_do_not_stand_as_reachable' tests/integration/test_simulation_view.py
---

**Problem.** A failed run's marks still stand as reachable: _bookmark_standings never sees that start() refuses to resume it, so every mark on it reads as not yet

**Why it matters.** `SimulationController._bookmark_standings` passes
`reached_instants_s`, `reached_crossings`, `opened_at_s`, `elapsed_s`,
`run_length_cap_s` and `stopped_at_cap` — and nothing about whether the run
can take another step. `MarkStanding.STILL_RUNNING` says in its own docstring
that "the run can still reach this mark, and has not yet", so on a run
`SimulationController.start` refuses to resume — "cannot resume a failed
simulation … reset it first" — the first half of that is false. The same
`stopped_at_cap` argument beside it exists precisely to stop a run that has
finished answering from reading as one that has not, which is the pattern this
case is missing.

It is older than `PL-LHBY` and independent of two runs: a lone failed run has
carried the same standing since `PL-CTD7`. What changed is only that the
standing is now drawn in words on an attributed row, where before it rendered
as silence and nobody could read it wrong.

**Found by** the adversarial review of `PL-LHBY`, which reproduced it by
failing one of two runs and reading the whole screen at one instant: the run's
own panel said `Stopped — simulation error` while its mark clause claimed the
mark was still ahead of it.

**What it is not.** Not an argument for folding the transport state into the
standing vocabulary generally. A *paused* run is correct as it stands — it can
be resumed, so "not yet" holds of it. The failure case is the one where the
model can decide the mark is unreachable and does not say so, which is exactly
the distinction `BEFORE_THIS_BRANCH` and `NOT_REACHED_WITHIN_CAP` were split
out for.

**Done when.** A run that cannot take another step reports a standing that
claims no reachability, and a test fails one of two displayed runs and reads
the row.
