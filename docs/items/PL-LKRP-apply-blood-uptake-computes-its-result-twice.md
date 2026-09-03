---
id: PL-LKRP
title: apply_blood_uptake computes its result twice and accepts bool where parameters.py rejects it
status: needs-decision
blocked-by: PL-GS5X
priority: P3
effort: S
classes: refactor
touches: src/anesthesia_sim/core/alveolar.py, tests/unit/test_alveolar.py
added: 2026-09-02
---

**Problem.** Two small things in one method.
`AlveolarCompartment.apply_blood_uptake()` evaluates
`self.agent_amount_l - blood_uptake_l` twice - once inside the guard, once
into `resulting_amount_l` - so an edit can make the value checked and the
value assigned diverge. Separately, its `isinstance(blood_uptake_l, (int,
float))` accepts `bool`, where `parameters.py`'s `_validate_positive_finite`
rejects it explicitly.

**Why it matters.** Neither is a live defect. The doubled expression is a
maintenance hazard in a method whose whole job is a guarded assignment; the
`bool` inconsistency means the codebase answers "is a bool a number?"
differently in two places, and only one of them wrote the answer down.

**Where.** `src/anesthesia_sim/core/alveolar.py`, `apply_blood_uptake()`.

**Decision needed.** Whether either is worth touching. Computing once and
reusing is unambiguous. The `bool` question is a real choice: reject it for
consistency with the parameter loader, or decide that the loader's
strictness is about untrusted file input and does not belong on an internal
call, and say so.

**Done when.** The decision is recorded, and if the method changes, the
`bool` behaviour - whichever way it goes - is asserted by a test rather than
left implicit.

**Measured 2026-09-02.** Confirmed as written.
`AlveolarCompartment.apply_blood_uptake(False)` is accepted and leaves the
compartment at `0.05 L`, because `isinstance(False, (int, float))` is `True`;
`core/parameters.py`'s `_validate_positive_finite(True)` refuses with "must
be a number". Two answers to the same question, in one package.

The doubled expression needs no probe - `self.agent_amount_l -
blood_uptake_l` appears on both the guard line and the assignment line, and
the hazard is a future edit to one of them.

**`PL-GS5X` now owns this decision, 2026-09-03.** Both defects live inside
`AlveolarCompartment.apply_blood_uptake`, whose only production caller is
`core/uptake_system.py:345` — sub-step 5 of the five the exact matrix
exponential replaces. Its other five callers are all in
`tests/unit/test_alveolar.py`. So the question "is either worth touching" cannot
be answered ahead of the item that decides whether the method survives at all:
the pulmonary uptake term becomes a matrix entry, and a guarded subtraction
applied after the fact may have nothing left to guard.

Kept at `needs-decision` rather than blocked, because the decision is still owed
and the `bool` half of it is a convention question the whole codebase answers —
`isinstance(blood_uptake_l, (int, float))` accepts `bool` where
`core/parameters.py`'s `_validate_positive_finite` rejects it — which survives
whatever happens to this particular method.
