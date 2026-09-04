---
id: PL-F52R
title: Draw the MAC-awake reference band on the chart
priority: P1
effort: S
status: done
classes: safety, science, ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/data/agents, tools/contrast_check.py, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-08-25
closed: 2026-09-04
pr: 288
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_interface_never_predicts_a_time_to_wake_up' tests/unit/test_simulation_view.py
---

**Problem.** A washout curve on its own has no endpoint. A learner turns the
vaporizer off, watches the alveolar trace fall, and has nothing to read it against -
so "how much longer does a three-hour case take to wake up than a twenty-minute
one" has no answer on the display, even though the model computes it.

**Why it matters.** The reference is what turns the washout curve from a shape into
a conclusion, and context-sensitive emergence is the lesson the compressed playback
(PL-SN2C) exists to make reachable. Without it the milestone delivers the ability to
watch a washout and not the ability to draw anything from it.

**Safety notes.** This is the item in the milestone closest to clinical prediction,
and the distinction has to be built in rather than disclaimed. Draw a *band* on the
chart, labelled as a population value for return of responsiveness. Never a readout
of the form "time to wake-up: 14 min": that reads as a prediction for this patient,
which the model does not support and which no amount of surrounding disclaimer
undoes. MAC-awake is also a different endpoint from MAC - responsiveness to command
rather than movement to incision - and the label has to say which.

**First step.** The value is not established and must not be taken from memory.
Source MAC-awake for each of the three agents from the primary literature, record it
in the agent data files with its citation the way `mac_percent` already is, and
check whether one fraction of MAC covers all three or whether each needs its own
value. The band follows the sources; do not draw it before they exist. Depends on
PL-DHV7 for the unit.

**Required property - which trace the band is read against.** The band must be
read against the *vessel-rich* trace, or against both alveolar and vessel-rich
with the difference between them stated. Measured on a 3-hour 1 MAC sevoflurane
case with the vaporizer turned off at 10 L/min: alveolar crosses 0.33 MAC at
3.01 min and vessel-rich at 6.72 min - 2.2x earlier.

The model has no effect-site compartment and defines F_a === F_A, so the
alveolar trace is the fastest curve on the chart and the furthest from where
responsiveness actually returns. A single band drawn across a six-trace chart
is read against whichever trace the eye reaches first, and that systematically
teaches an early wake-up - the opposite of the lesson the milestone exists to
deliver, and the direction with clinical consequence if it were carried across.

This is a distinct hazard from the one the Safety notes already guard. That
guard - never a per-patient time prediction - protects against over-reading the
number. This protects against reading a correct number against the wrong
compartment, which no amount of labelling the band as a population value
addresses.


**Appended 2026-09-01 — the primary source, and why it makes the trace choice
decide the number.** The **First step.** above requires MAC-awake to be sourced
from the primary literature rather than memory. An external review supplies it:

> Katoh T, Suguro Y, Kimura T, Ikeda K. Cerebral awakening concentration of
> sevoflurane and isoflurane predicted during slow and fast alveolar washout.
> Anesth Analg. 1993;77(5):1012-7. PMID 8214700.
> doi:10.1213/00000539-199311000-00024

| Washout | Sevoflurane | Isoflurane |
| --- | --- | --- |
| Slow | 0.34 ± 0.05 | 0.31 ± 0.05 |
| Fast | 0.22 ± 0.07 | 0.22 ± 0.05 |

**This sharpens the "Required property" section above rather than repeating
it.** That section already establishes that the band must be read against the
vessel-rich trace, on the grounds that reading it against the alveolar trace
teaches an early wake-up. Katoh adds the reason the two are not
interchangeable *values*: the paper attributes the slow/fast difference to
end-tidal-to-arterial and arterial-to-cerebral gradients — which is precisely
what this simulator represents as the alveolar-to-vessel-rich difference. So
the trace choice does not merely change how the band is interpreted; it
changes which published number is the correct one to draw.

