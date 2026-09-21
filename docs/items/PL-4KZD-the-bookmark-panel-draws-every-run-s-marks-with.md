---
id: PL-4KZD
title: The bookmark panel draws every run's marks with the reference run's standings, so while two runs are shown the row states one run's answer with nothing saying which
priority: P1
effort: S
status: done
classes: defect, safety
feature: scenario-branching
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_simulation_view.py
added: 2026-09-20
closed: 2026-09-20
payoff: stops a mark's row attributing one run's answer to the other while two managements are being compared
verify: grep -q 'def test_a_branch_that_halted_on_a_target_the_trunk_is_still_running_for_says_so' tests/unit/test_dashboard_frame.py
recurrences: 2026-09-20 PL-GHMB
---

**Problem.** The bookmark panel draws every run's marks with the reference run's standings, so while two runs are shown the row states one run's answer with nothing saying which

**Why it matters.** A standing is per-run by construction - it is computed from
that run's own clock, its own `began_at_s` and its own halt set - but the panel
is drawn once, from `snapshots[0]`. `_refresh_bookmarks`'s docstring gives the
reason: "Reading one run is correct rather than a simplification:
`_apply_to_every_run` is the only thing that writes a mark, so every displayed
run carries the same set". That is true of `snapshot.bookmarks` and false of
`snapshot.bookmark_standings`. The set is shared; the answers are not.

**Measured 2026-09-20** against `4c282700`. A trunk marked at a MAC target of
0.4 xMAC on the alveolar compartment halts there and reads `reached`; the
branch forked at that halt reads `still_running`, at the fork and 300 s later.
Two different answers, one panel, and the panel shows the reference run's with
nothing on the row naming a run.

The same shape on a time bookmark: a trunk standing at 3 h with a mark at 1 h
and a branch standing at 1 h disagree about that mark, correctly - they are at
different places on the case.

**It is masked today and will not stay masked.** While a standing is close to a
permanent latch, the two runs' answers usually agree, so the wrong row is
usually the right row by accident. `PL-3K9B`'s decision makes a time bookmark's
standing answer where the run *is*, which is exactly the quantity two runs
differ in - so the panel's single row starts being wrong for one of the two
runs most of the time.

**What it is not.** Not an argument for per-run mark sets: the marks are shared
deliberately (`app/controller.py`'s `_branch_from`), because a comparison is two
managements answering one question. It is the *answers* that need attributing.

**Where.** `app/simulation_view.py`'s `_refresh_bookmarks` and
`app/dashboard_frame.py`'s `bookmark_panel`, whose docstring already states the
adjacent guarantee - "so a panel cannot be drawn from one run's marks and
another run's answers" - which holds within a snapshot and says nothing about
which run's snapshot was chosen.

**Done when.** While more than one run is displayed, a mark's row either states
which run its standing belongs to or states both; and no row can be drawn that
attributes one run's answer to the set every run carries.

**Folded into `PL-LHBY`** (project owner, 2026-09-20, ratified, over working
this item alone). `PL-LHBY` - a branch halted on a learner's mark reports
nothing, because the marks panel draws standings from the reference run only -
is the same root, the same classes and the same priority, and is the carrier:
it reproduces offscreen against the merged tree and its `touches` reach
`app/qt_widgets.py`, which this item's do not. `PL-25DD` is the third of the
family. All three carry `feature: two-run-attribution`.

`PL-3K9B` made this live rather than masked (merged 2026-09-20, `#805`). A
time bookmark's standing is now positional - read from each run's own clock -
which is exactly the quantity two runs differ in, so the single row drawn from
`snapshots[0]` is now wrong for one of the two runs most of the time a
comparison is on screen, where before the two answers usually agreed.

**Closed 2026-09-20 with `PL-LHBY`, and the condition that note set was met
first.** It said not to drop this item before `PL-LHBY` was on the gate in its
place, or the gate would read clear while the defect stood. `#806` admitted
`PL-LHBY` to v0.5.0's frozen list, and the change closing both landed after
that, so the gate never read clear on an open defect. One change answers both:
this item's "done when" is contained in `PL-LHBY`'s, which adds the two
consequences reproduced offscreen and the requirement that
`MarkStanding.BEFORE_THIS_BRANCH` become reachable on screen.

The `verify:` command was rewritten on closing. It named
`tests/unit/test_simulation_view.py`, a file that has never existed in this
repository - that view's tests are in `tests/integration/test_simulation_view.py`
and `tests/unit/test_dashboard_frame.py` - so as written it could not have
passed on any tree. It now names the unit test holding this item's own "done
when": a row whose runs disagree names each one.
