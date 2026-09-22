---
id: PL-59WB
title: chart_time_base.fit_to_run takes a parameter called run_length_s but is passed a case instant, which is the duration_s-was-not-a-duration defect one module over
priority: P2
effort: S
status: ready
classes: defect
feature: core-domain-language
touches: src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_time_base.py, tests/unit/test_chart_frame.py
added: 2026-09-14
payoff: the fitted axis's input is named for what it is, the newest case instant, so a reader who believes the name cannot 'correct' the caller into drawing a branch as one point at its fork
verify: grep -q 'def test_the_fitted_window_reaches_a_branch_s_newest_instant_rather_than_its_length' tests/unit/test_chart_frame.py && ! grep -q 'run_length_s' src/anesthesia_sim/app/chart_time_base.py
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

**Re-verified 2026-09-22, on `053fd744`, with a branch drawable since `PL-8PSW`
(v0.4.26): the first claim holds and the second does not.** The caller has
moved: `app/chart_frame.py`'s `assemble_chart_frame` passes
`max(run.snapshot.elapsed_s for run in runs)`, the newest case instant any run
on the chart has reached. Measured with the reference adult on sevoflurane,
trunk advanced to 900 s, forked there, branch advanced 60 s:

| Fitted to | Rung | Window | Trunk drawn | Branch drawn |
| --- | --- | --- | --- | --- |
| the newest instant, as today (960 s) | 1800 s | 0-1800 s | 0-900 s | 900-960 s, 31 points |
| each run's own length (max 900 s) | 900 s | 0-900 s | 0-900 s | one point, at 900 s |

So 1800 s is not coarser than the data needs. It is the narrowest rung that
holds the case from induction, because `fitted_window` pins the left edge at
the case's zero, `tick_times` rules from the same zero, `docs/MODEL.md`
§ "One simulated-time frame" makes the chart's axis the case's, and the view
keeps the trunk as run 0 whenever a branch is drawn. The span is coarser only
against a window pinned at the branch's own opening, which would be a different
"Fit run" rule rather than a fix to this one. The edit the brief warns against,
fitting to lengths, reduces the branch's whole minute to one point at its fork.

**What that changes here.** The value passed is right, so the rename is the
whole fix: the caller keeps its value under a name that says what it is, and
the "rather than `elapsed_s`" below, written on the second claim, is
superseded. The class stays `defect`, on a different ground from the one given
above: "How much simulated time the run has recorded" is false for an input
reachable since v0.4.26, and it points a reader at the one edit that draws a
branch as a point. The test pins today's behaviour rather than changing it, and
is checked against that edit.

**Done when.** `fit_to_run` names the quantity it actually needs, its caller
passes that quantity rather than `elapsed_s`, and a test covers a branch whose
opening instant is greater than its recorded length. `PL-CZTR` is the same
defect on `ResumePoint`; do them together.

**Done when, as re-verified 2026-09-22.** `fit_to_run`'s parameter names the
newest case instant rather than a length, `assemble_chart_frame` passes the
same value under that name, and `tests/unit/test_chart_frame.py` holds a branch
whose opening instant exceeds its own length drawn whole in the narrowest
fitted rung, failing if the caller is changed to pass lengths.
