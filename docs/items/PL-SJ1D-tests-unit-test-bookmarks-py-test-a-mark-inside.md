---
id: PL-SJ1D
title: tests/unit/test_bookmarks.py: test_a_mark_inside_a_step_is_reached_at_the_step_s_end_and_not_rounded_back calls its 0.05 s step coarser than 0.1 s and says the reaching step ends at 45.4 s, but 0.05 s is finer and its reaching step ends at 45.35 s (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: tests/unit/test_bookmarks.py
added: 2026-10-25
closed: 2026-10-25
pr: 1817
payoff: the bookmark test's docstring agrees with the step and time its assertions check
verify: ! grep -qF '45.4 s, at a coarser step' tests/unit/test_bookmarks.py
---

**Problem.** tests/unit/test_bookmarks.py: test_a_mark_inside_a_step_is_reached_at_the_step_s_end_and_not_rounded_back calls its 0.05 s step coarser than 0.1 s and says the reaching step ends at 45.4 s, but 0.05 s is finer and its reaching step ends at 45.35 s (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 410 of `tests/unit/test_bookmarks.py` ("45.4 s, at a coarser step"), while the assertions below it use `SimulationStep(0.05)` and `45.35`.

**Why it matters.** The docstring is the statement of what the test proves about when a mark is reached. One that contradicts its own assertions leaves a reader unable to tell which is intended.

**Done when.** The docstring calls 0.05 s the finer step and gives 45.35 s as its reaching step's end, matching the assertions. No test changes behaviour.
