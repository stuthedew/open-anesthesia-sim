---
id: PL-BNPY
title: advance()'s rollback hangs off two except clauses rather than the unwind path, so a BaseException leaves a partial step
priority: P2
effort: S
status: done
classes: defect
milestone: v0.3.1
touches: src/anesthesia_sim/core/uptake_system.py, tests/unit/test_uptake_system_failure.py
added: 2026-09-02
closed: 2026-09-02
pr: 246
verify: uv run pytest tests/unit/test_uptake_system_failure.py && grep -q 'def test_a_nonlocal_unwind_mid_step_is_rolled_back_too' tests/unit/test_uptake_system_failure.py
---

**Problem.** `advance()` captured state, then restored it inside two
`except` clauses. Anything that unwound without being an `Exception` skipped
both and left exactly the partly applied step the method exists to prevent.
`KeyboardInterrupt` is the reachable case; `asyncio.CancelledError` is not,
because `_advance_step()` contains no `await` for a cancellation to arrive
at.

**Why it matters.** Atomicity is a property that is either total or not
claimed, and the docstring claimed it without qualification - "leaving the
system bit-identical to what it was on entry". A rollback keyed on catching
something can only undo what it thought to catch.

**Measured 2026-09-02, and it is concrete rather than theoretical.** A
sevoflurane system was stepped 100 times, its state captured, and
`PatientCompartments.advance` - the third of the five sub-exchanges - made to
raise a `BaseException` subclass, after `advance_fresh_gas()` and the
circuit-alveolar exchange had already written.

The circuit was left written and **not** rolled back:
`circuit_concentration_fraction` was `0.0020003856996684967` before the step
and `0.0020183972008138854` after it. The same probe with an ordinary
`RuntimeError` in the same position rolled back completely, so the
transactional path worked and the gap was precisely the non-`Exception`
unwind.

Writing the regression test surfaced a downstream consequence the probe had
not reached: against the unfixed code the *next* step raises
`AgentSimulationValidationError` (`unaccounted = -1.199308e-04 L`), because
the surviving partial write breaks the accounting identity for every step
after it. So the partial state does not merely sit there being wrong - it
halts the run one step later and blames the numerics, which is the same
misattribution `PL-006` and `PL-VYXP` each produced by a different route.

**Where.** `src/anesthesia_sim/core/uptake_system.py`, `advance()`.

**Decision needed.** *Answered by the project owner, 2026-09-02: option 1.*
A success flag plus `finally`, keeping both existing behaviours - restate a
configuration error as numerical, propagate everything else unchanged - and
making the rollback total. The alternative was to leave the structure and
qualify the docstring's claim to `Exception`.

**Done when.** The rollback runs on the unwind path rather than on an
enumerated subset of it, and a test raising a `BaseException` subclass from a
sub-exchange asserts the system is bit-identical to its pre-step capture.

**Done.** `advance()` sets `step_completed` after `_advance_step()` returns
and restores in a `finally` when it is unset, so the decision is "did the
step finish" rather than "was this something I thought to catch". The wide
`except Exception` clause is gone - `finally` subsumes it - and the reasoning
it carried, about why only `SimulationConfigurationError` is restated, moves
into the remaining clause.

Two tests, both watched failing against the unfixed code.
`test_a_nonlocal_unwind_mid_step_is_rolled_back_too` asserts the captured
state is restored exactly.
`test_a_nonlocal_unwind_leaves_the_run_readable_and_steppable` asserts the
next step succeeds and its accounting closes, which is what fails with
`AgentSimulationValidationError` above - and is the distinguishing property
here, since an unwind from outside the model, unlike a step the model could
not complete, leaves a run that can legitimately continue.
