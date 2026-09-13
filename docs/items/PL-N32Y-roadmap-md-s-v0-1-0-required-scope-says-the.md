---
id: PL-N32Y
title: ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas
status: untriaged
added: 2026-09-13
---

**Problem.** ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas

`ROADMAP.md` v0.1.0 § "Required scope" reads "Add sevoflurane blood:gas and
tissue:blood partition data with source provenance and validation". The blood:gas
half is right. The tissue half is not what shipped: the agent data files store
`tissue_gas_partition_coefficients`, and `TissueGroup.tissue_blood_partition_coefficient`
derives the blood-referenced form from it by dividing by blood:gas.

**Why it matters.** This is the exact confusion `PL-212V` was filed on — the
two ratios differ by a factor of $`\lambda_{b:g}`$, which is 0.65 for
sevoflurane and 0.42 for desflurane, so a reader who takes the stored numbers
for tissue:blood values reads every tissue capacity wrong by that factor. The
primary literature does not hold a convention that would catch it: Baker and
Farmery name the same quantity three ways in one chapter. `PL-212V` fixed the
specification; this is the same statement in the release history.

**The judgment this needs, and why it is not a typo fix.** A Required scope
list is a frozen record of what a release was scoped to do, so correcting one
edits history rather than a current claim. Either the line is corrected with a
note that the stored form is tissue:gas, or it is left as written and the
history is read as history. That is the project owner's call about how
`ROADMAP.md` records past releases, not a session's.

**Where.** `ROADMAP.md`, v0.1.0 § "Required scope".

**Found.** Doc sweep for `PL-H46J` and `PL-212V`, 2026-09-13.
