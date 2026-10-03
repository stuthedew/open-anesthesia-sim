---
id: PL-YXFF
title: tests/unit/test_formatting.py:108 says tools/import_boundary_check.py forbids core/ importing app/; it matches top-level package names only and declares no such boundary, so the claim is false; declare core-to-app as a dotted boundary and correct the comment
status: done
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, tests/unit/test_formatting.py, docs/ARCHITECTURE.md, docs/items/PL-L8RN-nothing-enforces-the-one-adapter-qsplitter.md, ROADMAP.md
added: 2026-10-03
closed: 2026-10-03
pr: 1326
verify: uv run pytest -q tests/unit/test_import_boundary_check.py -k 'dotted or compartments_may_not_import' && uv run python tools/import_boundary_check.py
---

**Problem.** tests/unit/test_formatting.py:108 says tools/import_boundary_check.py forbids core/ importing app/; it matches top-level package names only and declares no such boundary, so the claim is false; declare core-to-app as a dotted boundary and correct the comment

**Why it matters.** A comment in `test_concentration_decimals_are_a_choice_within_a_recorded_band` in `tests/unit/test_formatting.py` says a guard exists that does not. `tools/import_boundary_check.py` keys every boundary on `name.split(".")[0]` in `module_imports` and `_dynamic_root`, so `anesthesia_sim.app` and `anesthesia_sim.core` are both `anesthesia_sim` to it, and no declared boundary names `app`. The tree is clean today (`grep -rn anesthesia_sim.app src/anesthesia_sim/core/` finds nothing, 2026-10-03), so this is a false sense of coverage rather than a live violation: the next session that reads the comment, as the one that wrote it did, skips the test it would otherwise have written.

**Shape.** Let a boundary name a dotted prefix and match on it; declare `anesthesia_sim.app` forbidden under `core/`; a test in `tests/unit/test_import_boundary_check.py` with a fixture module that imports it; the comment reworded to the guard that then exists. PL-L8RN (blocked) asks for one module inside a package, a different granularity; a dotted prefix is enough here.

**Done when.** A `from anesthesia_sim.app import ...` under `core/` fails `make check`, and the comment in `test_concentration_decimals_are_a_choice_within_a_recorded_band` is true.

**Generator check.** Not a head: one tool, one gap. It is an instance of the prose-restates-tree family (PL-4FBP) in that a comment asserted a property of the tree nothing checked.

**Design at pickup, 2026-10-03** (not yet built; the session reset for length first).

- *Match every dotted name an import makes available*, not the first segment: `import a.b` gives `a.b`; `from X import a, b` gives `X`, `X.a` and `X.b`, so `from anesthesia_sim import app` is seen; a literal dynamic import gives its name. A boundary matches when a name equals its `package` or starts with `package + "."`; one `Imported` per statement, so a root boundary such as `pydantic` does not count `from pydantic import BaseModel` twice.
- *Resolve relative imports instead of skipping them.* `from ..app import formatting` under `core/` reaches `anesthesia_sim.app`; "a relative import cannot name a package outside the tree" holds only for root packages. Resolve against the importing module's package, read from its path under `src/`, with importlib's rule (`package.rsplit(".", level - 1)[0]`).
- *Declare* `anesthesia_sim.app` permitted in no module under `src/anesthesia_sim/core`, its `why` citing the layering in `docs/ARCHITECTURE.md` § "Layering" and `CLAUDE.md`'s rule that simulation code stays independent of the interface. Update the module docstring (a boundary may name a dotted prefix; a fourth invariant) and `module_imports`' line on relative imports.
- *Tests*: a fixture under `core/` importing `app` absolutely, by `from anesthesia_sim import app`, and relatively, each fails; `app/` importing `core/` passes; existing assertions on `Imported` fields updated to the new shape.
- *Then* reword the comment in `test_concentration_decimals_are_a_choice_within_a_recorded_band` to name the boundary that exists. Reading `from X import name` as `X.name` also gives PL-L8RN the granularity it asked for; say so, do not widen this item.

**Built as designed, 2026-10-03.** `Imported` carries every dotted name a statement makes available, and `reaches(package)` is the match; a `from` statement now renders the names it imports, so `from anesthesia_sim import app` reads as that rather than as `from anesthesia_sim import ...`. `test_the_compartments_may_not_import_the_interface` fails on the root-only reader with the new boundary declared - measured by putting the old reader back with only the entry added: exit 0 where it should be 1 - and passes on this one. The real tree passes: 13 boundaries, 42 modules, 0 errors. `docs/ARCHITECTURE.md` now counts four claims the tool measures, and `PL-L8RN`'s brief records that its prerequisite landed, with the one limit its entry should state.
