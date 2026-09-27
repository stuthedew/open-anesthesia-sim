---
id: PL-HBH2
title: docs/MODEL.md's fat-perfusion note weighs the stored fat flow against Heinonen's PET adipose perfusion alone, though Yasuda 1991's two human washout fits put the fat group's time constant (1,340-2,130 min) and flow (2.1-2.4 mL/100 mL/min) where the stored parameters already sit (1,496-2,603 min, 2.07), so its 'would over-estimate fat loading' reading may be one-sided
priority: P1
effort: S
status: ready
classes: science, docs
feature: late-washout-evidence
touches: docs/MODEL.md, src/anesthesia_sim/data/patients/reference_adult.json
added: 2026-09-26
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
