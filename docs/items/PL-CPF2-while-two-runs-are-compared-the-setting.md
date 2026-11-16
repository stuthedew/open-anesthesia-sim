---
id: PL-CPF2
title: While two runs are compared, the setting controls View shows two rows of dials and neither row names its run
status: untriaged
feature: every-view-in-run-state-tests
added: 2026-11-11
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
