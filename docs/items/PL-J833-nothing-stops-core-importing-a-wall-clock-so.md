---
id: PL-J833
title: Nothing stops core/ importing a wall clock, so the never-wall-clock rule is prose rather than a check
status: untriaged
added: 2026-09-04
---

**Problem.** `CLAUDE.md` requires simulation time to be explicit state and never
the wall clock, and `docs/MODEL.md` § "The reproducibility guarantee" now states
that a run is a function of its inputs and its step count and of nothing else.
Nothing measures either. `core/` imports no clock today (checked 2026-09-04:
no `time`, `datetime` or `random` import anywhere under
`src/anesthesia_sim/core/`), and any later edit could add one with every gate
staying green.

**Why it matters.** This is the shape `tools/import_boundary_check.py` was built
for, in its own words: a claim answerable by reading the tree, asserted in prose
that would go on asserting it after it stopped being true. A clock or an
unseeded generator reached from a compartment makes two runs given identical
inputs differ, which is the property `PL-VM40` documented as a guarantee and the
planned forking milestone rests on - and unlike the drift `PL-VM40` removed, it
would not be nanoseconds.

**Where.** `tools/import_boundary_check.py`'s `BOUNDARIES` tuple, which is a
declaration with the reason beside each entry; `tests/unit/test_import_boundary_check.py`.
Confirm the checker reports an empty `allowed` list correctly - the existing
entry permits one module, and a boundary that permits none may need the
unused-allowance branch to be told about it.

**Done when.** A module under `src/anesthesia_sim/core/` importing `time`,
`datetime` or `random` fails `make check`, with the reason for each confinement
written beside it; and the check still passes on the tree as it stands.
