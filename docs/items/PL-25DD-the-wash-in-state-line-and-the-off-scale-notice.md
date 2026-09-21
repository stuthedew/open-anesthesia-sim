---
id: PL-25DD
title: The wash-in state line and the off-scale notice sit in the shared chart column with no run attribution once a branch is drawn
priority: P1
effort: S
status: done
classes: defect, safety, ux
feature: two-run-attribution
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-09-20
closed: 2026-09-21
pr: 823
payoff: stops a learner reading the branch's F_A/F_I or off-scale notice as the trunk's, which inverts the comparison a branch exists to teach
verify: grep -q 'def test_the_wash_in_state_and_off_scale_lines_name_their_run' tests/integration/test_simulation_view.py
---

**Problem.** The wash-in state line and the off-scale notice sit in the shared chart column with no run attribution once a branch is drawn

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.

**Why it matters.** Both lines carry a clinical value and neither says whose it
is. `WASH_IN_STATE_TEMPLATE` is `"Now: F_A/F_I = {ratio}"` and
`OFF_SCALE_NOTICE_TEMPLATE` names compartments and a ceiling; neither template
takes a run. `SimulationView._place_run` puts one bare label per run into each
shared column - `_holder(self._off_scale_column, (run.build_off_scale_notice(),))`
and the `_wash_in_state_column` line under it - so a second run stacks a second
unlabelled line under the first, in the chart column, while the run names live
in the readout sections at the top of a different splitter. The only channel
separating them is stacking order, which nothing on screen declares.

That is the failure `CLAUDE.md`'s safety-critical standard names in terms: "the
correct number with the wrong units, label, patient context, stale state, model
name/version, or provenance is still a safety failure". Comparing two
managements of one patient is the whole point of a branch, so reading the
branch's F_A/F_I as the trunk's inverts the conclusion the comparison exists to
teach - and the off-scale notice misattributed says a compartment is clipped on
a run where it is not.

**Distinguish it from `PL-LHBY`** (the marks panel drawing every run's standings
from the reference run). There the screen asserts something *false*; here it
asserts something *true and unattributed*. Same feature, different fix: that one
computes a missing per-run value, this one labels values already computed
per run.

**Verified 2026-09-20** by reading `src/anesthesia_sim/app/simulation_view.py`'s
`_place_run` and `dashboard_frame.py`'s `wash_in_state` and `off_scale_notice`:
no run identity is passed to either template or placed beside either label.

**On scope.** `.claude/rules/ui-reader.md` governs what may be added as standing
text, so the attribution is a label or a name beside the line rather than a
sentence. Whether `docs/MODEL.md`'s hazard table also owes a row for this class
of misreading is the implementing session's call; it is left out of `touches`
deliberately, because adding it makes the item non-delegable.

**Built 2026-09-21** as `dashboard_frame.compared_run_line(line, frame,
run_index)`, applied by `RunView.refresh` to both lines. Two calls the item
left open, and why they went this way:

- **Composed rather than built into `wash_in_state` and `off_scale_notice`**,
  following `compared_trace_legend_label`, which is the same join already made
  for the legend. What a line *says* is a property of one run's state; *which
  run it belongs to* is a property of how many runs the chart draws and where
  this one sits. Building the name into each formatter would have hidden a
  presentation fact inside two value formatters and forced `wash_in_state`'s
  unit tests through a real frame to reach the undrawn-stretch suffix they
  currently inject. The error-preventing alternative - deriving the name inside
  each function so no caller could omit it - was weighed and refused on that
  cost; there is one caller, and the integration test holds it.
- **The run leads the line** (`"{run} — {line}"`) where it trails in
  `COMPARED_TRACE_LEGEND_TEMPLATE`. A legend is read by curve, so the
  compartment leads there. These columns stack one line per run, each opening
  with identical words, so the run is the only differentiator - and one at the
  end of a wrapped sentence is one the reader must hunt for.

**`docs/MODEL.md` owed no new row**, and the hazard table is why: the row
"reading one run's concentration as the other's while two are compared" already
covers this class, and its mitigation claimed "the run is named in text
wherever a value is shown" - which these two lines made false. The row's
mitigation and `Held by` were extended rather than a fourth row added, so
`docs/MODEL.md` joined `touches`.

**Done when.** With two runs drawn, each wash-in state line and each off-scale
notice says which run it is about, by a channel that does not depend on stacking
order - and a test in `tests/integration/test_simulation_view.py` holds it
against a branched case.
