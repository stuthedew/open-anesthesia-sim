---
id: PL-F5GN
title: The oracle's independence check walks only ImportFrom, so a plain import bypasses it
priority: P2
effort: S
status: done
classes: defect, test
feature: numerical-domain
milestone: v0.4.9
touches: tests/reference/test_coupled_dynamics.py
added: 2026-09-03
closed: 2026-09-07
pr: 452
verify: uv run pytest 'tests/reference/test_coupled_dynamics.py::test_oracle_imports_no_solver_from_core' && grep -q 'ast.Import)' tests/reference/test_coupled_dynamics.py
---

**Problem.** `test_oracle_imports_no_solver_from_core` exists so that the
independent solution in `tests/reference/test_coupled_dynamics.py` cannot
quietly start comparing the implementation against itself. Its docstring is
explicit that this is what makes the module evidence rather than a tautology,
and the check is mechanical rather than left to review - which is right.

It walks only `ast.ImportFrom`:

```python
if isinstance(node, ast.ImportFrom)
if (node.module or "").startswith("anesthesia_sim")
```

So `from anesthesia_sim.core import uptake_system` is caught, and
`import anesthesia_sim.core.uptake_system as solver` is not. Neither is
`importlib.import_module("anesthesia_sim.core.uptake_system")`.

**Why it matters.** The gap is small and nothing exploits it today - the module
imports only the two parameter loaders, `AgentUptakeSystem`, and two
constants modules, and `_build_derivative()` uses the loaders alone. The
defect is in what the check *claims*: it is the single mechanism standing
between this module and a tautology, and a reader who sees a mechanical check
stops reviewing the imports by eye. A check that is trusted further than it
holds is worse than no check, which is the argument `CLAUDE.md` makes for
retiring one that fires without meaning.

**Where.** `tests/reference/test_coupled_dynamics.py`,
`test_oracle_imports_no_solver_from_core`.

**Approach.** Extend the comprehension to `ast.Import` as well, taking the
first dotted segment past `anesthesia_sim` for a plain import so the
`ALLOWED_PACKAGE_IMPORTS` comparison still means what it means. Add a case for
a dynamic import by name if it can be done without guessing - a literal
`importlib.import_module("anesthesia_sim...")` is decidable from the AST, an
expression is not, and the docstring should say the check covers static
imports rather than implying it covers every route.

**Done when.** `import anesthesia_sim.core.uptake_system` inside the module
fails the check, and the docstring states which import forms it decides.

**Worked.** The comprehension became three module-private helpers above the
test — `_package_imports` over the source text, with
`_reached_by_importing_module` and `_dynamic_import_target` under it — because
one comprehension over three node types could not carry the reason each form
contributes what it does. `_DYNAMIC_IMPORTERS` holds `import_module` and
`__import__`, matching `tools/import_boundary_check.py`, which had already
settled the dynamic-import shape; `_dynamic_import_target` follows its
`_dynamic_root` closely, including declining a relative literal.

The brief said to take the first dotted segment past `anesthesia_sim` for a
plain import, so `import anesthesia_sim.core.uptake_system` contributes
`core`. It did not say what a bare `import anesthesia_sim` contributes, which
has no such segment; that reports the package's own name. Neither is on
`ALLOWED_PACKAGE_IMPORTS` and neither can be, since that list holds names
taken *from* a module — so every plain import of the package fails, which is
the intent rather than an accident of the encoding, and the docstring on
`_reached_by_importing_module` says so.

Two things the brief did not ask for. The module test now matches on the root
dotted segment rather than `startswith("anesthesia_sim")`, which was the
expression being rewritten: the old form would also have claimed an import of
a package merely named with that prefix. No current import changes hands —
the module still yields exactly its six allowlisted names — and relative
imports are now skipped explicitly rather than by falling through `node.module
or ""`.

Second, the test carries an assertion the brief's **Done when** implies but
could not be written the obvious way: proving that `import
anesthesia_sim.core.uptake_system` fails the check by putting one in the
module would be adding a real bypass to the oracle. So the four bypass forms
are asserted as source strings passed to `_package_imports`. That is a
structure the brief left open, and it is the part of the diff a reviewer is
most likely to want to look at.

Checked outside the suite that each static form is caught — plain, aliased,
`from`, `importlib.import_module(...)` and `__import__(...)` with literal
arguments — and that a computed name and a same-prefix package are both left
alone. The computed name is the one real hole; per the brief it is stated in
the docstring rather than guessed at.
