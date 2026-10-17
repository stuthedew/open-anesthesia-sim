---
id: PL-9YHR
title: The published-data gates cannot resolve most stored parameters - fat tissue:gas x2 and x0.5, fat volume x2, muscle tissue:gas x1.5 and vessel-rich tissue:gas x0.8 each pass every Yasuda-tied assertion, and only 6 of 25 simulation-affecting x1.10 perturbations fail one - while the gate's resolving power is recorded only for alveolar ventilation and cardiac output
priority: P1
effort: L
status: ready
classes: science, test, docs
feature: validation-resolving-power
touches: tests/reference/test_published_wash_in_and_elimination.py, docs/MODEL.md
added: 2026-10-17
payoff: docs/MODEL.md's validation claim says which stored parameters the published-data gates can and cannot detect an error in, so a green gate is not read as validating values it cannot resolve
verify: grep -q 'def test_the_published_data_gate_fails_at_a_stated_perturbation' tests/reference/test_published_wash_in_and_elimination.py
---

**Problem.** The published-data gates cannot resolve most stored parameters - fat tissue:gas x2 and x0.5, fat volume x2, muscle tissue:gas x1.5 and vessel-rich tissue:gas x0.8 each pass every Yasuda-tied assertion, and only 6 of 25 simulation-affecting x1.10 perturbations fail one - while the gate's resolving power is recorded only for alveolar ventilation and cardiac output

**Severity: high for what a reader can conclude; nothing displayed is wrong
today.** Audit findings DP-3 (confirmed), DP-4 (verifier: "partly") and ORC-3
(reference tier, verifier: "partly"). The corrected claims are what this item
states.

**Evidence.** An experiment rebuilt the published-data module's system from
modified parameters; it reproduced the module's baseline
`MODELLED_ELIMINATION_RATIOS` (0.2328, 0.3227, 0.1626) exactly. Each of these
changes passed every published-data assertion in
`tests/reference/test_published_wash_in_and_elimination.py` (wash-in within
1 SD at FGF 1-10 for all four cohorts, both orderings, and the sign of
elimination):

- fat tissue:gas x2 and x0.5;
- fat volume x2;
- muscle tissue:gas x1.5;
- vessel-rich tissue:gas x0.8.

Muscle tissue:gas x0.5, a perfusion swap, a 5 L venous pool, half the
alveolar volume and a missing division by blood:gas each failed. Fat x2 moves
sevoflurane's model-to-fit ratio in the late-washout module from 0.67 to 0.46
at 800 min and from 1.22 to 0.79 at 1400 min. Both stay inside the fitted fat
term's 53-94% SD, so the published curves cannot catch a 2x fat error either.

In full pytest runs, only 6 of 25 simulation-affecting x1.10 perturbations
failed a published-data assertion, several of them only in the off-default
case at FGF 1 L/min. Isoflurane blood:gas ±10% passes every published
assertion: x1.1 fails only the dead-space tripwire, and x0.9 sits at
+0.93 SD. The x1.10 changes to sevoflurane fat, isoflurane vessel-rich, muscle
and fat, desflurane muscle and fat, the venous pool, fat volume and the
default fresh gas flow were caught only by literal pins. Those to sevoflurane
vessel-rich and muscle, desflurane vessel-rich, alveolar gas volume and the
vessel-rich, muscle and circuit volumes were caught only by pins and
tripwires. The pins are `PINNED_REFERENCE_STATES` in
`tests/reference/test_coupled_dynamics.py` (rel 1e-9), the late-washout module's
recorded tables (`RATIO_REGRESSION_TOLERANCE` 0.01) and doc_check, all of them
regression pins of the model's own output. The verifier ran sevoflurane
vessel-rich 1.1 to 1.21 over all of `tests/reference`: 11 failed, every one a
pin of the model's own output plus one tripwire
(`test_the_apparatus_dead_space_moves_every_cohort_together`, -0.96 to
-1.01 SD). No 30-minute published-band assertion failed.

Measured sevoflurane blood:gas edges on the current model: x0.86 gives
+1.01 SD (fail), x0.87 +0.95 (pass), x1.05 -0.97 (pass) and x1.06 -1.03 (fail).
The documented sharpness table is current, but a test placed at those exact
points would sit 0.01-0.03 SD from flipping.

