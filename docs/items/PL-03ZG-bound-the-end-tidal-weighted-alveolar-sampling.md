---
id: PL-03ZG
title: Bound the end-tidal-weighted alveolar sampling bias, which is the last open candidate for desflurane's washout residual
status: untriaged
feature: model-spec-accuracy
added: 2026-09-13
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
