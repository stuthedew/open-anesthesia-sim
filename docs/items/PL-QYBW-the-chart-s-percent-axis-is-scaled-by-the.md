---
id: PL-QYBW
title: The chart's percent axis is scaled by the alveolar peak, so the slow compartments are compressed into 1-2 px and two runs' fat curves cannot be told apart by pointing
priority: P2
effort: M
status: needs-decision
classes: ux, defect
feature: compartment-trace-legibility
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md, tests/unit/test_chart_frame.py, tests/integration/test_qt_chart.py
added: 2026-09-19
payoff: makes the slow compartments this simulator exists to teach visible on the chart that teaches them, instead of a flat line under 2 px
---

**Problem.** The chart's percent axis is scaled by the alveolar peak, so the slow compartments are compressed into 1-2 px and two runs' fat curves cannot be told apart by pointing

**Corrected 2026-09-23: the axis is not scaled by the alveolar peak.** The
title and the line above say it is, and it was not when this was filed. Since
`PL-CC23` (2026-09-04), `chart_axis_top_percent` in
`src/anesthesia_sim/app/formatting.py` tops the axis at `CHART_AXIS_TOP_MAC`, three times the running agent's 1 MAC, fixed
for the whole session and blind to every trace. The 6.00% measured below is
3 x sevoflurane's 2.00%, and at 1 MAC the alveolar trace reaches a third of the
way up. The compression and both consequences stand. What changes is the option
space: the ceiling is a decided ruler, not a fitted one, with two properties an
answer keeps or knowingly reopens. It is one ruler for every agent, which
`PL-CC23` bought because a dial-maximum ceiling had drawn the agents at scales
up to 1.39x apart; and it is fixed rather than fitted, for the reason the
constant's comment carries over from the `docs/MODEL.md` paragraph that opens
"Why the axis is fixed rather than fitted". The title is left as filed because
`ROADMAP.md`'s two frozen lists quote it.

**Found 2026-09-19 while measuring `PL-JVHL`** (the hover answering for
whichever run is marginally nearer). That item is the symptom; this is the
mechanism underneath it.

`chart_axis_top_percent` tops the percent axis at a fixed 3 MAC -
`axis_top_percent` came out 6.00% on every case measured, against a fat
trace whose whole excursion is under 0.04%. At `theme.CHART_HEIGHT` (360 px)
that is 0.0167 %/px, so the six compartments the chart draws are not equally
readable: alveolar spans ~90 px and fat spans **under 2 px**.

**Measured 2026-09-19**, branched sevoflurane case, trunk held at 1 MAC,
fork at 10 min, the two runs' fat curves:

| Instant | Trunk | Branch (vaporizer off) | Apart on screen |
| ---: | ---: | ---: | ---: |
| 1200 s | 0.0086% | 0.0056% | 0.18 px |
| 2400 s | 0.0197% | 0.0062% | 0.81 px |
| 3492 s | 0.0300% | 0.0063% | 1.42 px |

**Why it matters.** Two consequences, and the second is the one that makes
this more than a legibility complaint:

1. **The compartments this chart exists to teach are the ones it draws
   least.** Fat and muscle are where the interesting behaviour of an inhaled
   agent lives - the slow filling that makes a long case different from a
   short one - and they are rendered as a flat line on the axis.
2. **Two runs' slow-compartment curves cannot be told apart by pointing.**
   At 0.2-1.4 px apart, no hover targeting rule can let a reader aim at one
   rather than the other, which is why `PL-JVHL`'s two candidate mechanisms
   both measured identically to the behaviour they were meant to replace.

**Not obviously a defect, which is why this is a captured finding rather than
a fix.** A shared axis is what makes the compartments comparable to each
other, and that comparison - alveolar above mixed venous above muscle above
fat - is a real teaching point that a per-compartment scale would destroy.
Any answer here has to keep it: a second axis for the slow compartments, a
log or split scale, or a separate detail view are all options with different
costs, and choosing between them is a design round rather than an edit.

