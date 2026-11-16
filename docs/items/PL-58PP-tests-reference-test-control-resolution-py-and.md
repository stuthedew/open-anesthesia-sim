---
id: PL-58PP
title: tests/reference/test_control_resolution.py and tests/unit/test_playback.py restate the interface tick as 0.1 s, citing Flet as the reason and a dashboard test that checks the copy, and no test compares the copy with SIMULATION_TICK_INTERVAL_S
status: untriaged
feature: one-source-of-truth
added: 2026-11-14
---

**Problem.** tests/reference/test_control_resolution.py and tests/unit/test_playback.py restate the interface tick as 0.1 s, citing Flet as the reason and a dashboard test that checks the copy, and no test compares the copy with SIMULATION_TICK_INTERVAL_S

**What happens.** Found 2026-11-14 while splitting the dashboard tests (`PL-1FPR`). Each file defines `TICK_INTERVAL_S = 0.1` with a comment saying it is restated "rather than imported from `app/simulation_view.py`, because that module needs Flet", and that the dashboard tests check the shipped constant equals it. Neither holds now. The interface is Qt, and the shipped constant is `SIMULATION_TICK_INTERVAL_S` in `src/anesthesia_sim/app/dashboard_frame.py`, which `tests/unit/test_dashboard_frame.py` already imports. No test compares either restated 0.1 with it: `grep -rn TICK_INTERVAL tests` finds only uses of the shipped constant and the two copies. The pre-split file never held such a check either, so the claim was already stale before the split. The split only re-pointed the comments at the new directory.

**Recommendation.** Import `SIMULATION_TICK_INTERVAL_S` from `anesthesia_sim.app.dashboard_frame` in both files, delete the two copies and the comments that justify them, and check that neither test file needs Qt as a result. Where a test needs the value independently of the code, as `.claude/rules/test-oracles.md` allows for an expected value, keep the copy and add the missing comparison instead.

**Why it matters.** A comment that promises a check that does not exist leaves a copy that can drift unseen. A change to the tick would leave the playback and control-resolution tests passing against the old value.
