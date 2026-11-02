---
id: PL-DPDG
title: The weekly drift run of 2026-11-01 found 17 tests restating two supported-range constants (15 MAXIMUM_ELAPSED_SIMULATION_TIME_S, 2 MAXIMUM_INPUT_FRACTION), added by #1861, #1862 and #1901 after the 2026-10-26 run passed; tools/restated_constants.py runs only in drift.yml, which does not gate, so nothing refused them at review
priority: P2
effort: M
status: done
classes: defect
feature: drift-2026-11-01
milestone: v0.6.13
touches: tests/unit/test_circuit.py, tests/unit/test_tissue.py, tests/unit/test_blood.py, tests/unit/test_governing_equations.py, tests/unit/test_numerical_envelope_sweep.py, tests/unit/test_supported_ranges.py, tools/restated_constants.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-01
closed: 2026-11-02
pr: 1930
payoff: moving a supported-range limit fails only the tests that check it on purpose, so a session can trust the suite during a safety-critical change
verify: ! grep -rqF 'nextafter(86_400.0, inf)' tests/unit
not-delegable: only a run of tools/restated_constants.py proves the whole item, and it takes about 31 minutes in the drift workflow, which no admitted verify shape runs; the grep covers only the three step tests in test_circuit.py, test_tissue.py and test_blood.py
reenters: PL-40SJ
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

**Checked at triage, 2026-11-01.** Three corrections to the paragraphs above.

- The job named 22 cases, not 17, because it named restating cases for all five
  limits it moved. `MAXIMUM_FRESH_GAS_FLOW_L_MIN` named three: cases `[6]` and
  `[7]` of `test_require_canonical_state_refuses_more_agent_than_a_case_can_move`
  in `tests/unit/test_governing_equations.py`, and the `[FreshGasFlow]` case of
  `test_every_core_operation_refuses_inputs_outside_its_floating_point_domain`
  in `tests/unit/test_numerical_envelope_sweep.py`.
  `MAXIMUM_ALVEOLAR_VENTILATION_L_MIN` and `MAXIMUM_CARDIAC_OUTPUT_L_MIN` each
  named the matching case of that sweep test. `MAXIMUM_INPUT_FRACTION` named
  `tests/unit/test_numerical_envelope_sweep.py` as a whole, and
  `test_a_dial_and_a_fraction_above_the_input_ceiling_are_refused_in_their_own_units`
  in `tests/unit/test_supported_ranges.py`. The 15 for
  `MAXIMUM_ELAPSED_SIMULATION_TIME_S` are as listed above. Cases `[6]` and `[7]`
  are named under two limits, so the run names 20 distinct cases.
- In the three step tests, only the first case, `nextafter(86_400.0, inf)`,
  copies the limit. The tool judges the cases of a parametrized test together,
  so it names the other cases too.
- The `restated-constants` job runs monthly, on the first of the month, not
  weekly. The run of 2026-10-26 (40277678595) was the weekly run, and it
  skipped this job, so it did not pass it.

**Whether the check should also run on pull requests: no, for the reason
`drift.yml` already records.** The comment above the `restated-constants` job
(`PL-0Z0F`) says why it runs monthly. A copied value does no harm until a limit
moves. Moving a limit is a deliberate safety-critical change, made with
`docs/MODEL.md` revised beside it, and the comment says to run the job by hand
before moving one. This run took 31 minutes, one run of the suite for each of
five limits. Running that on every pull request would cost far more than
finding copies once a month. This item is recorded as a re-entry of
`PL-40SJ`, so if two more filings re-enter that head, `bin/docket inflow` asks
the question again with a count behind it. `PL-2T6B` corrects the comment's
count of four runs.

**Why it matters.** When a supported-range limit moves, these tests fail
although nothing is wrong. The tool's docstring names the harm: that kind of
failure teaches a session to edit the test rather than the code, at the moment
a safety-critical change most needs its tests trusted. The copies cannot make a
displayed value wrong, because a moved limit makes them fail loudly rather than
pass wrongly. So the item is classed `defect` under the one-source-of-truth
rule, not `safety`, and takes `P2`, the band `PL-T5J5`'s eight copies took.

**Done when.** Each case named above reads its limit from
`anesthesia_sim.core.supported_ranges`, or computes its value from that limit.
A case that must fail when a limit moves is listed instead in `TRIPWIRES` in
`tools/restated_constants.py`, with its reason. A manual run of the drift
workflow's `restated-constants` job names no test.

**Generator check.** `PL-40SJ`'s fact, the value of a named constant read
from its one definition. That head closed on 2026-10-03 under `#1326`, and its last member
closed on 2026-10-25. These copies were written after both dates. `tools/literal_home_check.py` refuses a second
copy only under `src/`. `tools/restated_constants.py` covers tests but runs
only in the weekly drift workflow, which reports and does not gate. So a test
may copy a supported-range constant for up to a week with nothing refusing
it. Whether that check should also run on pull requests is a separate
question, and is for the triage of this item. Recorded as
`reenters: PL-40SJ`, since the head's fix refuses a copy only under `src/`.

**Closed 2026-11-02 in #1930.** A local run of `tools/restated_constants.py` on
the fixed branch named no test as restating a limit, for all five limits it
moves, and exited 0. Every test that still fails when a limit moves is listed
with the reason it fails on purpose. `tests/unit/test_numerical_envelope_sweep.py`
fails to collect when `MAXIMUM_INPUT_FRACTION` moves, because its import reads
the limit, so it is listed as not judged instead of as a restatement. The
`restated-constants` job of the next manual `drift.yml` run confirms the result
in CI.
`bin/docket verify --self` returned ACCEPT for all four drift items, with
`make check` passing.