**Scope.** Decide whether the chart keeps one percent axis; if not, what
replaces it and what the reader is told about the change of scale, which
`CLAUDE.md`'s safety-critical standard reaches directly - a curve whose scale
differs from its neighbour's and does not say so is a misleading visual
encoding.

**Decision needed.** Whether the chart keeps one shared percent axis for all
six compartments, and if it does not, what replaces it and what the reader is
told about the change of scale. The options carry different costs and none is
free:

1. **Keep the shared axis.** The comparison it buys - alveolar above mixed
   venous above muscle above fat, all on one scale - is a real teaching point
   and the ordering is itself the lesson. Cost: fat stays within a few pixels
   of zero for the first hours, so its slow filling, and the difference
   between two runs' fat, cannot be seen on this chart. (As filed this said
   fat *and muscle* stay under 2 px, and that `PL-0RZ0` could not be fixed.
   Both are corrected by the design round below: muscle is legible from about
   twenty minutes, and `PL-0RZ0` closed by making every compartment in reach
   answer rather than by separating the traces.)
2. **A second axis for the slow compartments.** Recovers the detail. Cost: two
   curves on one plot at different scales is the misleading visual encoding
   `CLAUDE.md`'s safety-critical standard names, unless the change of scale is
   unmissable - so this option is only as good as its labelling, and the
   labelling is the hard part rather than the axis.
3. **A log or split scale.** One axis, all six legible. Cost: a log axis
   changes what "twice as much" looks like, which is the comparison a learner
   is being taught to make by eye; and a split scale has option 2's labelling
   problem with a discontinuity added.
4. **A separate detail view** for the slow compartments. Keeps the main chart
   honest and unchanged. Cost: the comparison across compartments moves to the
   reader's memory between two views, which is the thing option 1 exists to
   avoid, and it is the largest build of the four.
5. **Show what the slow compartments hold, beside what they read** (added
   2026-09-23). Options 1-4 each re-scale one quantity, partial pressure. But
   fat's trace near zero an hour in is its true partial pressure: its capacity
   is large and its blood supply small, so it fills slowly while it goes on
   taking agent up. Eger and Saidman teach uptake by drawing each tissue
   depot's capacity, set by its volume and solubility, as an area (Eger EI II,
   Saidman LJ. Illustrations of inhaled anesthetic uptake, including
   intertissue diffusion to and from fat. *Anesth Analg*
   2005;100(4):1020-1033, https://doi.org/10.1213/01.ANE.0000146961.70058.A1,
   reached through PubMed, PMID 15781517). A tissue compartment's partial
   pressure is already its `agent_amount_l` over its `capacity_l`
   (`src/anesthesia_sim/core/tissue.py`), so an amount view needs no new model state, and it is
   one shared axis on which fat is large rather than small. Cost: a second
   quantity needs its own unit and label and must never be read as a partial
   pressure, which is what drives effect; its unit is `PL-B396`'s open
   question (litres of vapour against liquid millilitres); and where it is
   drawn is a layout decision in its own right.

