---
id: PL-S64T
title: docs/MODEL.md § Known limitations says a learner would expect desflurane to wash out faster than Yasuda's volunteers did, and the shipped simulator draws it washing out slower
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** docs/MODEL.md § Known limitations says a learner would expect desflurane to wash out faster than Yasuda's volunteers did, and the shipped simulator draws it washing out slower

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. It was not corrected there, because the correction changes what a Known limitation tells a clinician, which is the project owner's call.

**What the document says.** § "Known limitations", in the paragraph that opens "Desflurane's five-minute washout disagrees with the published human measurement":

> As a diagnostic, the model was run with the rebreathing circuit removed. It then reproduces the published $`F_A/F_{A0}`$ at five minutes for sevoflurane and for both isoflurane cohorts, but washes desflurane out 2.33 published standard deviations too *fast*. This is the one comparison in this project against a human measurement that fails in the direction that overstates recovery. A learner who took desflurane's early washout as a physiologic prediction would expect a faster fall than Yasuda's volunteers showed.

**What the tree shows.** The faster fall exists only in a test. `tests/reference/test_published_wash_in_and_elimination.py` keeps the two conditions apart: `MODELLED_ELIMINATION_RATIOS` gives desflurane 0.1626 as shipped, and `OPEN_CIRCUIT_ELIMINATION_RATIOS` gives 0.0935 with the circuit removed, under the comment "These values come from a condition that the shipped simulator has no setting for". The published five-minute ratio is 0.14 ± 0.02, so the shipped value is 1.13 SD above the volunteers' mean, which is a slower fall. § "Published wash-in and elimination validation test" prints the same row ("| Desflurane | n=8 | 0.1626 | 0.14 ± 0.02 | +1.13 SD |") and requires that any restatement of the circuit-removed figures say that no setting of the simulator produces them. This paragraph restates 2.33 SD without that sentence.

**The question for the project owner.** What should a learner be told about desflurane's early washout on screen? Two readings are both true:

1. On screen, at every setting, desflurane's five-minute washout is slower than the volunteers' was, because the simulator's circle system rebreathes agent and the study's circuit did not.
2. The model's tissue return for desflurane is too low. If the circuit matched the study's, the model would predict a faster recovery than the volunteers showed.

**Recommendation:** say both, in this order, in place of the last two sentences quoted above:

> No setting of the simulator produces this condition. As shipped, with its rebreathing circuit, desflurane's five-minute ratio is 1.13 published standard deviations above the volunteers' mean, so the fall on screen is slower than theirs. The circuit hides a disagreement in the other direction: the model returns too little desflurane from the tissues, and with a circuit like the study's it would overstate how fast a patient recovers.

The reason is that a learner acts on what the screen shows. The present text warns of a faster fall that no learner can see, and leaves out the slower fall that every learner sees.

**Done when.** The paragraph says which direction the on-screen washout differs in, and says that the circuit-removed figure comes from a condition no setting produces.
