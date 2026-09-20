---
id: PL-624C
title: test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis draws its own frame, so it cannot detect a fork that fails to redraw
status: untriaged
feature: branch-display-tests
added: 2026-09-20
---

**Problem.** test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis draws its own frame, so it cannot detect a fork that fails to redraw

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.
