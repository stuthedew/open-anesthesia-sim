---
id: PL-V7FG
title: tests/unit/test_state_capture.py: test_a_step_after_a_setting_moved_propagates_with_the_new_matrix says the two systems differ in setting ventilation before or after the first step, but both set it after and differ only in clearing the propagator cache (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: tests/unit/test_state_capture.py
added: 2026-10-25
payoff: the state-capture test says it guards the propagator cache, which is what it guards
verify: ! grep -qF 'that ventilation was set before the first step or after it' tests/unit/test_state_capture.py
---

**Problem.** tests/unit/test_state_capture.py: test_a_step_after_a_setting_moved_propagates_with_the_new_matrix says the two systems differ in setting ventilation before or after the first step, but both set it after and differ only in clearing the propagator cache (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 504 of `tests/unit/test_state_capture.py`: the systems differ in "that ventilation was set before the first step or after it".

**Why it matters.** The docstring names the one difference the test isolates. Naming the wrong one hides that the test is about the propagator cache, which is the fault it exists to catch.

**Done when.** The docstring says the two systems differ only in whether the propagator cache was cleared. No test changes behaviour.
