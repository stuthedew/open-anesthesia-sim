---
id: PL-03ZG
title: Bound the end-tidal-weighted alveolar sampling bias, which is the last open candidate for desflurane's washout residual
priority: P1
effort: M
status: dropped
classes: science
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-13
closed: 2026-09-13
reason: the hypothesis it was written to bound is struck, on the project owner's decision of 2026-09-13 - Carpenter & Eger 1989 (PMID 2930000), the one primary human measurement of the alveolar-to-arterial gradient it rests on, has the difference larger for MORE soluble agents (P_A/P_a 1.23 for halothane against 1.11 for isoflurane, P = .009) where the hypothesis needs it to grow as solubility falls, and attributes it to physiologic dead space contamination whose sign follows F_I, making it negative through an elimination run at F_I = 0. Both push the published F_A/F_A0 down, so the mechanism deepens desflurane's residual instead of explaining it. Computing the log-normal V/Q bound this item proposed would answer a question the measurement has already answered differently. docs/MODEL.md carries the exclusion under "Desflurane's residual, and why the parameter file was not changed"
---

**Problem.** Bound the end-tidal-weighted alveolar sampling bias, which is the last open candidate for desflurane's washout residual

**Where this came from.** It is candidate 1 of `docs/MODEL.md`
§ "Desflurane's residual, and why the parameter file was not changed", and the
only one of the two open candidates this project can act on. `PL-RFLN` closed
having ruled out the apparatus's dead space and left this standing.

**What is already settled, so it is not re-derived.** The obstacle was that
the flow-weighted alveolar reading of the ventilation-perfusion calculation
moves every agent the wrong way, so the hypothesis rested entirely on which
weighting the published `F_A` came from. The methods sections settle it:
Yasuda 1991 *Anesthesiology* sites the end-tidal port **at the tracheal tube**,
with about 50 ml of corrugated Teflon between it and the nonrebreathing valve
to protect the sample from inspired gas, and samples mixed expired gas
**separately** from a 1-l aluminium mixing chamber, reporting it as `F_M`. So
the reading the fifth row of the candidate table rules out is `F_M`, not the
`F_A` the published ratio is built from. The hypothesis is unblocked and
undemonstrated.

**What is missing.** The **end-tidal-weighted** bias, computed instead of the
flow-weighted one, and a bound on how much of desflurane's 2.33 published SD
it could carry. The mechanism: in a lung with ventilation-perfusion
dispersion, a unit at ratio `r` sits at
`P_A/P_v_bar = lambda_b:g / (lambda_b:g + r)` through an elimination, so the
last units to empty carry the highest partial pressure during washout and the
lowest during wash-in, biasing a ratio of the two upward at both ends by an
amount that grows as solubility falls. On a log-normal perfusion distribution
at log SD 1.0 with a 5% shunt, the arterial retention this model fixes at
`lambda_b:g / (lambda_b:g + V_A/Q)` is understated by 44% for desflurane, 30%
for sevoflurane and 15% for isoflurane - the rank order the residuals have.

**Why it matters.** `docs/MODEL.md` currently records two open candidates and
says neither is demonstrated. This is the half that is reachable; the other is
the published value itself, which nothing this project can run will settle.
Bounding this one either names the cause or establishes that the residual
exceeds what end-tidal weighting could carry, and both are closes.

**Route.** A test-only multi-alveolar-compartment diagnostic, parallel to
`_eliminate_without_rebreathing()` in
`tests/reference/test_published_wash_in_and_elimination.py`: a log-normal
ventilation-perfusion distribution, each unit run through the same equations,
and the **last-emptying** unit's fraction read as `F_A` rather than the
flow-weighted mixture. It bounds the size; it does not demonstrate that the
mechanism is the cause.

**Watch the scope.** This is a diagnostic, not a model change. Nothing here
proposes giving the shipped simulator a dispersed lung - `docs/MODEL.md`
specifies one perfectly mixed alveolar compartment with `F_a == F_A`, and
changing that is a milestone-sized decision the roadmap has not reached.

## The dispersion the existing figures were computed at is broader than measured normals (2026-09-13)

`docs/MODEL.md`'s candidate 1 quotes its retention understatement - 44% for
desflurane, 30% for sevoflurane, 15% for isoflurane - from "a log-normal
perfusion distribution at log SD 1.0 with a 5% shunt". Checked against the
primary source for what normal human V/Q dispersion actually is, and **log SD
1.0 is above even the older cohort's measured value**, so those percentages are
an upper bound rather than a typical figure:

