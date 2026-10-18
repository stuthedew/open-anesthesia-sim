---
id: PL-RXW0
title: Four reference tests claim more than they hold: two elimination tests named 'against published human measurement' are self-derived pins with 6-12% bands, the open-circuit residual's 'closed-form bound' is not a bound, the 24 h washout pins values past the supported run length, and the analytic circuit wash-in test takes tau from the code under test
priority: P3
effort: M
status: done
classes: test, docs
feature: tests-detect-wrong-values
milestone: v0.5.26
touches: tests/reference/test_published_wash_in_and_elimination.py, tests/reference/test_late_washout_against_published_fits.py, tests/reference/test_circuit_wash_in_closed_form.py, docs/MODEL.md, README.md
added: 2026-10-17
closed: 2026-10-17
pr: 1516
payoff: no reference test is named or described as validation, a bound or an independent solution when it is a regression pin, so a reader does not over-trust what passed
verify: ! grep -qF 'five_minute_elimination_ratio_against_published_human_measurement' tests/reference/test_published_wash_in_and_elimination.py && grep -q '^ELIMINATION_DURATION_MIN = 1410$' tests/reference/test_late_washout_against_published_fits.py
---

**Problem.** Four reference tests claim more than they hold: two elimination tests named 'against published human measurement' are self-derived pins with 6-12% bands, the open-circuit residual's 'closed-form bound' is not a bound, the 24 h washout pins values past the supported run length, and the analytic circuit wash-in test takes tau from the code under test

**Severity: low.** Four small findings with one shape: a test name or
docstring that claims more than the test enforces. Audit findings ORC-5, ORC-6,
ORC-7 and ORC-8 (reference tier). The verifier confirmed ORC-5, ORC-6 and
ORC-8, and rated ORC-7 "partly" true; its corrected claim is used below.

**1. Two elimination tests named as validation are regression pins (ORC-5).**
`test_five_minute_elimination_ratio_against_published_human_measurement` and
`test_five_minute_elimination_ratio_without_rebreathing_against_published_human_measurement`,
both in `tests/reference/test_published_wash_in_and_elimination.py`, assert
drift from `MODELLED_ELIMINATION_RATIOS` and `OPEN_CIRCUIT_ELIMINATION_RATIOS`.
Those are the model's own outputs. The allowed drift is
`ELIMINATION_REGRESSION_TOLERANCE_SD = 1.0` published SD, which is a band of
±8.6%, 7.4%, 12.3% and 6.2% relative. The docstrings say this honestly, but
the names count as validation in any report or mutation-score reading. The
only tighter check is the 1e-4 absolute pin in
`test_the_twenty_four_hour_run_opens_from_the_five_minute_gate_s_own_ratio`,
in the late-washout module. If that slow module is ever split off or
deselected (`PL-4Z5Y` discusses where it runs), desflurane's ratio could drift
by 12% while the four-figure tables in the docstrings and `docs/MODEL.md` go
stale. Fix: rename both as regression pins and tighten them in place to an
absolute 1e-4, keeping the distance from the published mean in the failure
message.

**2. The open-circuit "closed form" is not a bound (ORC-6).** The docstring of
`test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero` says "The
residual has a closed form". The test takes the peak F_I/F_A at the end of the
step, after F_A has already fallen, so V_A x dt / V_C is not an upper bound.
At the tested elimination flow of 10 L/min the margin is only 3.848e-4,
1.531e-4 and 4.787e-4 relative (sevoflurane, isoflurane, desflurane). At
elimination flows of 0, 1 and 4 L/min a correct driver exceeds the "bound" by
a factor of 1.000355 to 1.001237. A stored-value perturbation found the same
thing from the other side: at a 6.6 L circuit, isoflurane's peak 0.0010101252
exceeds the bound 0.0010101010 and the test fails, and at the Gas Man
Workbook's published 8.0 L circuit volume it fails for all three agents. The
machine data file records 8.0 L as the published figure its 6.0 L departs
from, on a ruling that the choice is not critical. Nothing fails today. Fix: compare F_I at the end of the step with F_A at the start of the
step. That is rigorous, because during a washout
dF_I/dt <= (V_A/V_C) F_A(t) <= (V_A/V_C) F_A(0). Or assert against
(1 - exp(-V_A dt / V_C)) x F_A(0) / F_A(dt).

