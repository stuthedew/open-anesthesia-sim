---
id: PL-5BD7
title: UptakeEquationSettings keeps whatever numeric and container types it is given, so as the propagator caches' key two equal records can form different bits (a float subclass or numpy scalar sums without CPython's compensation) and a list of tissues is unhashable; nothing in src/ builds either today (found reviewing #1359)
priority: P2
effort: S
status: ready
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/governing_equations.py, tests/unit/test_governing_equations.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-04
payoff: a run is served the same propagator however its equal settings were built, so identical inputs give identical results bit for bit and no accepted settings record breaks the cache
verify: grep -q 'def test_equal_settings_form_the_same_propagator_bit_for_bit_whatever_built_them' tests/unit/test_governing_equations.py
---

**Problem.** UptakeEquationSettings keeps whatever numeric and container types it is given, so as the propagator caches' key two equal records can form different bits (a float subclass or numpy scalar sums without CPython's compensation) and a list of tissues is unhashable; nothing in src/ builds either today (found reviewing #1359)

**Evidence, from the adversarial review of `PL-CNCF`'s pull request
(2026-10-04).** Both propagator caches key on the settings record by value:
`AgentUptakeSystem._propagator_for` on the stepped path, and since `PL-CNCF`
the propagators `RunDefinition.evaluate_anchored` keeps between frames. Value
keying assumes two equal records form the same propagator, bit for bit. That
holds for every record `equation_settings()` builds, because it builds each
field the same way every time. It does not hold for every record the
constructor accepts.

- *Equal, but formed differently.* An `np.float64` circuit volume is a `float`
  subclass, so `mypy` accepts it, and it compares and hashes equal to the plain
  float. Yet `exp(A*t)` came out different in 16, 39 and 48 of the 81 entries'
  bits at 0.84, 7 and 600 s (re-run in the session that filed this). CPython's `sum` runs its compensated (Neumaier,
  since 3.12) path only on exact floats, so a subclass takes plain addition.
  A run whose third stretch was an `np.float32`-volume copy of the first had
  the first stretch's propagator served to it by the kept store: 710 of 2 137
  columns differed from the pre-`PL-CNCF` code, worst 1.43e-4 relative. That
  input already skewed the old code too (3.9e-4 between display and
  `state_at` in that stretch).
- *Unhashable.* `tissues` given as a list is accepted at run time, and
  `evaluate_anchored` now raises a bare `TypeError: cannot use 'tuple' as a
  dict key (unhashable type: 'list')` where it drew the window before.
  `state_at` still answers.

Neither is reachable: no module in `src/` imports numpy, `equation_settings()`
always builds a tuple, and `mypy` refuses a list. The fix is one place either
way: the record's own constructor normalizing what it holds, exact floats and a
tuple, which is the parse-don't-validate pattern
(`.claude/rules/core-domain.md`) applied to the record rather than to a single
quantity. The reviewer's scripts were in the session scratchpad and are not
kept: `equal_not_identical.py` and `edges.py`.

**Reproduced 2026-10-05, at triage.** On Python 3.14.7, against `main` at
`b67dace8`,
`uv run python -c "import dataclasses, numpy as np; from anesthesia_sim.core.uptake_system import AgentUptakeSystem; from anesthesia_sim.core.governing_equations import build_system_matrix; from anesthesia_sim.core.matrix_exponential import matrix_exponential; s = AgentUptakeSystem.for_agent('sevoflurane').equation_settings(); t = dataclasses.replace(s, circuit_volume_l=np.float64(s.circuit_volume_l)); a, b = (matrix_exponential(build_system_matrix(r), 7.0) for r in (s, t)); print(s == t, hash(s) == hash(t), sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb)), max(abs(x - y) / abs(x) for ra, rb in zip(a, b) for x, y in zip(ra, rb) if x)); hash(dataclasses.replace(s, tissues=list(s.tissues)))"`
printed `True True 39 1.275320593174873e-15` and then raised `TypeError:
unhashable type: 'list'`. Two records equal and hashing alike formed
propagators differing in 39 of 81 entries at 7 s, by at most 1.3e-15 relative,
and a record holding its tissues as a list was built and could not be a key.
The same run with `np.float32` gave 2.0e-6 relative at 7 s, the input behind
the 1.43e-4 the review measured over a run.

**Why it matters, and why `defect` at `P2` rather than `science`.** Value
keying is what lets the two caches skip a matrix exponential safely, and it
rests on equal records forming the same propagator bit for bit; where they do
not, which propagator a stretch is served depends on which equal record was
cached first, so identical inputs stop giving identical results, against
`CLAUDE.md`'s determinism rule. It is not classed `science` because no
supported path reaches it: no module in `src/` imports NumPy,
`equation_settings()` builds a tuple of plain floats every time, and `mypy`
refuses a list. Of what a caller `mypy` does not read can hand in, the one
input that moves a value past rounding - `np.float32`, at 1e-4 over a run - is
refused by `require_a_number` once `PL-3800` brings the volume guards to it,
since it is neither an `int` nor a `float` subclass; what is left is an
`np.float64` at the last bit, which breaks bit-identity but no clinical value,
and a list that raises rather than answers.

**Done when.** `UptakeEquationSettings` and `TissueGroupEquationSettings` hold
each plain-`float` field as an exact `float` and the tissues as a `tuple`,
whatever `int` or `float` subclass and whatever sequence they were built from -
normalized in `__post_init__`, or a list refused with a `TypeError` naming it,
the implementer's call - so two records that compare equal form the same
propagator bit for bit and every record is hashable. The checked flow and
concentration types are held as they are, since each is one type in every
record. A test in `tests/unit/test_governing_equations.py` named
`test_equal_settings_form_the_same_propagator_bit_for_bit_whatever_built_them`
pins it for an `np.float64` volume and a list of tissues.
