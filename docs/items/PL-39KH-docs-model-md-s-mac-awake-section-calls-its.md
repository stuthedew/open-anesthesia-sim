---
id: PL-39KH
title: docs/MODEL.md's MAC-awake section calls its benchmark a 3-hour 1 MAC sevoflurane case, but the default 2% dial at 4 L/min brings alveolar and vessel-rich only to 1.69% (0.84 MAC) in 3 hours, and it blames the vessel-rich trace's failure to reach the 1 MAC line on a short case, when ongoing uptake keeps every trace below the line however long the case
priority: P1
effort: S
status: ready
classes: docs, science
feature: mac-awake-reference-text
touches: docs/MODEL.md
added: 2026-10-25
payoff: a learner no longer reads a 1 MAC dial as meaning the brain reaches 1 MAC given time
verify: ! grep -qF '3-hour 1 MAC sevoflurane case' docs/MODEL.md && ! grep -qF 'because it never equilibrated' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "MAC-awake as a chart reference" describes the band-crossing measurement as "a 3-hour 1 MAC sevoflurane case". Reproduced on main: the default dial of 2.0% at the default 4 L/min gives alveolar 1.688% and vessel-rich 1.685% after 3 hours, which is 0.84 MAC. So the 2.83 and 6.51 min crossings describe washout from about 0.84 MAC. The same section says the vessel-rich trace misses the 1 MAC line "on a short case, because it never equilibrated". At a 1 MAC dial no patient trace reaches the line even after 3 hours, because muscle and fat uptake keeps alveolar below inspired and inspired below the dial.

**Why it matters.** A learner who follows this text reads "dial 1 MAC" as "the brain reaches 1 MAC given time". The benchmark should name the dial and the alveolar level it actually reached, and the second sentence should give the right cause.

**Done when.** `docs/MODEL.md` § "MAC-awake as a chart reference" names the benchmark by its dial and the alveolar level it reached, not as a "3-hour 1 MAC sevoflurane case", and gives ongoing muscle and fat uptake as the reason no trace reaches the 1 MAC line, not a short case that "never equilibrated".

**Found by.** `PL-TBQS` reviewer replay on #288, finding r04 F3. Checked against main on 2026-10-25 by running `AgentUptakeSystem.for_agent("sevoflurane")` at its defaults for 108,000 steps of 0.1 s.
