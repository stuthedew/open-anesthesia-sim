---
id: PL-SPMQ
title: core/ states no governing equation anywhere; the only textbook transcription in the repo is the test oracle, so a reviewer cannot follow the science in the code the way the owner requires
priority: P1
effort: S
status: done
closed: 2026-09-03
pr: 256
classes: science, planning
feature: numerical-domain
not-delegable: the whole of this item was a decision about the numerical method; no command can prove a decision, and the implementation it authorized is PL-GS5X.
touches: src/anesthesia_sim/core, docs/MODEL.md
added: 2026-09-03
---

**Problem.** The project owner stated the bar for planned-milestone item 29
(2026-09-03): a human reviewer who knows the standard variables and equations
should be able to follow `core/` and recognize them, without referring to
`docs/MODEL.md` and without a lookup table.

The naming items scoped for that pass — `PL-9SH6`, `PL-3TLK`, `PL-212V` — meet
that bar for **variables**. Nothing meets it for **equations**, and `core/`
currently states none.

The textbook alveolar balance is one equation:

$$\frac{dF_A}{dt} = \frac{\dot V_A(F_C-F_A) - Q\lambda_{b:g}(F_A-F_v)}{V_A}$$

In `core/`, its two terms are computed in two different steps of
`AgentUptakeSystem._advance_step`, separated by a third, and neither appears as
that expression. The ventilation term lives inside
`_exchange_circuit_and_alveoli`, whose body is a two-compartment coupled
relaxation around an equilibrium fraction with a rate of
$`\dot V_A(1/V_C + 1/V_A)`$ — correct, and in no textbook, because it is an
artifact of solving that pair in isolation. The pulmonary uptake term
$`Q\lambda_{b:g}(F_A-F_v)`$ is never formed at all: the alveolar-blood transfer
is whatever the tissues took, applied afterwards by `apply_blood_uptake`.

**The equations already exist in this repository, in exactly the form the bar
asks for, in the wrong place.** `tests/reference/test_coupled_dynamics.py:562`,
inside `_build_derivative`:

```text
        d_alveolar = (
            ventilation_l_s * (circuit - alveolar)
            - cardiac_output_l_s * blood_gas * (alveolar - venous)
        ) / alveolar_volume_l
```

Quoted verbatim, with its own indentation, from
`tests/reference/test_coupled_dynamics.py`. The fence is `text` rather than
`python` deliberately: `ruff format` rewrites a `python` block, and de-indented
to column zero it rewraps this onto one line, which would stop it being a
faithful quotation of the source.

A reader who knows the subject recognizes that on sight. `core/` has nothing
resembling it.

**Why relocating it is not the fix.** `test_oracle_imports_no_solver_from_core`
(line 1105) forbids the oracle importing anything from `anesthesia_sim` beyond
the parameter loaders, deliberately: re-deriving the equations from the
specification is evidence, and calling the implementation under test would make
the independent-solution gate a tautology. That gate is a safety-critical
verification asset and must not be weakened to serve readability.

**The cause is the numerical method, not the naming.** The operator split is
what hides the equations: three of its five composed sub-steps
(`_exchange_circuit_and_alveoli`, the separate `apply_blood_uptake`, and the
composition order itself) are objects of the splitting scheme rather than of the
domain, so no amount of renaming makes them recognizable.

**Three options, put to the project owner 2026-09-03.**

- **A. Naming only**, as currently scoped. Variables become recognizable;
  equations still have to be reconstructed across three steps. Does not meet the
  stated bar. Already scoped, no further cost.
- **B. State the equations in `core/` and prove the split agrees.** A module
  holding the right-hand side in textbook form, plus a test that the shipped
  split matches it to the documented splitting bound. The reviewer can read the
  equations inside `core/`, but the code that actually runs is still the split,
  so following the computation still lands in five sub-steps. A half measure.