> Wagner PD, Laravuso RB, Uhl RR, West JB. *Continuous distributions of
> ventilation-perfusion ratios in normal subjects breathing air and 100 per
> cent O2.* J Clin Invest 1974;54(1):54-68. PMID 4601004,
> DOI [10.1172/JCI107750](https://doi.org/10.1172/JCI107750).

Twelve normal subjects by the multiple inert gas elimination technique. Four
young semirecumbent subjects (21-24 y) gave mean log SD of **0.43 for blood
flow and 0.35 for ventilation**, with no intrapulmonary shunt breathing air;
five older subjects (39-60 y) gave **0.76 and 0.44**, again no shunt on air,
developing a mean 3.2% shunt only on 100% oxygen. Read from the abstract and
checked against PubMed 2026-09-13.

The method's own theory paper, which is the reference for the retention
framework this item's bound is built on:

> Wagner PD, Saltzman HA, West JB. *Measurement of continuous distributions of
> ventilation-perfusion ratios: theory.* J Appl Physiol 1974;36(5):588-99.
> PMID 4826323,
> DOI [10.1152/jappl.1974.36.5.588](https://doi.org/10.1152/jappl.1974.36.5.588).

**What this changes for the work.** The bound should be computed across the
measured range rather than at one assumed dispersion - 0.35 to 0.76 log SD is
what normal anaesthetized-age adults actually show, and Yasuda's volunteers sit
inside it. If the end-tidal-weighted bias at log SD 0.76 already fails to carry
2.33 SD, the candidate is closed without needing an argument about which
dispersion to assume. Running it only at 1.0, as the existing figures do, risks
the opposite error: reporting a bias large enough to matter at a dispersion
broader than the subjects had.

**Do not read this as correcting the fifth candidate row.** That row rejected
the *flow-weighted* reading, and its rejection does not depend on the
dispersion - it moves every agent the wrong way at any width. What is bounded
here is the end-tidal-weighted reading, which is the one still open.

## A measured human anchor for this candidate, found 2026-09-13 in Yasuda's own discussion

Reading the *Anesthesiology* paper for `PL-ZDWL` turned up the authors flagging
this item's mechanism themselves, at page 497:

> "The data may be suspect in that there is an underlying assumption that the
> FA accurately indicates the anesthetic partial pressures in arterial blood.
> Although there appears to be a good correlation between the two, gradients
> exist. These will be larger during periods of considerable change in
> concentration (i.e., during the periods of initial administration and
> elimination) and thus may confound our ability to accurately predict volumes
> and time constants for the lungs and the VRG."

That is candidate 1 stated by the people who produced the measurement, and
their citation for it is a human study by the same group:

> Carpenter RL, Eger EI II. *Alveolar-to-arterial-to-venous anesthetic partial
> pressure differences in humans.* Anesthesiology 1989;70(4):630-5.
> PMID 2930000,
> DOI [10.1097/00000542-198904000-00014](https://doi.org/10.1097/00000542-198904000-00014).

Retrieved from PubMed and verified against the abstract 2026-09-13; not held in
the corpus.

**Why it matters more than the modelled bound this item was written around.**
The abstract reports two things this item currently has no measurement for.
First, a **size**: "The difference between PA and Pa was approximately 20% of
the difference between inspired gas (PI) and Pa", in eight surgical patients
given isoflurane or halothane. Second, and more useful, a **cause**: "The
differences between PA and Pa appear to be due primarily to **contamination of
alveolar gas by physiologic dead space gas**" - not ventilation-perfusion
dispersion as such.

That reframes the work. This item's brief builds its bound from a log-normal
V/Q distribution; the primary measurement attributes the gradient chiefly to
dead-space dilution of the sampled alveolar gas, which is a different mechanism
with a different dependence on solubility and a different sign through an
elimination, where the diluting gas is agent-free. **Compute the bound against
what was measured rather than only against the assumed distribution**, and say
which of the two the model's `F_a == F_A` actually violates.

**One caution before this is treated as settling anything.** `PL-RFLN`
established that Yasuda interposed about 50 ml of apparatus dead space at the
tracheal port expressly "to protect the end-tidal sample from contamination
with inspired gas", so the published protocol was guarding against exactly
Carpenter's mechanism. Whether that guard works, and what it leaves, is the
question - not whether the mechanism exists.

**Route.** Carpenter 1989 is not in the corpus and PubMed carries an abstract
but no PubMed Central record, so the methods and the gradient's direction
through elimination need the full text - a request to the project owner, per
`.claude/rules/citing-sources.md`.

## Carpenter & Eger read at the source 2026-09-13, and it points this candidate the other way

The project owner supplied it the same day; it is now corpus holding
`carpenter-eger-1989-alveolar-to-arterial-to-venous-anesthetic-partial-pressure-differences-in-humans.pdf`.
**Read at full text as page images** - a scan with no text layer. Eight surgical
patients, isoflurane (n = 4) or halothane (n = 4), mechanically ventilated via a
nonrebreathing circuit, with arterial, venous, end-tidal and inspired samples
taken simultaneously; end-tidal through a catheter tipped near the tracheal end
of the endotracheal tube.

**Two measured results, and each contradicts a different half of this item's
brief.**

**1. The solubility dependence runs the opposite way.** This item's brief, and
`docs/MODEL.md` candidate 1, say the bias grows *as solubility falls* - and
quote 44% for desflurane against 15% for isoflurane as "the rank order the
residuals have". Carpenter and Eger measured the reverse, and state it as a
prediction their data confirm (p. 634): end-tidal-to-arterial differences
"should be greater with anesthetics having higher blood solubility. Indeed,
`P_A - P_a` differences were greater for halothane than for isoflurane."
Measured `P_A/P_a`: **halothane 1.23 +/- 0.13 against isoflurane 1.11 +/- 0.09,
P = .009** (p. 632). Desflurane is the least soluble agent in the comparison, so
on the measured relation it should show the *smallest* gradient, not the
largest.

**2. Through an elimination the bias is downward, not upward.** The mechanism
they establish is contamination of the end-tidal sample with **physiologic dead
space gas, which is unchanged inspired gas** (p. 634), and the regression across
combined data is

    (P_A - P_a) = 0.22 (P_I - P_a) + 0.02        (p. 632)

whose slope they read as end-tidal samples being "contaminated by approximately
20% physiologic dead space gas" - agreeing with Eger and Bahlman's earlier
80%/20% estimate, their reference 3. **The sign therefore follows `P_I`.** During
administration `P_I > P_A`, the contaminant is richer than alveolar gas and the
sample reads high, which is what they measured. Through an elimination on a
non-rebreathing circuit `P_I = 0`, the contaminant is agent-free, and the sample
reads **low**.

**What that does to the published ratio, worked through.** `F_A0` is measured at
the end of the 30-minute administration, where the bias is upward; the 5-minute
value is measured into a fresh circuit at `F_I = 0`, where it is downward. Both
push `F_A/F_A0` **down**. Taking the 80/20 split at desflurane's own numbers -
`F_I` = 2.0%, `F_A/F_I` = 0.90 at 30 min, so true alveolar ~1.80%:

    F_A0 measured = 0.80(1.80) + 0.20(2.00) = 1.84
    F_A  measured = 0.80 x F_A true          (F_I = 0)
    published ratio / true arterial ratio = 0.80 x 1.80 / 1.84 = 0.78

So the published 0.14 would correspond to a true arterial ratio near **0.18**,
and this model's 0.0935 would sit further from it than the -2.33 SD already
recorded, not closer. **Candidate 1 does not explain the residual on this
evidence; it deepens it.**

**Three caveats, and the first is the one that could overturn this.**

1. **The regression was never measured at `P_I = 0`.** Figure 4's abscissa spans
   `P_I - P_a` of about 0.10 to 0.70% atm, all positive - administration and
   maintenance. Extrapolating to the elimination limb is an extrapolation of the
   *mechanism* (dead space gas is unchanged inspired gas, so at `F_I` = 0 it
   dilutes) rather than of the fitted line. Sound, but not measured.
2. **Yasuda's apparatus guarded against part of this.** The ~50 ml of Teflon at
   the tracheal port was interposed expressly "to protect the end-tidal sample
   from contamination with inspired gas" (`PL-RFLN`). That guards the *apparatus*
   path; Carpenter's 20% is **physiologic** dead space, inside the patient, which
   no external dead space can remove. So the guard does not answer this.
3. **Different populations.** Carpenter studied surgical patients aged 52 +/- 16
   with isoflurane and halothane; Yasuda studied volunteers aged 25 +/- 5 with
   desflurane, isoflurane and halothane. Physiologic dead space differs with age.

**What this item should now do**, which is not what its brief says. The
V/Q-dispersion bound is no longer the first thing to compute. The first thing is
to decide whether candidate 1 survives at all, because the one primary human
measurement of the quantity it rests on has the wrong sign through elimination
and the wrong solubility dependence. Computing a log-normal V/Q bound would be
answering a question the measurement has already answered differently.

`docs/MODEL.md` now records that, without deleting the hypothesis - whether
candidate 1 is struck is the project owner's call and is in the reply that
found this.

## Struck, and this item dropped with it (project owner, 2026-09-13)

The owner agreed the recommendation the same session. `docs/MODEL.md` moves
end-tidal sampling out of the live candidate list into an eighth row of the
excluded table and an account below it carrying what was proposed, what the
methods sections unblocked, and what Carpenter & Eger struck it on. One
candidate remains - the published value - and nothing this project runs can
settle it.

**What is deliberately kept rather than deleted**, because a reader meeting the
eighth row is owed why: the V/Q mechanism and its 44/30/15% rank order, the
methods finding that the published `F_A` is a tracheal end-tidal sample and the
fifth row therefore excludes `F_M` rather than `F_A`, and the two things that
would reopen it - Carpenter's regression never being fitted at `F_I` = 0, and
his patients being 52 +/- 16 years old against Yasuda's 25 +/- 5. Reopening
needs both to resolve in the hypothesis's favour **and** the measured solubility
ordering to reverse.

**One consequence recorded in the specification.** If the sampling bias is real
and signed as measured, the published 0.140 is low - so every statement that
this model washes desflurane out too fast is conservative rather than
optimistic.
