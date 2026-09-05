---
id: PL-J833
title: Nothing stops core/ importing a wall clock, so the never-wall-clock rule is prose rather than a check
priority: P2
effort: S
status: done
classes: infra, docs
feature: core-guard-coverage
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, docs/ARCHITECTURE.md, docs/MODEL.md, README.md
added: 2026-09-04
closed: 2026-09-05
verify: uv run pytest tests/unit/test_import_boundary_check.py && grep -q 'datetime' tools/import_boundary_check.py
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

**Resolved 2026-09-05.** Three entries in `BOUNDARIES`, each confined to
`src/anesthesia_sim/core` with an empty `allowed` and the reason beside it:
`time` and `datetime` for the wall clock, `random` for the process-global
generator, which breaks the same guarantee by the other route. A clock import
under `core/` now exits 1 from `make check` and CI, naming the file, the line
and the reason.

**The empty `allowed` needed one fix, and it was in the rendering rather than
in `analyze`.** The unused- and missing-allowance loops iterate over
`boundary.allowed`, so they simply do not run - the case the brief asked to
confirm was already correct. `format_report` was not: `", ".join(())` rendered
"time is allowed only in , because". It now says "permitted in no module under
`src/anesthesia_sim/core/`, because".

**The tree stops at `core/`, and that asymmetry is now pinned by a test.**
`docs/MODEL.md` "The reproducibility guarantee" explicitly permits the
interface its wall clock - what it forbids is a tick's real duration reaching
the run - so a boundary over the whole package would fail on an import the
design allows. `test_the_interface_may_read_the_clock_the_compartments_may_not`
holds that end-to-end through `main`.

**One regression this change introduced and closed.** With four boundaries over
nesting trees, `scanned` counted module-*reads* rather than modules: 68 for a
29-module package, growing when a boundary was added rather than when the
source did. That number is the tool's evidence that it inspected anything at
all, so it now counts distinct paths, with
`test_nesting_trees_do_not_inflate_the_module_count` holding it there.

**Docs swept:** `README.md` (the tools paragraph, now describing a table of
invariants rather than one), `docs/ARCHITECTURE.md` (the package-map comment
and the prose describing the tool, plus the new paragraph on why the two
trees differ), `docs/MODEL.md` ("The reproducibility guarantee" now says the
clock half is measured and names the check).
`src/anesthesia_sim/core/parameters.py`'s `_StrictPayload` docstring was read
and is unchanged: it describes the Pydantic boundary, which this did not touch.
