---
id: PL-59WB
title: chart_time_base.fit_to_run takes a parameter called run_length_s but is passed a case instant, which is the duration_s-was-not-a-duration defect one module over
priority: P2
effort: S
status: ready
classes: defect
feature: core-domain-language
touches: src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_chart_time_base.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_chart_time_base.py && ! grep -q 'def fit_to_run(run_length_s' src/anesthesia_sim/app/chart_time_base.py
---


**Problem.** chart_time_base.fit_to_run takes a parameter called run_length_s but is passed a case instant, which is the duration_s-was-not-a-duration defect one module over

**Found 2026-09-14** by a completeness pass over `PL-ZMRT` (one
simulated-time frame). It is the same defect that change renamed
`RunDefinition.duration_s` to `reached_s` to remove, surviving one module over
and unnoticed because the rename was scoped to `core/run_definition.py`.

`app/chart_time_base.py`'s `fit_to_run(run_length_s: float)` is passed
`max(snapshot.elapsed_s for snapshot in snapshots)` by its only caller in
`app/simulation_view.py` - a case *instant*, not a length. For a trunk the two
coincide. For a branch forked at 900 s and advanced 60 s it receives 960.0
while the run it is fitting is 60 s long.

**The behaviour is correct and must not change.** The function wants the axis's
right edge, and the right edge is the case instant. That is exactly why the
name is the whole of the defect: a reader who believes the parameter and
"fixes" the caller to pass a length would put a branch's axis 900 s short.
`fitted_window`'s "pinned at zero" wording was corrected in the same pass;
this parameter was not, because renaming it reaches `simulation_view.py`.

Nothing is reachable-wrong today - no branch is drawn until `PL-8PSW` (overlay
two branches on one time axis) - so this is a rename ahead of the code that
would be misled by it, which is the cheapest moment to do it.

**Verified 2026-09-14.** `app/chart_time_base.py:139` declares
`fit_to_run(run_length_s: float)` and documents it as "How much simulated time
the run has recorded, in" seconds; `:168-179` treats it as a span, comparing it
against `time_base.span_s`. Its one production caller is
`app/chart_time_base.py`'s `fit_to_run(elapsed_s)`.

**Why it matters, and whether it can draw a wrong chart.** On the trunk the two
coincide - a run opening at induction has elapsed time equal to its length - so
nothing is wrong today. On a **branch** they do not: a branch opens at the fork
instant on the case's axis, so its `elapsed_s` is a case instant and exceeds the
branch's own recorded length. A time base fitted to the larger number chooses a
coarser span than the branch's data needs, which is a chart axis chosen from the
wrong quantity. That is a displayed-value correctness question rather than a
naming preference, which is why it is `defect` rather than `refactor` - and it
becomes reachable with `PL-8PSW`, not later.

**Done when.** `fit_to_run` names the quantity it actually needs, its caller
passes that quantity rather than `elapsed_s`, and a test covers a branch whose
opening instant is greater than its recorded length. `PL-CZTR` is the same
defect on `ResumePoint`; do them together.