- **C. Replace the split with the exact matrix exponential.** The system is
  linear and time-invariant within a step, so one matrix exponential solves it
  exactly. The running code then *is* the equations: assembling the 6x6 system
  matrix is transcribing the ODEs term for term, and the three non-domain
  sub-steps disappear.

**The case for C beyond readability**, from `docs/MODEL.md` § "Selected method
(as implemented)": measured against the same RK4 oracle at 5% delivered over 60 s
and 3600 s horizons, the exponential's worst disagreement across all six states
is $`1.3\times10^{-16}`$ to $`4.8\times10^{-14}`$, against
$`5.2\times10^{-6}`$ to $`1.7\times10^{-5}`$ for the shipped split. It also
removes the applicability-domain bound on step size that `PL-VP7N` guards.

**What C costs.** It reopens `PL-6GS0`, closed 2026-08-30 (PR #94, shipped in
v0.2.8), which decided to keep the split. That decision weighed accuracy and
step size and concluded correctly on those grounds; the readability requirement
was not in its frame, which is the new information rather than a reversal. It is
a numerical-method change, so a **minor** rather than the patch item 29 was
planned as: displayed values move in the last digits, § "Displayed precision"'s
bounds are re-derived from the new behavior, and every pinned reference state in
the coupled-dynamics gate is re-pinned. It needs an `expm` — scipy is a heavy
dependency for this project, and a hand-rolled scaling-and-squaring Pade is
roughly fifty lines of numerics, which can sit in a clearly separated module
without hurting the domain-readability goal but is still code a reviewer must
trust.

**C also subsumes `PL-KZS3`.** That item asks whether `BreathingCircuit` should
store the amount like the other three compartments. An exact solver advances a
state vector of fractions, which is the opposite answer, so `PL-KZS3` should not
be decided until this one is.

**Why it matters.** The bar the owner stated is the whole purpose of the pass:
`ROADMAP.md` item 29 exists so that reviewing the coupled-gas equations of
planned-milestone items 6 and 7 is done against code that reads like the
textbook. Delivering recognizable variables over unrecognizable equations would
satisfy the letter of the item and miss what it is for.

**Done when.** The owner has chosen A, B or C; item 29's scope and version are
amended to match; and `PL-H46J` and `PL-VZL0` are reframed per the note below.

**Two corrections to the scope recorded in PR #256, which hold under any of the
three.** `PL-H46J`'s Code column was described as the spine of the pass; under
this bar it is not, it is scaffolding for the drift check in `PL-FZ6T`, and a
reader must never need to open it. `PL-VZL0` leads with "cite `docs/MODEL.md`
always"; a citation is a pointer to go and look something up, so the emphasis
inverts — the equation visible at the site is the deliverable and the citation is
provenance.

**Closed 2026-09-03. The project owner chose C, the exact matrix exponential.**
The three things this item's `Done when` asked for are all in place:

- Option C chosen, and recorded in `ROADMAP.md` planned-milestone item 29 and
  its `v0.4.x` timeline row, which now says the step takes a **minor** rather
  than a patch and says why.
- Three items carry the work — `PL-P0BB` (the state vector and what owns the
  trajectory, which subsumes the dropped `PL-KZS3`), `PL-GS5X` (the
  implementation, superseding `PL-6GS0`), `PL-X9KD` (re-deriving every
  published statement justified by the splitting error).
- `PL-H46J` and `PL-VZL0` reframed: the Code column is scaffolding for the
  drift check and never a reading aid, and the citation is provenance while the
  equation at the site is the deliverable.

One thing found after this brief was written and worth recording here: the
implementation is not hypothetical. `git show
475fb92^:tools/review-verification/verify_physics.py` — the harness retired
under `PL-STNV` — carries `build_system_matrix`, `multiply`,
`matrix_exponential` and `propagate` in about thirty lines of numerics, importing
`math` and nothing else. It produced the accuracy figures `docs/MODEL.md`
already quotes. So option C needs no new dependency; the project has no numpy
and no scipy, and a 7x7 exponential does not justify adding one under a
safety-critical path. `PL-GS5X` records what must change before it can ship.
