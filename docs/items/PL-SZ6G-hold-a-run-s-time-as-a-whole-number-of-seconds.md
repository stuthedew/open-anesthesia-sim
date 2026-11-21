---
id: PL-SZ6G
title: Hold a run's time as a whole number of seconds and step it by one exact 1 s step, so a control change takes effect at the next whole second
priority: P1
effort: L
status: ready
classes: feature, science
feature: run-computed-one-way
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, tests, docs/MODEL.md, docs/INTERFACE.md, docs/ARCHITECTURE.md
deferred-from: v0.7.0 - filed 2026-11-21, after the gate froze, as the build of the design the owner chose in PL-7CY5; each of the four pull requests leaves main releasable, so the release does not wait for the feature to finish
added: 2026-11-21
payoff: a control change lands on a whole second that the screen, the record and every branch agree on, and no chart column or last step can fall one rounding unit past where it belongs
verify: grep -qF 'next whole second' docs/MODEL.md && ! grep -rqF 'MINIMUM_SIMULATION_STEP_S' src/anesthesia_sim
not-delegable: changes the step and the instant type in core/ and what a learner sees at 1x playback, so the project owner reads the pull request
---

**Problem.** Hold a run's time as a whole number of seconds and step it by one exact 1 s step, so a control change takes effect at the next whole second

**Why it matters.** A run's instants are `float` today (`CaseInstant` in `src/anesthesia_sim/core/supported_ranges.py`) and its step is 0.1 s, which a binary float cannot hold exactly. Six closed items came from that, two of which a learner could see: a chart's last column one rounding unit past its stop (`PL-9SL5`) and a run's last step past 86 400 s (`PL-8H2R`). The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** Simulated time becomes a whole count of seconds, and `SimulationStep` becomes a fixed 1 s step formed once per stretch of constant settings by `matrix_exponential`. The playback loop takes whole steps as real time allows, and a control change takes effect at the next whole second and is recorded at that second. `MAXIMUM_SIMULATION_STEP_S` and the declared control-resolution tolerance in `core/simulation_step.py` and `docs/MODEL.md` § "Supported simulation step" move to the 1 s figures that `PL-7CY5` measured: 0.066, 0.50 and 1.34 percentage points for the case opening, the unperfused load then dial off, and the ventilator start, with desflurane the worst agent. `tests/reference/test_control_resolution.py` re-measures them. The variable step, its 1 ms floor, and the guards for steps no control offers go.

**Done when.** Every instant in `core/` and `app/` is a whole number of seconds, a run steps only by the 1 s step, the control-resolution table and its test state the 1 s figures, and `docs/MODEL.md` says what a learner sees: a control change takes effect at the next whole second.

**Generator check.** Work the owner asked for on 2026-11-21, building the design that `PL-7CY5` decided. It is not a head. The fact is `PL-GJ1W`'s, how far a computed value can be from the exact one: a whole-second instant and a whole-second step remove the rounded instant that `PL-9SL5` and `PL-8H2R` came from.

**Checked 2026-11-21.** `python3 -c "print(3 * 0.1)"` prints `0.30000000000000004`: three of today's 0.1 s steps do not land on 0.3 s, and `CaseInstant` in `src/anesthesia_sim/core/supported_ranges.py` is a `float` subclass that holds that product.
