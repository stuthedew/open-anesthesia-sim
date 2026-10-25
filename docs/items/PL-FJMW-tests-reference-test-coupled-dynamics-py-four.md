---
id: PL-FJMW
title: tests/reference/test_coupled_dynamics.py: four stale or false statements - _unperfused_load_then_dial_off is called the only gate trajectory taking a control to its minimum though _ventilator_start does, its quoted errors date from the 0.05 s oracle, _envelope_corner's summary contradicts its body, and the SHIPPED_STEP_S comment cites app.simulation_view (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: tests/reference/test_coupled_dynamics.py
added: 2026-10-25
payoff: the coupled-dynamics gate's comments state which trajectories it covers and how large its errors are as they are now
verify: ! grep -qF 'only gate trajectory that takes any control to its minimum' tests/reference/test_coupled_dynamics.py && ! grep -qF 'app.simulation_view.SIMULATION_STEP_S' tests/reference/test_coupled_dynamics.py
---

**Problem.** tests/reference/test_coupled_dynamics.py: four stale or false statements - _unperfused_load_then_dial_off is called the only gate trajectory taking a control to its minimum though _ventilator_start does, its quoted errors date from the 0.05 s oracle, _envelope_corner's summary contradicts its body, and the SHIPPED_STEP_S comment cites app.simulation_view (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 272 ("the only gate trajectory that takes any control to its minimum") and line 407 citing `app.simulation_view.SIMULATION_STEP_S`. `app/simulation_view.py` defines no `SIMULATION_STEP_S`.

**Why it matters.** This file is the reference gate for the coupled model. Its comments say which trajectories reach which limits and how large its errors are. A reader deciding whether a new trajectory is needed, or whether a quoted error still holds, is misled by each of the four.

**Done when.** The four statements are true of the file as it stands: the trajectory claim names `_ventilator_start` too, the quoted errors are those of the current oracle step, `_envelope_corner`'s summary matches its body, and the step's citation names where the interface's step is defined. No test changes behaviour.
