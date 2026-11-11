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
   call from every widget. Three functions cost 0.4 to 0.7 ms a frame and
   eight cost 1.6 ms, of a 54 ms frame with a 200 ms budget. Reimplement
   only the functions a control needs, and run
   `tests/benchmarks/frame_cost.py` after each control moves.
3. A control keeps its style sheet until it moves. With the style installed
   and every sheet kept, each widget that a sheet draws was pixel-identical
   to the shipped dashboard.
4. On a Mac the application runs Qt's macOS style today. A style over Fusion
   gives Fusion's look to every control that no style sheet draws, such as a
   scroll bar or a spin box. The owner saw the dashboard this way on
   2026-11-11 under the light and the dark appearance, and it looked the
   same under both.
5. Take every colour from a role of the declared palette. The `Disabled`
   group stays the host's (`PL-05M4`).

**Order.** The design of the first control comes from `PL-MF90` (choose one
token set and one component set). The trial's five-state button is a
placeholder.