0.34 is the value that belongs against the vessel-rich trace. 0.22 is the
value that belongs against the alveolar trace during a fast washout. Drawing
0.34 against the alveolar trace — the intuitive choice, since alveolar is the
number a monitor shows — over-predicts time to wakefulness, the clinically
wrong direction and the same failure the section above identifies, now with a
magnitude attached.

**A gap this source leaves.** Katoh covers sevoflurane and isoflurane only.
The **First step.** asks whether one fraction of MAC covers all three agents;
this source cannot answer that for desflurane, which still needs its own
primary citation before the band is drawn for it. Do not extrapolate the
sevoflurane fraction to desflurane.

**Who sources what is left (2026-09-02).** Desflurane's MAC-awake is the one
value still missing, and the working arrangement is that a session proposes it
with its primary citation and the project owner reviews rather than searches —
the reviewer is a physician, the searching is not the scarce half. Two limits
on that: a proposed value is a *candidate* until the owner has seen the source,
and nothing is written into a data file before then; and the Katoh values above
were verified by an external review rather than by any session here, so they
are owed the same read before the band is drawn from them.

**Found.** External multi-domain review, relayed by the project owner
2026-09-01; the bibliographic values are as that review verified them and were
not re-derived here.

**Appended 2026-09-02 — desflurane's candidate value, and the denominator trap
it comes with.** Retrieved from PubMed; both values are *candidates* pending the
project owner's read of the sources, and nothing is written into
`desflurane.json` here.

> Chortkoff BS, Eger EI II, Crankshaw DP, Gonsowski CT, Dutton RC, Ionescu P.
> Concentrations of desflurane and propofol that suppress response to command
> in humans. Anesth Analg. 1995;81(4):737-43. PMID 7574003.
> doi:10.1097/00000539-199510000-00014

> Song J-G, Cao Y-F, Yang L-Q, Yu W-F, Li Q, Song J-C, Fu X-Y, Fu Q. Awakening
> concentration of desflurane is decreased in patients with obstructive
> jaundice. Anesthesiology. 2005;102(3):562-5. PMID 15731594.
> doi:10.1097/00000542-200503000-00014

> Rampil IJ, Lockhart SH, Zwass MS, Peterson N, Yasuda N, Eger EI II, Weiskopf
> RB, Damask MC. Clinical characteristics of desflurane in surgical patients:
> minimum alveolar concentration. Anesthesiology. 1991;74(3):429-33.
> PMID 2001020. doi:10.1097/00000542-199103000-00007

| Source | Population | MAC-awake | As a fraction |
| --- | --- | --- | --- |
| Chortkoff 1995 | 22 male volunteers | 2.60 ± 0.46 % | **0.36 MAC**, stated in the paper |
| Song 2005 (control arm) | non-jaundiced surgical patients | 2.17 ± 0.25 % | 0.36 MAC against Rampil's 31–65 yr MAC |

**The two agree at 0.36 MAC, and that agreement is the reason to trust it** —
different populations, different countries, twelve years apart, and neither
derived from the other. It also sits in order beside Katoh above: isoflurane
0.31, sevoflurane 0.34, desflurane 0.36. So the **First step.**'s question is
answered: one fraction does *not* cover all three, but the spread is narrow
(0.31–0.36) and each agent should carry its own value.

**The trap, and why this section exists.** Chortkoff's 0.36 is anchored to a
MAC of 7.22 % (2.60/0.36), which is Rampil's **18–30 yr** figure of 7.25 %.
This repository records `mac_percent: 6.0`, which is Rampil's **31–65 yr**
figure. Taking Chortkoff's *absolute* 2.60 % and dividing it by the 6.0 % in
the data file gives **0.433 MAC — 20 % higher than the published 0.36**, and
in the direction that draws the band too high and teaches a *later* wake-up
than the literature supports.