**3. The 24 h washout runs past the supported run length (ORC-8).**
`ELIMINATION_DURATION_MIN = 1440` in
`tests/reference/test_late_washout_against_published_fits.py` comes after a
30-minute wash-in, so the run covers 88,200 s of case time.
`CaseInstant(88200.0)` raises `SimulationConfigurationError` ("outside the
supported run length of 0 to 86400 s"). The test runs only because it steps
`AgentUptakeSystem.advance` directly, which has no run-length guard. The
comment "the measurement ends where the claim does" is off by 30 minutes, and
the 1440-minute entries describe a state the model refuses to represent
elsewhere, as do `docs/MODEL.md`'s "+15 to 29% at 24 hours" figures. Fix: end
the elimination at 1410 min, or drive the run through `SimulationState`, which
enforces the limit, and restate the 24-hour figures to match.

**4. The analytic circuit wash-in takes tau from the code under test (ORC-7).**
`test_circuit_matches_analytic_wash_in` in `tests/reference/test_circuit_wash_in.py`
builds its expected value from `circuit.time_constant_s` and
`fraction_from_percent`, both shipped code. The suite still catches a unit
error shared by both, through the literal `time_constant_s` pins (90, 120, 180
and 49.5 s) in `tests/unit/test_circuit.py`, and `advance_fresh_gas` is not on
the shipped run path. `docs/MODEL.md` § "Preserved circuit reference tests"
requires the v0.0.2 analytic tests to "remain unchanged", so do not edit that
file. If anything is done, add a new test that writes the time constant as the
literal 60.0 s with its arithmetic in a comment.

**Why it matters.** A name or docstring that claims validation, or a closed
form, misleads anyone counting what the suite validates. Two of the four
claims hold only at the single operating point that is tested.

**Where.** `tests/reference/test_published_wash_in_and_elimination.py`;
`tests/reference/test_late_washout_against_published_fits.py`;
`tests/reference/test_circuit_wash_in.py` (read only; see point 4);
`docs/MODEL.md` where it restates the 24-hour figures.

**Done when.** Each of the four tests either enforces what its name and
docstring claim, or its name and docstring are changed to say what it does
enforce, and `tests/reference/test_circuit_wash_in.py` is unchanged.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**Done, 2026-10-17 (branch `claude/tests-detect-wrong-values-link-2-gonkg6`, pull request #1516).**
All four fixes are done. The `verify:` line also names fix 3, since the
rename alone made it pass while three of the four fixes were open.

1. *Done.* The two tests are now
   `test_five_minute_elimination_ratio_regression_pin` and
   `test_five_minute_elimination_ratio_without_rebreathing_regression_pin`.
   They assert `abs(ratio - modelled) <= ELIMINATION_RATIO_PIN_TOLERANCE`, which
   is 1e-4 and replaces `ELIMINATION_REGRESSION_TOLERANCE_SD`. The failure
   message still gives the distance from the published mean. The late-washout
   module's five-minute pin imports the same constant instead of its own
   `1e-4`. `docs/MODEL.md` says "regression pin" at the three places that said
   "regression band" for elimination. *Fail-before:* this tightens a test
   rather than fixing code, so the record is arithmetic. A drift of 5e-3 in
   desflurane's ratio is 0.25 published SD, which the old band passed, and is
   50 times the new tolerance.
2. *Done.* The driver records F_I at the end of each step over F_A at the
   start of it, in `peak_inspired_to_starting_alveolar_ratio`, and the test
   also runs at an elimination flow of 0 L/min. *Fail-before:* the old metric,
   F_I over F_A both at the end of the step, at 0 L/min was 1.001005, 1.001237
   and 1.000911 times the bound for sevoflurane, isoflurane and desflurane
   (`uv run python` with the module's own driver, 2026-10-17), so the old
   assertion fails there. The new metric is 0.99924 to 0.99931 of the bound at
   0 L/min and 0.99785 to 0.99790 at the run's own 10 L/min.
3. *Done.* `ELIMINATION_DURATION_MIN` is 1410 and the last entry of
   `STATED_MINUTES` is 1410, so the run is 30 minutes of wash-in and 1410
   minutes of elimination and ends at 86,400 s of case time. The last entry of
   each `RECORDED_COMPARISONS` ratio tuple, the last entries of
   `RECORDED_TAIL_REDUCTIONS` and `RECORDED_METABOLISED_SHARE` now hold the
   1410-minute values. They were measured twice on 2026-10-17 with
   `_washout_curve(..., 1410)`, once by the thread that stopped for length and
   once by the one that finished. The second run also reproduced every
   1440-minute value the module held, so the protocol had not changed. Every
   other entry and every crossing hour is unchanged. Model over fit still
   rises between minutes 1400 and 1410 in every cohort and in both conditions.
   The module docstring and `docs/MODEL.md` § "The first 24 hours of
   elimination against the published mean curves" and § "Supported run
   length" restate the figures: the late excess is 12 to 24% at 23.5 hours and
   a factor of 2.1 for desflurane, where it read 15 to 29% at 24 hours and a
   factor of 2.2. The open-circuit metabolised share is 7.1%, where it read
   7.2%; the recorded 0.0715 had been rounded up from 0.07147. The metabolism
   sentence reads 3.0 of the 24.0 points at 23.5 hours. The supported run
   length, the test names and the section headings are unchanged.
   A new test, `test_the_run_ends_at_the_supported_run_length`, holds the
   run's step count to `maximum_step_count` from `core/supported_ranges.py`,
   the simulator's own count of the steps the supported run length allows.
   *Fail-before:* with `ELIMINATION_DURATION_MIN` set back to 1440 the test
   fails, because 18,000 steps of wash-in and 864,000 of elimination make
   882,000 against the 864,000 allowed (`uv run python` with the module
   imported and the constant patched, 2026-10-17). The whole late-washout
   module passes: 41 passed in 137.71 s with `pytest -n 4`.
4. *Done.* `tests/reference/test_circuit_wash_in.py` is unchanged. A new file,
   `tests/reference/test_circuit_wash_in_closed_form.py`, runs the same
   circuit (6.0 L, 6.0 L/min, 8%) against F_D (1 - e^(-t/tau_C)) with
   tau_C = 60.0 s and F_D = 0.08 written as literals, the arithmetic in a
   comment. *Fail-before:* with `SECONDS_PER_MINUTE` in `core/circuit.py`
   patched to 30.0, a unit error that both `time_constant_s` and
   `advance_fresh_gas` share, the preserved analytic test passes at all four
   times and the new test fails at all four. At 60 s the patched circuit holds
   0.0691732 against the closed form's 0.0505696 (`uv run python` calling
   both test functions, 2026-10-17).
