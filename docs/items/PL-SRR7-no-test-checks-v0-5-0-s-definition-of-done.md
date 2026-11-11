---
id: PL-SRR7
title: No test checks v0.5.0's definition-of-done claim that the memory a run holds is bounded by its number of control events; only the rule file run-is-its-definition.md guards it
status: untriaged
added: 2026-11-10
---

**Problem.** No test checks v0.5.0's definition-of-done claim that the memory a run holds is bounded by its number of control events; only the rule file run-is-its-definition.md guards it

**Where.** `ROADMAP.md` § "Completed: v0.5.0", definition of done: "the memory a run holds is bounded by its number of control events". `PL-49R8` added `.claude/rules/run-is-its-definition.md`, a rule against bringing back a sample store. A search of `tests/`, `tools/` and the queue's checks on 2026-11-10 found no test that asserts the bound. The nearest is `test_querying_a_run_does_not_change_the_keyframes_it_stores` in `tests/reference/test_canonical_evaluation.py`.

**Why it matters.** A completed release lists the bound as met. A change that stores per-step state again would pass every check, and a long case would grow without limit, as it did before `PL-2FM6`.

**Done when.** A test fails if the memory a run holds grows with its simulated length rather than with its number of control events, or the definition of done says the bound is guarded by the rule file only.

**Found by.** `PL-VM1Q`'s question 39, 2026-11-10.

