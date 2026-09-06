---
id: PL-B1WW
title: The reference gate's oracle step is not converged during a transient, so 86-99.8 percent of what it reports is the oracle's own RK4 truncation rather than the shipped step's error
priority: P2
effort: S
status: needs-decision
classes: test
feature: numerical-domain
touches: tests/reference/test_coupled_dynamics.py
added: 2026-09-06
---

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

**Decision needed.** Whether to buy the gate's sensitivity back at the cost of
CI time: refine `ORACLE_STEP_S` from 0.05 s to about 0.0125 s, so that what the
trajectory gates report is the shipped step's error rather than the oracle's —
or leave it at 0.05 s, accept a gate that is conservative but roughly three
orders of magnitude looser than the residual it watches, and say so beside the
constant. There is no correctness argument on either side; the two costs below
are the whole of it.

**What it costs.** RK4 time rises fourfold per halving, on a file already
running about 49 s. That is the whole of the decision: it is a CI-cost question,
not a correctness one, which is why `PL-X9KD` left it open rather than settling
it. `HELD_RUN_ROUNDING_BOUND`'s gate already measures the shipped step's own
residual directly and needs no oracle refinement.

**Why it matters.** The gate's headline number is not a measurement of the thing
its name implies. It reads as "how far the shipped step is from the truth" and
is, on the transients that set it, 86 to 99.8 percent a measurement of the
oracle. Two costs follow, and only the second is worth an item.

The first is comprehension: a reader tightening or loosening this tolerance,
or quoting it as evidence of the solver's accuracy, is reasoning about the wrong
quantity. `PL-X9KD` has already removed the overclaim from the comments, so this
is now a trap for whoever edits the file next rather than a false statement in
it.

The second is sensitivity. The tolerance sits about three orders of magnitude
above the shipped step's own residual (7.7e-13 against 9.2e-16), so a regression
that made the shipped step a hundred times worse would still pass. The gate
would catch anything that *returns* — a method error, a sign, a units slip —
because those miss by orders of magnitude, and `HELD_RUN_ROUNDING_BOUND`
measures the shipped residual directly with no oracle in the way. So nothing
wrong can reach a reader through this; what is lost is the ability to notice a
quiet degradation of the exact step, which is the reason the gate exists at all.

**Triage note, 2026-09-06: classed `test` rather than `science`, deliberately.**
The store pins `science` to P1, and every P1 item here is one where a clinician
could be misled. This gate is conservative rather than wrong — it bounds the sum
of both solutions' errors, so it never accepts an error it should reject, and
the brief's own measurements are what establish that. It is a question about how
sharp a verification gate should be for the CI time it costs. Overrule this if
the loss of sensitivity above reads as a correctness guarantee rather than a
test-quality one; the class is the only thing that would change.

**Where.** `tests/reference/test_coupled_dynamics.py` — `ORACLE_STEP_S`,
`_oracle_step_for`'s "half the step under test" rule, and
`test_lockstep_oracle_step_matches_the_pinned_one`, which fails unless the first
two move together. `PINNED_REFERENCE_STATES` do not need re-pinning: all nine
were measured passing under the module's own `rel=1e-9, abs=1e-15` at both
0.0125 s and 0.003125 s.

**Done when.** Either `ORACLE_STEP_S` is refined to about 0.0125 s with
`_oracle_step_for` moved with it and the added runtime measured and recorded, or
the decision to leave it at 0.05 s is written into the file beside the constant
— saying that the reported figure is dominated by the oracle on transients, that
the gate is therefore conservative, and that `HELD_RUN_ROUNDING_BOUND` is where
the shipped step's own residual is measured.

**Found.** `PL-X9KD`, 2026-09-06.
