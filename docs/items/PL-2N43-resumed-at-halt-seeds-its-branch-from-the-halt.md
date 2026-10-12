---
id: PL-2N43
title: resumed_at_halt seeds its branch from the halt's recorded crossing, so a time bookmark added inside the halting step while the trunk stands on the halt reads BEFORE_THIS_BRANCH on that branch, where resumed_at_mark reads the same mark PASSED (reproduced 2026-10-12: a 45.35 s mark halts at 45.4 s, a 45.33 s mark added while standing)
status: untriaged
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-10-12
---

**Problem.** resumed_at_halt seeds its branch from the halt's recorded crossing, so a time bookmark added inside the halting step while the trunk stands on the halt reads BEFORE_THIS_BRANCH on that branch, where resumed_at_mark reads the same mark PASSED (reproduced 2026-10-12: a 45.35 s mark halts at 45.4 s, a 45.33 s mark added while standing)
