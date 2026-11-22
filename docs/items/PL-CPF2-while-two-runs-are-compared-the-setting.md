---
id: PL-CPF2
title: While two runs are compared, the setting controls View shows two rows of dials and neither row names its run
priority: P1
effort: S
status: done
classes: defect, safety, ux
feature: every-view-in-run-state-tests
milestone: v0.6.20
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/run_surfaces.py, tests/integration/simulation_view
added: 2026-11-11
closed: 2026-11-22
pr: 2214
filed-pr: 2125
payoff: while two runs are compared, a learner reads each dial setting against the run it belongs to
tests: tests/integration/simulation_view/test_simulation_view_views.py::test_each_row_of_dials_names_its_run_while_two_are_drawn_and_only_then
reenters: PL-GTH6
---

**Problem.** While two runs are compared, the setting controls View shows two rows of dials and neither row names its run

**Found on 2026-11-11 by the builder of `PL-RF2S`'s second pull request, and
not fixed there.** The accounting panel, the schematic and the agent cost
panel each carry the run's name while two runs are compared
(`compared_panel_heading`, `RunSchematic.show_name`, `RunAgentCost.show_name`).
`RunDials` and `ParameterControls` carry none, so a learner tells the two rows
apart only by their order. The same was true before that pull request, when
`RunView.build_parameter_controls` built the rows.

**Where it belongs.** `PL-RF2S`'s third pull request makes a run's name travel
with its values. Each row is already written from a `RunPresentation`, which
holds `name`, so the row can show it on every tick. Not yet checked: whether
an open item decided that the rows stay unnamed.

**Checked 2026-11-22.** `RunDials` in `app/views.py` and `ParameterControls` in `app/run_surfaces.py` still show no run name. The accounting panel names its run through `compared_panel_heading`, and the schematic and agent cost panels each have a `show_name`. No open item decides that the rows stay unnamed: of the open items, only this one and `PL-RF2S` mention the dial rows, and `PL-RF2S`'s third step is that each run's name travels with its values. The rows were unnamed at the freeze too.

**Why it matters.** While two runs are compared, a learner reading a dial setting must know which run it belongs to, and today only the rows' order says so. Every other panel names its run. A setting read against the wrong run makes the learner's comparison of the two runs wrong.

**Done when.** While two runs are compared, each row of dials names its run, with the name that the chart's legend and the other panels use. A test shows both names with two runs displayed, and no name with one.

**Generator check.** The fact misread is which run a displayed value belongs to once two runs are shown, which `PL-GTH6`'s `misread:` states. `PL-GTH6` closed on 2026-10-25 and this was filed on 2026-11-11, so it is an instance of that head's fact filed after the head closed, recorded as a re-entry of `PL-GTH6`.

**Done 2026-11-22.** While two runs are drawn, each row of dials carries the run's name above it (`RunDials.name_text`); with one run drawn the name is hidden. Docs checked: `docs/INTERFACE.md` (updated where the dials are described), `docs/ARCHITECTURE.md` and `README.md` (no statement about the dial rows, by `grep -n -i "row of dials\|dial row"`).
