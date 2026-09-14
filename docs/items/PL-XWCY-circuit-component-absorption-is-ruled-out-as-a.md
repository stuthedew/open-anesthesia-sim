---
id: PL-XWCY
title: Circuit-component absorption is ruled out as a cause of desflurane's residual by the one paper that measured it, and is a live candidate for the other two agents
priority: P1
effort: M
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.22
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-09-13
closed: 2026-09-13
pr: 550
verify: python3 tools/doc_check.py check && grep -qi 'circuit-wall absorption' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Desflurane's residual, and why the parameter
file was not changed" carries the candidates for the one published comparison
this project misses in the direction of washing out too fast. `PL-RFLN` struck
the published apparatus's dead space off that list on 2026-09-13. Circuit-wall
absorption has never been on it, and the paper now held decides it in both
directions.

**The evidence.** Targ AG, Yasuda N, Eger EI II. Anesth Analg 1989
Aug;69(2):218-25, PMID 2764290, read at full text 2026-09-13. Measuring washin
and washout in a real conventional circuit against the ideal exponential, it
finds I-653's rates "closely approximated the maximal possible theoretical
rates" and lying close to the ideal line at every flow, while isoflurane,
sevoflurane and halothane lag it - the ranking following the component
partition coefficients, which are lowest for I-653 throughout Table 1.

**What that decides.** For **desflurane**, the model's inert circuit is the
assumption the measurement most nearly supports, so wall absorption cannot
explain a desflurane elimination that is too fast - and the direction is wrong
as well as the magnitude, since a real absorbing circuit releases agent back
and would slow washout rather than speed it. Struck, like the dead space.

For **sevoflurane and isoflurane**, the same measurement says the opposite: a
real circuit measurably retards both relative to ideal, and this model has no
term for it. That is not a residual anybody has complained about yet; it is a
named, quantified, agent-dependent departure that the wash-in comparisons in
`tests/reference/test_published_wash_in_and_elimination.py` are measured
against, and the sevoflurane and isoflurane cohorts there already sit +3.79 SD
and +4.15 SD.

**Whether those two facts are one item or two is the first judgment here.** The
strike is a paragraph in `docs/MODEL.md`; the sevoflurane/isoflurane direction
is a possible partial explanation of an existing discrepancy and wants its own
analysis.

**Where.** `docs/MODEL.md` § "Desflurane's residual, and why the parameter file
was not changed"; `tests/reference/test_published_wash_in_and_elimination.py`
for the cohorts it would bear on.

**Done when.** Circuit-wall absorption is recorded as struck for desflurane
with the measurement behind it, and the sevoflurane/isoflurane direction is
either analysed or filed as its own item with what it would take.
**Why it matters.** Two things, and only the first is bookkeeping. Striking
circuit-wall absorption for desflurane removes a candidate from the list a
reader of `docs/MODEL.md` consults to judge how far the model's one published
disagreement is understood, and a list still naming a mechanism the literature
has ruled out overstates how much is unknown - which is the mirror of false
precision and lands under the same clause of the clinical-output standard.

The second half is live. The same measurement says a real conventional circle
system measurably retards sevoflurane and isoflurane relative to the ideal
exponential, this model has no term for it, and the sevoflurane and isoflurane
cohorts in `tests/reference/test_published_wash_in_and_elimination.py` already
sit at +3.79 SD and +4.15 SD - in the direction that departure would explain. A
named, quantified, agent-dependent mechanism pointing at an existing
discrepancy is not a tidy-up, and it is why this is `science` rather than
`docs` alone.

**The one-item-or-two judgment the brief names is the session's**, and it can
be taken from the evidence rather than from direction: the strike is settled by
the paper and is a paragraph, while the sevoflurane/isoflurane direction is an
open analysis against the reference suite. Splitting is the expected answer;
the Done-when already admits it.

---

**Outcome, 2026-09-13. The strike landed; the split did not, and the brief's
reason for expecting one does not survive reading the source.**

The paper was re-read at full text this session rather than taken from this
brief's transcription. The desflurane half held exactly as written and is now
the ninth row of the candidate table in `docs/MODEL.md` § "Desflurane's
residual, and why the parameter file was not changed", with a block giving
what it proposed and what struck it. The abstract's conclusion - absorption of
I-653 "should not hinder induction of or recovery from anesthesia" - and
Figures 3 and 5, where desflurane's curves lie close to the ideal exponential
at every flow, are the evidence; the direction is the independent second
reason, and it needed no measurement.

**The sevoflurane/isoflurane half was analysed rather than split off, and the
analysis says it is not a candidate.** Three findings, any one sufficient, and
the second is a straightforward misreading in this brief:

1. **It is already recorded.** `PL-LS3H` closed in v0.4.20 (`#539`) with the
   Table 1 coefficients, the ranking, the statement that the inert circuit is
   most nearly true for desflurane and least for halothane, and the decision
   not to add a wall term - all under "Known limitations", which is where a
   limitation of the simulator belongs. Filing an item to analyse it again
   would have duplicated closed work.
2. **The +3.79 SD and +4.15 SD this brief attributes to the wash-in cohorts
   are the elimination rows.** They are five-minute `F_A/F_A0` figures. The
   wash-in comparison has no departure at all for a mechanism to explain:
   every agent stays inside its published spread at every fresh gas flow from
   1 to 10 L/min.
3. **On the elimination rows the mechanism moves the wrong way, and is absent
   from the published measurement besides.** `docs/MODEL.md` already
   attributes most of that departure to the rebreathing circuit - removing it
   takes sevoflurane to -0.15 SD and isoflurane to +0.66 SD. Wall absorption
   is a *further* circuit-side agent store that returns agent through the
   washout, so adding it pushes both rows further above their means rather
   than toward them. That is this brief's own directional argument for
   desflurane, pointed at the two agents the mechanism is strongest for. And
   the published cohorts breathed a non-rebreathing apparatus with the potent
   agents' inspired fraction zero by construction, so no circle-system wall
   effect is in the published number to begin with.

The general form is now recorded in `docs/MODEL.md` because it will recur: a
mechanism belonging to this model's circle system cannot explain a
disagreement with a measurement made without one. It can only be a statement
about what the simulator shows a learner.

**Two stale cross-references in the same section were repaired with it**, both
left by `#536`'s end-tidal strike: the closing paragraph named `PL-ZDWL` as
still reading a ventilation value the section already records as unpublished,
and named `PL-03ZG` as bounding a live candidate when it is `dropped` and the
candidate struck. The section said "One candidate remains" and then named two.

**No test.** The model has no wall term, so there is nothing to regress, and
the item's own `verify:` is documentation-only. The one test worth having -
pinning the direction, that a larger circuit-side agent store can only slow
the alveolar washout - would need a circuit-volume override on
`_private_washed_in_system`, whose docstring states that its single parameter
override exists for one named test and that every other caller leaves it
`None`. Widening a shared fixture against its own stated design is a decision
rather than a fix, so it is captured as `PL-P1P6` instead.
