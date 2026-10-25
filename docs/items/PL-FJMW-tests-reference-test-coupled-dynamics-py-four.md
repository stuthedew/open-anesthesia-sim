---
id: PL-FJMW
title: tests/reference/test_coupled_dynamics.py: four stale or false statements - _unperfused_load_then_dial_off is called the only gate trajectory taking a control to its minimum though _ventilator_start does, its quoted errors date from the 0.05 s oracle, _envelope_corner's summary contradicts its body, and the SHIPPED_STEP_S comment cites app.simulation_view (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: tests/reference/test_coupled_dynamics.py
added: 2026-10-25
closed: 2026-10-25
pr: 1816
payoff: the coupled-dynamics gate's comments state which trajectories it covers and how large its errors are as they are now
verify: ! grep -qF 'only gate trajectory that takes any control to its minimum' tests/reference/test_coupled_dynamics.py && ! grep -qF 'app.simulation_view.SIMULATION_STEP_S' tests/reference/test_coupled_dynamics.py && ! grep -qF 'All five run 600 s' tests/reference/test_coupled_dynamics.py && ! grep -qF 'worst trajectory' tests/reference/test_coupled_dynamics.py
---

**Problem.** tests/reference/test_coupled_dynamics.py: four stale or false statements - _unperfused_load_then_dial_off is called the only gate trajectory taking a control to its minimum though _ventilator_start does, its quoted errors date from the 0.05 s oracle, _envelope_corner's summary contradicts its body, and the SHIPPED_STEP_S comment cites app.simulation_view (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 272 ("the only gate trajectory that takes any control to its minimum") and line 407 citing `app.simulation_view.SIMULATION_STEP_S`. `app/simulation_view.py` defines no `SIMULATION_STEP_S`.

**Why it matters.** This file is the reference gate for the coupled model. Its comments say which trajectories reach which limits and how large its errors are. A reader deciding whether a new trajectory is needed, or whether a quoted error still holds, is misled by each of the four.

**Re-scoped 2026-10-25, on starting it.** The same staleness reaches three more places in the file. `_envelope_corner`'s docstring says "All five run 600 s at 0.1 s", but `_unperfused_load_then_dial_off` runs 900 s. The comment above `MIN_CARDIAC_OUTPUT_L_MIN` and the docstring of `test_envelope_limits_match_the_supported_input_ranges` both call the unperfused load "the worst trajectory this gate drives". Both also say that raising a minimum above zero would fail nothing. That is false since `PL-0MLQ`: with `MINIMUM_CARDIAC_OUTPUT_L_MIN` set to 0.5, `CardiacOutput(0.0)` raises `SimulationConfigurationError`, so the trajectory would raise rather than silently leave the domain.

**Measured 2026-10-25** with `_worst_error_over_phases` at the 0.0125 s oracle (worst agent, desflurane, for each trajectory): ordinary use 1.5786e-14, envelope corner held 1.5377e-14, ventilator start 1.3906e-14, reference point held 1.3427e-14, unperfused load 8.7985e-15. These match `_envelope_corner`'s docstring to every digit, so that docstring's figures stay and the unperfused load's own docstring is brought into line with them.

**Done when.** Every statement above is true of the file as it stands. The trajectory claim names `_ventilator_start` too. The quoted errors are those of the current oracle step. `_envelope_corner`'s summary matches its body, and its body gives the unperfused load's 900 s. The step's citation names where the interface's step is defined. The two minimum-range passages name the trajectories that reach a minimum and say what raising one would do. No test changes behaviour.
