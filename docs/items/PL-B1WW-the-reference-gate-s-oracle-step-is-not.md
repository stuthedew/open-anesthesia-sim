---
id: PL-B1WW
title: The reference gate's oracle step is not converged during a transient, so 86-99.8 percent of what it reports is the oracle's own RK4 truncation rather than the shipped step's error
priority: P2
effort: S
status: done
classes: test
feature: numerical-domain
touches: tests/reference/test_coupled_dynamics.py, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-07
pr: 431
verify: uv run pytest tests/reference/test_coupled_dynamics.py::test_lockstep_oracle_step_matches_the_pinned_one -q && grep -q "^ORACLE_STEP_S = 0.0125$" tests/reference/test_coupled_dynamics.py && grep -q "^EXACT_STEP_ORACLE_TOLERANCE = 4e-13$" tests/reference/test_coupled_dynamics.py
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

Re-measured 2026-09-07 as a maximum over the whole trajectory rather than at
that one instant, the gate's reported figure falls as the oracle is refined and
then stops falling, which is where the oracle has stopped being what is
measured: 7.7377e-13 at 0.05 s, 4.7351e-14 at 0.025 s, 1.3906e-14 at 0.0125 s,
1.2490e-14 at 0.00625 s. The knee is at 0.0125 s, which is what makes it the
right target rather than 0.025 s — at 0.025 s the oracle still contributes
about two thirds of the reported number.

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

**What it costs — measured, 2026-09-07, and it is a fraction of what this
brief assumed.** The fourfold-per-halving figure is true of the RK4 term in
isolation and was never measured against the deliverable. Refining
`ORACLE_STEP_S` to 0.0125 s with `_oracle_step_for` returning `shipped / 8`:

    this file, serially                39.5 s -> 79.2 s     (+39.7 s, 2.0x)
    whole suite, as CI invokes it      43.0 s -> 55.5 s     (+12.5 s, 1.29x)

The file does not quadruple because about 25 s of it is not oracle work, and
the suite absorbs even that because CI runs `pytest -n $(cpu_count * 2) --dist
worksteal` (`.github/workflows/quality.yml`) and this file's 61 tests are
parametrized across workers, so it was never the critical path alone. Suite
figures are the mean of two paired runs on a 4-CPU container at `-n 8`; a first
run of each pair was discarded as cold. **So the price of the decision is about
12.5 s per CI run, not a file running for three minutes.**

Measured on CI itself once the change landed (#431), across four runs of
`quality.yml`'s `pytest` step:

    main, before the change   82 s
    the branch                86 s, 89 s
    main, after the change    80 s

**The effect is not resolvable above CI's run-to-run noise.** Hosted runners
vary by more than the change costs — `main` carrying the refinement was
*faster* than `main` without it — so no honest CI figure exists to quote. An
earlier draft of this paragraph read "+7 s, about 8%" from the first pair
alone, and a still earlier extrapolation from the local percentage predicted
+20 to +25 s. Both are withdrawn: one sample of a noisy quantity is not a
measurement, and this item exists because a decision was posed on a cost that
was estimated instead of measured.

The local `+12.5 s` above stands as the controlled figure — a quiet 4-CPU box,
paired runs, cold runs discarded — and is what a future reader should quote. It
is an upper bound on what CI pays.

`HELD_RUN_ROUNDING_BOUND`'s gate already measures the shipped step's own
residual directly and needs no oracle refinement.

**What it buys — measured over everything both trajectory gates drive.** The
worst residual anywhere falls 13x, and `EXACT_STEP_ORACLE_TOLERANCE` could
follow it down from `5e-12` to about `4e-13` at the same 6.5x margin:

    oracle at 0.05 s (today)     7.7377e-13   desflurane, ventilator start, 0.1 s step
    oracle at 0.0125 s           5.8870e-14   desflurane, ventilator start, 0.025 s step

The worst case also *moves*, which is the substantive gain rather than the
number. Today it sits at the **coarsest** shipped step, where the oracle is
least converged — the signature of oracle truncation. Refined, it moves to the
**finest** shipped step, where four times as many steps accumulate four times
as much rounding. That is the behaviour
`test_the_disagreement_does_not_shrink_with_the_step`'s own docstring predicts
and the gate currently cannot show, because oracle truncation swamps it.

Re-pinning is confirmed unnecessary rather than assumed: the whole suite, 2096
tests, passes unmodified at `ORACLE_STEP_S = 0.0125` with `_oracle_step_for`
returning `shipped / 8`, `test_lockstep_oracle_step_matches_the_pinned_one`
included — `0.1 / 8.0 == 0.0125` exactly, division by a power of two being
exact in binary floating point.

**Richardson extrapolation was measured and is not worth it.** Carrying two RK4
streams at `h/2` and `h/4` and combining them as `(16*y_fine - y_coarse) / 15`
is a fifth-order oracle at 3x the current oracle cost against 4x for the plain
refinement, and it reaches the same floor: worst 1.6029e-14 against 1.5786e-14
for a plain 0.0125 s oracle, both being the shipped step's own residual rather
than either oracle's truncation. It buys about a quarter of the oracle term,
which is roughly 3 s of CI, in exchange for a new mechanism inside the one
component of this module whose value is that a reviewer can audit it line by
line against a textbook. Rejected on the measurement, and recorded here so the
next reader does not re-derive it.

Speeding up `_rk4_step` and the derivative closure was also considered and
rejected for the same reason: the oracle's readability is what makes it an
independent check, and `CLAUDE.md` puts auditability above speed on exactly
this kind of path.

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

**Decided and done, 2026-09-07** (project owner: refine, on the measured cost
above). `ORACLE_STEP_S` is 0.0125 s, `_oracle_step_for` returns `shipped / 8`,
and `EXACT_STEP_ORACLE_TOLERANCE` came down from `5e-12` to `4e-13` — the
oracle refinement alone would have bought no sensitivity with the tolerance
left where it was.

The new bound is sized on the **subdivision spread**, not on the residual, and
that is the one thing the brief did not anticipate. Solving the gate
trajectories at 0.1, 0.05 and 0.025 s with no oracle involved moves the shipped
answer by up to 1.0691e-13 — larger than the 5.8870e-14 worst residual it
accompanies — so platform variation and not the measurement sets the floor.
`4e-13` clears the spread by 3.7x and the residual by 6.8x, which is the rule
`HELD_RUN_ROUNDING_BOUND` was already sized by (3.2x on its own spread).

Sensitivity measured rather than asserted: scaling every shipped state by
(1 + 1e-11) takes the worst gate figure to 1.8084e-12, which the old `5e-12`
passed silently and the new bound fails. A 2e-12 relative degradation still
passes — the floor above is why.

Verified: `make check` green, 2096 tests, 100% core coverage, 57.1 s for the
whole suite with `--cov` at `-n 8` against about 43 s before. Swept
`docs/MODEL.md` § "Independent-solution test", which carried the same figures
and the same superseded convergence claim, and `README.md` and
`docs/WORKING_NOTES.md`, which carry neither.

Filed on the way: `PL-D3XX` — v0.4.7's venous-pool change had moved every
measured residual in this file and none of the tables had been re-derived,
which is fixed in the same commit.
