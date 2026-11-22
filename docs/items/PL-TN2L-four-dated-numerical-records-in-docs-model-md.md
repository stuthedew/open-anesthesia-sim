---
id: PL-TN2L
title: Four dated numerical records in docs/MODEL.md do not reproduce on today's tree: the mass-balance headroom, the column built from shorter pieces, the alveolar volumes that halt a run, and what the envelope sweep holds one step to
priority: P2
effort: M
status: ready
classes: defect
feature: model-spec-accuracy
touches: docs/MODEL.md
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
payoff: four passages of docs/MODEL.md that argue from measured figures give the figures of the model that ships, or say that theirs are a dated run's
---

**Problem.** Four dated numerical records in docs/MODEL.md do not reproduce on today's tree: the mass-balance headroom, the column built from shorter pieces, the alveolar volumes that halt a run, and what the envelope sweep holds one step to

**Why it matters.** Each passage argues from its figures in the present tense: how much room the mass-balance tolerance leaves, why the 24-hour chart keeps its method, and which alveolar volumes halt a run. A reader takes them as figures of the model that ships, and they are figures of a dated run.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. Each record below carries a date, so none is wrong as a record. Each is used in a present-tense sentence, and today's tree gives different figures. `PL-SZ6G` (a run's time as a whole number of seconds) changes the step that every one of them was measured at, so measure again after it merges, not before.

1. **The mass-balance headroom.** § "Mass-balance identity": "The mass-balance tolerance of 1e-10 leaves about 450x headroom at the horizon that the reference runs use, and about 16x at 8 h." The tables it rests on are dated 2026-09-06. On today's tree the worst relative residual at any step over the three reference runs is 1.28e-13 (sevoflurane), which is about 780 times below the tolerance. With wash-in held for 8 h it is 1.45e-12, about 70 times below. The tables do not say whether the 1 h, 4 h and 8 h runs include a washout, so they cannot be reproduced exactly.
2. **The column built from shorter pieces.** § "The numerical envelope": "**Neither shorter calculations nor a different method would shrink the 24-hour chart's excess, so the chart keeps its method.**", with "Computing the column in one piece gave a worst error of 6.0×10⁻⁷. Building it from pieces of 100 s, 10 s or 1 s gave 5.9×10⁻⁷, 5.8×10⁻⁷ and 5.8×10⁻⁷." At the hardest corner with no fresh gas, one 86400/59 s column measured today gives 5.65e-7 in one piece (the figure the same section prints lower down), and 1.2e-7, 1.8e-7 and 1.7e-7 from pieces of 100 s, 10 s and 1 s. Over the chart's 59 columns, the excess over 0.99 falls from 3.3e-5 to between 7e-6 and 1e-5. Only at maximum fresh gas did pieces not help (9.5e-7 in one piece; 8.3e-7, 1.1e-6 and 1.4e-6 in pieces). `PL-81Q2`, the closed item that recorded the decision, does not say which flows were used or how the pieces were combined. If today's figures stand, the bold sentence is too strong: shorter pieces shrink the excess three to five times, and the paragraph should give the reason the chart still keeps its method.
3. **The alveolar volumes that halt a run.** § "The numerical envelope": "At an alveolar volume of $`10^{-8}`$ to $`10^{-10}`$ L, the mass-balance check halts the run". Today the check also halts a sevoflurane run at 10⁻⁵, 10⁻⁶ and 10⁻⁷ L, after 74 s, 50 s and less than 1 s. None of these volumes can be built now, so nothing a learner sees depends on it.
4. **What the envelope sweep holds one step to.** § "The numerical envelope": "It must also lie at or below 0.99, and the agent balance must close, both to within the error bound of the propagators that produced the result ... That bound uses the squarings each propagator actually needed". That is true of the two 24-hour runs. `_require_the_system` in `tests/unit/test_numerical_envelope_sweep.py` holds one step of the whole model to the bound at the largest number of squarings any corner needs (`MOST_SQUARINGS`), and its balance to the simulator's own one part in 10⁹. A compartment stepped alone has no propagator bound.

The scripts that produced today's figures are not in the tree. Each figure above was measured with the test modules' own helpers at the 0.1 s step.

**Done when.** Each of the four passages either states figures measured on the tree that ships, with the date, or says in its own sentence that the figures are those of the dated run.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.

**Checked 2026-11-21:** `PL-Z6C8` removed the passage of `docs/MODEL.md` on the column built from shorter pieces, because the chart no longer computes its columns. The other three records remain.

**Checked 2026-11-22** against `d4e8200`: partly done, and its blocker `PL-SZ6G` (whole-second stepping) closed with #2180. That merge re-measured the first record: § "Mass-balance identity" now gives about 250x headroom at the reference runs' horizon and about 22x at 8 h, from a table measured on the shipped tree. It also turned the third record into a dated past-tense record "at the step of 0.1 s that a run then took". `PL-Z6C8` had already removed the second record. What is left is the fourth: § "The numerical envelope" still says "That bound uses the squarings each propagator actually needed", while `_require_the_system` in `tests/unit/test_numerical_envelope_sweep.py` holds one step of the whole model to `propagator_rounding(MOST_SQUARINGS)`.
