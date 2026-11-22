---
id: PL-Z06P
title: docs/MODEL.md says Gas Man tracks four compartments, and Gas Man's own parameter file lists six volumes
priority: P2
effort: S
status: done
classes: defect
feature: model-spec-accuracy
milestone: v0.6.19
touches: docs/MODEL.md
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-21
pr: 2190
payoff: docs/MODEL.md describes Gas Man's compartments as its cited source and its own parameter file do, circuit and venous volume included
verify: grep -qF 'the circuit as a fifth' docs/MODEL.md
---

**Problem.** docs/MODEL.md says Gas Man tracks four compartments, and Gas Man's own parameter file lists six volumes

**Why it matters.** The sentence describes the program that most of the stored values come from. A reader who compares it with § "Parameter provenance" finds a circuit volume and a venous volume that the sentence leaves out, and cannot tell which passage is right.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. It was not corrected there, because the correction depends on what two cited sources say, and neither was read.

**What the document says.** § "Model boundary": "Gas Man tracks four compartments: alveolar gas and the vessel-rich, muscle, and fat groups."

**What the tree records.** The first `sources` entry of `src/anesthesia_sim/data/patients/reference_adult.json` quotes the Workbook's Appendix C listing of `GASMAN.INI`: "[Volumes] CKT=8.0, ALV=2.5, VRG=6.0, MUS=33.0, FAT=14.5, VEN=1.0". That is six volumes, with a circuit and a venous pool among them. § "Parameter provenance" gives Gas Man's 1.0 L venous pool a mixed-venous time constant, and says a run that reproduces a published Gas Man trajectory must set the circuit volume to 8.0 L. The sentence is unchanged in substance since v0.1.0, before Appendix C was read on 2026-09-15.

**What to do.** Read the two sources the passage cites (the STA abstract and the *BMC Anesthesiology* paper) for how each describes Gas Man's compartments. If neither says four, write: "Gas Man's patient has the same alveolar gas and vessel-rich, muscle and fat groups, and its parameter file also gives a circuit volume and a venous volume (§ "Parameter provenance")." If one does, attribute the four-compartment description to it.

**Done when.** The sentence agrees with Gas Man's parameter file, or names the source that describes four compartments.

**What the two sources say, read 2026-11-21.**

- Philip JH, Philip BK. Gas Man Version 4.1 Teaches Inhalation Kinetics. Society for Technology in Anesthesia, Abstract 57. The whole one-page abstract was read from the address `docs/MODEL.md` gives. It does not describe or count Gas Man's compartments.
- Do distribution volumes and clearances relate to tissue volumes and blood flows? A computer simulation. *BMC Anesthesiology* 2006 (PMID 16772041, doi:10.1186/1471-2253-6-7). The full text was read from PubMed Central (PMC1508141) through PubMed. Its appendix says: "In Gas Man, the patient is modeled as four compartments: the lung, vessel rich group, muscle and fat; the circuit is a fifth." It then calls the whole "the five-compartment system". It gives no venous volume.

**What was done.** The paper describes four patient compartments, so the sentence now attributes that description to it, adds the circuit as the paper does, and says that Gas Man's parameter file also gives a venous volume, with a pointer to § "Parameter provenance".

**Documents checked.** `docs/MODEL.md` §§ "Model boundary" and "Parameter provenance"; and a search of `docs/`, `README.md`, `ROADMAP.md`, `src/` and `tests/` for "four compartments" and "four-compartment". The only other description of Gas Man is in the Weber et al. note of `reference_adult.json`, which quotes that paper's own "four-compartment" sentence and says what it leaves out.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.