**Design round, 2026-09-23: what was measured, and what it changes.** Current
tree, reference adult, vaporizer dial held at 1 MAC, 0.1 s steps, the 360 px
plot under `CHART_AXIS_TOP_MAC` = 3. Height above zero of each trace, and fat's
share of the stored agent (from each compartment's `agent_amount_l`):

| Agent | 30 min: muscle / fat | 60 min | 180 min | Fat's share of stored agent, 30 / 60 / 180 min |
| --- | --- | --- | --- | --- |
| Sevoflurane | 14.9 / 0.9 px | 29.9 / 1.9 px | 69.9 / 6.4 px | 14% / 20% / 30% |
| Isoflurane | 12.0 / 0.6 px | 24.8 / 1.5 px | 60.2 / 5.1 px | 16% / 21% / 32% |
| Desflurane | 25.9 / 1.7 px | 48.4 / 3.7 px | 93.7 / 11.7 px | 13% / 20% / 33% |

The branched case re-measured (trunk at 1 MAC, branch's vaporizer off at
10 min), trunk against branch: fat 0.0088% / 0.0053% at 20 min, 0.0311% /
0.0059% at 58 min, 0.21 px and 1.51 px apart; muscle 3.8 px apart at 20 min,
24.3 px at 58 min. That is within a few percent of the 2026-09-19 table above.

Five findings follow, and together they narrow the question:

1. **Only fat is compressed.** Muscle is legible from about twenty minutes on
   every agent. `ROADMAP.md` v0.4.0's teaching goal, the reservoirs behind
   context-sensitive emergence with "the muscle and fat curves visibly
   diverging from the alveolar one", is carried by muscle on today's axis.
   Fat's line near zero is its true partial pressure, and the lag it shows is
   the lesson.
2. **The pointing half is already answered.** `PL-JVHL` and `PL-0RZ0` made
   every run and every compartment inside the hover radius answer under its
   own name, so both runs' fat values are read even 0.2 px apart. What
   remains is only that the drawing cannot show the difference.
3. **What the flat line hides is how much fat holds, and that is planned item
   27's lesson.** Item 27 (Gas Man's "Picture", compartments drawn to their
   capacity) exists to teach it, so option 5 is item 27. Its stated rationale
   is wrong in one clause, though: in this model fat overtakes muscle only at
   4.7-7.5 h and all other compartments combined at 7.0-9.5 h. `PL-H5DV` holds
   the correction.
4. **Options 4 and 5 are new display surfaces.** The standing rule in
   `ROADMAP.md` (planned item 34, project owner 2026-09-17, ratified) holds
   every new surface until the View contract (`PL-TH35`) and view registry
   (`PL-R1WQ`) ship. A surface wanted before then is filed against item 36's
   catalogue, not built.
5. **Option 3, measured.** A fixed log axis from 0.001 to 3 MAC (3.48 decades,
   104 px a decade) puts the two runs' fat curves 23 px apart at 20 min and
   75 px apart at 58 min, so it would work. The cost is that it has to draw
   below the 0.01-point resolution the readouts claim (§ "Displayed precision"
   in `docs/MODEL.md`). Floored at that resolution instead (0.005 MAC for
   sevoflurane), the branch's fat stays below the floor for the whole case.
   Offered as a reader's choice beside the linear axis, it is a display mode on
   a chart of clinical values. v0.6.0's View contract (`PL-TH35`) is about to
   decide where a View's own settings live, so a mode built now would be built
   twice.

**Recommendation (session, 2026-09-23 - not yet the project owner's
decision): option 1. Keep the one shared linear axis, and record why.** It is
the truthful drawing of the quantity that drives effect. It keeps every
property `PL-CC23` and the fixed-axis argument bought. Its one real cost, fat's
invisible filling, is a question about amount, which planned item 27 exists to
answer. The option most worth having instead is 3, as a reader-selected log
scale. It is the only option that keeps one shared axis, the compartments'
order and a fixed ruler while separating fat. But it should be built only after
`PL-TH35`, and only for a named lesson that needs a partial pressure's
*shape* rather than an amount or a value. `ROADMAP.md` names none today. The
strongest candidate is not fat itself but the washout tail. Bailey found that
"the major differences in the rates at which desflurane, sevoflurane,
isoflurane, and enflurane are eliminated occur in the final 20% of the
elimination process". From a 1 MAC case, that final 20% lies in roughly the
bottom 20 px of today's axis. Carpenter et al. found that "slowly
equilibrating compartments could only be identified during washout". Those
two point at a semilog washout View for item 36's catalogue, not at a mode on
this chart.
Options 2 and 4 are not recommended: 2 is the misleading two-scale encoding
this item already names, and 4 is a new surface that item 36's catalogue can
take if it is ever wanted.

