---
id: PL-BNPY
title: advance()'s rollback hangs off two except clauses rather than the unwind path, so a BaseException leaves a partial step
status: needs-decision
priority: P2
effort: S
classes: defect
touches: src/anesthesia_sim/core/uptake_system.py, tests/unit/test_uptake_system_failure.py
added: 2026-09-02
---

**Problem.** `advance()` captures state, then restores it inside two
`except` clauses. Anything that unwinds without being an `Exception` skips
both and leaves exactly the partly applied step the method exists to
prevent. `KeyboardInterrupt` is the reachable case;
`asyncio.CancelledError` is not, because `_advance_step()` contains no
`await`.

**Why it matters.** Atomicity is a property that is either total or not
claimed. The docstring claims it without qualification - "leaving the system
bit-identical to what it was on entry" - and a partly applied step is, in its
own words, "not a solution of anything". The probability is very low; the
cost of the guarantee being conditional is that the docstring is wrong for a
case nobody has enumerated.

**Where.** `src/anesthesia_sim/core/uptake_system.py`, `advance()`.

**Decision needed.** Whether to move the rollback onto the unwind path or to
qualify the claim:

1. A success flag plus `finally`, keeping both current behaviours - restate
   a configuration error as numerical, re-raise everything else unchanged -
   and making the rollback total.
2. Leave it and say in the docstring that the guarantee covers `Exception`,
   which is what a `KeyboardInterrupt` mid-step is being traded for.

Option 1 is a small restructure of one method with no behaviour change for
any currently reachable path. Not agreed.

**Done when.** The decision is recorded, and if the structure changes, a
test raises a `BaseException` subclass from a stubbed sub-exchange and
asserts the system is bit-identical to its pre-step capture.
