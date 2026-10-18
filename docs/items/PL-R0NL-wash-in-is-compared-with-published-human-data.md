---
id: PL-R0NL
title: Wash-in is compared with published human data at one instant, 30 minutes, so the first 15 minutes of the F_A/F_I rise, the phase the simulator most displays, are compared against nothing published and a doubled FRC that moves F_A/F_I at 1 min by -0.118 passes every gate
priority: P1
effort: L
status: done
classes: science, test
feature: validation-resolving-power
milestone: v0.5.26
touches: tests/reference/test_published_wash_in_and_elimination.py, docs/references, docs/MODEL.md
added: 2026-10-17
closed: 2026-10-18
pr: 1526
payoff: the first minutes of the wash-in curve, the phase the simulator shows most, are checked against published human data rather than against nothing
verify: grep -q 'def test_early_wash_in_matches_published_human_measurement' tests/reference/test_published_wash_in_and_elimination.py
---

**Problem.** Wash-in is compared with published human data at one instant, 30 minutes, so the first 15 minutes of the F_A/F_I rise, the phase the simulator most displays, are compared against nothing published and a doubled FRC that moves F_A/F_I at 1 min by -0.118 passes every gate

**Severity: high for validation coverage; nothing displayed is known to be
wrong.** Audit finding CMP-3, confirmed by the adversarial verifier.

**Evidence.** The only comparison of wash-in with published human data is
`test_thirty_minute_ratio_matches_published_human_measurement` in
`tests/reference/test_published_wash_in_and_elimination.py`. Through
`_wash_in_ratio`, it samples F_A/F_I once, at `WASH_IN_DURATION_S = 1800.0`.
The other reference modules compare elimination or self-consistency, not
early wash-in against published data.

A probe drove the validation protocol (FGF 10 L/min, 1% dial) on the module's
own configured system:

| Change | F_A/F_I at 1 min | at 5 min | at 30 min |
| --- | --- | --- | --- |
| Sevoflurane, alveolar gas volume (FRC) x2 | 0.443 to 0.325 (-0.118) | -0.033 | -0.0016 (-0.087 published SD) |
| Desflurane, FRC x2 | -0.145 | | -0.12 SD |
| Vessel-rich volume x0.5 | | +0.058 | +0.12 SD |
| FRC x1.1 (default operating point) | -0.0143 | | -0.0001 |
| Circuit volume x1.1 (default operating point) | -0.0047 | | -0.00005 |

So the one gated time point barely registers FRC or circuit volume.
`docs/MODEL.md` says so itself: the lineage "is worth least in the phase
the simulator most displays, the first minutes of the F_A/F_I rise".
`docs/references/README.md` records that only the 30-minute and 5-minute
ratios and the fits were taken from the papers, that the washout figures were
read only qualitatively, and that the wash-in apparatus methods were not read
in any pass. That the Yasuda figures carry an early time course that can be
extracted is inferred, not verified.

One nuance from the verifier: a parameter changed in the code still trips the
pins (an alveolar volume moved from 2.5 to 2.8 L fails
`test_control_resolution`). "Passes every gate" holds for an error that is
already in the shipped parameter set, which is how this finding is scoped.

**Why it matters.** A model or provenance error that makes the induction curve
wrong by 25-30% at 1-2 minutes would pass every gate. FRC, circuit mixing and
vessel-rich capacity are the likely sources. The 30-minute ratio moves by an
order of magnitude less than the published spread for such errors. The early
rise is the curve a learner watches most.

**Where.** `tests/reference/test_published_wash_in_and_elimination.py`
(`_wash_in_ratio`, `test_thirty_minute_ratio_matches_published_human_measurement`,
`WASH_IN_DURATION_S`); `docs/references/`; `docs/MODEL.md`.

**Measured by `PL-9YHR`, 2026-10-17: a doubled FRC does not pass every
gate for every agent.** The table above is at the default 10 L/min. The flow
sweep's 1 L/min point fails sevoflurane at alveolar gas volume x2 (-1.07 SD)
and desflurane (-1.06 SD), and isoflurane passes (-0.56 SD). The gate's last
passing factor upward is x1.82, x3.91 and x1.92, and downward the gate passes
sevoflurane and isoflurane at a tenth of the stored volume. `docs/MODEL.md`
§ "What the published-data gate can and cannot resolve" has the full table.
So the finding still holds for isoflurane, and for every agent the 30-minute
ratio at the default flow barely registers FRC.

**Recommended work.** Extract the Yasuda 1991 F_A/F_I time course from the
private reference corpus into `docs/references/`, for example at 1, 2, 3, 5,
10, 15, 20 and 25 min, as mean ± SD with page and figure locators. Add a test
that drives the published protocol with the inspired fraction held at the
airway. That needs an F_I-clamp driver like the existing open-circuit one,
since the shipped circuit lags by its time constant. Assert each time point
within the published SD. Where the model disagrees, assert a stated
regression band, as the elimination half does. Write down what a
disagreement in the early phase would mean before running the comparison.

**Done when.** Early wash-in time points, at least 1 to 5 minutes, are
compared against published values with locators, or this item records that
no published early time course exists to compare against.

**Related.** `PL-Z3V5` (ready) decides the format of an extraction note, which
the extracted time course would use. `PL-4QCJ` is the extraction note for the
Yasuda methods reading, from the same papers. `PL-9YHR` is the same feature,
for the stored parameters.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

## What the papers hold, 2026-10-18

