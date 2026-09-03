---
id: PL-X9KD
title: Re-derive Displayed precision and the supported step bound, and re-pin the coupled-dynamics reference states, after the exact step lands
priority: P1
effort: M
status: blocked
blocked-by: PL-GS5X
classes: science, safety
feature: numerical-domain
touches: docs/MODEL.md, tests/reference, src/anesthesia_sim/core
added: 2026-09-03
verify: uv run pytest tests/reference/test_coupled_dynamics.py && grep -q 'matrix exponential' docs/MODEL.md
---

**Problem.** Three published statements are derived from the operator split's
error and stop being true the moment `PL-GS5X` lands. Leaving any of them stale
is a safety failure under `CLAUDE.md`'s standard, because each is something a
reader can act on.

1. **§ "Displayed precision"** sets the displayed resolution *from* the
   splitting error, and § "Supported simulation step" states that 0.1 s is the
   largest step at which "every claim Displayed precision makes about the last
   displayed digit stays true". With no splitting error, both derivations are
   void — the constraint becomes input precision and interpretability rather
   than numerical error, which may well justify the same two decimals for a
   different reason. Re-derive; do not assume the answer is unchanged, and do
   not assume it changes.
2. **`MAXIMUM_SIMULATION_STEP_S`** bounds the split's applicability domain, and
   `PL-VP7N` refuses a step outside it. An exact step has no splitting error at
   any step size, so the bound's stated rationale disappears. It does not
   follow that no bound is needed: the compartment capacity guard, the
   scaling-and-squaring headroom, and what a user can meaningfully observe are
   all still real limits. Decide what the bound now means, or remove it and say
   why.
3. **The pinned reference states** in `tests/reference/test_coupled_dynamics.py`
   are the split's solution at the historical operating point. They must be
   re-pinned from the exact solver and the change recorded, not loosened until
   they pass.

**Why it matters.** These are the three places where the numerical method
reaches a clinician. A displayed digit justified by an error bound that no
longer exists is false precision with a citation; a step refusal citing a domain
that no longer applies is a wrong error message on a safety path; and a
reference state loosened rather than re-derived converts a regression gate into
a rubber stamp.

**Where.** `docs/MODEL.md` § "Displayed precision", § "Supported simulation
step" and § "Selected method (as implemented)"; `core/uptake_system.py`'s
`MAXIMUM_SIMULATION_STEP_S` and `require_supported_simulation_step`;
`tests/reference/test_coupled_dynamics.py`'s pinned states and its
`SPLITTING_ERROR_BOUND_PER_STEP_SECOND`, which has no referent after `PL-GS5X`.

**Interacts with `PL-88GQ`** (state every displayed decimal count as a
presentation decision), which is about the same section from the other side; if
both are open, do them together.

**Done when.** Each of the three is re-derived from the exact step's behavior
with the derivation recorded, no constant survives whose justification named the
splitting error, and `make check` passes.
