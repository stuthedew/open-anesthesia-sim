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

**Measured 2026-11-21, at the built one-second step.** Each figure is from a script run against this branch, and the tests named hold the ones that a test can hold.

1. *Control resolution.* A control change made one second late moves desflurane's alveolar fraction by at most 0.066 percentage points at the case opening, 0.50 after an unperfused load with the dial then closed, and 1.34 at a ventilator start. At the control grids of 2, 6 and 30 s (20x, 60x and 300x) the ventilator start gives 2.5, 5.8 and 10.3. `tests/reference/test_control_resolution.py` measures all of them again. After a ventilator start made one second late, the alveolar difference is 1.34 points at 1 s, 0.50 at 8 s, and above 0.14 until 17 s.
2. *A marked crossing.* With ventilation off for 120 s and then restored to 12 L/min, a 0.10 xMAC alveolar target on sevoflurane at 8% and 10 L/min halts showing 0.29 xMAC. The 0.1 s step showed 0.12. `test_an_alveolar_target_can_halt_many_counts_past_its_mark_when_ventilation_resumes` holds it against an uptake system built directly.
3. *Squarings in a shipped run.* The one-second step's propagator needs 2 squarings at each shipped agent's default flows and 3 at the widest supported flows. The 0.1 s step needed none. So the premise that `PL-D88N` (the fixed mass-balance tolerance) recorded, that no reachable step needs a squaring, no longer holds. Over 24 h the worst unaccounted share was 9.75e-12, for sevoflurane at its highest dial with fresh gas at 0.5 L/min, ventilation at 12 L/min and cardiac output at 10 L/min. The tolerance of one part in 10**9 stays.
4. *The numerical envelope.* Over all 2,560 corners (every flow at zero or its maximum, four splits of cardiac output) the one-second step needs at most 22 squarings, against 19 at 0.1 s. The same script gives 19 at 0.1 s, which is the published count. The table of `docs/MODEL.md` § "The numerical envelope", measured again against a 70-digit evaluation, worst error as a share over the six fractions and the two totals:

   | Corner | Squarings at 1 s | Step error | After 24 h |
   | --- | --- | --- | --- |
   | Shipped sevoflurane, widest flows | 3 | 2.2e-15 | 7.6e-11 |
   | Alveolar gas 0.01 L, blood:gas 10 000, every tissue:blood 1 | 22 | 1.3e-9 | 4.8e-5 |
   | Alveolar gas 0.01 L, blood:gas 10 000, tissue:blood as shipped | 22 | 1.2e-9 | 4.1e-5 |
   | Every volume 0.01 L, blood:gas 10 000, every tissue:blood 0.001 | 22 | 9.3e-10 | 4.0e-5 |
   | Vessel-rich group 0.01 L, its tissue:blood 0.001 | 18 | 1.2e-10 | 5.0e-6 |
   | Circuit 0.01 L | 10 | 3.4e-13 | 1.5e-8 |
   | Venous pool 0.01 L | 9 | 1.5e-13 | 5.3e-9 |

   The script reproduces the published 0.1 s rows (step errors 6.0e-16, 7.5e-11 and 1.3e-10, and 2.5e-5 after 24 h at the alveolar corner), so the two steps are compared by one method. The mass-balance check halts sevoflurane at the widest flows with every tissue:blood coefficient at 1 after 11 s (alveolar gas 0.01 L, blood:gas 10 000), 765 s (0.01 L, 100) and 904 s (1.0 L, 10 000). It does not halt within an hour at (0.01 L, 12), (2.5 L, 100) or (0.1 L, 1.3). At 0.1 s the three halts were at 4.3, 499 and 934 s.
5. *The wash-in crossing.* After the dial is closed, the first F_A/F_I above 1 is at most 1.0281, over 2,646 runs of the three agents at the highest fresh gas flow. The largest case is a circuit and alveolar gas at equilibrium with no cardiac output and little ventilation, where F_I falls for one second at the rate of fresh gas flow over circuit volume while F_A barely moves: exp((10/60)/6) is 1.0282. At 0.1 s the figure was 1.00235. `WASH_IN_TERMINUS_CEILING` is 1.05, so the crossing column is still drawn.

**Decided while building, 2026-11-21.**

1. `SimulationStep` and its guards are deleted, and `advance()` takes no step. A type that admits one value proves nothing that the constant does not.
2. The playback timer keeps its 100 ms interval. Each tick adds the rate times 100 ms to the simulated time that the run is owed, in whole milliseconds, and the run takes one step for each whole second owed (`OwedSimulatedTime` in `app/playback.py`). So 1x steps on every tenth tick and 5x on every second tick, and the remainder is carried exactly. A timer whose interval changed with the rate was refused, because Pause and a rate change would then be acted on up to a second late at 1x.
3. The numerical envelope's bounds stay. Their criterion was that no corner's step needs more squarings than a shipped run needs for one propagator over 24 h, which is 19. The one-second step needs 22 at the stiffest corner. The error that the criterion stood for is 4.8e-5 of the state after 24 h there, twice the 0.1 s step's 2.5e-5 and a tenth of the 4.9e-4 that refused a volume floor of 0.001 L. The floor is 122 times below the smallest shipped volume, and the mass-balance check halts a run at that corner after 11 s. Raising the floor to 0.1 L would restore 19 squarings and refuse a volume only 12 times below the smallest shipped one. Nothing a learner sees depends on the choice, so the session took it, as `PL-QX2G` (the numerical envelope) did.

**Held.** The project owner is being asked whether runs stay at whole seconds on the corrected figures that `PL-TPXK` (the review of the four streamlining decisions) recorded. Until he answers, this item's pull request stays a draft and nothing about playback at 1x or 5x is published in `docs/MODEL.md` or `docs/INTERFACE.md`.
