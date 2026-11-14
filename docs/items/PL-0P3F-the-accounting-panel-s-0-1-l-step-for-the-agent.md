---
id: PL-0P3F
title: The accounting panel's 0.1 L step for the agent totals is derived from partition-coefficient shifts measured only at 1 MAC with the reference flows; the model is linear in the dial, so at each agent's dial maximum and 10 L/min the 24 h shift is 3 to 4.6 times larger and one count of 0.1 L falls to about an eighth of an SD, at or past the seventh the section allows
priority: P1
effort: M
status: done
classes: defect, science
feature: model-claims-held-by-tests
touches: docs/INTERFACE.md, tests/integration/test_parameter_uncertainty.py
added: 2026-11-04
closed: 2026-11-14
pr: 2150
payoff: the accounting panel's 0.1 L step is derived at every setting the supported span allows, so no long high-dial run shows a last digit finer than the band
verify: grep -rqF 'def test_the_run_totals_litre_step_at_each_agent_s_dial_maximum' tests/
---

**Problem.** The accounting panel's 0.1 L step for the agent totals is derived from the shifts that one SD of a partition coefficient causes in the exhausted total, measured only at 1 MAC with the reference flows. The model is linear in the dial, so at each agent's dial maximum and 10 L/min the 24 h shift is 3 to 4.6 times larger. One step of 0.1 L then falls to about an eighth of an SD, at or past the seventh of an SD that `docs/INTERFACE.md` § "Displayed precision" allows.

**Checked 2026-11-04**, while building `PL-SP6H`. The second blind review pass on `#2024` perturbed the blood:gas coefficient by one SD in the model's system matrix and ran each agent for 24 h at its dial maximum and 10 L/min. The exhausted-total shift came out about 4.2 times the 1 MAC figure for sevoflurane, 4.6 times for isoflurane and 3.1 times for desflurane. The ratios of dial maximum to 1 MAC are 8/2.0, 5/1.2 and 18/6.0, or 4.0, 4.2 and 3.0, so the measurement agrees with linearity in the dial, to within the smaller effect of the higher flow. That run was a reviewer's and is not yet a test. At sevoflurane's figure the 24 h shift is about 0.8 L, so one step of 0.1 L is about an eighth of an SD, and a step of 0.01 L about an eightieth. The readouts' band runs down to "about a seventh" of an SD, so 0.1 L sits at or just past its fine end in the longest runs at the dial maximum. `PL-SP6H` narrowed the litre paragraph, in `docs/INTERFACE.md` § "The agent-accounting panel", to claim only the settings at which the shifts were measured.

**Why it matters.** The accounting panel shows the delivered, exhausted and stored totals at 0.1 L for every setting. A long run at a high dial setting may show a last digit finer than the band that § "Displayed precision" derives.

**Done when.** A test computes the one-SD shifts of the exhausted total at 1 MAC with the reference flows and at each agent's dial maximum with 10 L/min, at 1 h and 24 h. The litre paragraph states the range those give and names the test. Where one step of 0.1 L falls finer than a seventh of an SD, the paragraph says so, and the item moves to `needs-decision` with options for the litre step, because that choice changes what a learner sees.

**Generator check.** Stock of `PL-B6YV`'s fact, whether a `docs/MODEL.md` sentence about what the model computes matches what it computes. The litre paragraph's claim dates from `PL-BZR4` (2026-10-25), before that head closed on 2026-11-02, so this is not a re-entry. `PL-19W8` owes the test of the 1 MAC shifts, and this item's test extends it to the far end of the supported span.

**Built 2026-11-14, with `PL-TDX0`.** `test_the_run_totals_litre_step_at_each_agent_s_dial_maximum`
in `tests/integration/test_parameter_uncertainty.py` computes the exhausted
total's largest one-SD shift at 1 h and 24 h, at 1 MAC with the reference
flows and at each agent's dial maximum with 10 L/min, with the SDs `PL-TDX0`
corrected. The muscle coefficient gives the largest shift in every case, not
the blood:gas coefficient the section named. At 1 MAC the 24 h shifts are 0.61
to 0.68 L, so one 0.1 L step is a sixth to a seventh of an SD. At the dial
maximum with 10 L/min they are 2.1 to 2.8 L, a twenty-first to a twenty-eighth
of an SD. The litre paragraph states both and names the test.

The step is finer than the seventh of an SD the section allows, so this
item's own Done-when sends it to `needs-decision`. That decision is the same
one that the readouts, the schematic's amounts and its shares now face, for the
same reason, so it is held once, in `PL-W51N`, with the litre step listed among
its consequences. Two items asking the owner one question would split the
answer. This item closes with its test and paragraph done.
