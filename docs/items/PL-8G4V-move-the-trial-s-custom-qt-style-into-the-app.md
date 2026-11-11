---
id: PL-8G4V
title: Move the trial's custom Qt style into the app with the first control built in it, and delete the trial's two files
status: untriaged
feature: interface-pass-design-round
added: 2026-11-11
---

**Problem.** `PL-BVC5` (the trial of a custom Qt style against style sheets)
passed on 2026-11-11, so the interface pass builds its controls in a custom
style. The style exists only as `TrialStyle` in
`tests/benchmarks/style_trial.py`, which draws a placeholder push button and
a check box tick. Nothing under `src/` uses it.

**What to do.** Move the style into `src/anesthesia_sim/app/` with the first
control built in it, install it as the application's style in `main()`, and
delete that control's style sheet. Then delete
`tests/benchmarks/style_trial.py` and `tests/benchmarks/style_trial_checks.py`,
and move the checks worth keeping into the suite.

**What the trial found that this item must keep** (`PL-BVC5` has the
measurements).

1. Install the style on the application. Qt's `QWidget::setStyle` page says
   that real applications should avoid a style set on single widgets.
2. Every function the style reimplements in Python is entered for every
   call from every widget. Three functions cost too little to measure, and
   eight cost about 1 ms a frame, of a 55 ms frame with a 200 ms budget.
   The trial's comparison does not resolve a difference smaller than about
   1 ms. Reimplement only the functions a control needs, and run
   `tests/benchmarks/frame_cost.py` after each control moves.
3. A control keeps its style sheet until it moves. With the style installed
   and every sheet kept, each widget that a sheet draws was pixel-identical
   to the shipped dashboard. A scratch script made that comparison, and the
   branch does not hold it. Write it as a test in the suite with the first
   control: the dashboard under the style, against the dashboard without it,
   pixel by pixel outside the controls that have moved.
4. On a Mac the application runs Qt's macOS style today. A style over Fusion
   gives Fusion's look to every control that no style sheet draws, such as a
   scroll bar or a spin box. The owner saw the dashboard this way on
   2026-11-11 under the light and the dark appearance, and it looked the
   same under both.
5. Take every colour from a role of the declared palette. The `Disabled`
   group stays the host's (`PL-05M4`).

6. The trial's check box indicator is a placeholder, like its button, and
   does not move as it is. A style on the application draws every check box
   indicator, so it redrew the six legend check boxes that show and hide the
   chart's traces, whose style sheet sets only the label's colour. The
   trial's indicator reads only whether the box is checked. It draws an
   unavailable box like an available one, and a partly checked box like an
   unchecked one. Its tick is the panel colour on the primary colour, where
   `tools/contrast_check.py` declares the tick as painted from the palette's
   own roles. Leave the indicator to Fusion until `PL-MF90` designs it. When
   it moves, draw every state and update that contrast declaration.

**Order.** The design of the first control comes from `PL-MF90` (choose one
token set and one component set). The trial's five-state button is a
placeholder.
