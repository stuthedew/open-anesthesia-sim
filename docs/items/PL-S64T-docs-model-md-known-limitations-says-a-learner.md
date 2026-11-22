---
id: PL-S64T
title: docs/MODEL.md § Known limitations says a learner would expect desflurane to wash out faster than Yasuda's volunteers did, and at the default settings the simulator draws it washing out slower
status: done
feature: model-spec-accuracy
touches: docs/MODEL.md, docs/items/PL-1B8B-docs-model-md-s-sources-for-the-notes-above.md
added: 2026-11-21
closed: 2026-11-21
pr: 2199
verify: grep -qF 'washout on screen cannot be compared with theirs directly' docs/MODEL.md
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

**Done when.** The paragraph says that the volunteers' condition, with no circle system, differs from every setting of the simulator. It gives the on-screen figures beside the circuit-removed figure with the settings they hold at, says that the screen can fall faster than the volunteers at a high flow and raised ventilation, and says in which direction a real patient on the same circuit would differ from the screen if the published measurement is right. Revised on 2026-11-22 from the first version, which asked for the direction by setting (see the reviews below).

**Generator check.** Not a generator. One sentence restated a figure from a condition that only a test can produce, the circuit removed, without saying so, which § "Published wash-in and elimination validation test" already forbids. No other item in the `model-spec-accuracy` feature has that cause.

**Answered 2026-11-21.** The project owner chose option 1 (project owner, 2026-11-21, ratified, "Agree with recs", over keeping the present warning and adding its condition). Two statements in the recommended text were wrong, and the paragraph in `docs/MODEL.md` § "Known limitations" corrects them while keeping option 1's shape:

1. The recommended text called 0.163 the figure "at the default ventilation". It is the figure at a fresh gas flow of 10 L/min, which the published comparison pins in `FRESH_GAS_FLOW_L_MIN`. The simulator's default fresh gas flow is 4 L/min (`data/machines/reference_circle_system.json`), where the five-minute ratio is 0.285, 7.3 SD above the volunteers' mean. The recommended text also placed the faster fall only at a raised ventilation at 10 L/min. The grid below, run on 2026-11-21 with `_eliminate("desflurane", ...)` from `tests/reference/test_published_wash_in_and_elimination.py` after its 30-minute wash-in, shows it at 8 L/min of fresh gas too, and at a low cardiac output. Each figure is the five-minute $`F_A/F_{A0}`$, against the volunteers' 0.14 ± 0.02.

   | Fresh gas flow | Alveolar ventilation 4, 6, 8, 12 L/min | Cardiac output 2, 3 L/min (ventilation 4) |
   | --- | --- | --- |
   | 4 L/min | 0.285, 0.254, 0.237, 0.220 | 0.248, 0.268 |
   | 6 L/min | 0.217, 0.182, 0.163, 0.144 | 0.179, 0.200 |
   | 8 L/min | 0.183, 0.146, 0.126, 0.107 | 0.147, 0.166 |
   | 10 L/min | 0.163, 0.125, 0.105, 0.086 | 0.130, 0.148 |

2. The recommended text said the cause "is that the model returns too little desflurane from the tissues". § "Desflurane's residual, and why the parameter file was not changed" rules that explanation out against the measured human tissue solubility, and leaves the published value itself as the one hypothesis. The paragraph now says only that the model washes desflurane out faster than the volunteers without the circuit, and that rebreathing hides this at most settings.

**Docs sweep.** Searched the tree outside `docs/items/` for the replaced sentences ("faster fall", "overstates recovery", "2.33 published"). `docs/prose-review/model-description-draft.md` still holds the old sentence, and is left as it is, because it is a dated draft that says `docs/MODEL.md` wins where they differ. The docstrings in `tests/reference/test_late_washout_against_published_fits.py` and `tests/reference/test_published_wash_in_and_elimination.py` that mention a faster fall or 2.33 SD describe the condition with the circuit removed, and stay true. `docs/WORKING_NOTES.md` describes the same condition. `docs/INTERFACE.md` and `README.md` do not repeat the sentence.

**Blind review, 2026-11-21.** Two passes read the branch. Both found that the first rewrite placed the faster fall only at 10 L/min of fresh gas, when it also appears at 8 L/min with a raised ventilation and at 10 L/min with a low cardiac output. The grid above was run and the paragraph now names that region. Both noted that no test pins the 0.285 at the default fresh gas flow, and that the paragraph did not say the figures follow a 30-minute administration with the flow unchanged. The paragraph now says so, and `PL-M3J9` added the test on 2026-11-22, after the project owner answered the question on the pull request with "Whatever best practice is. Look it up." `PL-M3J9` records the guidance that answer rests on. Pass 2 found that the `verify:` phrase wrapped over two lines, so a plain `grep` could not find it, and the phrase is now one that sits on one line.

**Second blind review, 2026-11-22.** Pass 2 found that the paragraph judged the washout on screen, which always includes the circle system, against Yasuda's volunteers, who breathed through a non-rebreathing circuit. Pass 1 found the faster-fall region still misdescribed. The paragraph was rewritten to say the two conditions differ and to compare the on-screen figures with the circuit-removed 0.0935. The grid above and option 1's "by setting" shape are superseded. Option 1's purpose, telling a learner the direction of the error and not to read the screen as a recovery prediction, still applies. `PL-M3J9` records the applicability guidance this rests on.

**Third blind review, 2026-11-22.** Both passes found that the rewrite said the circuit slows the washout "far more than the model's error speeds it". At 10 L/min the circuit adds about 0.069 to the ratio against an error of about 0.047, which is not far more, and at a high flow with a raised ventilation the screen falls below the volunteers' mean. The paragraph now says the slowing depends on the fresh gas flow and the ventilation, names the default ventilation and cardiac output its figures hold at, and quotes 0.105 at 10 L/min of fresh gas and 8 L/min of alveolar ventilation as a faster fall. Pass 1 found that "the model's error is present at every setting" stated an extrapolation as fact, because the error was measured at the published protocol's settings only; the paragraph now says so and makes the last claim conditional on it. Pass 2 found that the paragraph dated all three figures 2026-11-21 when two are older pins; the date was removed and the paragraph points at the tests instead. Pass 2's note that 0.0935 carries four decimals beside three-decimal figures was left as it is, because § "Published wash-in and elimination validation test" and its tables print the same figure with four. Pass 2 also found that the new text differs from the "by setting" shape the project owner chose, without his read. The text goes back to him on the pull request before it merges.

**Sent to the owner 2026-11-22.** The reworked paragraph went to the project owner on the pull request for his read before it merges, because it replaces the "by setting" shape he agreed to with a comparison against the circuit-removed figure.