Song's 2.17 % avoids this only because its population matches the 6.0 %
denominator; it is a coincidence of age-matching, not a general safeguard.

Two consequences for the implementation:

- **Store the fraction, never the absolute percent.** Katoh already expressed
  MAC-awake "as a ratio to age-adjusted MAC", so the fraction is what all
  three sources actually share, and it is the only form that stays correct if
  `mac_percent` is ever changed or made age-aware (`PL-DHV7`, the MAC display
  unit, and the Nickalls/Mapleson age note already in `desflurane.json`).
- **Record which MAC each fraction was derived against**, because the number
  is meaningless without it. A fraction with no stated denominator is exactly
  the "correct number with the wrong context" failure `CLAUDE.md` names.

**A limitation to record with the value.** Katoh's slow-washout arm is
*descending* (15-min equilibration steps during washout); Chortkoff and Song
both determined MAC-awake by *ascending* stepwise equilibration. All three are
equilibrated rather than fast-washout determinations, which is why 0.36 belongs
against the vessel-rich trace alongside Katoh's 0.34/0.31 rather than against
the alveolar trace. But ascending and descending determinations are not
interchangeable, and no descending-washout desflurane MAC-awake was found on
PubMed. State that in `docs/MODEL.md` rather than presenting the three agents'
fractions as if they were measured identically.

**Appended 2026-09-02 — the project owner asks for two references, not one.**
"Would want MAC-awake and 1 MAC and make them clear what they are (visually
distinct)". This is a scope change to the section above, which specified a
single band, and it is the right one: Chortkoff 1995 states that *"along with
pharmacokinetics, the ratio of the awakening concentration to the anesthetizing
concentration (MAC-awake/MAC) determines time to awakening"*. Drawing both
makes that ratio the visible gap between them, so the chart shows the decrement
required for arousal rather than only the endpoint. That is the
context-sensitive emergence lesson stated geometrically.

**Let the mark type carry the distinction, not the colour.** The two references
differ in epistemic status, and the mark should say so:

| | Mark | Why |
| --- | --- | --- |
| MAC-awake | a **band** | A measured population value with real spread — Katoh ± 0.05 MAC, Chortkoff ± 0.46 % |
| 1 MAC | a **line** | A definitional anchor, not a distribution of the same kind |

Band-versus-line is a stronger separation than any colour pair, it reads
correctly in greyscale and with any colour-vision deficiency, and it satisfies
`.claude/rules/ui-color.md`'s "colour is never the only channel carrying a
distinction" without needing a second cue bolted on. Add line style and an
inline text label on each, and register every new colour in
`tools/contrast_check.py`'s `REQUIREMENTS` in the same change, naming the
background each is actually drawn on — the rule the tool cannot check for
itself.

**The hazard this introduces: the two references belong against *different*
traces.** MAC is by name and determination an *alveolar* quantity — Rampil 1991
determined desflurane's MAC as an end-tidal percentage in surgical patients.
The MAC-awake value this item draws is Katoh's slow-washout figure, which the
**Required property** section above already establishes belongs against the
*vessel-rich* trace, and which Katoh attributes to end-tidal-to-arterial and
arterial-to-cerebral gradients — exactly the alveolar-to-vessel-rich difference
this simulator represents.

Two horizontal lines across one chart implicitly invite reading both against
whichever trace the eye reaches first. That is the hazard the **Required
property** section names, now doubled: there are two chances to read against
the wrong curve rather than one.

**But the two are not equally trace-sensitive, and the asymmetry is the design
answer.** After a long case at a steady setpoint the alveolar and vessel-rich
traces have converged, so the 1 MAC anchor is robust to which one it is read
against. At MAC-awake they have not converged — measured in the section above
as 3.01 min versus 6.72 min, 2.2x — so the *lower* reference is the
trace-critical one. So: spend the labelling budget on the MAC-awake band, and
do not let the 1 MAC line acquire equal visual weight merely because it is
easier to draw.

