---
id: PL-XWCY
title: Circuit-component absorption is ruled out as a cause of desflurane's residual by the one paper that measured it, and is a live candidate for the other two agents
priority: P1
effort: M
status: ready
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-09-13
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
