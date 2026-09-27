---
id: PL-HBH2
title: docs/MODEL.md's fat-perfusion note weighs the stored fat flow against Heinonen's PET adipose perfusion alone, though Yasuda 1991's two human washout fits put the fat group's time constant (1,340-2,130 min) and flow (2.1-2.4 mL/100 mL/min) where the stored parameters already sit (1,496-2,603 min, 2.07), so its 'would over-estimate fat loading' reading may be one-sided
priority: P1
effort: S
status: done
classes: science, docs
feature: late-washout-evidence
touches: docs/MODEL.md, src/anesthesia_sim/data/patients/reference_adult.json, docs/references/README.md, docs/items/PL-YD2V-supported-run-length-and-the-validation-section.md
added: 2026-09-26
closed: 2026-09-27
pr: 1164
payoff: a learner reading the fat trace is told that the two human sources disagree about which way its fat loading errs, instead of being told one direction as settled
verify: grep -qF 'PL-HBH2' docs/MODEL.md && grep -qF 'Yasuda' src/anesthesia_sim/data/patients/reference_adult.json
---

**Problem.** docs/MODEL.md's fat-perfusion note weighs the stored fat flow against Heinonen's PET adipose perfusion alone, though Yasuda 1991's two human washout fits put the fat group's time constant (1,340-2,130 min) and flow (2.1-2.4 mL/100 mL/min) where the stored parameters already sit (1,496-2,603 min, 2.07), so its 'would over-estimate fat loading' reading may be one-sided

**Found 2026-09-26 while working `PL-WMCJ`.** The figures are in `docs/MODEL.md` § "Known limitations", the intertissue-diffusion note that item added, which carries the table, the pages of both Yasuda 1991 papers read from the private reference corpus, and how each ratio and crossing time was computed.

**Premise checked 2026-09-27.** `docs/MODEL.md` § "Known limitations"'s
fat-perfusion paragraph ("The fat group is perfused about twice as fast as the
reachable resting measurement...") weighs the stored fat flow against Heinonen
et al. alone, and concludes that a learner reading the fat trace as a
prediction "would over-estimate fat loading". The intertissue-diffusion table
three paragraphs below puts this model's fat time constant within one standard
deviation of the fitted fat group's in three of Yasuda 1991's four cohorts. The
Heinonen entry in `src/anesthesia_sim/data/patients/reference_adult.json`,
which the paragraph names as the comparison's home, is one-sided the same way -
"the model perfuses fat at ROUGHLY TWICE this measurement, which shortens the
fat compartment's time constant and so the slow tail of every washout curve the
simulator draws" - and the file names Yasuda nowhere.

**Why it matters.** The paragraph tells a learner which way the fat trace errs,
and the two pieces of human evidence the project holds point different ways: a
PET perfusion measurement in one depot says the stored flow is about twice too
fast, and whole-body washout fits say the time constant it produces is where
human washout's slowest compartment sits. Stating one of them as the direction
of the error is the overconfident presentation of a model limitation the
safety-critical standard rules out, in the section a reader consults to learn
how far to trust the fat and washout traces.

**Done when.** The fat-perfusion paragraph weighs Heinonen's measurement
against Yasuda 1991's washout-fitted fat group - its time constant, and the
flow per 100 mL it implies at this model's fat solubility, with how that was
computed - says the two disagree about the direction of the error and why
neither settles it, and states its reading of fat loading only as far as both
support. `reference_adult.json`'s Heinonen entry names the washout comparison
beside its own, and `docs/MODEL.md` cites `PL-HBH2` where the paragraph
changes.

**Closed 2026-09-27, in the `late-washout-evidence` chain's first pull
request.** Both Yasuda 1991 papers were re-read at the source from the private
corpus for this: the *Anesth Analg* paper's text layer (pp. 319, 322-23) and
the *Anesthesiology* paper's p. 496 as a page image. The title's 2.1-2.4 mL per
100 mL per minute is the papers' own fat-group blood flow, Table 5 of each
(2.4 ± 0.6 and 2.2 ± 0.5 for sevoflurane and isoflurane; 2.1 ± 0.4 and 2.2 ±
0.2 for desflurane and isoflurane), computed by them as the fat tissue/blood
partition coefficient times the fitted mammillary rate constant (p. 319). At
this model's stored fat solubilities - fat:gas over blood:gas, 52.3, 53.8 and
31.0 - the fitted time constants of 2,120, 2,130, 1,340 and 2,090 min give 2.5,
2.5, 2.3 and 2.6, against the stored 0.06 × 5.0 L/min into 14.5 L = 2.07. The
fat-perfusion paragraph now carries both comparisons, says the PET measurement
puts the stored flow at about twice the truth and the washout fits at or a
little below, and gives the reasons neither settles it: one depot at rest
against a whole-body compartment on one side; an assigned rather than measured
compartment on the other, with fitted volumes a third to two fifths of the
stored fat, an analysis accounting for about 25 L of body volume, flow
estimates off for the vessel-rich and muscle groups, nitrous oxide throughout,
and terminal fits over days the volunteers spent out of hospital. Its reading
of fat loading is now "uncertain by up to about a factor of two, direction
unsettled". The second caution in the intertissue-diffusion note, which read the
fat-perfusion note as acting one way, was made consistent; `docs/references/README.md`'s
Yasuda extraction note records what was taken; and the Heinonen entry names the
washout comparison beside its own. `PL-YD2V`'s brief carries a note to make its
two restatements ("about twice the reachable resting measurement") two-sided
as well. Filed, not fixed here: the roadmap's varying-perfusion note still
reads the fat flow against Heinonen alone (`bin/docket new`, this branch).