One consequence worth expecting rather than treating as a bug: on a short case
the vessel-rich trace never reaches the 1 MAC line, because it never
equilibrated. That is true and worth teaching, not a rendering fault.

**One decision, taken here rather than handed on.** The 1 MAC line is the
*nominal* 1 MAC from `mac_percent`, not the setpoint the learner happened to
dial. A fixed reference stays comparable across runs, which is what makes the
twenty-minute and three-hour cases answerable side by side; a line tracking the
dialled concentration would only restate where the trace already starts. Note
that `mac_percent` here is a flat adult value rather than age-adjusted (the
Nickalls/Mapleson note in the agent data files), while Katoh expressed
MAC-awake as a ratio to *age-adjusted* MAC — so the label must say "1 MAC
(reference adult)" rather than implying a patient-specific value.

> Eger EI II, Saidman LJ, Brandstater B. Minimum alveolar anesthetic
> concentration: a standard of anesthetic potency. Anesthesiology.
> 1965;26(6):756-63. PMID 5844267. doi:10.1097/00000542-196511000-00010

Cited as the origin of the term rather than for a value: the human MAC figures
this project uses come from Rampil 1991 and the Gas Man table already recorded
in the agent data files.

**Done when.** Each agent's MAC-awake value is in its data file with a cited
primary source, `docs/MODEL.md` records the provenance and states what the band does
and does not assert, the chart draws it as a labelled population band with no
per-patient time prediction anywhere in the interface, and the interface makes
clear which trace the band is to be read against.


**Closed 2026-09-04.** Every citation was retrieved from PubMed and checked
against its abstract in this session, which is what the 2026-09-02 note above
said the Katoh values were still owed: Katoh 1993 (PMID 8214700) reports
0.34 +/- 0.05 sevoflurane and 0.31 +/- 0.05 isoflurane by slow washout
"expressed as a ratio to age-adjusted MAC"; Chortkoff 1995 (PMID 7574003)
reports desflurane 2.60 +/- 0.46 % and states it as "36% of MAC"; Song 2005
(PMID 15731594) reports 2.17 +/- 0.25 % in its non-jaundiced control arm; and
Rampil 1991 (PMID 2001020) reports 7.25 % at 18-30 yr and 6.0 % at 31-65 yr.
All four match what the appends above record.

**One correction to the appends, which does not change the design.** The
2026-09-02 appends state two error directions the wrong way round: drawing
0.34 against the alveolar trace, and drawing the band 20 % too high from the
denominator mistake, were both described as teaching a *later* wake-up.
Concentration falls during emergence, so a higher reference is crossed sooner
and a faster-falling trace crosses any reference sooner - both errors
therefore teach an *earlier* wake-up, which is what the older "Required
property" section says and what the arithmetic gives. Every failure mode here
runs in that one direction, and `docs/MODEL.md` § "MAC-awake as a chart
reference" now states it once rather than twice inconsistently.

**Measured here, at the value actually drawn.** The Required-property section
measured the trace separation at 0.33 MAC. Re-measured at the band's own
centre on the same case - 3-hour 1 MAC sevoflurane, vaporizer off at 10 L/min
- the alveolar trace crosses 0.34 x MAC at 2.83 min and the vessel-rich trace
at 6.51 min, 2.30x later. `docs/MODEL.md` carries those figures.

**What landed.** `mac_awake` in all three agent data files as a validated
fraction with its standard deviation and the denominator it was derived
against; `MacAwakeReference` through `core/parameters.py` and the snapshot;
`mac_awake_band_percent` and `format_mac_awake_reference` in
`app/formatting.py`; a band and a 1 MAC line drawn behind the six traces,
each with its own legend mark type; six provenance rows; a new `docs/MODEL.md`
section; and an "Interface boundary" prohibition on displaying any
time-to-awakening figure, which `test_the_interface_never_predicts_a_time_to_wake_up`
holds against every string in the mounted tree.
