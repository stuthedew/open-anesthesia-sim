---
id: PL-GS5X
title: Replace the operator split with the exact matrix exponential, so the code that computes the answer is the governing equations
priority: P1
effort: L
status: ready
classes: science, refactor
feature: numerical-domain
touches: src/anesthesia_sim/core, docs/MODEL.md, tests/reference
added: 2026-09-03
verify: uv run pytest -q tests/reference/test_coupled_dynamics.py && grep -rq 'def build_system_matrix' src/anesthesia_sim/core/
---

**Problem.** The operator split hides the governing equations. `PL-SPMQ`
measures this: the alveolar balance's two terms are computed in two different
steps of `AgentUptakeSystem._advance_step`, separated by a third, and the
pulmonary uptake term $`Q\lambda_{b:g}(F_A-F_v)`$ is never formed at all. Three
of the five composed sub-steps are objects of the splitting scheme rather than
of the domain, so no renaming makes them recognizable.

The project owner chose the exact step on 2026-09-03 against the stated bar: a
reviewer who knows the standard variables and equations should follow `core/`
without referring to `docs/MODEL.md` or a lookup table.

**Why it matters, and why the exact step meets that bar where nothing else
does.** The system is
linear and time-invariant within a step, so one matrix exponential solves it
exactly, and assembling the matrix *is* transcribing the ODEs. From the retired
harness's `build_system_matrix`:

```text
    matrix[1][0] = ventilation_l_s / alveolar_volume_l
    matrix[1][1] = -(ventilation_l_s + cardiac_output_l_s * blood_gas) / alveolar_volume_l
    matrix[1][2] = cardiac_output_l_s * blood_gas / alveolar_volume_l
```

That row is $`\frac{dF_A}{dt} = \frac{\dot V_A(F_C-F_A) - Q\lambda_{b:g}(F_A-F_v)}{V_A}`$,
term for term, in the code that produces the number.

**The implementation exists in this repository's history.**
`git show 475fb92^:tools/review-verification/verify_physics.py` — the harness
retired under `PL-STNV`. It imports `math` and nothing else, and carries
`build_system_matrix` (7x7 augmented, the seventh state carrying the constant
fresh-gas forcing), `multiply`, `matrix_exponential` (scaling and squaring with
a 24-term Taylor series and four squarings of headroom) and `propagate`. The
numerics are about thirty lines.

**It is not a copy-paste, and three things must change.** The harness hard-coded
`DELIVERED_FRACTION` and `CIRCUIT_VOLUME_L` as experiment constants; a shipped
version builds the matrix from live settings and rebuilds it when one changes.
It carried no validation of its own numerics beyond the comparison; shipped code
needs the scaling-and-squaring parameters justified rather than inherited. And
it advanced a bare list; the shipped state has to interoperate with capture,
restore, reset and the accounting validator.

**No new dependency, deliberately.** The project's runtime dependencies are
`flet`, `flet-charts` and `pydantic`; there is no numpy and no scipy, and the
reference oracle hand-writes RK4 on plain lists. A 7x7 exponential does not
justify a compiled numeric dependency under a safety-critical path.

**Expected, unmeasured:** with settings constant the propagator is constant, so
it can be computed once per settings change and each step becomes one 7x7
matrix-vector product — 49 multiply-adds and no transcendentals, against the
five `exp()` calls the split makes every step. Measure rather than assume.

**Accuracy is not the motivation but is not a cost either.** `docs/MODEL.md`
§ "Selected method (as implemented)" records the measurement, made by this same
harness: worst disagreement against the RK4 oracle across all six states is
$`1.3\times10^{-16}`$ to $`4.8\times10^{-14}`$ for the exponential, against
$`5.2\times10^{-6}`$ to $`1.7\times10^{-5}`$ for the shipped split.

**This supersedes `PL-6GS0`**, closed 2026-08-30 in PR #94 and shipped in
v0.2.8, which decided to keep the split. That decision weighed accuracy and step
size and was right on those grounds; the code-readability requirement was not in
its frame. § "Selected method (as implemented)" and its "The exact alternative,
and why it is not taken" subsection are rewritten by this item, and must record
that the decision changed and on what new ground, rather than quietly reversing.

