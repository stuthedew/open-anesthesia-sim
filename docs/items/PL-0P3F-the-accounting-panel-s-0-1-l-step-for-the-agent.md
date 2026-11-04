---
id: PL-0P3F
title: The accounting panel's 0.1 L step for the agent totals is derived from partition-coefficient shifts measured only at 1 MAC with the reference flows; the model is linear in the dial, so at each agent's dial maximum and 10 L/min the 24 h shift is 3 to 4.6 times larger and one count of 0.1 L falls to about an eighth of an SD, at or past the seventh the section allows
priority: P1
effort: M
status: ready
classes: defect, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/reference
added: 2026-11-04
payoff: the accounting panel's 0.1 L step is derived at every setting the supported span allows, so no long high-dial run shows a last digit finer than the band
verify: grep -rqF 'def test_the_run_totals_litre_step_at_each_agent_s_dial_maximum' tests/
---

**Problem.** The accounting panel's 0.1 L step for the agent totals is derived from partition-coefficient shifts measured only at 1 MAC with the reference flows; the model is linear in the dial, so at each agent's dial maximum and 10 L/min the 24 h shift is 3 to 4.6 times larger and one count of 0.1 L falls to about an eighth of an SD, at or past the seventh the section allows

**Checked 2026-11-04**, while building `PL-SP6H`. The second blind review pass on `#2024` perturbed the blood:gas coefficient by one SD in the model's system matrix and ran each agent for 24 h at its dial maximum and 10 L/min. The exhausted-total shift came out about 4.2 times the 1 MAC figure for sevoflurane, 4.6 times for isoflurane and 3.1 times for desflurane. The model is linear in the dial, and the ratios of dial maximum to 1 MAC are 8/2.0, 5/1.2 and 18/6.0, which is 4.0, 4.2 and 3.0, so the measurement agrees with the linearity to within the flow's smaller effect. It is a reviewer's run and not yet a test. At sevoflurane's figure, the 24 h shift is about 0.8 L, so one count of 0.1 L is about an eighth of an SD and 0.01 L about an eightieth. The readouts' band runs down to "about a seventh" of an SD, so 0.1 L sits at or just past its fine end in the longest maximum-dial runs. `PL-SP6H` narrowed the litre paragraph to claim only the settings the shifts were measured at.

**Why it matters.** The accounting panel shows the delivered, exhausted and stored totals at 0.1 L for every setting. `docs/MODEL.md` now justifies that step only at 1 MAC with the reference flows. A long run at a high dial setting may show a last digit finer than the band the section derives.

**Done when.** A test computes the one-SD shifts of the exhausted total at 1 MAC with the reference flows and at each agent's dial maximum with 10 L/min, at 1 h and 24 h. The litre paragraph states the range those give and names the test. Where one count of 0.1 L falls finer than a seventh of an SD, the paragraph says so and the item moves to `needs-decision` with options for the litre step, since that choice changes what a learner sees.

**Generator check.** Stock of `PL-B6YV`'s fact, whether a `docs/MODEL.md` sentence about what the model computes matches what it computes. The sentence dates from `PL-BZR4` (2026-10-25), before that head closed on 2026-11-02, so this is not a re-entry. `PL-19W8` owes the 1 MAC shifts' test, and this item's test extends it to the span's far end.
