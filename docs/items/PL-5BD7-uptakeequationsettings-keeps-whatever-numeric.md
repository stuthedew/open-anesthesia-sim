---
id: PL-5BD7
title: UptakeEquationSettings keeps whatever numeric and container types it is given, so as the propagator caches' key two equal records can form different bits (a float subclass or numpy scalar sums without CPython's compensation) and a list of tissues is unhashable; nothing in src/ builds either today (found reviewing #1359)
status: untriaged
added: 2026-10-04
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
