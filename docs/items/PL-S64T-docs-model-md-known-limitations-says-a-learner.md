---
id: PL-S64T
title: docs/MODEL.md § Known limitations says a learner would expect desflurane to wash out faster than Yasuda's volunteers did, and at the default settings the simulator draws it washing out slower
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** docs/MODEL.md § Known limitations says a learner would expect desflurane to wash out faster than Yasuda's volunteers did, and at the default settings the simulator draws it washing out slower

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. It was not corrected there, because the correction changes what a Known limitation tells a clinician, which is the project owner's call.

**What the document says.** § "Known limitations", in the paragraph that opens "Desflurane's five-minute washout disagrees with the published human measurement":

> As a diagnostic, the model was run with the rebreathing circuit removed. It then reproduces the published $`F_A/F_{A0}`$ at five minutes for sevoflurane and for both isoflurane cohorts, but washes desflurane out 2.33 published standard deviations too *fast*. This is the one comparison in this project against a human measurement that fails in the direction that overstates recovery. A learner who took desflurane's early washout as a physiologic prediction would expect a faster fall than Yasuda's volunteers showed.

**What the tree shows.** The 2.33 SD comes from a condition that exists only in a test. `tests/reference/test_published_wash_in_and_elimination.py` keeps the two conditions apart: `MODELLED_ELIMINATION_RATIOS` gives desflurane 0.1626 as shipped, and `OPEN_CIRCUIT_ELIMINATION_RATIOS` gives 0.0935 with the circuit removed, under the comment "These values come from a condition that the shipped simulator has no setting for". § "Published wash-in and elimination validation test" requires that any restatement of the circuit-removed figures say that no setting of the simulator produces them, and this paragraph restates 2.33 SD without that sentence.

What a learner sees depends on the settings. The published five-minute ratio is 0.14 ± 0.02, and neither paper reports the volunteers' ventilation. Runs of the test module's own `_eliminate("desflurane", ...)` on 2026-11-21, with the shipped circuit:

| Setting changed from the defaults (alveolar ventilation 4 L/min, cardiac output 5 L/min, fresh gas 10 L/min) | Five-minute $`F_A/F_{A0}`$ | Against the volunteers' 0.14 ± 0.02 |
| --- | --- | --- |
| none | 0.163 | +1.13 SD, a slower fall |
| fresh gas 4 L/min | 0.285 | +7.3 SD, slower |
| fresh gas 1 L/min | 0.595 | +22.7 SD, slower |
| alveolar ventilation 5 L/min | 0.140 | equal |
| alveolar ventilation 6 L/min | 0.125 | −0.8 SD, a faster fall |
| alveolar ventilation 8 L/min | 0.105 | −1.7 SD, faster |
| alveolar ventilation 12 L/min | 0.086 | −2.7 SD, faster |
| cardiac output 2 L/min | 0.130 | −0.5 SD, faster |

So the sentence about what a learner would expect is true at a raised ventilation and false at the defaults and at any lower fresh gas flow. A blind review pass on `PL-RMNP`'s branch found the ventilation rows, after this item's first version said "at every setting".

**The question for the project owner.** What should the limitation tell a learner about desflurane's early washout on screen? Two options:

1. **Say what the screen shows, by setting, then the cause.** At the default ventilation the fall on screen is slower than the volunteers', and slower still at a low fresh gas flow, because the circle system rebreathes agent. At an alveolar ventilation of about 6 L/min or more it is faster than theirs. Under both sits one fault: the model returns too little desflurane from the tissues.
2. **Keep the present warning and add its condition.** Keep "would expect a faster fall", and add that this holds with the circuit removed or at a raised ventilation, and that no setting of the simulator removes the circuit.

**Recommendation:** option 1, with this text in place of the last two sentences quoted above:

> No setting of the simulator removes the circuit. As shipped, desflurane's five-minute ratio at the default ventilation is 1.13 published standard deviations above the volunteers' mean, so the fall on screen is slower than theirs, and a lower fresh gas flow slows it further. At an alveolar ventilation of about 6 L/min or more, the fall on screen is faster than theirs. The cause in both cases is that the model returns too little desflurane from the tissues, which the rebreathing circuit hides at the defaults. A learner should not take desflurane's early washout on screen as a prediction of how fast a patient recovers.

The reason is that a learner acts on what the screen shows, and the present text describes only one of the two directions the screen can err in.

**Done when.** The paragraph says in which direction the on-screen washout differs at the default settings and at a raised ventilation, and says that the circuit-removed figure comes from a condition no setting produces.
