---
id: PL-96SQ
title: A patient profile can open the run at an alveolar ventilation or cardiac output off the 0.1 L/min slider grid, which PL-1KQ9's refusal holds only for the fresh gas flow, so the slider and its readout would each show a flow the run does not hold (found building PL-1KQ9)
priority: P3
effort: S
status: done
classes: defect, ux
milestone: v0.6.0
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-18
closed: 2026-10-19
pr: 1673
payoff: no run opens at a ventilation or cardiac output that the slider and the readout beside it cannot both show
verify: grep -q 'def test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused' tests/unit/test_dashboard_frame.py
---

**Problem.** A patient profile can open the run at an alveolar ventilation or cardiac output off the 0.1 L/min slider grid, which PL-1KQ9's refusal holds only for the fresh gas flow, so the slider and its readout would each show a flow the run does not hold (found building PL-1KQ9)

`PL-1KQ9` made `setting_readouts` in `app/dashboard_frame.py` refuse a fresh
gas flow in force that is not one of the steps its slider offers, so a
machine profile cannot open a run that the slider and its readout cannot
both show. The alveolar ventilation and cardiac output sliders step at the
same 0.1 L/min (`FLOW_DISPLAY_DECIMALS`), and their opening values are a
patient profile's `default_alveolar_ventilation_l_min` and
`default_cardiac_output_l_min`, which `core/parameters.py` checks only as
positive and finite. A profile stating 5.25 L/min of cardiac output would
open with the slider at 5.2 (`slider_position` rounds half to even) and the
readout printing 5.2 over a run at 5.25. The shipped patient states 4.0 and
5.0, which are steps, so nothing shipped reaches it. `PL-1KQ9` held its
refusal to the fresh gas flow because that was the decision its design
round took.

The delivered dial is not in this item. Its value in force is a fraction
converted to percent, so an exact comparison with a step may fail on a
dial the slider set, and it needs its own reading before any refusal.

**Why it matters.** It is the same wrong-context display `PL-1KQ9` closed
for the fresh gas flow: a slider and a readout that each show a setting the
model is not running at. `CLAUDE.md`'s safety-critical standard counts that
as a safety failure. It is held at `P3` only because no shipped profile
reaches it.

**Done when.** `setting_readouts` refuses an alveolar ventilation or cardiac
output in force that is not one of its slider's steps, with the same
sentence shape as the fresh gas flow's refusal, and a test in
`tests/unit/test_dashboard_frame.py` pins 5.25 L/min for each. Recommended
route: apply `_is_offered_step` to all three flow controls in the loop, in
place of the fresh gas flow condition. Check before building that no
control path writes an off-grid value of either, such as a restore after a
refused setting or a branch opened from a timeline value.

**Checked 2026-10-19:** still real on `main` at `6fd84bd5`: `setting_readouts`
applied `_is_offered_step` only to the fresh gas flow. No control path writes
an off-grid value of either flow: the sliders write steps, a branch reads its
settings back from the timeline, and a refused setting restores the value it
replaced. So the opening value is the only way in.

**Regression test against the code before the fix.** `uv run pytest -q
tests/unit/test_dashboard_frame.py -k ventilation_or_cardiac` on `6fd84bd5`
with the new tests added failed both refusal cases with `Failed: DID NOT RAISE
ValueError`; the four on-grid cases passed.
