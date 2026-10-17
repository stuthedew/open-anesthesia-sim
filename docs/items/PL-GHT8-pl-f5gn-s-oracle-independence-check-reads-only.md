---
id: PL-GHT8
title: PL-F5GN's oracle-independence check reads only the import names in test_coupled_dynamics.py, not what the oracle functions call, so an oracle built from AgentUptakeSystem.for_agent().equation_settings() passes it, and the late-washout module's second hand-written oracle is never checked
priority: P2
effort: S
status: ready
classes: test
feature: tests-detect-wrong-values
touches: tests/reference/test_coupled_dynamics.py
added: 2026-10-17
payoff: an oracle quietly rebuilt from the code under test fails the independence check, so the reference tier keeps comparing the solver with something other than itself
verify: grep -q 'def test_oracle_bodies_call_no_solver_from_core' tests/reference/test_coupled_dynamics.py
---

**Problem.** PL-F5GN's oracle-independence check reads only the import names in test_coupled_dynamics.py, not what the oracle functions call, so an oracle built from AgentUptakeSystem.for_agent().equation_settings() passes it, and the late-washout module's second hand-written oracle is never checked

**Severity: medium.** Neither oracle breaks independence today; the check
would not notice if one did. Audit finding ORC-2 (reference tier), confirmed
by the adversarial verifier.

**Evidence.** `test_oracle_imports_no_solver_from_core` in
`tests/reference/test_coupled_dynamics.py` parses only its own file
(`Path(__file__)`). It checks the imported names against
`ALLOWED_PACKAGE_IMPORTS`, which includes `AgentUptakeSystem` for the side of
the test that runs the shipped code. Its docstring leaves names assembled at
run time to review. A probe showed what passes:

- an oracle whose `_build_derivative` calls
  `AgentUptakeSystem.for_agent(...).equation_settings()`;
- `sys.modules['anesthesia_sim.core.governing_equations']`;
- `importlib.import_module(AgentUptakeSystem.__module__)`.

A plain `from ...governing_equations import build_system_matrix` is caught.
The shipped code can also be reached through allowed names, for example
`equation_settings().tissues[i].washin_rate_s` or `system._propagator_for`.

`tests/reference/test_late_washout_against_published_fits.py` holds a second
hand-written oracle: `_open_circuit_system_per_min`, `_open_circuit_modes`
(using `numpy.linalg.eig`) and `_isolated_time_constants_min`. Its docstring
claims "nothing here reaches the implementation under test". No check reads
that file, and it imports four names outside the allowlist
(`AgentSimulationValidationResult`, `Fraction`, `MINUTES_PER_HOUR`,
`SECONDS_PER_MINUTE`). Both oracles use only the parameter loaders today.
`tools/import_boundary_check.py`, `tools/literal_home_check.py` and
`tools/fact_home_check.py` cover `src/` only, so nothing else checks this.

**Why it matters.** An edit that builds the oracle's matrix or rates from the
shipped code would turn both verification gates into comparisons of the
implementation with itself, and every check would stay green. These gates are
worth something only because they are independent.

**Where.** `tests/reference/test_coupled_dynamics.py`
(`ALLOWED_PACKAGE_IMPORTS`, `test_oracle_imports_no_solver_from_core`,
`_build_derivative`, `_rk4_step`, `_integrate_rk4`);
`tests/reference/test_late_washout_against_published_fits.py`.

**Recommended fix.** Keep the check a test, since it is simulator test work.
Have it read both oracle files and inspect the bodies of the designated oracle
functions (`_build_derivative`, `_rk4_step`, `_integrate_rk4`,
`_open_circuit_system_per_min`, `_open_circuit_modes`,
`_isolated_time_constants_min`). Those bodies may reference only the loader
names, `math` or `numpy`, and module-local helpers, and must not use
`sys.modules` or `__module__`. Keep the module-level import allowlist for the
side of each test that runs the shipped code.

**Done when.** Each of the three probe oracles above fails the check, and the
check reads the late-washout file.

**Related.** `PL-F5GN` (done) closed the plain-`import` gap in this check and
nothing more.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**What was done.** `test_oracle_bodies_call_no_solver_from_core` in
`tests/reference/test_coupled_dynamics.py` reads the oracle functions of both
files: `_build_derivative`, `_rk4_step` and `_integrate_rk4` here, and
`_open_circuit_system_per_min`, `_open_circuit_modes` and
`_isolated_time_constants_min` in
`tests/reference/test_late_washout_against_published_fits.py`. It follows
every module-level helper, class and constant they refer to. An oracle may use
the two parameter loaders, `math`, `cmath`, `numpy`, `Callable` and
`dataclass`, and its own module's names. It may not use another imported
name, import inside its body, read a dunder attribute or call a builtin that
reaches a namespace by name. A missing root fails the check, so a rename
cannot empty it. Five probes must each be refused: the three this item names,
a helper that calls the solver, and an import inside the body. One allowed
oracle must pass. The import check beside it is unchanged.

**Fail-before.** The three probes this item names were run through the old
check, `_package_imports(probe) <= ALLOWED_PACKAGE_IMPORTS`, with `uv run
python` from `tests/reference/` on 2026-10-17. It returned `True` for each, so
each passed. The new check returned "_build_derivative uses the imported name
AgentUptakeSystem", "_build_derivative uses the imported name sys", and
"_build_derivative reads the attribute __module__" for the third, with two
more lines for `importlib` and `AgentUptakeSystem`.
