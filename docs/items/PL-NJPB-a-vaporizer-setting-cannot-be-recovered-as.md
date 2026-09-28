---
id: PL-NJPB
title: A vaporizer setting cannot be recovered as dialled from RunSegment.settings: fraction times 100 misses the percent for 13 of 81 settings
priority: P3
effort: S
status: ready
classes: defect, anticipated
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
payoff: a recorded segment gives back the vaporizer percent the learner dialled, so save and load can restore it exactly
verify: grep -q 'def test_a_recorded_segment_gives_back_each_vaporizer_percent_as_dialled' tests/unit/test_run_definition.py
---

**Problem.** A vaporizer setting cannot be recovered as dialled from RunSegment.settings: fraction times 100 misses the percent for 13 of 81 settings

**Found by `PL-SM5V`, 2026-09-27, and not worked there.** That item made a
recorded segment hold each flow in the litres per minute that was set, because
dividing by sixty does not run backwards. The vaporizer has the same shape one
layer up: the dial is set in percent and the settings hold
`delivered_partial_pressure_fraction`. Measured in the container's Python:
`p / 100 * 100 != p` for 13 of the 81 settings from 0.0 to 8.0 % at 0.1 %
(0.9, 1.7, 1.8, 3.3 to 3.7, 6.6, 6.8, 7.0, 7.2 and 7.4); 0.9 reads back as
0.9000000000000001. Rebuilding settings from the fraction is exact, since the
compartment holds the fraction too, so nothing inside `core/` is affected.
What is not recoverable is the percent the learner dialled, which a save and
load format (planned item 9) or anything else recovering the dial from a
segment would need. Where the percent becomes a fraction was not located;
start by finding that conversion and whether the control timeline records the
percent as dialled.

**Why it matters.** A save and load format (planned item 9), or anything
else restoring the dial from a recorded segment, would restore
0.9000000000000001 % where the learner dialled 0.9 %. Nothing reads it back
today, hence `anticipated`, but each recorded shape built on the fraction before
then adds to what has to change.

**Where, located at triage, 2026-09-28.** `src/anesthesia_sim/app/controller.py`
builds the setting's fraction (its `delivered_partial_pressure_fraction=Fraction(`
construction), and `core/uptake_system.py` converts the agent's percent with
`fraction_from_percent`. Whether the control timeline records the percent as
dialled was not checked.

**Done when.** A recorded segment gives back every setting from 0.0 to 8.0 % at
0.1 % exactly as dialled, held by a test in `tests/unit/test_run_definition.py`
beside `PL-SM5V`'s flow round-trip.