**What is already disclosed or protected (verifier).** The module docstring
and `docs/MODEL.md` both say that neither comparison sees fat and that neither
may be read as covering the slow tail. The movement table gives the muscle and
fat sensitivity per +10%. `README.md` says passing "shows this implementation
reproduces its parameter set's intent, not that the parameter set is
independently right". `test_agreement_is_sensitive_to_ventilation_and_cardiac_output`
asserts that the gate detects changes along alveolar ventilation and cardiac
output, using `AGREEMENT_TOLERANCE_SD` itself, so widening that constant past
about 1.1 SD fails it. `test_operating_point_is_the_parameter_files_own_defaults`
pins ventilation at 4.0 and cardiac output at 5.0. The unit-conversion
constants are caught by the independent-solution oracle in
`test_coupled_dynamics.py` (`SECONDS_PER_MINUTE` 60 to 66: 36 failed;
`PERCENT_PER_UNIT_FRACTION` 100 to 110: 33 failed).

So the gap is narrower than the audit first stated. No test asserts that the
gate detects a change along any parameter axis, so the blood:gas and
vessel-rich sharpness tables are prose only. And the resolving power is not
recorded for the partition coefficients, the tissue volumes, the alveolar gas
volume (FRC), the circuit volume or the venous pool.

**Why it matters.** A reviewer, or the project owner, may take a green
reference suite as evidence that the coefficients are right when the suite
cannot see them. Fat solubility and fat volume set the hours-long washout tail
that a learner reads emergence from. And if a later change made the gate
blind along a parameter axis, nothing would say so.

**Where.** `tests/reference/test_published_wash_in_and_elimination.py`
(`AGREEMENT_TOLERANCE_SD`, the sharpness tables in the module docstring);
`tests/reference/test_coupled_dynamics.py` (`PINNED_REFERENCE_STATES`);
`tests/reference/test_late_washout_against_published_fits.py`;
`docs/MODEL.md` beside the validation claim.

**Recommended work.**

1. Add a parametrized detection-power test that rebuilds the system from
   modified `AgentParameters` and asserts that some published-data assertion
   FAILS. Choose perturbations with margin, for example blood:gas x0.80 and
   x1.10, not the 0.01 SD edges above. That turns the sharpness table into an
   assertion.
2. Record, per parameter and cohort, the factor at which each cohort leaves
   the 1 SD band, in a test that fails if the factor moves.
3. State the measured pass ranges for muscle and fat, and for FRC, circuit
   volume and venous pool, beside the validation claim in `docs/MODEL.md`.
   `PL-L9FC` carries the matching README sentence.
4. Do not widen or narrow `AGREEMENT_TOLERANCE_SD` on this evidence. The limit
   is the published data, not the band.
5. Treat `PINNED_REFERENCE_STATES` and the late-washout tables as detectors of
   accidental edits, and never cite them as validation of these values. Where
   a check of the stored values is wanted, use source-transcription tests:
   tissue:gas against Yasuda, Targ and Eger 1989 Table 1 (for example
   sevoflurane vessel-rich 1.1 against brain 1.15 ± 0.07, -4.35%, asserted to
   within 0.5 percentage points), volumes and flows against the Workbook's
   page-168 table, the venous pool against Davis and Mapleson, and the derived
   tissue:blood values against Baker and Farmery Table 2 (`PL-H536`).

**Done when.** A test asserts that the published-data gate fails at stated
perturbations of blood:gas and vessel-rich tissue:gas, and `docs/MODEL.md`
states, beside the validation claim, which stored parameters the gates can
and cannot resolve, with the measured factors.

**Related.** `PL-L9FC` (ready; README's validation paragraph states only the
wash-in half). `PL-H536` (ready; Baker and Farmery cross-check of derived
tissue:blood). `PL-Z3V5` (ready; extraction notes with locators, which
source-transcription tests need). `ROADMAP.md` planned-milestone item 31 (a
selectable primary-literature partition-coefficient set). `PL-R0NL` is the
same feature, for the early wash-in curve.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
