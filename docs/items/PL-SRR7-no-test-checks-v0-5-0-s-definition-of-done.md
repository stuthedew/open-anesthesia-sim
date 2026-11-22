---
id: PL-SRR7
title: No test checks v0.5.0's definition-of-done claim that the memory a run holds is bounded by its number of control events; only the rule file run-is-its-definition.md guards it
priority: P2
effort: S
status: dropped
classes: test, perf
touches: tests/unit/test_run_definition.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; the bound holds today and only a later change could break it
added: 2026-11-10
closed: 2026-11-22
reason: Obsolete by design: since PL-MH9J (#2180) and the owner's ratified choice in PL-7CY5, a run stores one state per second, so its memory is bounded by the supported run length (core/stored_states.py: a 24-hour run holds 86 401 states, about 6.2 MB) rather than by its control events; the v0.5.0 claim it would test no longer describes the code, and ROADMAP's completed v0.5.0 section is a historical record
payoff: a change that makes a long case grow memory without limit fails a test instead of shipping
verify: grep -q 'def test_the_memory_a_run_holds_grows_with_its_control_events_not_its_length' tests/unit/test_run_definition.py
---

**Problem.** No test checks v0.5.0's definition-of-done claim that the memory a run holds is bounded by its number of control events; only the rule file run-is-its-definition.md guards it

**Where.** `ROADMAP.md` § "Completed: v0.5.0", definition of done: "the memory a run holds is bounded by its number of control events". `PL-49R8` added `.claude/rules/run-is-its-definition.md`, a rule against bringing back a sample store. A search of `tests/`, `tools/` and the queue's checks on 2026-11-10 found no test that asserts the bound. The nearest is `test_querying_a_run_does_not_change_the_keyframes_it_stores` in `tests/reference/test_canonical_evaluation.py`.
<!-- absent: tests/reference/test_canonical_evaluation.py -->

**Why it matters.** A completed release lists the bound as met. A change that stores per-step state again would pass every check, and a long case would grow without limit, as it did before `PL-2FM6`.

**Done when.** A test fails if the memory a run holds grows with its simulated length rather than with its number of control events, or the definition of done says the bound is guarded by the rule file only.

**Found by.** `PL-VM1Q`'s question 39, 2026-11-10.

**Generator check.** A one-off: a release's definition of done claims a bound that no test asserts. No head's `misread:` states which claims in a release's definition of done a test guards.

**Checked 2026-11-21:** the definition of done this item checks no longer describes the code. Since `PL-MH9J` a run stores one state for each second it reaches, so its memory is bounded by the supported run length rather than by its number of control events: about 7.6 MB for a 24-hour run (`core/stored_states.py`). `tests/reference/test_canonical_evaluation.py` was deleted by `PL-Z6C8`. A test for this item would now check the memory a run of the supported length holds.
<!-- absent: tests/reference/test_canonical_evaluation.py -->
