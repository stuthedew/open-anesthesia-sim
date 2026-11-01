---
id: PL-DPDG
title: The weekly drift run of 2026-11-01 found 17 tests restating two supported-range constants (15 MAXIMUM_ELAPSED_SIMULATION_TIME_S, 2 MAXIMUM_INPUT_FRACTION), added by #1861, #1862 and #1901 after the 2026-10-26 run passed; tools/restated_constants.py runs only in drift.yml, which does not gate, so nothing refused them at review
status: untriaged
feature: restated-constants
added: 2026-11-01
---

**Problem.** The weekly drift run of 2026-11-01 found 17 tests restating two supported-range constants (15 MAXIMUM_ELAPSED_SIMULATION_TIME_S, 2 MAXIMUM_INPUT_FRACTION), added by #1861, #1862 and #1901 after the 2026-10-26 run passed; tools/restated_constants.py runs only in drift.yml, which does not gate, so nothing refused them at review

**Evidence.** The `restated-constants` job of drift run 41279184121
(https://github.com/stuthedew/open-anesthesia-sim/actions/runs/41279184121)
perturbed each supported-range constant. `MAXIMUM_ELAPSED_SIMULATION_TIME_S`
86400.0 -> 172800.0 failed 40 tests, 15 named as restating it: the
`[86400.00000000001]`, `[1000000.0]`, `[1e+308]` and `[1.797...e+308]` cases of
the "step past the run length is refused when stepped alone" tests in
`tests/unit/test_circuit.py`, `test_tissue.py` and `test_blood.py`, two cases
in `test_governing_equations.py`, and three in
`test_numerical_envelope_sweep.py`. `MAXIMUM_INPUT_FRACTION` 0.99 -> 1.98
failed 7, 2 named as restating it. The run of 2026-10-26 (40277678595) passed.
`git log` names `#1861` (`PL-YT3T`), `#1862` (`PL-58D7`, `PL-T6P0`) and
`#1901` (`PL-9B1M`, `PL-D88N`), all merged after it, as the changes to these
files.

**Generator check.** `PL-40SJ`'s fact, the value of a named constant read
from its one definition. That head closed on 2026-10-25, and these copies
were written in the week after. `tools/literal_home_check.py` refuses a second
copy only under `src/`. `tools/restated_constants.py` covers tests but runs
only in the weekly drift workflow, which reports and does not gate. So a test
may copy a supported-range constant for up to a week with nothing refusing
it. Whether that check should also run on pull requests is a separate
question, and is for the triage of this item.
