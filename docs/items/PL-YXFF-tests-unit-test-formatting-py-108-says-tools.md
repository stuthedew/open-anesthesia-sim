---
id: PL-YXFF
title: tests/unit/test_formatting.py:108 says tools/import_boundary_check.py forbids core/ importing app/; it matches top-level package names only and declares no such boundary, so the claim is false; declare core-to-app as a dotted boundary and correct the comment
status: untriaged
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, tests/unit/test_formatting.py
added: 2026-10-03
---

**Problem.** tests/unit/test_formatting.py:108 says tools/import_boundary_check.py forbids core/ importing app/; it matches top-level package names only and declares no such boundary, so the claim is false; declare core-to-app as a dotted boundary and correct the comment

**Why it matters.** A comment in `test_concentration_decimals_are_a_choice_within_a_recorded_band` in `tests/unit/test_formatting.py` says a guard exists that does not. `tools/import_boundary_check.py` keys every boundary on `name.split(".")[0]` in `module_imports` and `_dynamic_root`, so `anesthesia_sim.app` and `anesthesia_sim.core` are both `anesthesia_sim` to it, and no declared boundary names `app`. The tree is clean today (`grep -rn anesthesia_sim.app src/anesthesia_sim/core/` finds nothing, 2026-10-03), so this is a false sense of coverage rather than a live violation: the next session that reads the comment, as the one that wrote it did, skips the test it would otherwise have written.

**Shape.** Let a boundary name a dotted prefix and match on it; declare `anesthesia_sim.app` forbidden under `core/`; a test in `tests/unit/test_import_boundary_check.py` with a fixture module that imports it; the comment reworded to the guard that then exists. PL-L8RN (blocked) asks for one module inside a package, a different granularity; a dotted prefix is enough here.

**Done when.** A `from anesthesia_sim.app import ...` under `core/` fails `make check`, and the comment in `test_concentration_decimals_are_a_choice_within_a_recorded_band` is true.

**Generator check.** Not a head: one tool, one gap. It is an instance of the prose-restates-tree family (PL-4FBP) in that a comment asserted a property of the tree nothing checked.
