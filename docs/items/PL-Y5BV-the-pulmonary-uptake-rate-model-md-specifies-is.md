---
id: PL-Y5BV
title: The pulmonary uptake rate MODEL.md specifies is never computed
priority: P2
effort: S
status: ready
classes: defect, test
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/reference/test_coupled_dynamics.py
added: 2026-08-30
verify: uv run pytest -k pulmonary_uptake_identity
---

**Problem.** `docs/MODEL.md:358-361` specifies the pulmonary uptake rate as
$`\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)`$. That expression is
never computed anywhere in `core/`. `core/uptake_system.py:161-166` takes
the *net change in the patient compartments* over the step and applies it to
alveolar gas through `AlveolarCompartment.apply_blood_uptake` instead. The two
agree through a telescoping identity — what the tissues and venous blood gained
is what the blood carried away — which is correct, but no test asserts it, and
the mixed-venous fraction $`F_v`$ never enters the alveolar update as a term.

**Why it matters.** The consequence is a specific blind spot rather than a
present error. Because the alveolar update is defined by the patient's own
bookkeeping, a wrong venous capacity would still telescope, still close mass
balance to ~2e-15 L, and still refine cleanly under step halving — so all three
of the guards this project relies on would stay green while the value that
governs uptake was wrong. The document names an equation the tests do not
reach.

**Where.** `docs/MODEL.md:358-361`; `core/uptake_system.py:161-166`;
`core/patient.py:127-137`.

**Approach.** Recommended: assert the identity in a test across a range of
states — several agents, several operating points, early wash-in through
near-equilibrium — comparing the applied alveolar uptake against
$`Q\lambda_{b:g}(F_A-F_v)`$ evaluated at the step's own fixed arterial
fraction, to the tolerance the split allows. That closes the blind spot rather
than documenting it.

The weaker alternative, if the identity turns out to hold only to within the
splitting error at usable tolerances, is to derive it in "Selected method (as
implemented)" and name there the test that stands in for it. Prefer the test:
a derivation records that someone checked once, a test checks on every run.

**Relation to other items.** PL-8LDF (tie MODEL.md's required invariants to
named tests) covers the eighteen "Required invariants". This is a governing
*equation* rather than an invariant, so it is outside that scope — but the two
are the same shape, and PL-8LDF's mechanism may be the right home for this link
once it exists.

**Scope note.** As with PL-2HTF, this is an instance of the class PL-036
describes; do not re-scope PL-036 to cover it. Cite it there as evidence.

**Class note.** Captured with a suggested `science` class, filed as
`defect`/`test`: `docket check` will not seat a `science`-classed item below
`P1`, and nothing computed today is wrong — what is missing is a guard, which
is the shape of the `core-guard-coverage` items and is classed the same way
here.

**Done when.** The relationship between `Q*lambda*(F_A - F_v)` and the applied
alveolar uptake is asserted by a test across a range of states, or derived in
`docs/MODEL.md` with the standing-in test named, and the document no longer
specifies an equation nothing checks.
