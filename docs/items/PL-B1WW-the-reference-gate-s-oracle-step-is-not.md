---
id: PL-B1WW
title: The reference gate's oracle step is not converged during a transient, so 86-99.8 percent of what it reports is the oracle's own RK4 truncation rather than the shipped step's error
status: untriaged
added: 2026-09-06
---

**Problem.** The reference gate's oracle step is not converged during a transient, so 86-99.8 percent of what it reports is the oracle's own RK4 truncation rather than the shipped step's error

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `tests/reference/test_coupled_dynamics.py`'s trajectory gates
compare the shipped exact step against an RK4 oracle driven at `ORACLE_STEP_S`
= 0.05 s. On the transients that set the gate's worst case the oracle is not
converged, so most of what the gate reports is the oracle's own truncation
error rather than the shipped solver's.

Decomposed against a converged oracle (RK4 at 0.0015625 s), at the instant and
state of the worst gate number - desflurane, ventilator start, alveolar, 307.4 s:

    what the gate reports   |shipped(0.1) - oracle(0.05)|   7.7470e-13
    the oracle's own error  |oracle(0.05) - converged|      7.7562e-13
    the shipped step's own  |shipped(0.1) - converged|      9.1593e-16

Halving the oracle's step divides its term by 15.94 then 15.38 against 2^4 - the
signature of RK4 truncation. Across the trajectories that set the tolerance the
oracle's share is 86 to 99.8 percent. The shipped step's own residual is inside
1.5626e-14 anywhere in `ALL_GATE_TRAJECTORIES`.

**Why this is conservative rather than wrong.** What the gate bounds is the sum
of both solutions' errors, so any returning method error still fails it by
orders of magnitude. `PL-X9KD` corrected the comments, which had generalised a
"refining the oracle changes nothing" measurement from the one trajectory where
it is true (held default settings) to the family. Nothing currently overclaims.

**What would fix it.** Refine `ORACLE_STEP_S` to about 0.0125 s, which a
transient needs. `_oracle_step_for`'s "half the step under test" rule and
`ORACLE_STEP_S` would have to move together or
`test_lockstep_oracle_step_matches_the_pinned_one` fails. `PINNED_REFERENCE_STATES`
do **not** need re-pinning - measured, all nine still pass under the module's own
`rel=1e-9, abs=1e-15` at 0.0125 s and at 0.003125 s.

**What it costs.** RK4 time rises fourfold per halving, on a file already
running about 49 s. That is the whole of the decision: it is a CI-cost question,
not a correctness one, which is why `PL-X9KD` left it open rather than settling
it. `HELD_RUN_ROUNDING_BOUND`'s gate already measures the shipped step's own
residual directly and needs no oracle refinement.

**Found.** `PL-X9KD`, 2026-09-06.
