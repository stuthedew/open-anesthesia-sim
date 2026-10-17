---
id: PL-RXW0
title: Four reference tests claim more than they hold: two elimination tests named 'against published human measurement' are self-derived pins with 6-12% bands, the open-circuit residual's 'closed-form bound' is not a bound, the 24 h washout pins values past the supported run length, and the analytic circuit wash-in test takes tau from the code under test
priority: P3
effort: M
status: ready
classes: test, docs
feature: tests-detect-wrong-values
touches: tests/reference/test_published_wash_in_and_elimination.py, tests/reference/test_late_washout_against_published_fits.py, docs/MODEL.md
added: 2026-10-17
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

**Progress, 2026-10-17 (branch `claude/tests-detect-wrong-values-link-2-gonkg6`, pull request #1516).**
Fixes 1 and 2 are done and pushed. Fix 3 is measured and not yet written in.
Fix 4 is not started. The `verify:` line now also names fix 3, since the
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
3. *Measured, not written in.* Next steps, in order:
   - Set `ELIMINATION_DURATION_MIN = 1410` and replace 1440 with 1410 in
     `STATED_MINUTES` in `tests/reference/test_late_washout_against_published_fits.py`.
     Fix the comment above the constant: the run is 30 min of wash-in and
     1410 min of elimination, which ends at the supported 86,400 s of case
     time. The 1400-minute entry is the papers' own sample and stays.
   - Replace the last entry of each `RECORDED_COMPARISONS` ratio tuple with
     these 1410-minute values, measured 2026-10-17 with `_washout_curve(...,
     1410)`. Shipped: sevoflurane 1.240, isoflurane (Anesth Analg) 1.118,
     desflurane 2.110, isoflurane (Anesthesiology) 1.161. Open circuit: 0.816,
     0.718, 1.410, 0.746. Every other entry and every crossing hour is
     unchanged.
   - In `RECORDED_TAIL_REDUCTIONS` the last entry is 0.0241 (shipped) and
     0.0155 (open circuit). `RECORDED_METABOLISED_SHARE` becomes 0.0779 and
     0.0714, both inside the 0.002 tolerance of the old values.
   - Restate the module docstring and `docs/MODEL.md` (§ "The first 24 hours
     of elimination against the published mean curves" and the run-length
     paragraph near "That result does not move the 24 hours"). The 1440 rows
     become 1410 rows with the values above, rounded to two decimals:
     shipped 1.24, 1.12, 2.11, 1.16 and open 0.82, 0.72, 1.41, 0.75. The
     crossing table's "At 24 h" column becomes "At 23.5 h" with 1.24, 1.12,
     2.11 and 1.16. "By 15 to 29% at 24 hours and by a factor of 2.2 for
     desflurane" becomes "by 12 to 24% at 23.5 hours and by a factor of 2.1
     for desflurane". "Rises between minutes 1400 and 1440" becomes "1400 and
     1410"; model over fit still rises there in every cohort and condition.
     The metabolism sentence "3.1 of the 28.6 at 24" becomes "3.0 of the 24.0
     at 23.5 hours", and "7.8% ... by 24 hours" becomes "7.8% ... by the end of
     the run". Say that the run is 30 minutes of wash-in and 23.5 hours of
     elimination, so it ends at the supported run length. The supported run
     length itself does not change, and nor do the test names or section
     headings that say "24 hours".
   - Re-run the whole late-washout module.
   - This changes clinical prose in `docs/MODEL.md`, so the read request on
     #1516 names it as a point for the project owner.
4. *Not started.* Leave `tests/reference/test_circuit_wash_in.py` unchanged.
   Optionally add, in a new file, a test whose time constant is the literal
   60.0 s with its arithmetic in a comment.

Then close the item, run `bin/docket record 1516`, `make check` and
`bin/docket verify --self`, and finish #1516 as PL-0M7K and PL-GHT8 are
finished there.