An early time course exists in both papers, as a figure and not as a table.
Figure 2 of Yasuda et al., *Anesth Analg* 1991;72:316-24 (printed page 320),
plots F_A/F_I as mean ± SD for the sevoflurane and isoflurane cohort (n = 7).
Figure 2 of Yasuda et al., *Anesthesiology* 1991;74:489-98 (printed page 493),
plots the same for the desflurane and isoflurane cohort (n = 8). Each SD is
drawn as a one-sided bar. Both papers sampled end-tidal gas at the tracheal tube
at 0.75, 1, 1.5, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25 and 29 minutes, and gave the
agents as a square wave from a non-rebreathing circuit (*Anesth Analg* page
317). So the inspired fraction was held at the airway from the first breath.
The *Anesth Analg* figure also plots desflurane, but normalized to that study's
isoflurane, so the desflurane values here come from the *Anesthesiology* figure.

Both figures survive only as 300 dpi bilevel scans of the printed page. The
values are read from the page image by fitting the axis lines and tick marks
and locating each marker's centre. The scan is sheared by up to 0.8 degrees,
so each point is read along lines parallel to the plotted axes. Read this way,
each 30-minute mean lands within 0.006 of the value the paper's text states.

## Pre-registration, written 2026-10-18 before the model was compared

The comparison drives the shipped patient with the inspired fraction held at the
airway, as the papers' non-rebreathing circuit held it. It reads F_A/F_I at each
sample time from 1 to 25 minutes and compares it with the figure's mean, in units
of the figure's SD. The 30-minute value is already compared in
`test_thirty_minute_ratio_matches_published_human_measurement`.

What a disagreement would mean:

1. **Every point within 1 SD.** The early rise is consistent with the published
   cohorts at the resolution of the figure. The test asserts the 1 SD band, as
   the 30-minute comparison does, and the item closes.
2. **The model rises too fast in the first 3 minutes and agrees by 30.** The
   first minutes are set mostly by alveolar ventilation over the lung's gas
   volume, and the papers measured minute ventilation while the model uses the
   reference patient's default. So the first candidates are a model ventilation
   higher than the cohort's, or a functional residual capacity smaller than the
   cohort's. A structural error in the lung compartment comes after those.
3. **The model rises too slowly in the first 3 minutes.** The candidates are
   uptake into blood that is too large: a blood:gas coefficient or cardiac
   output above the cohort's, or a vessel-rich capacity that is too large.
4. **A disagreement only at 1 minute.** The first minute is the steepest part
   of the curve, so it is the most sensitive to when each sample was taken and
   to the airway dead space. It says little about the model unless 2 and 3
   minutes disagree too.
5. **A disagreement at 5 to 25 minutes with agreement at 30.** This would point
   at the vessel-rich and muscle groups, whose filling sets that phase.

In cases 2 to 5 the test asserts a stated regression band at the points that
disagree, as the elimination half does, and the disagreement is filed as its
own item rather than fixed here.

## Resolution, 2026-10-18

**The early curve exists in both papers, and it is now compared point by
point.** Figure 2 of each paper was read from its page scan, and the values,
the reading method and its error are recorded in
`docs/references/yasuda-1991-figure-2-wash-in.md`. The comparison drives the
shipped patient with F_I held at the airway and compares 37 points, from 1 to
25 minutes, in
`test_early_wash_in_matches_published_human_measurement`.

**Against the pre-registration.** Sevoflurane and both isoflurane cohorts fell
in case 1: every point within 1 SD, apart from the *Anesthesiology*
isoflurane at 12.5 minutes, at +1.06 SD. That point is within the figure's
reading error of the band, and it is held to the regression band. Desflurane
matched no case as written. It rises too fast from 1 to 10 minutes, at +1.70
to +2.10 SD, and agrees from 12.5 minutes on. Case 2 named ventilation and the
lung volume as the first candidates for a fast rise. The data rule them out,
because the isoflurane breathed by the same eight volunteers agrees, and an
operating-point error would move both agents together. The pre-registration
did not foresee a disagreement confined to one agent. The cause is filed as
`PL-CM1B`. Its five points from 1 to 10 minutes, and the isoflurane point at
12.5 minutes, are held to a band from -1 SD to +2.5 SD.

**What the gate can resolve now.** The edge search was repeated with the
early points in the gate. The alveolar gas volume that `PL-9YHR` found
unseen is now caught from above: doubled, it moves sevoflurane's 1-minute
F_A/F_I from 0.537 to 0.429, -2.85 SD, and the gate fails at +19% to +33%.
Blood:gas and the vessel-rich group are now held to a few percent on both
sides for sevoflurane and isoflurane. Many of those edges are narrow because
the model already sits at +0.75 to +0.94 SD at 12.5 and 15 minutes, and
`docs/MODEL.md` § "What the published-data gate can and cannot resolve" says
so beside the table. Smaller circuits and fat still go unseen.

**What changed in the resolving-power cases.** The edge search showed that
three changes the gate could not see before are now detected: vessel-rich
tissue:gas x0.80, the alveolar gas volume halved for isoflurane, and the
venous pool doubled for sevoflurane and isoflurane. They left
`UNDETECTED_CHANGES`. `DETECTED_CHANGES` now uses blood:gas x0.90 and x1.15,
vessel-rich tissue:gas x0.80 and x1.75, and alveolar gas volume x1.50.

**Not done here.** The points before 1 minute were not taken, because the
first-breath and 0.75-minute markers crowd the axis. The early comparison
runs only at the papers' own square-wave delivery, so the shipped circuit's
filling is not part of it. Both papers gave nitrous oxide as background,
which the model does not carry, and `docs/MODEL.md` says so.
