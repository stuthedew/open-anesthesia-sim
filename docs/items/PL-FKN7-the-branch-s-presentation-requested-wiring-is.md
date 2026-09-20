---
id: PL-FKN7
title: The branch's presentation_requested wiring is untested: every branch test reads the controller, none reads the display
status: untriaged
feature: branch-display-tests
added: 2026-09-20
---

**Problem.** The branch's presentation_requested wiring is untested: every branch test reads the controller, none reads the display

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.
