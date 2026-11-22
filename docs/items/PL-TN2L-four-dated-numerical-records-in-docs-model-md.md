---
id: PL-TN2L
title: Four dated numerical records in docs/MODEL.md do not reproduce on today's tree: the mass-balance headroom, the column built from shorter pieces, the alveolar volumes that halt a run, and what the envelope sweep holds one step to
priority: P2
effort: M
status: done
classes: defect
feature: model-spec-accuracy
milestone: v0.6.21
touches: docs/MODEL.md
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-22
pr: 2237
payoff: four passages of docs/MODEL.md that argue from measured figures give the figures of the model that ships, or say that theirs are a dated run's
verify: grep -qF 'is held to the simulator' docs/VERIFICATION.md
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

**Done 2026-11-22**, on `claude/project-thread-v9awbd` from `c0e9861e`. The restructure had moved all four passages from `docs/MODEL.md` to `docs/VERIFICATION.md`. Records 1 to 3 were already settled, as the check of 2026-11-22 above says: § "Mass-balance identity" gives about 250x and 22x from a table measured on the shipped tree (1e-10 against 3.90e-13 and 4.50e-12), § "Volumes outside the envelope" gives the tiny-volume halts in the past tense at the 0.1 s step a run then took, and the passage on the column built from shorter pieces is gone.

The fourth is fixed in § "The tests across the envelope". The paragraph said that every result of the first sweep test is held to 0.99 and to the agent balance within the bound for the squarings "each propagator actually needed". It now says what each kind of result is held to, as `tests/unit/test_numerical_envelope_sweep.py` does it:

1. A predicted 60 s run: the 0.99 limit and the agent balance, within the propagator bound at the squarings that a step at that corner and those flows needs (`_require_the_run`, `_propagator_error`). The 24-hour predictions: the 0.99 limit only, within `run_rounding` (`test_a_state_at_the_fraction_ceiling_stays_within_one_atmosphere`).
2. One step of the whole model: the 0.99 limit within `propagator_rounding(MOST_SQUARINGS)`, 22 squarings whatever the corner needs, and the agent balance by the simulator's own one part in 10⁹ (`_require_the_system`).
3. A compartment stepped alone: no propagator bound; each amount between its start and its equilibrium, and the circuit's balance within four rounding errors (`_require_the_compartments_alone`).

The same paragraph said the 24-hour predictions ran "at the two corners where rounding went furthest". `ROUNDING_CORNERS` holds three, and a separate test runs them, so the sentence now says three and names the test. No figure needed re-measuring: the change states which limit applies to which result, and every limit is read from the test code at `c0e9861e`.

Files checked: `docs/VERIFICATION.md` § "The tests across the envelope", § "The margin between 0.99 and 1", § "Volumes outside the envelope" and § "Mass-balance identity"; `docs/MODEL.md`, by `grep -n "squarings\|headroom\|halts"`, which finds none of the four records there.

**Blind review of #2237, 2026-11-22: fixed.** The rewritten list said the propagator bound carries "a margin of 8". Since 2026-11-14 the bound is `PROPAGATOR_ROUNDING_UNITS` = 10 times $`2^{s} \cdot 2^{-52}`$, derived from the arithmetic (`core/rounding.py`), and the same document says the measured margin of 8 ended then. The item now states the current bound, and a `provenance:` marker ties the 10 to the constant: with the constant set to 11, the documentation check fails with "states PROPAGATOR_ROUNDING_UNITS = 10 but core/rounding.py holds 11". The first paragraph also now names the one setting of the flows at which the 24-hour test runs each of its three corners: no fresh gas, 12 L/min of ventilation and 10 L/min of cardiac output, as `test_a_state_at_the_fraction_ceiling_stays_within_one_atmosphere` sets them. Two `provenance:` markers tie the 12 and the 10 to `core/supported_ranges.py`.
