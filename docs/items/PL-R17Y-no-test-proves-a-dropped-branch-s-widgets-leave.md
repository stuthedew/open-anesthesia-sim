---
id: PL-R17Y
title: No test proves a dropped branch's widgets leave the dashboard; the trunk-Reset test asserts Python-side state only
status: untriaged
feature: branch-display-tests
added: 2026-09-20
---

**Problem.** No test proves a dropped branch's widgets leave the dashboard; the trunk-Reset test asserts Python-side state only

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.