**The validation asset already exists and must not be weakened.**
`tests/reference/test_coupled_dynamics.py`'s independent RK4 oracle is what
proves a hand-rolled exponential correct, and
`test_oracle_imports_no_solver_from_core` must keep forbidding it from importing
the solver. Re-deriving the equations from the specification is evidence;
calling the implementation under test is not.

**Version: `v0.4.1`, a patch** (project owner, 2026-09-03). Recorded as a minor
earlier the same day and corrected: `ROADMAP.md` § "Versioning decision" chooses
by the capability boundary crossed, not by the size of the change, and this
crosses none — same model, same parameters, same controls, same agents, and
nothing the learner can do that they could not before. The displayed value moves
in its last digit, which v0.2.11 shipped as a patch already, and the guarantee
strengthens from bounded to exact, which is a stronger statement rather than a
new capability. Item 29 in `ROADMAP.md` carries the full reasoning and why no
exception is recorded.

**Sequencing.** Before the naming items `PL-9SH6` and `PL-VZL0`: this deletes
`_exchange_circuit_and_alveoli` and restructures `_advance_step`, so renaming
that code first is work thrown away. `PL-3TLK`'s $`F_C \rightarrow F_I`$
decision should be settled first even so, because the new matrix assembly should
be written with the domain's names from its first line.

**The `verify:` command is expensive on purpose, and the number is 23 s.**
`docket check` flagged the original — the whole of `tests/reference/` — as the
floor for every `make check` until this item closes: 34 s against a 0.7 s
median. Narrowed to `test_coupled_dynamics.py` alone, which is 23 s, and not
narrowed further. The cheap option is to pair the grep with a fast unit suite,
as `PL-9SH6` and `PL-3TLK` do, and it is wrong here: those are renames that
cannot move a number, while this replaces the numerical method, and the
independent-oracle gate is the one thing that would catch it going wrong. Nine
seconds a run is the right price for that. Measured 2026-09-03.

**Done when.** One exact step replaces the five composed sub-steps, the matrix
assembly reads as the governing equations without a lookup, the independent
oracle agrees to the tolerance `PL-X9KD` sets, `docs/MODEL.md` records the
superseded decision, and no dependency was added.

**What this item reaches outside its own release (added 2026-09-03).** Recorded
here because nothing else records it: an audit of the open queue found no
cross-reference in either direction between this release's items and v0.4.0's.

*Items this one subsumes, now `blocked-by: PL-GS5X`.* Close each out with this
one rather than working it first:

- `PL-Y5BV` (the pulmonary uptake rate `docs/MODEL.md` specifies is never
  computed) - forming $`Q\lambda_{b:g}(F_A-F_v)`$ as a matrix entry *is* the
  fix, and the identity test it specifies becomes a comparison of the matrix
  with itself.
- `PL-2HTF` (`docs/MODEL.md`'s numerical requirements contradict the split) -
  a single exponential satisfies § "Numerical method" requirement 2 rather than
  violating it, and this item deletes the sub-step ordering that item would
  document.
- `PL-LKRP` (`apply_blood_uptake` computes its result twice, accepts `bool`) -
  its only production caller is sub-step 5. Whoever writes the new step decides
  the method's fate, and that decision closes it.
- `PL-K9HV` is already `dropped`, superseded by `PL-X9KD`.

*Items whose stated reasoning this one falsifies* - each now carries a note
saying so, so no session has to rediscover it: `PL-SN2C`, `PL-DHV7`, `PL-RCTQ`,
`PL-WB0X` (v0.4.0); `PL-GYH2`, `PL-4GN8`, `PL-ZLNN`, `PL-11YF`, `PL-TG60`,
`PL-79YX`, `PL-6194`, `PL-10MX`, `PL-88GQ`.

*One thing to land before this item, not after.* `PL-22Z3` gates coverage at
100% on `core/`, which `core/` currently meets and nothing defends. This item
adds a hand-rolled `build_system_matrix`, `matrix_exponential`, `multiply` and
`propagate` to `core/`; landing the gate first forces the new solver in fully
covered, where landing it afterwards measures against code that may already have
dropped below the line.

*And one correction to `PL-X9KD`* worth knowing here, because this item's author
is the one who will read it: its third deliverable used to ask for
`PINNED_REFERENCE_STATES` to be re-pinned from the exact solver. Those are the
RK4 oracle's own solution, not the split's, and re-pinning them would convert
`test_independent_solution_matches_pinned_reference_states` into a
self-comparison. `PL-X9KD` is corrected; leave those states alone.