**Sources the recommendation rests on, and how deeply each was read.** Three
were retrieved from PubMed by this session and verified against their
abstracts on 2026-09-23: Eger and Saidman, Leeson et al., and Romano et al.
This session's research agent read four more from their abstracts, through
PubMed or Crossref: Bailey, Carpenter et al., Menge et al. and Isenberg et al.
Cockburn et al. comes from the authors' preprint. No full text was read.
- Eger EI II, Saidman LJ. *Anesth Analg* 2005;100(4):1020-1033,
  https://doi.org/10.1213/01.ANE.0000146961.70058.A1 - "Capacity to hold (take
  up) anesthetic is depicted by areas representing specific tissues"; "the
  increased anesthetic in fat occurs at a lower partial pressure and thus might
  not influence emergence materially". Capacity is the established teaching
  encoding for fat, which is item 27.
- Leeson S, Roberson RS, Philip JH. *Anesth Analg* 2014;119(4):829-835,
  https://doi.org/10.1213/ANE.0000000000000384 - a Gas Man simulation study,
  so the reference implementation's behaviour rather than a measurement: "Fat
  levels of anesthetic remained less than 0.15 MAC for all drugs up to the 6
  hours tested"; "muscle is a source of anesthetic and predisposes to
  reanesthetization while fat is a sink for anesthetic and fosters continued
  emergence". The emergence lesson runs through muscle, which today's axis
  draws.
- Bailey JM. *Anesth Analg* 1997;85(3):681-6,
  https://doi.org/10.1097/00000539-199709000-00036 (PMID 9296431); and Carpenter
  RL et al. *Anesth Analg* 1986;65(6):575-82,
  https://doi.org/10.1213/00000539-198606000-00004 (PMID 3706798). Both are
  quoted above; they are the case for a washout View.
- Romano A, Sotis C, Dominioni G, Guidi S. *Health Econ* 2020;29(11):1482-94,
  https://doi.org/10.1002/hec.4143 - a randomised study of the general public:
  deaths shown on a log scale gave "a less accurate understanding" than a
  linear one, and the authors recommend linear "at least as a default option".
  Menge DNL et al. (*Nat Ecol Evol* 2018;2(9):1393-1402,
  https://doi.org/10.1038/s41559-018-0610-7) found 93% correct readings on
  linear axes against 56% on log-log, among ecologists. Neither population is
  residents, who are taught semilog plots in pharmacokinetics. Both are
  reasons for linear as the default, not against a log option.
- Isenberg P, Bezerianos A, Dragicevic P, Fekete JD. *IEEE Trans Vis Comput
  Graph* 2011;17(12):2469-78, https://doi.org/10.1109/TVCG.2011.160 -
  "superimposed charts in which focus and context overlap on top of each other
  should be avoided". This is the case against option 2; reading option 2 as
  their "superimposed" chart is this session's inference.
- Cockburn A, Karlson A, Bederson BB. *ACM Comput Surv* 2009;41(1),
  https://doi.org/10.1145/1456650.1456652 - overview+detail costs "additional
  use of screen real estate" and "the mental effort and time required to
  integrate the distinct views". This is option 4's cost.

Not verified, so not relied on: whether Gas Man's graph offers a logarithmic
or reader-set vertical scale, and whether its Picture draws compartments to
capacity (item 27 asserts the second). gasmanweb.com was refused at the proxy;
the private reference corpus's *Workbook for Gas Man* would answer both.

**If option 1 is chosen**, the closing work is small. Record the decision and
its reasons in `docs/MODEL.md` § "Where more than one trace answers", whose
"The root cause is elsewhere and is not fixed here" paragraph still describes
this as open. Point item 27 at it. Close this item.

**This is the project owner's** rather than a session's: it changes what a
learner sees, and every option is defensible, which is the test rule 14 of
`.claude/rules/instruction-writing.md` sets. What is *not* theirs, and should be
in hand before they are asked, is the measurement `PL-0RZ0` owed - how much of
the chart's hoverable area has two compartments inside one hover radius - since
it sizes the cost of option 1. It is in hand: `PL-0RZ0` closed on it
2026-09-20, with two or more compartments in reach over 37.0% of the one-run
chart and 12.7% of 2 px moves there changing which one answers.

**Done when.** The roadmap or this item records which axis treatment the chart
takes and what the reader is told about it, and either the chart implements it
or the decision is recorded with the reason the shared axis stays.
