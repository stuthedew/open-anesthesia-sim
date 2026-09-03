---
id: PL-F5GN
title: The oracle's independence check walks only ImportFrom, so a plain import bypasses it
priority: P2
effort: S
status: ready
classes: defect, test
feature: numerical-domain
touches: tests/reference/test_coupled_dynamics.py
added: 2026-09-03
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
