---
id: PL-SZ6G
title: Hold a run's time as a whole number of seconds and step it by one exact 1 s step, so a control change takes effect at the next whole second
status: untriaged
feature: run-computed-one-way
added: 2026-11-21
---

**Problem.** Hold a run's time as a whole number of seconds and step it by one exact 1 s step, so a control change takes effect at the next whole second

**Why it matters.** A run's instants are `float` today (`CaseInstant` in `src/anesthesia_sim/core/supported_ranges.py`) and its step is 0.1 s, which a binary float cannot hold exactly. Six closed items came from that, two of which a learner could see: a chart's last column one rounding unit past its stop (`PL-9SL5`) and a run's last step past 86 400 s (`PL-8H2R`). The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** Simulated time becomes a whole count of seconds, and `SimulationStep` becomes a fixed 1 s step formed once per stretch of constant settings by `matrix_exponential`. The playback loop takes whole steps as real time allows, and a control change takes effect at the next whole second and is recorded at that second. `MAXIMUM_SIMULATION_STEP_S` and the declared control-resolution tolerance in `core/simulation_step.py` and `docs/MODEL.md` § "Supported simulation step" move to the 1 s figures that `PL-7CY5` measured: 0.066, 0.50 and 1.34 percentage points for the case opening, the unperfused load then dial off, and the ventilator start, with desflurane the worst agent. `tests/reference/test_control_resolution.py` re-measures them. The variable step, its 1 ms floor, and the guards for steps no control offers go.

**Done when.** Every instant in `core/` and `app/` is a whole number of seconds, a run steps only by the 1 s step, the control-resolution table and its test state the 1 s figures, and `docs/MODEL.md` says what a learner sees: a control change takes effect at the next whole second.
